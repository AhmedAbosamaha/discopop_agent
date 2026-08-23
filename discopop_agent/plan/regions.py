"""
Discovering code regions from DiscoPoP's output, and identifying them stably
-----------------------------------------------------------------------------
Everything that reads `Data.xml`, the loop counters and `patterns.json` into
CodeRegion objects.

`region_fingerprint` is the important part.  DiscoPoP assigns region IDs from a
single global counter, so patching one function renumbers every region after it
— and an ID can be REASSIGNED to a completely unrelated region.  Line numbers
shift for the same reason.  The region's TEXT does not, unless that exact region
was patched, so identity across a re-profile is content-based.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..types import CodeRegion

# Aggregate entries in patterns.json, not parallelization patterns in their own
# right — matching a region against them would attribute someone else's pattern.
_SKIP_PATTERN_TYPES = {"optimizer_output", "merged_pattern"}


def region_fingerprint(
    source_file: str, start_line: int, end_line: int, name: Optional[str] = None
) -> str:
    """Content-based identity for a code region, invariant under DiscoPoP's
    global ID drift and under line-number shifts caused by patching.

    DiscoPoP assigns region IDs from a single global counter (Structs.hpp:60),
    so patching one function renumbers every region after it — IDs cannot be
    used to track a region across a re-profile, and CAN be reassigned to a
    completely different, unrelated region.  Source line numbers also shift
    when a patch adds/removes lines above a region.  The region's *text*, by
    contrast, is unchanged unless that exact region was patched.

    The fingerprint normalises whitespace and drops blank/comment lines so that
    re-indentation alone does not break the match.  The enclosing region name
    (function name, when available) is folded in to disambiguate textually
    identical sibling regions in different functions.

    Used by phases/phase_a.py to track a candidate across re-profiles (matching
    survivors to their prior queue position) and by evidence/ to give the LLM
    a STABLE per-region key (EvidencePackage.region_fingerprint) — e.g. for
    keying a real per-region LLM session, where relying on the reusable
    region_id would risk silently resuming an unrelated region's session.
    """
    try:
        lines = Path(source_file).read_text().splitlines()
        region = lines[start_line - 1 : end_line]
    except (OSError, IndexError):
        region = []

    body = "\n".join(
        ln.strip() for ln in region
        if ln.strip() and not ln.strip().startswith("//")
    )
    return f"{name or ''}␟{body}"
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


def find_enclosing_function(
    profiler_dir: Path, file_id: int, start_line: int, end_line: int
) -> Optional[CodeRegion]:
    """Return the tightest function-type region in the same file that fully
    contains [start_line, end_line], or None.  Used by --edit-mode function to
    map a target region to the function the LLM should rewrite."""
    best: Optional[CodeRegion] = None
    for r in _parse_data_xml(profiler_dir):
        if r.region_type != "function" or r.file_id != file_id:
            continue
        if r.start_line <= start_line and r.end_line >= end_line:
            if best is None or (r.end_line - r.start_line) < (best.end_line - best.start_line):
                best = r
    return best
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
