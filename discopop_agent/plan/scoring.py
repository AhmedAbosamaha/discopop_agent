"""
Choosing which regions to work on, and in what order
------------------------------------------------------
With measured runtimes (see impact.py) candidates are ranked by the time
parallelizing them would SAVE, in seconds, and two filters apply that a work
count cannot express: a region DiscoPoP measured as cold is skipped outright,
and one that cannot save `min_impact` seconds is not worth an attempt.

Without measurements the old proxy is used instead:

    score = c * log2(1 + W) - lambda * 1[tier=2]

It is kept only as a fallback.  It ranked example4's sortedness CHECK loop above
the SORT it verifies, and on priority_mix its top pick was a loop that runs for
0.1 ms — because `log2` compresses three orders of magnitude into ten points and
W counts instructions rather than time.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..types import CodeRegion, HotspotCandidate
from .impact import ImpactModel
from .regions import (_load_loop_counts, _load_patterns, _parse_data_xml)


_CONFIDENCE: Dict[str, float] = {
    "do_all": 1.0,
    "reduction": 0.9,
    "pipeline": 0.7,
    "task_parallelism": 0.6,
    "gpu_pattern": 0.5,
    "combined_gpu_pattern": 0.5,
}
# Minimum workload for a region to be considered a Tier-2 candidate
_MIN_WORKLOAD_TIER2 = 100
# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def _workload_estimate(workload: int) -> float:
    """W: profiled workload proxy used in the scoring formula and the
    min-workload gate.  (This is a static work estimate, not a measured speedup.)"""
    return float(max(0, workload))


def _score(workload: int, confidence: float, tier: int, lambda_penalty: float) -> float:
    """score = c · log₂(1 + W) − λ · 1[tier=2]"""
    return confidence * math.log2(1 + _workload_estimate(workload)) - lambda_penalty * (tier - 1)
# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_candidates(
    discopop_dir: Path,
    source_file: str,
    lambda_penalty: float,
    min_workload: float = 1.0,
    impact: "ImpactModel | None" = None,
    min_impact: float = 0.0,
    skip_cold: bool = True,
) -> List[HotspotCandidate]:
    """
    Return hotspot candidates in priority order.

    With `impact` (hotspot detection has run), regions are ordered by PREDICTED
    TIME SAVED and two filters apply that the workload proxy cannot express:
    a region DiscoPoP measured as cold (`hotness == "NO"`) is skipped outright,
    and one whose predicted saving is under `min_impact` seconds is skipped as
    not worth an attempt.  Ties go to the OUTERMOST region — an inner loop and
    the loop containing it show nearly the same time, and the outer one is the
    better target (more work per thread, and parallelizing it covers the inner).

    Without `impact` the old workload proxy and `min_workload` are used, so
    behaviour is unchanged wherever hotspot detection is unavailable.
    Covers loops, functions, and CUs — not just loops.
    """
    profiler_dir = discopop_dir / "profiler"
    patterns_path = discopop_dir / "explorer" / "patterns.json"

    regions = _parse_data_xml(profiler_dir)
    loop_counts = _load_loop_counts(profiler_dir)
    pattern_index = _load_patterns(patterns_path)

    # Annotate loop iteration counts
    for r in regions:
        if r.region_type == "loop":
            key = f"{r.file_id}:{r.start_line}"
            r.iteration_count = loop_counts.get(key, 1)
            # Workload proxy for loops: iteration_count * (end_line - start_line + 1)
            if r.workload == 0:
                r.workload = r.iteration_count * max(1, r.end_line - r.start_line)

    # Deduplicate by (file_id, start_line, end_line) — Data.xml has repeated
    # entries across profiling runs; keep the one with the highest workload
    dedup: Dict[Tuple[int, int, int], CodeRegion] = {}
    for r in regions:
        key = (r.file_id, r.start_line, r.end_line)
        if key not in dedup or r.workload > dedup[key].workload:
            dedup[key] = r
    unique_regions = list(dedup.values())

    candidates: List[HotspotCandidate] = []

    for region in unique_regions:
        # Skip trivial CUs (very low workload, not worth parallelizing)
        if region.region_type == "cu" and region.workload < _MIN_WORKLOAD_TIER2:
            continue

        # Look for a Tier-1 pattern via start_line or region_id
        pattern: Optional[dict] = None
        pattern_type: Optional[str] = None
        tier = 2
        confidence = 0.3  # base confidence for Tier-2

        for lookup_key in (
            f"{region.file_id}:{region.start_line}",
            region.region_id,
        ):
            if lookup_key in pattern_index:
                pattern_type, pattern = pattern_index[lookup_key]
                if pattern.get("applicable_pattern", False):
                    confidence = _CONFIDENCE.get(pattern_type, 0.5)
                    tier = 1
                break

        # Refine workload from pattern if available.  The new explorer may emit
        # a null/absent workload, so coerce to int before comparing.
        workload = region.workload
        if pattern:
            p_workload = pattern.get("workload", 0)
            if not isinstance(p_workload, int):
                p_workload = 0
            if p_workload > workload:
                workload = p_workload

        workload_est = _workload_estimate(workload)
        score = _score(workload, confidence, tier, lambda_penalty)

        saving = frac = None
        hotness = None
        if impact is not None and impact.available:
            saving = impact.predicted_saving(
                region.file_id, region.start_line, region.end_line
            )
            frac = impact.fraction(region.file_id, region.start_line, region.end_line)
            hs = impact.lookup(region.file_id, region.start_line, region.end_line)
            hotness = hs.hotness if hs else None

        if saving is not None:
            # Measured: rank on seconds saved, and let DiscoPoP's own verdict
            # retire the cold regions the proxy would happily have queued.
            if skip_cold and hotness == "NO":
                continue
            if saving < min_impact:
                continue
            score = saving
        else:
            # No measurement for this region — fall back to the proxy gate.
            if workload_est < min_workload:
                continue

        candidates.append(HotspotCandidate(
            region=region,
            source_file=source_file,
            pattern=pattern,
            pattern_type=pattern_type,
            confidence=confidence,
            workload_estimate=workload_est,
            score=score,
            tier=tier,
            impact_seconds=saving,
            runtime_fraction=frac,
            hotness=hotness,
        ))

    # Highest predicted saving first.  Two tie-breaks, in order:
    #   1. a LOOP beats the FUNCTION containing it.  A function's measured time
    #      is just the sum of its loops, and a loop is the thing OpenMP actually
    #      parallelizes, so at equal time the loop is the actionable unit —
    #      otherwise `main` (100% of runtime, by definition) heads every queue.
    #   2. the OUTERMOST region wins, so an enclosing loop is attempted before
    #      the loop nested inside it, whose time it already contains.
    # A FUNCTION's measured time is by definition at least that of every loop
    # inside it, so ranking on time alone puts `main` (100% of runtime) at the
    # head of every queue — and "restructure all of main" is not the actionable
    # unit.  When a loop inside a function already accounts for essentially all
    # of the function's time, the loop IS the target, and the function is
    # demoted to just below it: still ahead of smaller regions, no longer ahead
    # of the loop that carries its time.
    _COVERED_BY_LOOP = 0.9
    for c in candidates:
        if c.region.region_type != "function" or c.impact_seconds is None:
            continue
        inner = [
            o for o in candidates
            if o.region.region_type == "loop" and o.impact_seconds is not None
            and o.region.file_id == c.region.file_id
            and c.region.start_line <= o.region.start_line
            and o.region.end_line <= c.region.end_line
            and o.impact_seconds >= _COVERED_BY_LOOP * c.impact_seconds
        ]
        if inner:
            c.score = max(o.score for o in inner) * 0.999

    # Measured regions come first, then the rest.  Without this the sort
    # compares two incompatible scales: a measured region scores in SECONDS
    # (0.0003) and an unmeasured one on the log-workload proxy (19.6), so
    # sorting descending put every unmeasured region ahead of every measured one
    # — exactly backwards.  And the ordering is not arbitrary: if hotspot
    # detection ran and did not report a region, that is DiscoPoP's own
    # measurement saying the region is below its threshold, so ranking it last
    # is what the evidence supports.  With no measurements at all this term is
    # constant and the proxy ordering is unchanged.
    measured_available = impact is not None and impact.available

    def _rank(c: HotspotCandidate) -> Tuple[int, float, int]:
        unmeasured = 1 if (measured_available and c.impact_seconds is None) else 0
        # Highest predicted saving first; then the OUTERMOST region, so an
        # enclosing loop is attempted before the loop nested inside it whose
        # time it already contains.
        return (unmeasured, -c.score,
                -(c.region.end_line - c.region.start_line))

    candidates.sort(key=_rank)
    return candidates
