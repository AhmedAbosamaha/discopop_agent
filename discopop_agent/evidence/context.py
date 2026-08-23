"""
The structural context around a region: loops, calls, trip counts, source text
-------------------------------------------------------------------------------
Everything the model needs in order to reason about a region that is not a
dependence: how the loops nest and how many iterations each activation runs, what
the region calls (and whether it recurses), which variables are local to it, and
the source itself.

Iterations PER ACTIVATION is the number that matters, not the total across
activations: each activation of a loop is its own parallel region, so it is the
per-activation count that has to cover thread startup.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


# ---------------------------------------------------------------------------
# Source region extractor
# ---------------------------------------------------------------------------


def _extract_source_region(source_file: str, start_line: int, end_line: int) -> str:
    """Return source lines [start_line-2 … end_line+2] annotated with line numbers.
    Lines inside [start_line, end_line] are marked with >>>."""
    lines = Path(source_file).read_text().splitlines()
    lo = max(0, start_line - 3)
    hi = min(len(lines), end_line + 3)
    region = []
    for i, code_line in enumerate(lines[lo:hi], start=lo + 1):
        marker = ">>>" if start_line <= i <= end_line else "   "
        region.append(f"{i:4d} {marker} {code_line}")
    return "\n".join(region)


def _read_span(source_file: str, start_line: int, end_line: int) -> str:
    """Return the raw source text for lines [start_line, end_line] (no prefixes)."""
    lines = Path(source_file).read_text().splitlines()
    return "\n".join(lines[max(0, start_line - 1):end_line])


def _lineid_line(lid: str) -> int:
    """Extract the line number from a 'fileId:line' LineID string, or -1."""
    try:
        return int(str(lid).split(":")[1])
    except (IndexError, ValueError):
        return -1


def _load_loop_trip_counts(
    profiler_dir: Path, file_id: int, start_line: int, end_line: int
) -> List[dict]:
    """Observed trip counts for loops in [start_line, end_line], read from the
    `BGN loop` markers in dynamic_dependencies.txt.

    Marker format:  `<file>:<line> BGN loop <total> <entries> <avg> <max>`
    (entries = activations of the loop, avg = iterations per activation).  These
    use file:line ids that match the source, unlike loop_counter_output.txt which
    is keyed on instrumented lines that can drift.  Returns [] if unavailable.
    """
    f = profiler_dir / "dynamic_dependencies.txt"
    if not f.exists():
        return []
    out: List[dict] = []
    for line in f.read_text().splitlines():
        parts = line.split()
        if len(parts) < 7 or parts[1] != "BGN" or parts[2] != "loop" or ":" not in parts[0]:
            continue
        try:
            fid, ln = (int(x) for x in parts[0].split(":", 1))
            total, entries, avg, mx = (int(x) for x in parts[3:7])
        except ValueError:
            continue
        if fid != file_id or not (start_line <= ln <= end_line):
            continue
        out.append({"line": ln, "total": total, "entries": entries, "avg": avg, "max": mx})
    return out


def _load_local_vars(
    discopop_dir: Path, file_id: int, start_line: int, end_line: int
) -> List[str]:
    """Names of variables DiscoPoP tracks as loop-LOCAL inside [start_line,
    end_line], read from the CU graph in explorer/detection_result_dump.json.

    Only local_vars are used: a CU's `accessMode` for a pointer/array reflects the
    pointer access, not element reads/writes, so it is unreliable for arrays —
    but the local-vs-global scope of scalars IS reliable and tells the LLM which
    scalars are already per-iteration private.  Returns [] if unavailable.
    """
    import json

    f = discopop_dir / "explorer" / "detection_result_dump.json"
    if not f.exists():
        return []
    try:
        nodes = json.loads(f.read_text())["pet"]["g"]["_node"]
    except (OSError, ValueError, KeyError, TypeError):
        return []
    names: List[str] = []
    for nd in nodes.values():
        data = nd.get("data", {}) if isinstance(nd, dict) else {}
        if "CUNode" not in str(data.get("py/object", "")) or data.get("file_id") != file_id:
            continue
        s, e = data.get("start_line"), data.get("end_line")
        if s is None or e is None or e < start_line or s > end_line:
            continue
        for v in data.get("local_vars", []) or []:
            n = v.get("name")
            if n and n not in names:
                names.append(n)
    return names


def _load_loop_nest(
    discopop_dir: Path, file_id: int, start_line: int, end_line: int
) -> List[Dict[str, Any]]:
    """Loop structure for the region, from the explorer's PEGraph LoopNodes
    (explorer/detection_result_dump.json): line span, induction variables, and
    observed iteration statistics per loop, plus a containment depth (0 =
    outermost within the region).  Returns [] if unavailable."""
    import json

    f = discopop_dir / "explorer" / "detection_result_dump.json"
    if not f.exists():
        return []
    try:
        nodes = json.loads(f.read_text())["pet"]["g"]["_node"]
    except (OSError, ValueError, KeyError, TypeError):
        return []
    loops: List[Dict[str, Any]] = []
    for nd in nodes.values():
        data = nd.get("data", {}) if isinstance(nd, dict) else {}
        if "LoopNode" not in str(data.get("py/object", "")) or data.get("file_id") != file_id:
            continue
        s, e = data.get("start_line"), data.get("end_line")
        if s is None or e is None or e < start_line or s > end_line:
            continue
        ld = data.get("loop_data") or {}
        loops.append({
            "start": s,
            "end": e,
            "index_vars": [str(v) for v in (data.get("loop_indices") or [])],
            "entries": ld.get("entry_count", 0),
            "avg": ld.get("average_iteration_count", 0),
            "total": ld.get("total_iteration_count", 0),
            "max": ld.get("maximum_iteration_count", 0),
        })
    # The dump can hold several LoopNodes for one source span (e.g. after
    # re-profiling a patched file) — keep the best-populated one per span, and
    # drop never-executed spans when at least one loop actually ran, so the
    # depth computation below sees each loop once.
    by_span: Dict[Tuple[int, int], Dict[str, Any]] = {}
    for lp in loops:
        key = (lp["start"], lp["end"])
        if key not in by_span or (lp["entries"], lp["total"]) > (
            by_span[key]["entries"], by_span[key]["total"]
        ):
            by_span[key] = lp
    loops = list(by_span.values())
    if any(lp["total"] > 0 for lp in loops):
        loops = [lp for lp in loops if lp["total"] > 0]
    loops.sort(key=lambda l: (l["start"], -l["end"]))
    for lp in loops:
        lp["depth"] = sum(
            1 for o in loops
            if o is not lp and o["start"] <= lp["start"] and o["end"] >= lp["end"]
        )
    return loops


def _demangle(name: str) -> str:
    """Best-effort Itanium demangle of a simple `_Z<len><name>...` symbol; falls
    back to the mangled name."""
    import re
    m = re.match(r"_Z(\d+)(\w+)", name)
    if m:
        n = int(m.group(1))
        if len(m.group(2)) >= n:
            return m.group(2)[:n]
    return name


def _load_calls_in_region(
    profiler_dir: Path, file_id: int, start_line: int, end_line: int,
    enclosing_function: str = "",
) -> List[Dict[str, Any]]:
    """Function calls made inside [start_line, end_line], from Data.xml's
    callsNode entries: [{line, callee, recursive}].  `recursive` is set when the
    callee is the region's own enclosing function.  Returns [] if unavailable."""
    import xml.etree.ElementTree as ET

    f = profiler_dir / "Data.xml"
    if not f.exists():
        return []
    try:
        # Data.xml holds one <Nodes> document per translation unit back-to-back;
        # wrap them in a synthetic root so ElementTree accepts the file.
        root = ET.fromstring("<DP>" + f.read_text() + "</DP>")
    except ET.ParseError:
        return []
    names = {
        n.get("id"): n.get("name", "")
        for doc in root for n in doc if n.get("name")
    }
    calls: List[Dict[str, Any]] = []
    seen: Set[Tuple[int, str]] = set()
    for doc in root:
        for n in doc:
            starts = n.get("startsAtLine", "")
            if ":" not in starts:
                continue
            fid_s, _ = starts.split(":", 1)
            if fid_s != str(file_id):
                continue
            calls_node = n.find("callsNode")
            if calls_node is None:
                continue
            for c in calls_node.findall("nodeCalled"):
                at = c.get("atLine", "")
                try:
                    line = int(at.split(":")[-1])
                except ValueError:
                    continue
                if not (start_line <= line <= end_line):
                    continue
                callee = _demangle(names.get((c.text or "").strip(), (c.text or "").strip()))
                key = (line, callee)
                if key in seen:
                    continue
                seen.add(key)
                calls.append({
                    "line": line,
                    "callee": callee,
                    "recursive": bool(enclosing_function)
                    and callee == _demangle(enclosing_function),
                })
    return sorted(calls, key=lambda c: c["line"])


