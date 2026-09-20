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

import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

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
    "accesses",        # per array: the index expressions written and read
    "inner_patterns",  # loops inside the region DiscoPoP already reports parallel
    "runtime_share",   # the region's measured share of program runtime
    "failure",         # why the previous attempt failed the gate
)


def _wanted(include: Optional[Set[str]]) -> Callable[[str], bool]:
    """Section filter: None means every section, a set means exactly those."""
    return (lambda name: True) if include is None else (lambda name: name in include)


def _induction_vars(ev: EvidencePackage) -> Set[str]:
    return {v for lp in ev.loop_nest for v in lp["index_vars"]}


def _signature_line(ev: EvidencePackage) -> Optional[int]:
    """The enclosing function's signature line, when it holds nothing but the signature.

    DiscoPoP records a parameter's initial store there, so every use of `n` or of the
    array pointer shows up as a RAW "on line 414" — a dependence on the function being
    CALLED, which no restructuring touches (review P5)."""
    ln = ev.enclosing_function_start
    text = ev.line_text.get(ln, "")
    if not ln or ";" in text or re.search(r"\b(for|while|do)\b", text):
        return None
    return ln


def _evidence_sections(ev: EvidencePackage, deps_header: str,
                       include: Optional[Set[str]] = None,
                       speed_judged: bool = True,
                       llm_pragmas: bool = True) -> List[str]:
    """The evidence body shared by every edit mode.  Only the surrounding
    header/source/task text differs between --edit-mode diff, function and direct.

    `include` names the sections to render; None means all of them.  Each section
    is independently omittable so the ablation can ask what any one of them is
    actually worth — measured on gate pass rate, attempts to first pass, and
    prompt tokens.  Note `failure` is NOT DiscoPoP evidence: it is the gate's own
    diagnostic from the previous attempt, so an ablation that leaves it in is
    measuring static analysis against a model that still gets empirical feedback.
    """
    want = _wanted(include)
    region = (ev.start_line, ev.end_line)
    parts: List[str] = []
    if want("accesses"):
        section = _fmt_accesses(ev)
        if section:
            parts.append(section)
    if want("deps"):
        skip, sig = _induction_vars(ev), _signature_line(ev)
        parts += [
            f"{deps_header}\n"
            "(grouped per variable, each tagged [array element] or [scalar])",
            _fmt_deps(ev.raw_deps, "RAW — read-after-write (the blocking ones)",
                      ev.line_text, region, skip, sig),
            _fmt_deps(ev.war_deps, "WAR — write-after-read", region=region,
                      skip_vars=skip, signature_line=sig),
            _fmt_deps(ev.waw_deps, "WAW — write-after-write", region=region,
                      skip_vars=skip, signature_line=sig),
        ]
        if skip:
            parts.append(
                f"  (Not listed: dependences on the induction variable(s) "
                f"{', '.join(sorted(skip))} — they are never what blocks a loop; see "
                "'Loop structure' for which of them a pragma has to privatise.)\n")
    if want("reductions") and ev.reduction_vars:
        parts.append(f"### Reduction variables: {', '.join(ev.reduction_vars)}\n")
    for name, section in (
        ("classification", _fmt_classification(ev)),
        ("extra_vars", _fmt_extra_vars(ev)),
        ("array_note", _array_dep_note(ev)),
        ("loop_nest", _fmt_loop_nest(ev, speed_judged, llm_pragmas)),
        ("calls", _fmt_calls(ev)),
        ("blockers", fmt_blockers(ev.prevented_deps)),
        ("inner_patterns", _fmt_inner_patterns(ev, llm_pragmas)),
    ):
        if want(name) and section:
            parts.append(section)
    if want("failure") and ev.tier1_failure_reason:
        # On a first attempt nothing has gone wrong yet: the text only says why the
        # region reached the model at all.
        first = ev.tier1_failure_reason.startswith("DiscoPoP found no applicable")
        parts.append(f"### {'Why this region is here' if first else 'What went wrong'}\n"
                     f"{ev.tier1_failure_reason}\n")
    return parts


