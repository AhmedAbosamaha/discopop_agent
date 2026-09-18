"""
Impact model — rank regions by the time parallelizing them would actually save
-----------------------------------------------------------------------------
The old score was `c · log₂(1 + W) − λ · 1[tier=2]`, with W an instruction-count
proxy from Data.xml.  It got the ranking wrong in a way that is easy to see once
measured times are available:

  * On example4 the sortedness CHECK loop (512 instructions) scored 9.0 while the
    SORT it verifies (1,050,624) scored 5.0 — `log₂` compresses three orders of
    magnitude into ten points, and λ then outweighs them.
  * On array_accumulator the top-ranked region was the inner `k` loop, a serial
    `x = x*c + …` recurrence that can never be parallelized, because it has the
    highest instruction count.  The outer loop — the actual Do-All, and 99.7% of
    the program's runtime — ranked below it.

Both failures come from asking "how much work is in here?" instead of "how much
of the program's runtime would parallelizing this remove?".  This module asks the
second question, in seconds, using Amdahl's law:

    S = 1 / (1 − f + f/(P·e))          predicted whole-program speedup
    ΔT = T_total · f · (1 − 1/(P·e))   predicted time saved

`f` is the region's measured share of runtime, `P` the thread count, `e` the
parallel efficiency actually observed on this machine.  ΔT is in seconds, which
is what removes the need for λ: benefit and cost are finally in the same unit.

Where `f` comes from: `.discopop/hotspot_detection/Hotspots.json`, produced by
DiscoPoP's own hotspot detection — a component the repository has always shipped
and the agent never used.  Each entry carries `fid`, `lineNum`, `typ`, `hotness`
(YES/NO/MAYBE) and `avr`, the measured average runtime.  When that file is
absent, everything here reports "no data" and the caller falls back to the old
proxy, so nothing depends on hotspot detection being available.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class Hotspot:
    """One measured region from Hotspots.json."""
    file_id: int
    line: int
    node_type: str          # "LOOP" | "FUNCTION"
    name: str
    hotness: str            # "YES" | "MAYBE" | "NO"
    avg_runtime: float      # seconds, inclusive of anything nested inside


@dataclass
class ImpactModel:
    """Measured runtime per region, and what parallelizing each would be worth.

    `total_runtime` is the whole program's measured time — taken as the largest
    inclusive time in the file, which is the outermost function (`main` measured
    0.375 s on array_accumulator while its hottest loop measured 0.374 s).  Using
    the largest observed time rather than a separate wall-clock measurement keeps
    `f` consistent with the numbers it is divided into.
    """
    by_line: Dict[Tuple[int, int], Hotspot] = field(default_factory=dict)
    total_runtime: float = 0.0
    threads: int = 1
    # Parallel efficiency, calibrated during the run (Stage 4).  1.0 means
    # perfect scaling; the first measured pragma replaces this guess with what
    # the machine actually delivered.
    efficiency: float = 1.0
    _efficiency_samples: List[float] = field(default_factory=list)
    # Regions already covered by an accepted parallelization.  Parallelizing an
    # outer loop parallelizes everything inside it, so an inner region's
    # remaining value is zero — without this the agent re-attacks time it has
    # already won.
    covered: List[Tuple[int, int, int]] = field(default_factory=list)
    # Share of the runtime each covered span accounts for, when it is known at the
    # moment of covering.  A region that CONTAINS covered spans is worth only what
    # is left after them.
    covered_time: Dict[Tuple[int, int, int], float] = field(default_factory=dict)

    @property
    def available(self) -> bool:
        return bool(self.by_line) and self.total_runtime > 0

    def lookup(self, file_id: int, start_line: int, end_line: int) -> Optional[Hotspot]:
        """The measurement for this region.

        Hotspots are keyed on their first line.  An exact match is preferred;
        failing that, the hottest measurement whose line falls inside the region
        is used, since DiscoPoP's region spans and the hotspot detector's line
        attribution do not always agree on where a loop begins.
        """
        exact = self.by_line.get((file_id, start_line))
        if exact is not None:
            return exact
        inside = [h for (f, l), h in self.by_line.items()
                  if f == file_id and start_line <= l <= end_line]
        return max(inside, key=lambda h: h.avg_runtime) if inside else None

    def fraction(self, file_id: int, start_line: int, end_line: int) -> Optional[float]:
        h = self.lookup(file_id, start_line, end_line)
        if h is None or self.total_runtime <= 0:
            return None
        return min(h.avg_runtime / self.total_runtime, 1.0)

    def remaining_fraction(
        self, file_id: int, start_line: int, end_line: int
    ) -> Optional[float]:
        """Share of the runtime still SEQUENTIAL in this region, or None if unmeasured.

        0.0 for a region inside a covered span — a loop nested in one that already
        runs in parallel has nothing left to win.  For a region that CONTAINS covered
        spans (a function one of whose loops was parallelised) it is the region's
        share minus theirs: what remains is what a further attempt could still win.
        Covering used to be all-or-nothing on the span of whatever was EDITED, which
        hid a sibling loop in the same function from Phase B and left a deeper
        restructuring level (--restructure-depth) with nothing it could ever see.
        """
        mine = [(cf, cs, ce) for cf, cs, ce in self.covered if cf == file_id]
        # Inside a parallel construct there is nothing left to win — measured or not.
        # (An unmeasured nested region used to come back as "no measurement" and
        # could then be queued on the workload proxy.)
        if any(cs <= start_line and end_line <= ce for _cf, cs, ce in mine):
            return 0.0
        f = self.fraction(file_id, start_line, end_line)
        if f is None:
            return None
        inside = [c for c in mine if start_line <= c[1] and c[2] <= end_line]
        # Only the outermost ones count: a covered loop inside a covered loop is
        # already part of the outer one's time.
        outer = [c for c in inside
                 if not any(o is not c and o[1] <= c[1] and c[2] <= o[2] for o in inside)]
        spoken = 0.0
        for c in outer:
            known = self.covered_time.get(c)
            spoken += known if known is not None else (self.fraction(*c) or 0.0)
        return max(f - spoken, 0.0)

    def predicted_saving(
        self, file_id: int, start_line: int, end_line: int
    ) -> Optional[float]:
        """ΔT in seconds, or None when this region has no measurement.

        Computed on what is still sequential (`remaining_fraction`), so it is 0.0
        for a region whose time is already spoken for.
        """
        f = self.remaining_fraction(file_id, start_line, end_line)
        if f is None:
            return None
        speedup_factor = 1.0 - 1.0 / max(self.threads * self.efficiency, 1.0)
        return self.total_runtime * f * speedup_factor

    def predicted_program_speedup(
        self, file_id: int, start_line: int, end_line: int
    ) -> Optional[float]:
        """Whole-program speedup if this one region were parallelized."""
        f = self.fraction(file_id, start_line, end_line)
        if f is None:
            return None
        parallel_part = f / max(self.threads * self.efficiency, 1e-9)
        return 1.0 / max(1.0 - f + parallel_part, 1e-9)

    def remap_lines(self, file_id: int, lmap: Dict[int, int],
                    measurements: bool = True) -> int:
        """Move the measurements onto a rewritten file, dropping what moved away.

        With `measurements=False` only the covered spans move: the runtimes were
        just re-measured on the new file and are already in its coordinates.

        Measurements are keyed by LINE, so after a rewrite shifts lines they do
        not merely go stale — they are silently mis-attributed, and a region can
        inherit the runtime of whatever used to sit at its line number.  A fast
        refresh has the exact old->new line map, so the honest thing is to
        translate what survived and discard the rest: a region with no
        measurement falls back to the workload proxy, which is wrong-ish, while
        a region with the WRONG measurement is ranked confidently and wrongly.

        Returns how many measurements were dropped.
        """
        moved: Dict[Tuple[int, int], Hotspot] = {}
        dropped = 0
        for (fid, line), hs in (self.by_line.items() if measurements else ()):
            if fid != file_id:
                moved[(fid, line)] = hs
                continue
            new_line = lmap.get(line)
            if new_line is None:
                dropped += 1
                continue
            moved[(fid, new_line)] = Hotspot(fid, new_line, hs.node_type, hs.name,
                                             hs.hotness, hs.avg_runtime)
        if measurements:
            self.by_line = moved
        # Covered spans move with the file too; one that no longer exists is
        # dropped rather than left pointing at unrelated lines.
        moved_covered: List[Tuple[int, int, int]] = []
        moved_time: Dict[Tuple[int, int, int], float] = {}
        for f, s, e in self.covered:
            if f != file_id:
                target: Optional[Tuple[int, int, int]] = (f, s, e)
            else:
                ns, ne = lmap.get(s), lmap.get(e)
                target = (f, ns, ne) if ns is not None and ne is not None else None
            if target is None:
                continue
            moved_covered.append(target)
            if (f, s, e) in self.covered_time:
                moved_time[target] = self.covered_time[(f, s, e)]
        self.covered = moved_covered
        self.covered_time = moved_time
        return dropped

    def adopt(self, fresh: "ImpactModel") -> None:
        """Take a new measurement's numbers, keep what this run has learned.

        `covered` and `efficiency` are run-level knowledge — which regions are
        already parallelized, and what this machine actually delivers — and a
        re-measurement says nothing about either.
        """
        self.by_line = fresh.by_line
        self.total_runtime = fresh.total_runtime

    def mark_covered(self, file_id: int, start_line: int, end_line: int,
                     share: Optional[float] = None) -> None:
        """Record that this span now runs in parallel.

        `share` is the runtime share it accounts for, when the caller knows it and
        the measurement keyed on the span's own line may not (a rewritten loop's
        measurement is dropped with its lines)."""
        span = (file_id, start_line, end_line)
        if span not in self.covered:
            self.covered.append(span)
        if share is not None:
            self.covered_time[span] = share

    def snapshot(self) -> Tuple[Any, ...]:
        """The line-keyed state, to put back when a rewrite is reverted."""
        return (dict(self.by_line), list(self.covered), self.total_runtime,
                dict(self.covered_time))

    def restore(self, snap: Tuple[Any, ...]) -> None:
        self.by_line, self.covered, self.total_runtime = dict(snap[0]), list(snap[1]), snap[2]
        self.covered_time = dict(snap[3]) if len(snap) > 3 else {}

    def observe_speedup(self, measured: float) -> None:
        """Calibrate efficiency from a speedup the gate actually measured.

        The gate times one binary at one thread against the same binary
        unrestricted, so `measured` is the region's own scaling, and
        `measured / P` is the efficiency that produced it.  The median of the
        samples is used so a single noisy measurement cannot swing later
        predictions.
        """
        if measured <= 0 or self.threads <= 1:
            return
        e = max(min(measured / self.threads, 1.0), 0.01)
        self._efficiency_samples.append(e)
        ordered = sorted(self._efficiency_samples)
        mid = len(ordered) // 2
        self.efficiency = (ordered[mid] if len(ordered) % 2
                           else (ordered[mid - 1] + ordered[mid]) / 2)


def load_hotspots(discopop_dir: Path, threads: Optional[int] = None) -> ImpactModel:
    """Read Hotspots.json into an ImpactModel; empty model when it is absent."""
    model = ImpactModel(threads=threads or (os.cpu_count() or 1))
    f = discopop_dir / "hotspot_detection" / "Hotspots.json"
    if not f.exists():
        return model
    try:
        raw = json.loads(f.read_text())
    except (OSError, ValueError):
        return model

    for entries in raw.values():
        if not isinstance(entries, list):
            continue
        for e in entries:
            try:
                hs = Hotspot(
                    file_id=int(e["fid"]),
                    line=int(e["lineNum"]),
                    node_type=str(e.get("typ", "")),
                    name=str(e.get("name", "")),
                    hotness=str(e.get("hotness", "MAYBE")).upper(),
                    avg_runtime=float(e.get("avr", 0.0)),
                )
            except (KeyError, TypeError, ValueError):
                continue
            key = (hs.file_id, hs.line)
            # Keep the hottest when the same line is reported more than once.
            if key not in model.by_line or hs.avg_runtime > model.by_line[key].avg_runtime:
                model.by_line[key] = hs

    if model.by_line:
        model.total_runtime = max(h.avg_runtime for h in model.by_line.values())
    return model


def run_hotspot_detection(
    source_file: str, discopop_dir: Path, binary_args: Optional[List[str]],
    env: Dict[str, str],
    run_cmd: Callable[[List[str], Path, Dict[str, str]], Tuple[bool, str]],
) -> Tuple[bool, str]:
    """Produce Hotspots.json: instrument, run once, analyse.

    Cheap — about 2 s plus one ordinary run of the program, once per session,
    and completely separate from the dependence profile.  `run_cmd` is injected
    so this module stays free of the controller's subprocess conventions.

    The instrumented binary is written under a name of its own: it must not
    replace `a.out`, which is the dependence profiler's binary and is re-run
    later.
    """
    from ..profiling.tools import InstrumentedBuild
    dp = discopop_dir.resolve()

    # C is instrumented as C (discopop_hotspot_cc), never through the C++
    # wrapper; C programs also need libm linked explicitly.  A project goes
    # through the same unity unit as the dependence profile, so both speak of
    # the same files by the same ids.
    build = InstrumentedBuild(source_file, ".dp_hotspot.out", hotspot=True)
    binary = build.binary
    try:
        ok, err = run_cmd(build.cmd, build.cwd, env)
    finally:
        build.cleanup()
    if not ok:
        return False, f"hotspot instrumentation failed: {err[-160:]}"

    ok, err = run_cmd([str(binary)] + (binary_args or []), build.cwd, env)
    if not ok:
        return False, f"the hotspot-instrumented program failed: {err[-160:]}"

    # The analyzer insists on running from inside .discopop — it resolves
    # hotspot_detection/private relative to the working directory.
    ok, err = run_cmd(["discopop_hotspot_analyzer"], dp, env)
    if not ok:
        return False, f"hotspot analyzer failed: {err[-160:]}"

    binary.unlink(missing_ok=True)
    result = dp / "hotspot_detection" / "Hotspots.json"
    if not result.exists():
        return False, "the analyzer produced no Hotspots.json"
    return True, "measured per-region runtimes are available"


def describe(model: ImpactModel, file_id: int, start: int, end: int) -> str:
    """One-line human summary of a region's measured share and predicted value."""
    f = model.fraction(file_id, start, end)
    if f is None:
        return "no measurement"
    saving = model.predicted_saving(file_id, start, end) or 0.0
    speedup = model.predicted_program_speedup(file_id, start, end) or 1.0
    h = model.lookup(file_id, start, end)
    hot = f" [{h.hotness}]" if h else ""
    return (f"{f*100:.1f}% of runtime{hot} → up to {saving*1e3:.1f} ms saved, "
            f"program {speedup:.2f}×")
