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
from typing import Any, Dict, List, Optional, Set, Tuple

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


def demangle(name: str) -> str:
    """The plain name of an Itanium-mangled C++ symbol, or `name` unchanged.

    DiscoPoP writes C++ function names mangled into Data.xml — `_Z7computeiiPd…`,
    `_ZL7pb_emitd` for a file-local `static` function, `_ZN3foo3barE…` for a
    nested one — while everything that NAMES a function (``--exclude-functions``,
    the source text, the model's prompt) uses the plain name. Returning the
    innermost identifier is exactly what those comparisons need; parameter types,
    template arguments and ABI tags are dropped. C names are returned unchanged.
    """
    import re
    if not name.startswith("_Z"):
        return name
    if name.startswith("_ZZ"):
        # A `static` local: `_ZZ4mainE7contrib` is `contrib` inside main().  The
        # entity follows the LAST `E<len>` whose length fits what remains (an
        # optional `_<n>` discriminator may trail it).
        for hit in reversed(list(re.finditer(r"E(\d+)", name))):
            n, start = int(hit.group(1)), hit.end()
            rest = name[start + n:]
            if n and start + n <= len(name) and re.fullmatch(r"(_\d*)?", rest):
                return name[start:start + n]
        return name
    i = 2
    if name.startswith("L", i):             # internal linkage (static)
        i += 1
    nested = name.startswith("N", i)
    if nested:
        i += 1
        while i < len(name) and name[i] in "rVKOR":   # cv/ref qualifiers
            i += 1
        if name.startswith("St", i):         # std::
            i += 2
    last = ""
    while i < len(name):
        m = re.match(r"\d+", name[i:])
        if not m:
            break
        n = int(m.group(0))
        i += len(m.group(0))
        if i + n > len(name):
            break
        last = name[i:i + n]
        i += n
        if not nested:
            break
        while name.startswith("B", i):        # ABI tag, e.g. B8ne190107
            t = re.match(r"B(\d+)", name[i:])
            if not t:
                break
            i += len(t.group(0)) + int(t.group(1))
        if i < len(name) and name[i] in "EI":
            break
    return last or name


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

    seen_ids: Set[str] = set()
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


# Which pattern speaks for a loop when DiscoPoP reports several on one line.  The
# loop patterns come first because they are the ones DiscoPoP generates a patch
# for; `reduction` leads `do_all` because where both are reported the reduction
# pattern is the one that carries the accumulator's clause.
_PATTERN_PREFERENCE = ("reduction", "do_all", "pipeline", "geometric_decomposition",
                       "task", "task_parallelism")


def _pattern_rank(ptype: str, pattern: Dict[str, Any]) -> Tuple[int, int]:
    applicable = str(pattern.get("applicable_pattern")) == "True"
    order = (_PATTERN_PREFERENCE.index(ptype) if ptype in _PATTERN_PREFERENCE
             else len(_PATTERN_PREFERENCE))
    return (0 if applicable else 1, order)


def line_key(file_id: int, line: int) -> str:
    return f"L{file_id}:{line}"


def node_key(node_id: str) -> str:
    return f"N{node_id}"


def _load_pattern_options(patterns_path: Path) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
    """Every pattern per start line (`line_key`) and per node id (`node_key`), best
    first (see `_pattern_rank`).

    The two are DIFFERENT key spaces that happen to be spelled alike: `1:4` is line
    4 of file 1 as a start line and node 4 of file 1 as a node id.  They used to
    share one dictionary, so a function starting at line 4 was handed the pattern of
    node 1:4 — a loop somewhere else — became "already parallelisable", and was
    never sent to the model."""
    import json
    options: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    if not patterns_path.exists():
        return options
    data = json.loads(patterns_path.read_text())
    for ptype, plist in data.get("patterns", {}).items():
        if ptype in _SKIP_PATTERN_TYPES:
            continue
        for p in plist:
            keys = []
            start = str(p.get("start_line", ""))
            if ":" in start:
                try:
                    keys.append(line_key(int(start.split(":")[0]), int(start.split(":")[1])))
                except ValueError:
                    pass
            if p.get("node_id"):
                keys.append(node_key(str(p["node_id"])))
            for key in keys:
                if not any(q is p for _t, q in options.get(key, [])):
                    options.setdefault(key, []).append((ptype, p))
    for key in options:
        options[key].sort(key=lambda tp: _pattern_rank(tp[0], tp[1]))
    return options


def _load_patterns(patterns_path: Path) -> Dict[str, Tuple[str, Dict[str, Any]]]:
    """
    Index patterns.json by both start_line and node_id.
    Returns {key: (pattern_type, pattern_dict)} — the BEST pattern per key.

    It used to keep whichever pattern came FIRST in the file, and patterns.json
    lists `task` before `do_all` before `reduction`.  A task entry — which DiscoPoP
    generates no patch for, and which is usually not even applicable — therefore
    hid the loop pattern on the same line: 44 such lines across the suite (T0.6),
    each one a DiscoPoP suggestion that no arm, the DiscoPoP baseline included,
    could ever apply.  On 11 kernel lines a `do_all` likewise hid a `reduction`.
    """
    return {key: opts[0] for key, opts in _load_pattern_options(patterns_path).items()}
