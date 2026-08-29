"""
Rendering an EvidencePackage into the text the model reads
------------------------------------------------------------
Layout decisions here are the result of watching small models misread the
evidence: dependences are grouped per VARIABLE rather than listed per line,
quoted against the statements they point at, and tagged array or scalar.
DiscoPoP's Do-All blockers get their own section with each one's origin, because
that is the list the model should be targeting.

One thing deliberately absent: CU-graph variable types.  The CU graph reports
every scalar as `ptr (8B)` (alloca slots), which misinformed more than it helped.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from ..types import EvidencePackage


# Iterations per loop activation below which OpenMP thread startup (tens of
# microseconds) tends to outweigh the work, so the parallel build is not faster
# and the L4 performance gate reverts the rewrite.  A coarse rule of thumb — it
# is stated to the model as one, not as a hard cutoff.
_FINE_GRAINED_ITERS = 1000


# The evidence package, named section by section, so an ablation can remove one
# and measure what it was worth.  `--evidence` selects a subset; the names here
# are the vocabulary that flag speaks.
EVIDENCE_SECTIONS = (
    "deps",            # RAW / WAR / WAW, grouped per variable
    "reductions",      # variables DiscoPoP saw accumulating
    "classification",  # its own private/shared/reduction clause suggestion
    "extra_vars",      # static-only and loop-local names
    "array_note",      # how to fix an array-carried dependence
    "loop_nest",       # nesting, induction variables, observed trip counts
    "calls",           # what the region calls
    "blockers",        # doall_prevented — why it will not parallelize this
    "failure",         # why the previous attempt failed the gate
)


def _evidence_sections(ev: EvidencePackage, deps_header: str,
                       include: Optional[Set[str]] = None) -> List[str]:
    """The evidence body shared by every edit mode.  Only the surrounding
    header/source/task text differs between --edit-mode diff, function and direct.

    `include` names the sections to render; None means all of them.  Each section
    is independently omittable so the ablation can ask what any one of them is
    actually worth — measured on gate pass rate, attempts to first pass, and
    prompt tokens.  Note `failure` is NOT DiscoPoP evidence: it is the gate's own
    diagnostic from the previous attempt, so an ablation that leaves it in is
    measuring static analysis against a model that still gets empirical feedback.
    """
    want = (lambda name: True) if include is None else (lambda name: name in include)
    region = (ev.start_line, ev.end_line)
    parts: List[str] = []
    if want("deps"):
        parts += [
            f"{deps_header}\n"
            "(grouped per variable, each tagged [array element] or [scalar])",
            _fmt_deps(ev.raw_deps, "RAW — read-after-write (the blocking ones)",
                      ev.line_text, region),
            _fmt_deps(ev.war_deps, "WAR — write-after-read", region=region),
            _fmt_deps(ev.waw_deps, "WAW — write-after-write", region=region),
        ]
    if want("reductions") and ev.reduction_vars:
        parts.append(f"### Reduction variables: {', '.join(ev.reduction_vars)}\n")
    for name, section in (
        ("classification", _fmt_classification(ev)),
        ("extra_vars", _fmt_extra_vars(ev)),
        ("array_note", _array_dep_note(ev)),
        ("loop_nest", _fmt_loop_nest(ev)),
        ("calls", _fmt_calls(ev)),
        ("blockers", fmt_blockers(ev.prevented_deps)),
    ):
        if want(name) and section:
            parts.append(section)
    if want("failure") and ev.tier1_failure_reason:
        parts.append(f"### What went wrong\n{ev.tier1_failure_reason}\n")
    return parts


def _fmt_deps(
    deps: list,
    label: str,
    line_text: Optional[Dict[int, str]] = None,
    region: Optional[Tuple[int, int]] = None,
) -> str:
    """Render one dependence class aggregated PER VARIABLE (a flat list of raw
    dep lines drowns a small model), quoting the source statement each line
    number points at so the model never has to cross-reference by itself.
    Dependences with an endpoint OUTSIDE `region` (e.g. a later consumer of the
    data in another function) are summarised, not listed — they are not what the
    rewrite has to remove."""
    if not deps:
        return f"  {label}: none\n"
    groups: Dict[Tuple[str, str], List[Any]] = {}
    for d in deps:
        groups.setdefault((d.variable, getattr(d, "kind", "scalar")), []).append(d)
    lines = [f"  {label}:"]
    quoted: Set[int] = set()
    for (var, kind), ds in groups.items():
        tag = "array element" if kind == "array" else "scalar"
        pairs = sorted({(d.from_line, d.to_line) for d in ds})
        if region:
            lo, hi = region
            inside = [p for p in pairs if lo <= p[0] <= hi and lo <= p[1] <= hi]
            crossing = len(pairs) - len(inside)
        else:
            inside, crossing = pairs, 0
        shown = ", ".join(f"{a}→{b}" for a, b in inside[:8])
        more = f"  (+{len(inside) - 8} more)" if len(inside) > 8 else ""
        cross = (
            f"  (+{crossing} with an endpoint outside the region: values "
            "produced here are consumed by later code — the rewrite must "
            "preserve them)" if crossing else ""
        )
        where = shown or (
            "(loop-carried; the profiler did not resolve exact in-region line "
            "pairs — see the Do-All blockers section)"
        )
        lines.append(f"    {var}  [{tag}]  at lines {where}{more}{cross}")
        if line_text:
            for ln in sorted({x for p in inside[:8] for x in p}):
                stmt = line_text.get(ln, "").strip()
                # Skip closing-brace-only lines — DiscoPoP attributes loop-carried
                # deps to them, but quoting `}` tells the model nothing.
                if stmt.strip("{}(); ") and ln not in quoted:
                    quoted.add(ln)
                    lines.append(f"        line {ln}: `{stmt}`")
    return "\n".join(lines) + "\n"


def _fmt_digest(ev: EvidencePackage) -> str:
    """Compact factual summary placed FIRST in the prompt: what blocks
    parallelization, on which variables, in which loops.  Small models weight
    the beginning of the prompt most heavily; every fact here is repeated in
    detail in later sections."""
    array_raw = sorted({d.variable for d in ev.raw_deps if getattr(d, "kind", "scalar") == "array"})
    scalar_raw = sorted({d.variable for d in ev.raw_deps if getattr(d, "kind", "scalar") == "scalar"})
    out = ["### Evidence digest (details in the sections below)"]
    if array_raw:
        out.append(
            f"  - Loop-carried RAW on ARRAY ELEMENTS of: {', '.join(array_raw)} "
            "— see 'Choosing the fix' below."
        )
    if scalar_raw:
        out.append(
            f"  - RAW on SCALARS: {', '.join(scalar_raw)} — usually a reused "
            "location or an accumulator, not a value travelling between iterations."
        )
    if not ev.raw_deps:
        out.append("  - No RAW dependences observed — the blocker is structural "
                   "(control flow) or granularity, not data flow.")
    for lp in ev.loop_nest:
        idx = ", ".join(lp["index_vars"])
        idx_part = f" (index: {idx})" if idx else ""
        out.append(
            f"  - {'  ' * lp['depth']}Loop lines {lp['start']}–{lp['end']}"
            f"{idx_part}: {lp['entries']} activation(s) × ~{lp['avg']} iterations."
        )
    if ev.calls_in_region:
        callees = ", ".join(
            f"{c['callee']}()" + (" [RECURSIVE]" if c["recursive"] else "")
            for c in ev.calls_in_region
        )
        out.append(f"  - The region CALLS other functions: {callees} — their side "
                   "effects must stay correct under any restructuring.")
    if ev.reduction_vars:
        out.append(f"  - DiscoPoP already recognizes reduction variable(s): "
                   f"{', '.join(ev.reduction_vars)}.")
    return "\n".join(out) + "\n"


def _fmt_loop_nest(ev: EvidencePackage) -> str:
    """Loop structure with induction variables and iteration statistics.
    Supersedes the flat trip-count list when PEGraph loop data is available."""
    if not ev.loop_nest:
        return _fmt_trip_counts(ev)
    out = ["### Loop structure (nesting, induction variables, observed iterations)"]
    for lp in ev.loop_nest:
        idx = ", ".join(lp["index_vars"]) or "unknown"
        # Each activation of a loop is one parallel region, so what has to
        # amortise thread startup is the iterations per activation, not the
        # total across all activations.
        if lp["avg"] < _FINE_GRAINED_ITERS:
            verdict = f"  <-- too fine-grained on its own (~{lp['avg']} per activation)"
        else:
            verdict = "  <-- enough work per activation to be worth it"
        out.append(
            f"  {'  ' * lp['depth']}- loop at lines {lp['start']}–{lp['end']}  "
            f"induction variable(s): {idx}  |  {lp['entries']} activation(s) "
            f"× ~{lp['avg']} iterations = {lp['total']:,} total (max {lp['max']})"
            f"{verdict}"
        )
    out.append(
        f"  (Marked against ~{_FINE_GRAINED_ITERS} iterations per activation — "
        "below that, thread startup costs more than the loop saves.)"
    )
    return "\n".join(out) + "\n"


def _fmt_calls(ev: EvidencePackage) -> str:
    """Call sites inside the region.  A call means the body has effects the
    region source alone may not show; a recursive call rules out simple loop
    parallelization of the surrounding structure."""
    if not ev.calls_in_region:
        return ""
    out = ["### Function calls inside the region"]
    for c in ev.calls_in_region:
        rec = "  [RECURSIVE — calls the enclosing function itself]" if c["recursive"] else ""
        out.append(f"  - line {c['line']}: calls {c['callee']}(){rec}")
    out.append(
        "  Iterations that call a function are independent only if the calls do "
        "not touch overlapping shared state; check the callee's side effects "
        "before assuming Do-All."
    )
    return "\n".join(out) + "\n"


def _fmt_classification(ev: EvidencePackage) -> str:
    """Render DiscoPoP's own OpenMP data-sharing classification for the region,
    when a pattern was detected.  Returns '' when nothing was classified."""
    if not (ev.shared_vars or ev.private_vars or ev.firstprivate_vars
            or ev.lastprivate_vars or ev.classified_reduction_vars):
        return ""
    out = ["### DiscoPoP variable classification (from its own analysis)"]
    if ev.shared_vars:
        out.append(
            f"  shared        : {', '.join(ev.shared_vars)}   "
            "(the data structures — a loop-carried dep on these is ALGORITHMIC, "
            "not removable by privatizing/renaming)"
        )
    if ev.private_vars:
        out.append(
            f"  private       : {', '.join(ev.private_vars)}   "
            "(each iteration can safely have its own copy)"
        )
    if ev.firstprivate_vars:
        out.append(f"  firstprivate  : {', '.join(ev.firstprivate_vars)}")
    if ev.lastprivate_vars:
        out.append(f"  lastprivate   : {', '.join(ev.lastprivate_vars)}")
    if ev.classified_reduction_vars:
        out.append(f"  reduction     : {', '.join(ev.classified_reduction_vars)}")
    return "\n".join(out) + "\n"


def _fmt_trip_counts(ev: EvidencePackage) -> str:
    """Render observed loop trip counts, with a granularity hint.  Returns '' when
    no trip-count data is available for the region."""
    if not ev.loop_trip_counts:
        return ""
    out = ["### Loop trip counts (observed at runtime — judge parallel granularity)"]
    for lc in ev.loop_trip_counts:
        verdict = (
            "  <-- TOO FINE-GRAINED on its own: parallelize an enclosing loop "
            "instead, or make each iteration do more work"
            if lc["avg"] < _FINE_GRAINED_ITERS
            else "  <-- enough iterations per activation to be worth parallelizing"
        )
        out.append(
            f"  loop at line {lc['line']}: {lc['entries']} activation(s) "
            f"× ~{lc['avg']} iterations each = {lc['total']:,} total "
            f"(max {lc['max']}/activation){verdict}"
        )
    out.append(
        f"  Rule of thumb used above: each activation is a separate parallel "
        f"region, so it is the ~{_FINE_GRAINED_ITERS} iterations PER ACTIVATION "
        "that must amortise thread startup, not the total across activations. "
        "Prefer the outermost loop marked worth parallelizing."
    )
    return "\n".join(out) + "\n"


def _fmt_extra_vars(ev: EvidencePackage) -> str:
    """Render loop-local (already-private) variables and static-only (likely
    spurious) dependence variables.  Returns '' when neither is present."""
    lines = []
    if ev.local_vars_in_region:
        lines.append(
            f"  loop-local (already per-iteration private — no privatization "
            f"needed): {', '.join(ev.local_vars_in_region)}"
        )
    if ev.static_only_vars:
        lines.append(
            f"  static-only deps (compiler-conservative, NEVER observed at "
            f"runtime → the dependence is likely spurious; exposing or privatizing "
            f"may already be safe): {', '.join(ev.static_only_vars)}"
        )
    if not lines:
        return ""
    return "### Additional DiscoPoP variable facts\n" + "\n".join(lines) + "\n"


def _array_dep_note(ev: EvidencePackage) -> str:
    """The one question worth forcing when the blocking RAW deps are on array
    elements, injected only when the profile shows them.  Which decoupling is
    valid turns entirely on the answer, and it is the thing most easily got
    wrong by inspection.  Returns '' when the blocking deps are all scalar."""
    array_vars = sorted({d.variable for d in ev.raw_deps if getattr(d, "kind", "scalar") == "array"})
    if not array_vars:
        return ""
    return (
        "### Choosing the fix for this array dependence\n"
        f"The blocking RAW dependence is on ARRAY ELEMENTS ({', '.join(array_vars)}), "
        "so a value is moving through the data itself — renaming or copying the "
        "array does not change that.  The decision to make first: can a value "
        "written during one sweep be read again LATER IN THE SAME SWEEP?\n"
        "  - No — each result depends only on the previous sweep.  You can read "
        "from one buffer and write to another, swapping them per sweep.\n"
        "  - Yes — the update travels along the array as the sweep runs, so a "
        "second buffer would change the answer.  Split each sweep into ordered "
        "sub-passes over disjoint elements instead; every bound then has to be "
        "re-derived, because a value now moves a shorter distance per sweep "
        "than the original order carried it.\n"
    )


def fmt_blockers(prevented: list) -> str:
    """Render DiscoPoP's exact Do-All blockers (from doall_prevented.json).
    Returns '' when none are available (old explorer / clean loop)."""
    if not prevented:
        return ""
    out = [
        "### Why DiscoPoP could not parallelize (Do-All blockers)",
        "DiscoPoP identified these exact dependences as what blocks Do-All — "
        "target these specifically:",
    ]
    for b in prevented[:20]:
        origin = str(b.get("origin", "")).upper()
        note = ("dynamic — a real, observed dependency; it must be removed"
                if "DYNAMIC" in origin
                else "static — may be resolvable by privatizing / first-writing the variable inside the loop")
        # Strip enum prefixes (DepType.RAW -> RAW), tidy the variable name.
        dtype = str(b.get("dep_type", "?")).split(".")[-1]
        var = str(b.get("var_name", "?"))
        # Line info is optional in the new detector; show it only when present.
        src = str(b.get("source_line") or "").split(":")[-1]
        snk = str(b.get("sink_line") or "").split(":")[-1]
        if src and snk and src != "None" and snk != "None":
            where = f"line {src} → {snk}"
        else:
            ls, le = b.get("loop_start"), b.get("loop_end")
            where = f"loop-carried (loop at line{'s' if ls != le else ''} {ls}" + (f"–{le}" if ls != le else "") + ")"
        out.append(f"  - {dtype} on `{var}`  {where}  [{note}]")
    return "\n".join(out) + "\n"
