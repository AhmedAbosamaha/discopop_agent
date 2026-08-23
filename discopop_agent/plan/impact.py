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
from typing import Callable, Dict, List, Optional, Tuple


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

    def predicted_saving(
        self, file_id: int, start_line: int, end_line: int
    ) -> Optional[float]:
        """ΔT in seconds, or None when this region has no measurement.

        Returns 0.0 for a region already inside an accepted parallelization —
        the time is spoken for, so there is nothing left to win here.
        """
        f = self.fraction(file_id, start_line, end_line)
        if f is None:
            return None
        for cf, cs, ce in self.covered:
            if cf == file_id and cs <= start_line and end_line <= ce:
                return 0.0
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

    def remap_lines(self, file_id: int, lmap: Dict[int, int]) -> int:
        """Move the measurements onto a rewritten file, dropping what moved away.

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
        for (fid, line), hs in self.by_line.items():
            if fid != file_id:
                moved[(fid, line)] = hs
                continue
            new_line = lmap.get(line)
            if new_line is None:
                dropped += 1
                continue
            moved[(fid, new_line)] = Hotspot(fid, new_line, hs.node_type, hs.name,
                                             hs.hotness, hs.avg_runtime)
        self.by_line = moved
        # Covered spans move with the file too; one that no longer exists is
        # dropped rather than left pointing at unrelated lines.
        moved_covered: List[Tuple[int, int, int]] = []
        for f, s, e in self.covered:
            if f != file_id:
                moved_covered.append((f, s, e))
                continue
            ns, ne = lmap.get(s), lmap.get(e)
            if ns is not None and ne is not None:
                moved_covered.append((f, ns, ne))
        self.covered = moved_covered
        return dropped

    def adopt(self, fresh: "ImpactModel") -> None:
        """Take a new measurement's numbers, keep what this run has learned.

        `covered` and `efficiency` are run-level knowledge — which regions are
        already parallelized, and what this machine actually delivers — and a
        re-measurement says nothing about either.
        """
        self.by_line = fresh.by_line
        self.total_runtime = fresh.total_runtime

    def mark_covered(self, file_id: int, start_line: int, end_line: int) -> None:
        self.covered.append((file_id, start_line, end_line))

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
    src = Path(source_file).resolve()
    binary = src.parent / ".dp_hotspot.out"
    dp = discopop_dir.resolve()

    ok, err = run_cmd(["discopop_hotspot_cxx", str(src), "-o", str(binary)],
                      src.parent, env)
    if not ok:
        return False, f"hotspot instrumentation failed: {err[-160:]}"

    ok, err = run_cmd([str(binary)] + (binary_args or []), src.parent, env)
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
