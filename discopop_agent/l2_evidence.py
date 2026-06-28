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
from typing import List, Tuple

from .l1_planner import find_enclosing_function
from .types import Dependency, EvidencePackage, HotspotCandidate


# ---------------------------------------------------------------------------
# Dependency parser
# ---------------------------------------------------------------------------

def _parse_dep_line(line: str) -> List[Tuple[str, int, int, str]]:
    """Parse one line of dynamic_dependencies.txt.

    Format: <instr>@<from_line> NOM  <DEP_TYPE> <instr>@<to_line>|<var>(<region>) …
    Returns list of (dep_type, from_line, to_line, variable).
    """
    results = []
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
        variable = var_part.split("(")[0]
        results.append((dep_type, from_line, to_line, variable))

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
        for dep_type, fl, tl, var in _parse_dep_line(line):
            in_region = (start_line <= fl <= end_line) or (start_line <= tl <= end_line)
            if not in_region:
                continue
            dep = Dependency(dep_type=dep_type, from_line=fl, to_line=tl, variable=var)
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
            key = (d.dep_type, d.from_line, d.to_line, d.variable)
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
        enclosing_function_name=fn_name,
        enclosing_function_start=fn_start,
        enclosing_function_end=fn_end,
        enclosing_function_source=fn_source,
    )
