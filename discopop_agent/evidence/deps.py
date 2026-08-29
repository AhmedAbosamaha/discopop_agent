"""
Reading DiscoPoP's dependence output
--------------------------------------
The dep-line format is `<sink> NOM <TYPE> <source>|<var>(<memregion>)`, where the
SINK is the LATER access (docs/data/Profiling_and_instrumentation_output.md).
`_parse_dep_line` assigns from_line=sink and to_line=source, so a rendered arrow
reads later->earlier — backwards from data flow, and worth knowing before
reading a prompt built from it.

An endpoint appears in three forms, and only one of them is a source position:

    49      instruction 49
    56@24   instruction 56, plus callpath STATE 24 -- the number after the `@`
            is NOT a line, and the explorer strips it before use
            (parser.py: `sink = sink[: sink.index("@")]`)
    1:18    a plain fileID:lineID, which IS a source line

Reading the state as a line is the mistake this module used to make: it took
`56@24` to mean line 24 and gave the `1:18` form line 0.  Since `_load_dependencies`
filters by line, that silently selected the wrong dependences for a region --
`1:18` endpoints were excluded always, and the rest survived by coincidence.
Everything downstream inherited it, including the dependence lists put in front
of the model (see evidence/package.py).

Instruction ids become positions through `instructionID_to_lineID_mapping.txt`,
whose lines are `<instructionID> <fileID>:<line>:<column>` (or `*` for an
instruction with no source position -- about a fifth of them).  That file is the
only thing that can answer "where is this dependence", so line filtering without
it is guesswork, and `_load_dependencies` now loads it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def _load_instruction_lines(profiler_dir: Path) -> Dict[str, Tuple[int, int]]:
    """Map instruction id -> (file id, source line).

    Instructions with no source position (`*`) are absent from the map, so a
    dependence that refers to one resolves to "unknown" rather than to a
    plausible-looking wrong line.
    """
    out: Dict[str, Tuple[int, int]] = {}
    f = profiler_dir / "instructionID_to_lineID_mapping.txt"
    if not f.exists():
        return out
    for raw in f.read_text().splitlines():
        parts = raw.split()
        if len(parts) < 2 or parts[1] == "*":
            continue
        bits = parts[1].split(":")
        if len(bits) < 2:
            continue
        try:
            out[parts[0]] = (int(bits[0]), int(bits[1]))
        except ValueError:
            continue
    return out


def _endpoint_position(
    token: str, instr_lines: Dict[str, Tuple[int, int]]
) -> Tuple[int, int]:
    """Resolve one endpoint to (file id, line); (0, 0) when it cannot be placed."""
    token = token.strip()
    if not token:
        return (0, 0)
    if ":" in token:                       # fileID:lineID — already a position
        bits = token.split(":")
        try:
            return (int(bits[0]), int(bits[1]))
        except (ValueError, IndexError):
            return (0, 0)
    instr = token.split("@")[0]            # drop callpath state, as the explorer does
    return instr_lines.get(instr, (0, 0))


def _parse_dep_line(
    line: str, instr_lines: Optional[Dict[str, Tuple[int, int]]] = None,
) -> List[Tuple[str, int, int, str, str]]:
    """Parse one line of dynamic_dependencies.txt.

    Format: <sink> NOM  <DEP_TYPE> <source>|<var>(<region>) …
    Returns list of (dep_type, from_line, to_line, variable, kind).

    `instr_lines` resolves instruction ids to source lines (see
    `_load_instruction_lines`).  Without it the variable names and dependence
    types are still correct — that is all `_all_observed_dep_vars` needs — but
    both line numbers come back 0, meaning "not placed", rather than a wrong
    number that would pass a line filter.
    """
    results: List[Tuple[str, int, int, str, str]] = []
    parts = line.strip().split()
    if len(parts) < 4:
        return results

    lines_map = instr_lines or {}
    _from_file, from_line = _endpoint_position(parts[0], lines_map)

    dep_type = parts[2]
    if dep_type not in ("RAW", "WAR", "WAW"):
        return results

    for target in parts[3:]:
        if "|" not in target:
            continue
        to_part, var_part = target.split("|", 1)
        _to_file, to_line = _endpoint_position(to_part, lines_map)
        variable, kind = _classify_var(var_part.split("(")[0])
        results.append((dep_type, from_line, to_line, variable, kind))

    return results


def _load_dependencies(
    profiler_dir: Path,
    start_line: int,
    end_line: int,
) -> Tuple[List[Dependency], List[Dependency], List[Dependency]]:
    """Load deps where at least one endpoint falls inside [start_line, end_line].

    Endpoints are resolved through the instruction->line mapping first; an
    endpoint with no source position cannot be placed in any region and is not
    counted as being in this one.
    """
    raw: List[Dependency] = []
    war: List[Dependency] = []
    waw: List[Dependency] = []

    dep_file = profiler_dir / "dynamic_dependencies.txt"
    if not dep_file.exists():
        return raw, war, waw

    instr_lines = _load_instruction_lines(profiler_dir)
    for line in dep_file.read_text().splitlines():
        if not line.strip() or line.startswith("START"):
            continue
        for dep_type, fl, tl, var, kind in _parse_dep_line(line, instr_lines):
            in_region = (fl and start_line <= fl <= end_line) or \
                        (tl and start_line <= tl <= end_line)
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
    # Endpoints here are bare INSTRUCTION IDS -- `74 NOM RAW 60|k(S-...)` means
    # instruction 74 depends on instruction 60, NOT line 74 on line 60.  This
    # function used to read them as lines (and `55@43` as line 43, which is the
    # callpath state), so the region filter below compared instruction ids
    # against a line range: variables were selected because an unrelated id
    # happened to land inside the span, and every dependence whose id exceeded
    # the file's line count was excluded outright.  Same mistake the module
    # docstring describes, left behind in this one function.
    instr_lines = _load_instruction_lines(profiler_dir)

    def _line_of(token: str) -> int:
        pos = instr_lines.get(token.split("@")[0])
        return pos[1] if pos else -1

    static_vars: set = set()
    for line in f.read_text().splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[2] not in ("RAW", "WAR", "WAW"):
            continue
        sink_line = _line_of(parts[0])
        if sink_line < 0:
            continue
        for target in parts[3:]:
            if "|" not in target:
                continue
            src, var_part = target.split("|", 1)
            src_line = -1 if src == "*" else _line_of(src)
            if not ((start_line <= sink_line <= end_line) or (start_line <= src_line <= end_line)):
                continue
            name, _ = _classify_var(var_part.split("(")[0])
            static_vars.add(name)
    return sorted(static_vars - observed_vars)