def _line_text_map(source_file: str, start_line: int, end_line: int) -> Dict[int, str]:
    """{absolute line number: raw source text} for [start_line, end_line]."""
    lines = Path(source_file).read_text().splitlines()
    lo, hi = max(1, start_line), min(len(lines), end_line)
    return {i: lines[i - 1] for i in range(lo, hi + 1)}


def _brace_match_end(source_file: str, start_line: int) -> int:
    """Return the 1-based line of the closing `}` that balances the first `{` at
    or after start_line, ignoring braces in // and /* */ comments and in string /
    char literals.  Returns 0 if not found.

    DiscoPoP's function `endsAtLine` points at the last *statement*, not the
    closing brace (e.g. it reports the `return 0;` line, not the `}` after it),
    so for function-mode splicing we recompute the true span here."""
    lines = Path(source_file).read_text().splitlines()
    depth = 0
    opened = False
    in_block = False
    for idx in range(max(0, start_line - 1), len(lines)):
        line = lines[idx]
        i = 0
        while i < len(line):
            two = line[i:i + 2]
            if in_block:
                if two == "*/":
                    in_block = False
                    i += 2
                    continue
                i += 1
                continue
            if two == "//":
                break
            if two == "/*":
                in_block = True
                i += 2
                continue
            ch = line[i]
            if ch in ('"', "'"):
                q = ch
                i += 1
                while i < len(line):
                    if line[i] == "\\":
                        i += 2
                        continue
                    if line[i] == q:
                        i += 1
                        break
                    i += 1
                continue
            if ch == "{":
                depth += 1
                opened = True
            elif ch == "}":
                depth -= 1
                if opened and depth == 0:
                    return idx + 1
            i += 1
    return 0