def _fmt_deps(
    deps: List[Any],
    label: str,
    line_text: Optional[Dict[int, str]] = None,
    region: Optional[Tuple[int, int]] = None,
    skip_vars: Optional[Set[str]] = None,
    signature_line: Optional[int] = None,
) -> str:
    """Render one dependence class aggregated PER VARIABLE (a flat list of raw
    dep lines drowns a small model), quoting the source statement each line
    number points at so the model never has to cross-reference by itself.
    Dependences with an endpoint OUTSIDE `region` (e.g. a later consumer of the
    data in another function) are summarised, not listed — they are not what the
    rewrite has to remove."""
    # Two kinds of entry are noise at the same weight as the signal, and are left
    # out: dependences on a loop's own induction variable, and "dependences" whose
    # source is the function's signature line — the parameter being passed in.
    deps = [d for d in deps
            if d.variable not in (skip_vars or set())
            and not (signature_line and signature_line in (d.from_line, d.to_line))]
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
        # `*` is DiscoPoP's placeholder for an access it could not attribute to a name.
        shown_var = "(memory DiscoPoP could not name)" if var == "*" else var
        lines.append(f"    {shown_var}  [{tag}]  at lines {where}{more}{cross}")
        if line_text:
            for ln in sorted({x for p in inside[:8] for x in p}):
                stmt = line_text.get(ln, "").strip()
                # Skip closing-brace-only lines — DiscoPoP attributes loop-carried
                # deps to them, but quoting `}` tells the model nothing.
                if stmt.strip("{}(); ") and ln not in quoted:
                    quoted.add(ln)
                    lines.append(f"        line {ln}: `{stmt}`")
    return "\n".join(lines) + "\n"


def _fmt_digest(ev: EvidencePackage, include: Optional[Set[str]] = None) -> str:
    """Compact factual summary placed FIRST in the prompt: what blocks
    parallelization, on which variables, in which loops.  Small models weight
    the beginning of the prompt most heavily; every fact here is repeated in
    detail in later sections.

    Every line belongs to a named evidence section and is dropped with it.  The
    digest used to be printed unconditionally, so `--evidence none` — the arm the
    evidence claim is measured against — still opened with DiscoPoP's dependence
    variables, its loop nest and the measured trip counts (review P9).  With no
    section selected there is no digest at all."""
    want = _wanted(include)
    ind = _induction_vars(ev)
    sig = _signature_line(ev)
    real = [d for d in ev.raw_deps
            if d.variable not in ind and not (sig and sig in (d.from_line, d.to_line))]
    array_raw = sorted({d.variable for d in real if getattr(d, "kind", "scalar") == "array"})
    scalar_raw = sorted({d.variable for d in real if getattr(d, "kind", "scalar") == "scalar"})
    out: List[str] = []
    if want("runtime_share") and ev.runtime_share:
        out.append(f"  - This region accounts for about {ev.runtime_share * 100:.0f}% of the "
                   "program's measured runtime.")
    if want("deps"):
        if array_raw:
            out.append(
                f"  - Loop-carried RAW on ARRAY ELEMENTS of: {', '.join(array_raw)} "
                "— a value moves between iterations through the data; see 'Choosing "
                "the fix' below."
            )
        if scalar_raw:
            out.append(
                f"  - RAW on SCALARS: {', '.join(scalar_raw)} — usually a reused "
                "location or an accumulator, not a value travelling between iterations."
            )
        if not real:
            out.append("  - No RAW dependences observed apart from loop counters and "
                       "parameters — the blocker is structural (control flow), not "
                       "data flow.")
    if want("accesses"):
        for name, acc in list(ev.array_accesses.items())[:4]:
            if acc["writes"]:
                out.append(f"  - `{name}` is written as {', '.join(acc['writes'][:3])} and "
                           f"read as {', '.join(acc['reads'][:5]) or '(not read)'}.")
    if want("loop_nest"):
        for lp in ev.loop_nest:
            idx = ", ".join(lp["index_vars"])
            idx_part = f" (index: {idx})" if idx else ""
            out.append(
                f"  - {'  ' * lp['depth']}Loop lines {lp['start']}–{lp['end']}"
                f"{idx_part}: {lp['entries']} activation(s) × ~{lp['avg']} iterations."
            )
    if want("inner_patterns") and ev.inner_patterns:
        where = ", ".join(f"line {p['line']}" for p in ev.inner_patterns[:6])
        out.append(f"  - DiscoPoP ALREADY reports parallel loop(s) inside this region "
                   f"({where}) — those need a pragma, not a rewrite.")
    if want("calls") and ev.calls_in_region:
        callees = ", ".join(
            f"{c['callee']}()" + (" [RECURSIVE]" if c["recursive"] else "")
            for c in ev.calls_in_region
        )
        out.append(f"  - The region CALLS other functions: {callees} — their side "
                   "effects must stay correct under any restructuring.")
    if want("reductions") and ev.reduction_vars:
        out.append(f"  - DiscoPoP already recognizes reduction variable(s): "
                   f"{', '.join(ev.reduction_vars)}.")
    if not out:
        return ""
    return "\n".join(["### Evidence digest (details in the sections below)"] + out) + "\n"


