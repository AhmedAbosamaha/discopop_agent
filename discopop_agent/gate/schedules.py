"""
Running the same binary many ways, and what the differences mean
-------------------------------------------------------------------
The old correctness stage ran a patched program once and diffed its output.  One
run is one schedule, and a data race is schedule-dependent: a race that surfaces
in one interleaving out of fifty passes a single run comfortably.  The gate's
docstring already said as much — "a racy pragma can still print the right answer
on a small profiled input" — but nothing acted on it.

This stage acts on it, and it is the cheap half of the redesign: no new build,
just the same binary run several times under different OpenMP environments.  The
value is in the shape of the disagreement rather than its size, because two very
different phenomena both show up as "the numbers moved":

  Moves between runs at a FIXED thread count      -> a race.  Hard failure,
                                                     whatever the magnitude.
  Stable at fixed threads, moves ACROSS counts    -> reordered arithmetic.  This
                                                     is what a correct parallel
                                                     reduction looks like.

That distinction needs no tuning, which is what makes it worth more than any
tolerance.  A race is a defect at 1e-18; reordering is harmless at 1e-6.

One honest caveat on the fixed-thread rule.  A correct `reduction` clause may
combine per-thread partials in whatever order the threads finish, so a
reduction-bearing loop can move slightly between runs at the same thread count
without racing.  That is why the fixed-thread check is not "byte-identical" but
"agrees within the measured noise floor": structure must be identical and values
must stay inside the program's own numerical noise.  Anything past that is
treated as a race, because nothing benign moves a value that far.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from .equivalence import compare_outputs

# Enough coverage to break the "one schedule" assumption without turning the
# gate into a benchmark run.  The thread counts are small on purpose: races
# surface from having more than one thread, not from having many, and a gate
# that pinned every core would be unusable on a shared machine.
DEFAULT_THREADS: Tuple[int, ...] = (1, 2, 4)
DEFAULT_SCHEDULES: Tuple[str, ...] = ("static", "dynamic,1", "guided")
DEFAULT_REPEATS = 3


@dataclass
class ScheduleStress:
    """What the schedule matrix found."""
    ok: bool = True
    verdict: str = "stable"        # stable | race | beyond-floor | error | skipped
    hard: bool = False             # a failure no other evidence may override
    diagnostic: str = ""
    covered: List[str] = field(default_factory=list)
    max_deviation: float = 0.0
    reordered: bool = False        # values moved across thread counts, within floor
    # stdout of the anchor run (t_max, static schedule).  Carried out so the
    # caller can compare it against the REFERENCE for free: this stage only ever
    # compared its runs to EACH OTHER, so a rewrite that is perfectly
    # self-consistent and wrong passed it without comment.
    anchor: Optional[str] = None


def _run_env(
    binary: Path, work_dir: Path, binary_args: Optional[Sequence[str]],
    env_extra: Dict[str, str], timeout: int = 120,
) -> Tuple[bool, str, str]:
    """One run under a specific OpenMP environment. Returns (ok, stdout, diag)."""
    env = dict(os.environ)
    env.update(env_extra)
    try:
        r = subprocess.run(
            [str(binary)] + list(binary_args or []),
            capture_output=True, text=True, timeout=timeout, cwd=work_dir, env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "", f"run timed out ({timeout} s)"
    if r.returncode != 0:
        return False, r.stdout, f"non-zero exit ({r.returncode}):\n{r.stderr[-400:]}"
    return True, r.stdout, ""


def stress_schedules(
    binary: Path,
    work_dir: Path,
    binary_args: Optional[Sequence[str]] = None,
    floor: float = 0.0,
    threads: Sequence[int] = DEFAULT_THREADS,
    schedules: Sequence[str] = DEFAULT_SCHEDULES,
    repeats: int = DEFAULT_REPEATS,
) -> ScheduleStress:
    """Run `binary` across a small matrix of OpenMP schedules and thread counts.

    The binary must be the `-fopenmp` build; on a build without it every
    configuration is the same single-threaded program and the stage proves
    nothing (it will simply pass).
    """
    thread_list = [t for t in threads if t >= 1] or [1]
    t_max = max(thread_list)
    covered: List[str] = []

    # --- repeatability at one thread count: the race test -------------------
    anchor: Optional[str] = None
    for i in range(max(2, repeats)):
        ok, out, diag = _run_env(
            binary, work_dir, binary_args,
            {"OMP_NUM_THREADS": str(t_max), "OMP_SCHEDULE": "static"},
        )
        if not ok:
            return ScheduleStress(
                ok=False, verdict="error", hard=True,
                diagnostic=f"run failed at {t_max} threads: {diag}",
                covered=covered,
            )
        covered.append(f"T{t_max}/static#{i + 1}")
        if anchor is None:
            anchor = out
            continue
        m = compare_outputs(anchor, out, floor)
        if not m.equal:
            return ScheduleStress(
                ok=False, verdict="race", hard=True, covered=covered,
                max_deviation=m.max_deviation,
                diagnostic=(
                    f"the program does not repeat itself: two runs at the SAME "
                    f"thread count ({t_max}) printed different output. That is a "
                    f"data race, independent of how small the difference is.\n"
                    f"{m.diagnostic}"
                ),
            )
    assert anchor is not None

    # --- variation across thread counts and schedules -----------------------
    worst = 0.0
    reordered = False
    configs: List[Tuple[int, str]] = [(t, "static") for t in thread_list if t != t_max]
    configs += [(t_max, s) for s in schedules if s != "static"]
    for t, sched in configs:
        ok, out, diag = _run_env(
            binary, work_dir, binary_args,
            {"OMP_NUM_THREADS": str(t), "OMP_SCHEDULE": sched},
        )
        if not ok:
            return ScheduleStress(
                ok=False, verdict="error", hard=True, covered=covered,
                diagnostic=f"run failed at {t} threads, schedule {sched}: {diag}",
            )
        covered.append(f"T{t}/{sched}")
        m = compare_outputs(anchor, out, floor)
        worst = max(worst, m.max_deviation)
        if not m.equal:
            # Structural and integer changes are never a scheduling artefact.
            hard = m.mode in ("structural", "integer")
            return ScheduleStress(
                ok=False, verdict="race" if hard else "beyond-floor", hard=hard,
                covered=covered, max_deviation=m.max_deviation,
                diagnostic=(
                    f"output changed at {t} threads with schedule {sched} "
                    f"relative to {t_max} threads.\n{m.diagnostic}"
                ),
            )
        if m.mode == "numeric":
            reordered = True

    return ScheduleStress(
        ok=True, verdict="stable", covered=covered, anchor=anchor,
        max_deviation=worst, reordered=reordered,
        diagnostic=(
            f"stable across {len(covered)} configurations"
            + (f"; values moved by up to {worst:.2e} of output scale across "
               f"thread counts (reordered arithmetic)" if reordered else "")
        ),
    )
