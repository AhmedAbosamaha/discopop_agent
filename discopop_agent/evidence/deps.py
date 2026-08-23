"""
Reading DiscoPoP's dependence output
--------------------------------------
The dep-line format is `<sink> NOM <TYPE> <source>|<var>(<memregion>)`, where the
SINK is the LATER access (docs/data/Profiling_and_instrumentation_output.md).
`_parse_dep_line` assigns from_line=sink and to_line=source, so a rendered arrow
reads later->earlier — backwards from data flow, and worth knowing before
reading a prompt built from it.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from ..types import Dependency


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