def _fmt_accesses(ev: EvidencePackage) -> str:
    """Per array, the index expressions the region writes and reads.

    DiscoPoP reports THAT iterations depend on each other through `path`; which
    loop carries it, and whether a second buffer or an ordered split is the fix,
    is decided by comparing the subscripts written with the subscripts read —
    and that is one pass over the region's own source (review P6)."""
    rows = [(n, a) for n, a in ev.array_accesses.items() if a["writes"] or a["reads"]]
    if not rows:
        return ""
    out = ["### Array accesses in the region (index expressions, read from the source)"]
    for name, acc in rows[:12]:
        w = ", ".join(acc["writes"][:6]) or "—"
        r = ", ".join(acc["reads"][:8]) or "—"
        tag = "" if acc["writes"] else "   (read-only here: never a source of a dependence)"
        out.append(f"  {name}:  written as {w}  |  read as {r}{tag}")
    out.append(
        "  A loop whose index appears identically in every subscript that touches an "
        "array visits a different element on each of its iterations, so THAT loop does "
        "not carry a dependence through the array.  A dependence is carried by the loop "
        "whose index differs between a write and a read (`a[i]` written, `a[i-1]` read)."
    )
    return "\n".join(out) + "\n"


def _fmt_inner_patterns(ev: EvidencePackage, llm_pragmas: bool) -> str:
    """Loops inside the region DiscoPoP already reports as parallel (review P7)."""
    if not ev.inner_patterns:
        return ""
    out = ["### Already parallel according to DiscoPoP (inside this region)"]
    for p in ev.inner_patterns[:10]:
        kind = "Reduction" if p["kind"] == "reduction" else "Do-All"
        clauses = f"  with {p['clauses']}" if p.get("clauses") else ""
        out.append(f"  - loop at line {p['line']}: {kind}{clauses}")
    out.append(
        # Fix 85.  These loops are DiscoPoP's, in both modes.  Telling the model it may
        # annotate them "as it stands" (which this said under --llm-pragmas) invited it to
        # put its own pragma where DiscoPoP already had one: on jacobi-2d it wrote
        # `collapse(2)` over the two stencil loops from inside a function-level rewrite,
        # Phase B then found nothing left to annotate, and DiscoPoP's own `private(j)` —
        # twice as fast on that machine — was never measured.
        ("  These loops need no restructuring and DiscoPoP annotates them itself, after "
         "you are done.  Do NOT put a pragma on them: write pragmas only for loops you "
         "restructure or create.  What is asked of you is whatever stops a loop OUTSIDE "
         "them from running in parallel; if nothing can be done there, say so — leaving "
         "these loops to DiscoPoP is a valid answer."
         if llm_pragmas else
         "  These loops need no restructuring and DiscoPoP annotates them itself.  What "
         "is asked of you is whatever stops a loop OUTSIDE them from running in parallel.")
    )
    return "\n".join(out) + "\n"


def _index_declared_outside(header: str, var: str) -> Optional[bool]:
    """Is the loop's index variable declared OUTSIDE its `for` header?

    `for (j = 0; …)` — yes; `for (int j = 0; …)` — no; None when it cannot be told.
    It matters because OpenMP privatises only the index of the loop the pragma is
    ON.  In C code that declares `int i, j, k;` at the top of the function — every
    PolyBench kernel — the indices of the loops nested inside stay SHARED, and a
    `parallel for` on the outer loop without `private(j, k)` is a data race."""
    v = re.escape(var)
    if re.search(r"\bfor\s*\(\s*" + v + r"\s*=", header):
        return True
    if re.search(r"\bfor\s*\(\s*[A-Za-z_][\w:<>\s\*&]*[\s\*&]" + v + r"\s*[=({]", header):
        return False
    return None


