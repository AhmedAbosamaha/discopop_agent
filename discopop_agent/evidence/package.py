"""
Assembling everything known about one region into the package the LLM sees
---------------------------------------------------------------------------
`assemble` is the only public entry point of this package: it takes a candidate
and returns the EvidencePackage — source, dependences grouped per variable, the
loop nest, calls, trip counts, DiscoPoP's Do-All blockers, and (on a retry) what
failed last time and what DiscoPoP made of the model's own rewrite.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from ..plan import find_enclosing_function, region_fingerprint
from ..types import Dependency, EvidencePackage, HotspotCandidate
from .blockers import _var_classification, load_prevented_deps
from .context import (_array_accesses, _brace_match_end, _demangle,
                      _extract_source_region, _inner_patterns, _line_text_map,
                      _load_calls_in_region, _load_local_vars,
                      _load_loop_nest, _load_loop_trip_counts, _read_span)
from .deps import (_all_observed_dep_vars, _load_dependencies,
                   _load_reductions, _load_static_only_vars)


def assemble(
    candidate: HotspotCandidate,
    profiler_dir: Path,
    failure_reason: str = "",
) -> EvidencePackage:
    """Build the full evidence package for any code region candidate."""
    region = candidate.region
    fingerprint = region_fingerprint(
        candidate.source_file, region.start_line, region.end_line, region.name
    )
    # In a project every line number is qualified by the region's file; for a
    # single-file program there is only one file and nothing to qualify.
    from .. import project as project_mod
    fid = region.file_id if project_mod.active() is not None else None
    raw, war, waw = _load_dependencies(profiler_dir, region.start_line, region.end_line, fid)
    reductions = _load_reductions(profiler_dir, region.start_line, region.end_line, fid)
    source_region = _extract_source_region(
        candidate.source_file, region.start_line, region.end_line
    )

    # Enclosing function (for --edit-mode function).  If the region is already a
    # function, or no containing function is found, fall back to the region span.
    fn = find_enclosing_function(
        profiler_dir, region.file_id, region.start_line, region.end_line
    )
    if fn is not None:
        fn_name, fn_start, fn_end = _demangle(fn.name), fn.start_line, fn.end_line
    else:
        fn_name, fn_start, fn_end = _demangle(region.name), region.start_line, region.end_line
    # DiscoPoP's end line points at the last statement, not the closing brace —
    # recompute the true span so function-mode splicing replaces the whole function.
    true_end = _brace_match_end(candidate.source_file, fn_start)
    if true_end >= fn_start:
        fn_end = true_end
    fn_source = _read_span(candidate.source_file, fn_start, fn_end)

    # Do-All blockers recorded by DiscoPoP's new detector (if the new explorer
    # produced explorer/doall_prevented.json).  profiler_dir = <discopop>/profiler.
    prevented = load_prevented_deps(
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
        profiler_dir, observed_vars, region.start_line, region.end_line, fid
    )

    # Structural facts: loop nest with induction variables, declared variable
    # types, calls made inside the region, and the raw text of each source line
    # (so the prompt can quote the statement a dependence points at).
    loop_nest = _load_loop_nest(
        profiler_dir.parent, region.file_id, region.start_line, region.end_line
    )
    calls = _load_calls_in_region(
        profiler_dir, region.file_id, region.start_line, region.end_line,
        enclosing_function=fn_name,
    )
    line_text = _line_text_map(
        candidate.source_file,
        min(fn_start, region.start_line) - 2,
        max(fn_end, region.end_line) + 2,
    )

    # Which names are ARRAYS is read from the source, not guessed from DiscoPoP's
    # spelling: it prefixes array accesses with GEPRESULT_ in C++ and names them
    # plainly in C, so every PolyBench array used to reach the model tagged [scalar]
    # — next to a digest line saying scalar dependences are "usually a reused
    # location, not a value travelling between iterations" (review P1).
    accesses = _array_accesses(candidate.source_file, min(fn_start, region.start_line),
                               max(fn_end, region.end_line))
    arrays = set(accesses)

    def _retag(deps: List[Dependency]) -> List[Dependency]:
        # One spelling per variable: DiscoPoP's prefixed form arrives as `b[]`, its
        # plain form as `b` — sometimes both for one array in the same profile — and
        # the access summary and the source say `b`.
        out: List[Dependency] = []
        seen = set()
        for d in deps:
            var = d.variable[:-2] if d.variable.endswith("[]") else d.variable
            kind = "array" if (var in arrays or d.kind == "array") else d.kind
            key = (d.dep_type, d.from_line, d.to_line, var)
            if key not in seen:
                seen.add(key)
                out.append(Dependency(d.dep_type, d.from_line, d.to_line, var, kind))
        return out

    raw, war, waw = _retag(raw), _retag(war), _retag(waw)
    region_accesses = _array_accesses(candidate.source_file, region.start_line, region.end_line)
    inner = _inner_patterns(profiler_dir.parent, region.file_id, region.start_line,
                            region.end_line, region.start_line)
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
        region_fingerprint=fingerprint,
        prevented_deps=prevented,
        shared_vars=cls.get("shared", []),
        private_vars=cls.get("private", []),
        firstprivate_vars=cls.get("first_private", []),
        lastprivate_vars=cls.get("last_private", []),
        classified_reduction_vars=cls.get("reduction", []),
        loop_trip_counts=trip_counts,
        local_vars_in_region=local_vars,
        static_only_vars=static_only,
        loop_nest=loop_nest,
        calls_in_region=calls,
        line_text=line_text,
        enclosing_function_name=fn_name,
        enclosing_function_start=fn_start,
        enclosing_function_end=fn_end,
        enclosing_function_source=fn_source,
        array_accesses=region_accesses,
        inner_patterns=inner,
        runtime_share=candidate.runtime_fraction,
    )
