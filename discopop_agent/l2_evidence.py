"""
L2 Evidence Collector
---------------------
Reads DiscoPoP profiler output and assembles a structured EvidencePackage
for any code region — loop, function body, or CU — not just loops.

Package contents (per thesis slide 10):
  - Complete annotated source region
  - RAW / WAR / WAW data dependences observed at runtime
  - Reduction variables + operation
  - Iteration / execution count
  - Tier-1 failure reason + diagnostic
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from .l1_planner import find_enclosing_function
from .types import Dependency, EvidencePackage, HotspotCandidate


# ---------------------------------------------------------------------------
# Dependency parser
# ---------------------------------------------------------------------------

def _classify_var(raw_name: str) -> Tuple[str, str]:
    """Classify a dependency's variable by its DiscoPoP memory-region tag.

    DiscoPoP names array-element accesses `GEPRESULT_<array>` (the result of a
    GetElementPtr, i.e. an indexed array/pointer access on the underlying data),
    while scalar variables (loop counters, temps, accumulators) keep their plain
    name with an `(S-…)` region id.  Distinguishing the two is decisive: a
    loop-carried dep on array elements is algorithmic (cannot be privatized away),
    whereas a scalar dep is usually a storage conflict (privatizable).

    Returns (display_name, kind) where kind is "array" or "scalar".
    """
    if raw_name.startswith("GEPRESULT"):
        base = raw_name[len("GEPRESULT"):].lstrip("_")
        return (f"{base}[]" if base else raw_name, "array")
    return (raw_name, "scalar")


def _parse_dep_line(line: str) -> List[Tuple[str, int, int, str, str]]:
    """Parse one line of dynamic_dependencies.txt.

    Format: <instr>@<from_line> NOM  <DEP_TYPE> <instr>@<to_line>|<var>(<region>) …
    Returns list of (dep_type, from_line, to_line, variable, kind).
    """
    results: List[Tuple[str, int, int, str, str]] = []
    parts = line.strip().split()
    if len(parts) < 4:
        return results

    from_part = parts[0]
    from_line = int(from_part.split("@")[1]) if "@" in from_part else 0

    dep_type = parts[2]
    if dep_type not in ("RAW", "WAR", "WAW"):
        return results

    for target in parts[3:]:
        if "|" not in target:
            continue
        to_part, var_part = target.split("|", 1)
        to_line = int(to_part.split("@")[1]) if "@" in to_part else 0
        variable, kind = _classify_var(var_part.split("(")[0])
        results.append((dep_type, from_line, to_line, variable, kind))

    return results


def _load_dependencies(
    profiler_dir: Path,
    start_line: int,
    end_line: int,
) -> Tuple[List[Dependency], List[Dependency], List[Dependency]]:
    """Load deps where at least one endpoint falls inside [start_line, end_line]."""
    raw: List[Dependency] = []
    war: List[Dependency] = []
    waw: List[Dependency] = []

    dep_file = profiler_dir / "dynamic_dependencies.txt"
    if not dep_file.exists():
        return raw, war, waw

    for line in dep_file.read_text().splitlines():
        if not line.strip() or line.startswith("START"):
            continue
        for dep_type, fl, tl, var, kind in _parse_dep_line(line):
            in_region = (start_line <= fl <= end_line) or (start_line <= tl <= end_line)
            if not in_region:
                continue
            dep = Dependency(dep_type=dep_type, from_line=fl, to_line=tl, variable=var, kind=kind)
            if dep_type == "RAW":
                raw.append(dep)
            elif dep_type == "WAR":
                war.append(dep)
            else:
                waw.append(dep)

    def _dedup(deps: List[Dependency]) -> List[Dependency]:
        seen = set()
        out = []
        for d in deps:
            key = (d.dep_type, d.from_line, d.to_line, d.variable, d.kind)
            if key not in seen:
                seen.add(key)
                out.append(d)
        return out

    return _dedup(raw), _dedup(war), _dedup(waw)


# ---------------------------------------------------------------------------
# Reduction parser
# ---------------------------------------------------------------------------

def _load_reductions(profiler_dir: Path, start_line: int, end_line: int) -> List[str]:
    """Load reduction variables for any region overlapping [start_line, end_line]."""
    reds: List[str] = []
    red_file = profiler_dir / "reduction.txt"
    if not red_file.exists():
        return reds

    for line in red_file.read_text().splitlines():
        if "Loop Line Number" not in line:
            continue
        fields = {}
        for segment in line.split("  "):
            if ":" in segment:
                k, _, v = segment.partition(":")
                fields[k.strip()] = v.strip()
        try:
            region_line = int(fields.get("Loop Line Number", -1))
        except ValueError:
            continue
        if start_line <= region_line <= end_line:
            var = fields.get("Variable Name", "")
            op = fields.get("Operation Name", "")
            if var:
                reds.append(f"{var} ({op})" if op else var)

    return list(dict.fromkeys(reds))


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


def _load_prevented_deps(
    discopop_dir: Path, file_id: int, start_line: int, end_line: int
) -> List[dict]:
    """Load the Do-All blockers DiscoPoP's new detector recorded for this region.

    Reads explorer/doall_prevented.json (written by new_do_all_detector) and
    returns entries whose loop overlaps [start_line, end_line] in the same file,
    or whose blocking dependency's source/sink line falls inside the region.
    Returns [] if the file is absent (e.g. old explorer) or nothing matches.
    """
    import json

    f = discopop_dir / "explorer" / "doall_prevented.json"
    if not f.exists():
        return []
    try:
        records = json.loads(f.read_text())
    except (OSError, ValueError):
        return []

    matched: List[dict] = []
    for rec in records:
        lf = rec.get("loop_file")
        ls, le = rec.get("loop_start"), rec.get("loop_end")
        loop_overlaps = (
            lf == file_id and ls is not None and le is not None
            and not (le < start_line or ls > end_line)
        )
        src_ln, snk_ln = _lineid_line(rec.get("source_line", "")), _lineid_line(rec.get("sink_line", ""))
        dep_in_region = (start_line <= src_ln <= end_line) or (start_line <= snk_ln <= end_line)
        if loop_overlaps or dep_in_region:
            matched.append(rec)
    return matched


def _var_classification(pattern: Optional[dict]) -> dict:
    """Pull DiscoPoP's OpenMP data-sharing classification out of a detected
    pattern (a patterns.json entry, carried on the candidate).

    Returns a dict with lists for shared / private / first_private / last_private
    / reduction.  Empty ({}) when no pattern was detected for the region, in which
    case DiscoPoP has no classification to offer.  Pattern entries may be plain
    variable-name strings or dicts carrying a 'name' field; both are handled.
    """
    if not pattern:
        return {}

    def _names(key: str) -> List[str]:
        out: List[str] = []
        for v in pattern.get(key) or []:
            out.append(str(v.get("name", v)) if isinstance(v, dict) else str(v))
        return out

    return {
        "shared": _names("shared"),
        "private": _names("private"),
        "first_private": _names("first_private"),
        "last_private": _names("last_private"),
        "reduction": _names("reduction"),
    }


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


def _all_observed_dep_vars(profiler_dir: Path) -> set:
    """Every variable name that appears in ANY runtime (dynamic) dependence in the
    whole program.  Used as the reference for static-only detection: a variable
    observed dynamically anywhere is NOT spurious, even if a given region's window
    didn't capture that dep.  (Comparing against only a region's dynamic deps
    wrongly flags loop-induction variables, whose deps often sit at the loop
    header just outside the body window.)"""
    f = profiler_dir / "dynamic_dependencies.txt"
    out: set = set()
    if not f.exists():
        return out
    for line in f.read_text().splitlines():
        if not line.strip() or line.startswith("START"):
            continue
        for _dt, _fl, _tl, var, _kind in _parse_dep_line(line):
            out.add(var)
    return out


def _load_static_only_vars(
    profiler_dir: Path, observed_vars: set, start_line: int, end_line: int
) -> List[str]:
    """Variables that appear in STATIC dependences overlapping the region but were
    never observed in the runtime (dynamic) dependences ANYWHERE — i.e. compiler-
    conservative deps that did not actually occur, hence likely spurious /
    privatizable.  `observed_vars` must be the GLOBAL dynamic-dep variable set
    (see _all_observed_dep_vars), not a region-filtered one.

    static_dependencies.txt line:  `<sink_line> NOM <TYPE> <src_line>|<var>(<region>)`
    """
    f = profiler_dir / "static_dependencies.txt"
    if not f.exists():
        return []
    static_vars: set = set()
    for line in f.read_text().splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[2] not in ("RAW", "WAR", "WAW"):
            continue
        try:
            sink_line = int(parts[0].split(":")[-1])
        except ValueError:
            continue
        for target in parts[3:]:
            if "|" not in target:
                continue
            src, var_part = target.split("|", 1)
            try:
                src_line = int(src.split("@")[-1].split(":")[-1])
            except ValueError:
                src_line = -1
            if not ((start_line <= sink_line <= end_line) or (start_line <= src_line <= end_line)):
                continue
            name, _ = _classify_var(var_part.split("(")[0])
            static_vars.add(name)
    return sorted(static_vars - observed_vars)


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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def assemble(
    candidate: HotspotCandidate,
    profiler_dir: Path,
    failure_reason: str = "",
) -> EvidencePackage:
    """Build the full evidence package for any code region candidate."""
    region = candidate.region
    raw, war, waw = _load_dependencies(profiler_dir, region.start_line, region.end_line)
    reductions = _load_reductions(profiler_dir, region.start_line, region.end_line)
    source_region = _extract_source_region(
        candidate.source_file, region.start_line, region.end_line
    )

    # Enclosing function (for --edit-mode function).  If the region is already a
    # function, or no containing function is found, fall back to the region span.
    fn = find_enclosing_function(
        profiler_dir, region.file_id, region.start_line, region.end_line
    )
    if fn is not None:
        fn_name, fn_start, fn_end = fn.name, fn.start_line, fn.end_line
    else:
        fn_name, fn_start, fn_end = region.name, region.start_line, region.end_line
    # DiscoPoP's end line points at the last statement, not the closing brace —
    # recompute the true span so function-mode splicing replaces the whole function.
    true_end = _brace_match_end(candidate.source_file, fn_start)
    if true_end >= fn_start:
        fn_end = true_end
    fn_source = _read_span(candidate.source_file, fn_start, fn_end)

    # Do-All blockers recorded by DiscoPoP's new detector (if the new explorer
    # produced explorer/doall_prevented.json).  profiler_dir = <discopop>/profiler.
    prevented = _load_prevented_deps(
        profiler_dir.parent, region.file_id, region.start_line, region.end_line
    )

    # DiscoPoP's own OpenMP data-sharing classification for this region (shared /
    # private / first_private / last_private / reduction), taken from the pattern
    # it detected.  Empty when the region has no detected pattern.
    cls = _var_classification(candidate.pattern)

    # Phase-2 signals: observed loop trip counts (granularity), loop-local
    # variables (already private), and static-only dependence variables (deps the
    # compiler could not rule out but that never occurred at runtime).
    trip_counts = _load_loop_trip_counts(
        profiler_dir, region.file_id, region.start_line, region.end_line
    )
    local_vars = _load_local_vars(
        profiler_dir.parent, region.file_id, region.start_line, region.end_line
    )
    observed_vars = _all_observed_dep_vars(profiler_dir)
    static_only = _load_static_only_vars(
        profiler_dir, observed_vars, region.start_line, region.end_line
    )

    return EvidencePackage(
        region_id=region.region_id,
        region_type=region.region_type,
        start_line=region.start_line,
        end_line=region.end_line,
        source_file=candidate.source_file,
        source_region=source_region,
        iteration_count=region.iteration_count,
        raw_deps=raw,
        war_deps=war,
        waw_deps=waw,
        reduction_vars=reductions,
        tier1_failure_reason=failure_reason,
        prevented_deps=prevented,
        shared_vars=cls.get("shared", []),
        private_vars=cls.get("private", []),
        firstprivate_vars=cls.get("first_private", []),
        lastprivate_vars=cls.get("last_private", []),
        classified_reduction_vars=cls.get("reduction", []),
        loop_trip_counts=trip_counts,
        local_vars_in_region=local_vars,
        static_only_vars=static_only,
        enclosing_function_name=fn_name,
        enclosing_function_start=fn_start,
        enclosing_function_end=fn_end,
        enclosing_function_source=fn_source,
    )