def _fmt_loop_nest(ev: EvidencePackage, speed_judged: bool = True,
                   llm_pragmas: bool = True) -> str:
    """Loop structure with induction variables and iteration statistics.
    Supersedes the flat trip-count list when PEGraph loop data is available.

    The "too fine-grained" marker is printed only when the speed check will really
    run at this input size.  The campaign profiles at a deliberately small size —
    32 iterations per activation for every loop of a PolyBench kernel — so with the
    marker always on, every loop was branded not worth parallelising while the
    system prompt said to annotate "the outermost one that qualifies" (review P4)."""
    if not ev.loop_nest:
        return _fmt_trip_counts(ev, speed_judged)
    out = ["### Loop structure (nesting, induction variables, observed iterations)"]
    outside: List[str] = []
    for lp in ev.loop_nest:
        idx = ", ".join(lp["index_vars"]) or "unknown"
        # Each activation of a loop is one parallel region, so what has to
        # amortise thread startup is the iterations per activation, not the
        # total across activations.
        if not speed_judged:
            verdict = ""
        elif lp["avg"] < _FINE_GRAINED_ITERS:
            verdict = f"  <-- too fine-grained on its own (~{lp['avg']} per activation)"
        else:
            verdict = "  <-- enough work per activation to be worth it"
        header = ev.line_text.get(lp["start"], "")
        for v in lp["index_vars"]:
            if lp["depth"] > 0 and _index_declared_outside(header, v) and v not in outside:
                outside.append(v)
        out.append(
            f"  {'  ' * lp['depth']}- loop at lines {lp['start']}–{lp['end']}  "
            f"induction variable(s): {idx}  |  {lp['entries']} activation(s) "
            f"× ~{lp['avg']} iterations = {lp['total']:,} total (max {lp['max']})"
            f"{verdict}"
        )
    if speed_judged:
        out.append(
            f"  (Marked against ~{_FINE_GRAINED_ITERS} iterations per activation — "
            "below that, thread startup costs more than the loop saves.)"
        )
    else:
        out.append(
            "  (These counts come from a deliberately small profiling input; the code is "
            "measured at full size later.  They show the SHAPE of the nest — which loop "
            "is entered once and which thousands of times — not whether a loop is worth "
            "parallelising.)"
        )
    if outside and llm_pragmas:
        out.append(
            f"  NOTE: the ind{'ex' if len(outside) == 1 else 'ices'} {', '.join(outside)} "
            f"{'is' if len(outside) == 1 else 'are each'} declared outside the `for` that "
            "counts with it.  OpenMP privatises only the index of the loop the pragma is "
            "ON, so a pragma has to name in `private(...)` the index of every loop nested "
            "inside it — otherwise all threads share one counter, which is a race."
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


def _fmt_trip_counts(ev: EvidencePackage, speed_judged: bool = True) -> str:
    """Render observed loop trip counts, with a granularity hint.  Returns '' when
    no trip-count data is available for the region."""
    if not ev.loop_trip_counts:
        return ""
    if not speed_judged:
        out = ["### Loop trip counts (observed on a deliberately small profiling input)"]
        for lc in ev.loop_trip_counts:
            out.append(
                f"  loop at line {lc['line']}: {lc['entries']} activation(s) "
                f"× ~{lc['avg']} iterations each = {lc['total']:,} total "
                f"(max {lc['max']}/activation)")
        out.append("  Speed is measured later at full size, so these show the shape of "
                   "the nest, not whether a loop is worth parallelising.  Prefer the "
                   "outermost loop that can be made independent.")
        return "\n".join(out) + "\n"
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
    """The questions worth forcing when the blocking RAW deps are on array
    elements, injected only when the profile shows them.  Which decoupling is
    valid turns entirely on the answers, and it is the thing most easily got
    wrong by inspection.  Returns '' when the blocking deps are all scalar.

    The first question — which loop carries the dependence — was added when arrays
    started being recognised in the C kernels (review P1): the note then fires for
    nests like `C[i][j] += A[i][k] * B[k][j]`, where the honest answer is "only the
    k loop", and the old text ("a value is moving through the data itself") sent
    the model looking for a second buffer it did not need."""
    ind = _induction_vars(ev)
    array_vars = sorted({d.variable for d in ev.raw_deps
                         if getattr(d, "kind", "scalar") == "array" and d.variable not in ind})
    if not array_vars:
        return ""
    return (
        "### Choosing the fix for this array dependence\n"
        f"The blocking RAW dependence is on ARRAY ELEMENTS ({', '.join(array_vars)}): an "
        "iteration reads an element another iteration wrote.  Renaming the array does "
        "not change that.  Settle two things, in this order:\n"
        "  1. WHICH LOOP carries it.  Compare the subscripts written with the subscripts "
        "read.  A loop whose index sits identically in all of them is not the one — it "
        "may be parallel as it stands, and then the answer is a pragma on THAT loop, not "
        "a rewrite.\n"
        "  2. For a loop that does carry it: can a value written during one sweep be "
        "read again LATER IN THE SAME SWEEP?\n"
        "     - No — each result depends only on values from before the sweep.  Read "
        "from one buffer and write to another (or copy just the elements that are read "
        "across iterations before the sweep starts).\n"
        "     - Yes — the update travels along the array as the sweep runs, so a "
        "second buffer would change the answer.  Split each sweep into ordered "
        "sub-passes over disjoint elements instead; every bound then has to be "
        "re-derived, because a value now moves a shorter distance per sweep "
        "than the original order carried it.\n"
    )


def fmt_blockers(prevented: List[Dict[str, Any]]) -> str:
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
