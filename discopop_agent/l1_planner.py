"""
L1 Planning Layer
-----------------
Discovers every profiled code region (loops, functions, CUs) from
Data.xml and the profiler text files, matches them against DiscoPoP
patterns (Tier-1), and scores every candidate.

Regions with an applicable Tier-1 pattern are scored at tier=1.
Regions with no pattern but non-trivial workload become tier=2 candidates
for LLM-driven restructuring.

Score formula (thesis):
    score = c · log₂(1 + Ŝ) − λ · 1[tier=2]
    c = pattern confidence, Ŝ = workload proxy, λ = LLM-tier penalty
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .types import CodeRegion, HotspotCandidate

_CONFIDENCE: Dict[str, float] = {
    "do_all": 1.0,
    "reduction": 0.9,
    "pipeline": 0.7,
    "task_parallelism": 0.6,
    "gpu_pattern": 0.5,
    "combined_gpu_pattern": 0.5,
}
_SKIP_PATTERN_TYPES = {"optimizer_output", "merged_pattern"}

# Minimum workload for a region to be considered a Tier-2 candidate
_MIN_WORKLOAD_TIER2 = 100


# ---------------------------------------------------------------------------
# Data.xml parser
# ---------------------------------------------------------------------------

def _parse_data_xml(profiler_dir: Path) -> List[CodeRegion]:
    """
    Parse Data.xml (which may contain multiple <Nodes> root elements from
    repeated profiling runs) and return unique CodeRegion objects.

    Node types in DiscoPoP:
        0 = CU (computational unit / basic block)
        1 = Function
        2 = Loop
    """
    xml_path = profiler_dir / "Data.xml"
    if not xml_path.exists():
        return []

    text = xml_path.read_text()

    # Wrap repeated <Nodes>…</Nodes> blocks into a single root for parsing
    wrapped = "<Root>" + text + "</Root>"

    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(wrapped)
    except ET.ParseError:
        return []

    seen_ids: set = set()
    regions: List[CodeRegion] = []

    for node in root.iter("Node"):
        nid = node.get("id", "")
        if nid in seen_ids:
            continue
        seen_ids.add(nid)

        ntype_raw = node.get("type", "")
        if ntype_raw == "0":
            ntype = "cu"
        elif ntype_raw == "1":
            ntype = "function"
        elif ntype_raw == "2":
            ntype = "loop"
        else:
            continue

        name = node.get("name", "")

        def _parse_line(attr: str) -> Tuple[int, int]:
            """Parse "file_id:line" attributes → (file_id, line)."""
            val = node.get(attr, "1:0").strip()
            parts = val.split(":")
            try:
                return int(parts[0]), int(parts[1])
            except (IndexError, ValueError):
                return 1, 0

        file_id, start_line = _parse_line("startsAtLine")
        _, end_line = _parse_line("endsAtLine")

        # Workload from instructionsCount for CUs only.
        # Loops get a proxy (iteration_count × body_size) below.
        # Functions have no fallback and remain 0.
        workload = 0
        ic = node.find("instructionsCount")
        if ic is not None and ic.text:
            try:
                workload = int(ic.text.strip())
            except ValueError:
                pass

        regions.append(CodeRegion(
            region_id=nid,
            region_type=ntype,
            name=name,
            file_id=file_id,
            start_line=start_line,
            end_line=end_line,
            iteration_count=1,
            workload=workload,
        ))

    return regions


# ---------------------------------------------------------------------------
# Profiler text-file parsers
# ---------------------------------------------------------------------------

def _load_loop_counts(profiler_dir: Path) -> Dict[str, int]:
    """Parse loop_counter_output.txt → {file_id:start_line: iteration_count}."""
    counts: Dict[str, int] = {}
    f = profiler_dir / "loop_counter_output.txt"
    if not f.exists():
        return counts
    for line in f.read_text().splitlines():
        parts = line.strip().split()
        if len(parts) >= 3:
            counts[f"{parts[0]}:{parts[1]}"] = int(parts[2])
    return counts


def _load_patterns(patterns_path: Path) -> Dict[str, Tuple[str, dict]]:
    """
    Index patterns.json by both start_line and node_id.
    Returns {key: (pattern_type, pattern_dict)}.
    """
    import json
    index: Dict[str, Tuple[str, dict]] = {}
    if not patterns_path.exists():
        return index
    data = json.loads(patterns_path.read_text())
    for ptype, plist in data.get("patterns", {}).items():
        if ptype in _SKIP_PATTERN_TYPES:
            continue
        for p in plist:
            for key in (p.get("start_line", ""), p.get("node_id", "")):
                if key and key not in index:
                    index[key] = (ptype, p)
    return index


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
) -> List[HotspotCandidate]:
    """
    Return hotspot candidates sorted by score descending.
    Regions whose workload estimate is below min_workload are excluded so
    the controller never wastes budget on trivially small regions.
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

        # Refine workload from pattern if available
        workload = region.workload
        if pattern:
            p_workload = pattern.get("workload", 0)
            if p_workload > workload:
                workload = p_workload

        workload_est = _workload_estimate(workload)
        score = _score(workload, confidence, tier, lambda_penalty)

        # Skip regions whose workload estimate falls below the threshold.
        # For Tier-1 the check uses the raw workload estimate; for Tier-2
        # the λ penalty already makes low-workload regions score negatively,
        # but we apply the threshold explicitly to both tiers for clarity.
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
        ))

    candidates.sort(key=lambda c: -c.score)
    return candidates
