"""
L3 LLM Code Modification Engine
---------------------------------
Sends an EvidencePackage to Claude and expects a valid unified diff back.

The target is any code region (loop, function body, CU) — not just loops.
The LLM restructures the source so that DiscoPoP can detect parallelism;
it does NOT add OpenMP pragmas itself.

Prompt caching is applied to the stable system prompt.
On a bad-format response a free format re-prompt fires before consuming
a budget slot.
"""
from __future__ import annotations

import asyncio
import difflib
import re
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import anthropic

from . import viz
from .types import EvidencePackage

# ---------------------------------------------------------------------------
# System prompt (cached across all calls in a session)
# ---------------------------------------------------------------------------

_SYSTEM_CORE = textwrap.dedent("""\
    You are an expert in C/C++ parallelization and compiler dependency analysis,
    acting as the restructuring stage of DiscoPoP, an automatic OpenMP
    parallelism profiler.

    ------------------------------------------------------------------
    WHAT YOU DO
    ------------------------------------------------------------------
    DiscoPoP profiled one code region and could not extract safe parallelism
    from it.  You rewrite that region's SEQUENTIAL source so the parallelism
    becomes explicit and safe.  You do NOT insert OpenMP pragmas — DiscoPoP
    re-profiles your rewrite and inserts them itself.

    ------------------------------------------------------------------
    HOW YOUR REWRITE IS JUDGED (automatic, in this order)
    ------------------------------------------------------------------
      1. It must COMPILE.
      2. Its printed output must be BYTE-IDENTICAL to the original program's.
      3. DiscoPoP re-profiles it and must find a parallel pattern IN THE LINES
         YOU CHANGED.  No pattern -> reverted: passing 1-2 only proves the
         rewrite did no harm.
      4. DiscoPoP generates the `#pragma omp` itself; that build must be
         race-free, produce the same output, and be FASTER than sequential.
         Correct but not faster -> also reverted.
    Steps 1-2 are the constraint; steps 3-4 are the goal.  Before each retry you
    are told which step failed and what DiscoPoP found in YOUR rewrite — that
    feedback describes the code you just wrote, not the original.

    Free to change: execution order, operation count, loop bounds, extra
    buffers, extra passes.  Doing MORE work than the original is fine — a
    rewrite is judged by its OUTPUT, never by how closely it resembles the
    original.
    Must not change: the function's name or signature; any I/O, its order, or
    its formatting.

    ------------------------------------------------------------------
    WHAT COUNTS AS SUCCESS
    ------------------------------------------------------------------
    Expose at least one pattern DiscoPoP can exploit — Do-All (independent
    iterations), Reduction (associative/commutative accumulator), Pipeline
    (ordered stages, no back-edges), or Task-parallel (independent regions) —
    at a granularity that pays.  Each loop ACTIVATION is a separate parallel
    region, so it is the iterations per activation that must amortise thread
    startup.  The evidence marks each loop's granularity; prefer the outermost
    loop marked worth parallelizing.

    Your job is to EXPOSE PARALLELISM, not to speed up the sequential version.
    These are NOT valid answers: an early-exit or "did anything change this
    pass" shortcut; a faster but still serial algorithm; the original code
    renamed, reordered, unrolled, or returned unchanged.  Every rewrite must
    make some loop's iterations genuinely independent, or split the work into
    independent stages or tasks.

    ------------------------------------------------------------------
    REASON FROM THE EVIDENCE, NOT FROM THE ALGORITHM'S NAME
    ------------------------------------------------------------------
    Each request gives you the observed dependences (RAW / WAR / WAW with line
    and variable), reduction candidates, DiscoPoP's Do-All blockers, and — when
    a pragma was already tried — why it failed.  Decide from that evidence, not
    from what the code looks like.
      - RAW across iterations is the real blocker: removing these is the job.
      - WAR / WAW are usually STORAGE conflicts rather than true data flow; they
        dissolve under privatization or renaming.
      - A blocker of STATIC origin may be one DiscoPoP merely could not rule
        out; a DYNAMIC one was actually observed and must be genuinely broken.
      - Induction variables are handled by OpenMP automatically — never
        restructure to "fix" a dependence on one.

    ------------------------------------------------------------------
    METHOD — CLASSIFY EACH BLOCKER BY ITS CAUSE, THEN FIX THAT CAUSE
    ------------------------------------------------------------------
    Match on the DATA FLOW, not the surface syntax.  The first question is
    always: does a value genuinely FLOW from one iteration to another, or is a
    location merely REUSED?

      1. STORAGE REUSE (no value flows) — a scalar, temp, index, or scratch
         buffer is reused every iteration but carries nothing between them.
         Fix: give each iteration its own instance — declare it inside the loop
         body, or rename to break the reuse.  No algorithmic change.

      2. ACCUMULATION — every iteration reads and writes one variable through an
         associative, commutative operator (+, *, min, max, count, and/or).
         Fix: expose it as a clean reduction — one accumulation per iteration
         into one variable, and no other writes to shared state in the body.

      3. IN-PLACE COUPLING — within ONE sweep, iterations read elements that
         other iterations of the SAME sweep write.
         Fix: either decouple reads from writes (compute into a separate output
         buffer, then swap), or split the sweep into ordered sub-passes whose
         iterations touch DISJOINT elements.  Which of the two is valid depends
         on the read-back question; the evidence spells this out when this cause
         applies.
         A rename or a copy is NOT a decoupling: performing the same
         order-dependent updates on a copy leaves the dependence unchanged.

      4. TRUE RECURRENCE — iteration i's result is defined by iteration i-1's
         (running total, propagation, chained state).
         Fix: reformulate — a closed form in i, a parallel prefix scan, or a
         blocked / recursive-doubling version.  If it is genuinely serial and
         cannot be reassociated, leave it alone rather than emit an unsafe
         rewrite.

      5. NON-CANONICAL CONTROL FLOW — the trip count is not known up front:
         break, continue, return, goto, or a non-affine bound.
         Fix: convert to a fixed-trip-count loop with identical output — replace
         the early exit with a flag evaluated every iteration and tested after
         the loop; fold compound conditions into the bound.

      6. MIXED CONCERNS / TOO-FINE GRANULARITY — nothing blocks the iterations;
         the SHAPE of the parallel work is wrong.
         Fix: hoist loop-invariant work out; SPLIT (fission) independent
         statements into separate loops; or, when the parallel loop is simply
         too small, raise the work per iteration — parallelize an OUTER level,
         FUSE tiny adjacent loops, or BLOCK/TILE so each thread gets a large
         contiguous chunk.
         This is the cause when validation reported "correct but NOT faster":
         the dependence is already gone, so do not go hunting for one.

    ------------------------------------------------------------------
    CARRY THE FIX OUT COMPLETELY
    ------------------------------------------------------------------
    Change what the diagnosed cause requires and nothing else — unrelated
    statements, I/O, and code outside the region stay as they are.  But when the
    fix reshapes the schedule (buffering, sub-passes, fission, a scan), finish
    it: RE-DERIVE every loop bound, initial value, and boundary case for the NEW
    schedule instead of carrying it over.  A bound that was safe only because of
    the OLD execution order is a bug.  A half-measure that keeps the old
    schedule's bounds is the most common way to fail.

    ------------------------------------------------------------------
    OPENMP-CANONICAL FORM (every loop you intend to be parallel)
    ------------------------------------------------------------------
      - The condition compares the loop variable DIRECTLY against a
        loop-invariant bound:  RIGHT `i < n - 1`   WRONG `i + 1 < n`.
      - The increment is i++, i--, i += c, or i -= c with loop-invariant c.
      - No break, continue, return, or goto in the body.
      - The trip count is computable before the loop begins.
    NEVER introduce a new break, continue, return, or goto — not in the target
    loop and not in any enclosing loop you touch.  If the existing code has such
    control flow, convert it to canonical form (cause 5).
""")


# The PLAN every edit mode asks for before the code.  Kept in one place so the
# three modes state an identical reasoning contract, and deliberately GENERAL:
# the only case-specific question (same-sweep read-back) is requested solely
# when the model itself claims the cause it belongs to.
_PLAN_SPEC = """\
      1. "Blockers:" then ONE line per blocking dependence, in the form
         "<variable>: cause <1-6> — <the fix you are applying>".
         If any of those lines claims cause 3, add one further line:
         "Same-sweep read-back: YES/NO — <one line why>"  (can a value written
         during one sweep be read again later in the SAME sweep?  YES rules out
         a separate output buffer — you must partition into sub-passes instead.)
      2. "Loop headers:" then, for every loop you change or add, one
         "OLD: for(...)  ->  NEW: for(...)" pair using the exact header text.
         Re-derive each bound for the new schedule; where a NEW header is
         identical to its OLD one, append "(unchanged because ...)" saying why
         that bound is still correct under the new execution order."""


# Output-format instruction appended per edit mode.
_OUTPUT_DIFF = (
    "\n>>> OUTPUT FORMAT: A SHORT PLAN, THEN A UNIFIED DIFF. <<<\n"
    "First write PLAN — plain text, no code block:\n"
    + _PLAN_SPEC
    + "\n"
    "The diff must contain each NEW header verbatim.\n"
    "Then write the unified diff and END your response there: no markdown, no\n"
    "code fences, no commentary after it.  The diff begins with a '--- ' line,\n"
    "then '+++ ', then one or more '@@ ' hunks.  NO line of the PLAN may begin\n"
    "with '---', '+++' or '@@' — those markers start the diff, and text after\n"
    "the diff causes the response to be rejected.\n"
)

_OUTPUT_FUNCTION = (
    "\n>>> OUTPUT FORMAT: PLAN, THEN THE COMPLETE REWRITTEN FUNCTION. <<<\n"
    "First write PLAN — plain text, no code block:\n"
    + _PLAN_SPEC
    + "\n"
    "Then output the ENTIRE rewritten function — its signature and full body,\n"
    "from the opening `{` to the closing `}` — as ONE ```cpp code block\n"
    "containing each NEW header verbatim, and end your response there.  Do NOT\n"
    "output a diff, line numbers, or markers.  Rewrite only this one function;\n"
    "do not rename it or change its signature.  The agent applies the code block\n"
    "verbatim in place, so it must compile as-is.\n"
)

_OUTPUT_DIRECT = (
    "\n>>> OUTPUT FORMAT: EDIT THE FILE YOURSELF WITH YOUR TOOLS. <<<\n"
    "You have Read / Edit / Write tools on a private working COPY of the source\n"
    "file; its path is given in the request.  Do NOT print a diff and do NOT\n"
    "paste the rewritten code in your reply — apply the change to the file with\n"
    "the Edit tool.  Only the file's final content is used; your prose is not.\n"
    "\n"
    "Procedure for this turn:\n"
    "  1. Read the file (the request shows only an excerpt).\n"
    "  2. Write a short PLAN in plain text:\n"
    + _PLAN_SPEC
    + "\n"
    "  3. Apply the rewrite with Edit calls, matching the NEW headers exactly.\n"
    "  4. Stop.  One-line summary at most.\n"
    "\n"
    "Rules for the edits:\n"
    "  - Edit ONLY the file named in the request; create no other files.\n"
    "  - Restrict the change to the target region and the function containing\n"
    "    it; do not rename that function or change its signature.\n"
    "  - The file must still compile as a whole when you are done — you have no\n"
    "    compiler here, so re-read anything you are unsure about before editing.\n"
    "  - If you already edited this file on an earlier turn, the file still\n"
    "    holds those edits: build on them or replace them, but never restore the\n"
    "    original code.\n"
)

# Diff mode keeps the original system prompt verbatim; function and direct
# modes swap the trailing output instruction.
_SYSTEM = _SYSTEM_CORE + _OUTPUT_DIFF
_SYSTEM_FUNCTION = _SYSTEM_CORE + _OUTPUT_FUNCTION
_SYSTEM_DIRECT = _SYSTEM_CORE + _OUTPUT_DIRECT

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(evidence: EvidencePackage) -> str:
    region_label = {
        "loop": "loop",
        "function": "function body",
        "cu": "basic block",
    }.get(evidence.region_type, "code region")

    exec_info = (
        f"{evidence.iteration_count:,} iterations"
        if evidence.region_type == "loop"
        else f"executed (region id: {evidence.region_id})"
    )

    parts = [
        f"## Source file: {evidence.source_file}",
        f"## Target region: {region_label} at lines "
        f"{evidence.start_line}–{evidence.end_line}  "
        f"(DiscoPoP id {evidence.region_id}; {exec_info})\n",
        _fmt_digest(evidence),
        (
            "### Source\n"
            "(Each line is shown as `NNNN >>> code` where `NNNN` is the line number "
            "and `>>>` marks the target region. "
            "These prefixes are display-only — they are NOT part of the actual source file. "
            "When writing diff context lines (lines starting with a single space), "
            "copy only the raw code indentation, never the `NNNN >>>` prefix.)\n"
            "```cpp"
        ),
        evidence.source_region,
        "```\n",
    ]
    parts.extend(_evidence_sections(evidence, "### Runtime data dependences "
                                              "(observed across all executions)"))

    parts.append(
        f"### Task\n"
        f"Restructure the {region_label} at lines "
        f"{evidence.start_line}–{evidence.end_line} in {evidence.source_file} "
        f"so that after re-profiling DiscoPoP detects a genuinely parallel "
        f"pattern (Do-All, Reduction, Pipeline, or Task-Parallel) that compiles "
        f"cleanly, is race-free under ThreadSanitizer, and achieves measurable "
        f"speedup.\n"
        f"\n"
        f"Work through this checklist before writing the diff:\n"
        f"{_TASK_CHECKLIST}\n"
        f"IMPORTANT: diff context lines (lines beginning with a single space) must match "
        f"the actual file content exactly — use only the raw code indentation, "
        f"not the `NNNN >>>` display prefix shown in the Source section above.\n"
        f"\n"
        f">>> OUTPUT exactly as specified in the system instructions: the PLAN "
        f"(Blockers, then OLD -> NEW loop headers), then the "
        f"unified diff, and end the response there. No markdown, no code "
        f"fences, nothing after the diff."
    )
    return "\n".join(parts)


# The three analysis steps every edit mode asks for, verbatim.
_TASK_CHECKLIST = (
    "  1. Classify each variable under 'RAW' above into one of causes 1-6.\n"
    "  2. Apply that cause's fix COMPLETELY — every bound, initial value, and "
    "boundary case re-derived for the new schedule, in canonical form.\n"
    "  3. Put the parallelism at a level with enough work per activation to "
    "beat thread overhead (the loop structure above marks which levels those "
    "are).\n"
)


def _evidence_sections(ev: EvidencePackage, deps_header: str) -> List[str]:
    """The evidence body shared by every edit mode: dependences, reductions,
    DiscoPoP's classification, loop nest, calls, Do-All blockers, and the last
    failure reason.  Only the surrounding header/source/task text differs
    between --edit-mode diff, function and direct."""
    region = (ev.start_line, ev.end_line)
    parts = [
        f"{deps_header}\n"
        "(grouped per variable, each tagged [array element] or [scalar])",
        _fmt_deps(ev.raw_deps, "RAW — read-after-write (the blocking ones)",
                  ev.line_text, region),
        _fmt_deps(ev.war_deps, "WAR — write-after-read", region=region),
        _fmt_deps(ev.waw_deps, "WAW — write-after-write", region=region),
    ]
    if ev.reduction_vars:
        parts.append(f"### Reduction variables: {', '.join(ev.reduction_vars)}\n")
    for section in (
        _fmt_classification(ev),
        _fmt_extra_vars(ev),
        _array_dep_note(ev),
        _fmt_loop_nest(ev),
        _fmt_calls(ev),
        fmt_blockers(ev.prevented_deps),
    ):
        if section:
            parts.append(section)
    if ev.tier1_failure_reason:
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
            "— usually cause 3 or 4 (see 'Choosing the fix' below)."
        )
    if scalar_raw:
        out.append(
            f"  - RAW on SCALARS: {', '.join(scalar_raw)} — usually cause 1 "
            "(storage reuse) or cause 2 (a reduction)."
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


# Iterations per loop activation below which OpenMP thread startup (tens of
# microseconds) tends to outweigh the work, so the parallel build is not faster
# and the L4 performance gate reverts the rewrite.  A coarse rule of thumb — it
# is stated to the model as one, not as a hard cutoff.
_FINE_GRAINED_ITERS = 1000


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
            verdict = (
                f"  <-- TOO FINE-GRAINED on its own (~{lp['avg']} iterations per "
                f"activation, and each activation is a separate parallel region): "
                f"parallelize an enclosing loop instead, or make each iteration "
                f"do more work"
            )
        else:
            verdict = "  <-- enough iterations per activation to be worth parallelizing"
        out.append(
            f"  {'  ' * lp['depth']}- loop at lines {lp['start']}–{lp['end']}  "
            f"induction variable(s): {idx}  |  {lp['entries']} activation(s) "
            f"× ~{lp['avg']} iterations = {lp['total']:,} total (max {lp['max']})"
            f"{verdict}"
        )
    out.append(
        "  Induction variables are managed by OpenMP automatically — dependences "
        "on them are NEVER the real blocker; do not restructure to 'fix' them.\n"
        f"  Rule of thumb used above: below ~{_FINE_GRAINED_ITERS} iterations per "
        "activation, thread startup costs more than the loop saves, so step 4 "
        "rejects the rewrite for lack of speedup. Prefer the OUTERMOST loop you "
        "can legally parallelize among those marked worth parallelizing."
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
    """Cause 3/4 playbook, injected ONLY when the blocking RAW deps are on array
    elements.  The system prompt states cause 3 in one general paragraph; the
    tactical detail (which decoupling is valid, and the ways each one is
    silently botched) lives here so it reaches the model exactly when the
    profile says it applies, instead of costing every region its context.
    Returns '' when the blocking deps are all scalar — there privatization is
    the right move and none of this is relevant."""
    array_vars = sorted({d.variable for d in ev.raw_deps if getattr(d, "kind", "scalar") == "array"})
    if not array_vars:
        return ""
    return (
        "### Choosing the fix for this array dependence\n"
        f"The loop-carried RAW dependence is on ARRAY ELEMENTS "
        f"({', '.join(array_vars)}), not on a scalar.  Work down this list:\n"
        "  - Is the array SCRATCH space that each iteration fully overwrites "
        "before reading (no value flows between iterations)?  Then it is cause "
        "1 after all: give each iteration its own copy and stop there.\n"
        "  - Otherwise a value really does flow, so answer the SAME-SWEEP "
        "READ-BACK question: can a value written during one sweep be read again "
        "later in the SAME sweep?\n"
        "      NO  — each new value depends only on the previous sweep (a map or "
        "stencil).  Use a SEPARATE OUTPUT BUFFER: read every input from the "
        "previous-sweep buffer, write every result into the new one, then SWAP "
        "the two (or alternate their roles by sweep parity).  Do not copy back "
        "— that adds a whole extra pass per sweep; copy once after the last "
        "sweep only if later code must find the result in the original array.  "
        "Give the scratch buffer the SAME storage class and lifetime as the "
        "array it mirrors and allocate it ONCE outside the sweep loop; a large "
        "mirror declared inside the loop lands on the stack and is rebuilt "
        "every sweep.\n"
        "      YES — the update cascades along the array within the sweep, so a "
        "separate buffer is INVALID.  PARTITION instead: split each sweep into "
        "ordered sub-passes whose iterations touch DISJOINT, non-adjacent "
        "elements (even-indexed pairs then odd-indexed, or red cells then "
        "black).  Each sub-pass is then a Do-All, and running them in order "
        "reproduces the sequential result.  Under this schedule a value moves a "
        "SHORTER distance per sweep than the old cascade carried it, so "
        "RE-DERIVE every bound: each sub-pass must cover its whole class on "
        "every sweep.  A bound copied from the old code that shrinks as it "
        "progresses (because part of the array was already settled) is WRONG "
        "here, and doing more comparisons than the original is exactly what "
        "correctness requires.\n"
        "  - If neither applies because iteration i needs iteration i-1's "
        "result outright, it is cause 4 (recurrence): reformulate or leave it.\n"
        "  Copying or renaming the array is never a fix on its own: the same "
        "order-dependent updates performed on a copy carry the same dependence.\n"
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


def _build_function_prompt(evidence: EvidencePackage) -> str:
    """Prompt for --edit-mode function: show the whole enclosing function and the
    target region's dependence profile, and ask for the complete rewritten
    function back (no diff)."""
    region_label = {
        "loop": "loop", "function": "function body", "cu": "basic block",
    }.get(evidence.region_type, "code region")
    fname = evidence.enclosing_function_name or "(enclosing function)"

    parts = [
        f"## Source file: {evidence.source_file}",
        f"## Function to rewrite: {fname}  "
        f"(lines {evidence.enclosing_function_start}–{evidence.enclosing_function_end})",
        f"## Target region: {region_label} {evidence.region_id} at lines "
        f"{evidence.start_line}–{evidence.end_line}\n",
        _fmt_digest(evidence),
        "### Current function (rewrite this whole function):",
        "```cpp",
        evidence.enclosing_function_source,
        "```\n",
    ]
    parts.extend(_evidence_sections(
        evidence, "### Runtime data dependences in the target region (observed)"))

    parts.append(
        "### Task\n"
        f"Restructure the {region_label} (lines {evidence.start_line}–"
        f"{evidence.end_line}) inside `{fname}` so that after re-profiling "
        "DiscoPoP detects a genuinely parallel pattern (Do-All, Reduction, "
        "Pipeline, or Task-Parallel) that compiles cleanly, is race-free under "
        "ThreadSanitizer, and achieves measurable speedup.\n"
        "\n"
        "Work through this checklist:\n"
        f"{_TASK_CHECKLIST}"
        "\n"
        ">>> OUTPUT exactly as specified in the system instructions: the PLAN "
        "(Blockers, then OLD -> NEW loop headers), then the ENTIRE "
        "rewritten function as ONE ```cpp code block, and end the response "
        "there. Keep the same function name and signature."
    )
    return "\n".join(parts)


def _build_direct_prompt(evidence: EvidencePackage, ws_file: Path) -> str:
    """Prompt for --edit-mode direct: the model edits `ws_file` (a private
    working copy of the source) with its own Read/Edit/Write tools instead of
    emitting an edit as text.  The excerpt below is context only — the file on
    disk is the authority, and the model is told to read it."""
    region_label = {
        "loop": "loop", "function": "function body", "cu": "basic block",
    }.get(evidence.region_type, "code region")
    fname = evidence.enclosing_function_name or "(enclosing function)"

    parts = [
        f"## File to edit: {ws_file}",
        f"## Function containing the target region: {fname}  "
        f"(lines {evidence.enclosing_function_start}–{evidence.enclosing_function_end})",
        f"## Target region: {region_label} {evidence.region_id} at lines "
        f"{evidence.start_line}–{evidence.end_line}\n",
        _fmt_digest(evidence),
        "### The function as it currently stands in the file (excerpt — read the "
        "file itself before editing; line numbers here are the file's own):",
        "```cpp",
        evidence.enclosing_function_source,
        "```\n",
    ]
    parts.extend(_evidence_sections(
        evidence, "### Runtime data dependences in the target region (observed)"))

    parts.append(
        "### Task\n"
        f"Edit `{ws_file}` so that the {region_label} (lines "
        f"{evidence.start_line}–{evidence.end_line}) inside `{fname}` is "
        "restructured for parallelism: after re-profiling, DiscoPoP must detect "
        "a genuinely parallel pattern (Do-All, Reduction, Pipeline, or "
        "Task-Parallel) that compiles cleanly, is race-free under "
        "ThreadSanitizer, and achieves measurable speedup.\n"
        "\n"
        "Work through this checklist:\n"
        f"{_TASK_CHECKLIST}"
        "\n"
        ">>> Read the file, state the PLAN (Blockers, then OLD -> NEW loop "
        "headers), then APPLY the rewrite with the Edit tool. Do not print "
        "a diff or the rewritten code — the file's content is what is used. "
        "Keep the function's name and signature, and edit no other file."
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Diff validation
# ---------------------------------------------------------------------------

def _extract_diff(text: str) -> Optional[str]:
    """Pull the unified diff out of the response.  A short plain-text PLAN is
    allowed before it (see _OUTPUT_DIFF), so scan for the header rather than
    assuming the diff starts at line 0.  A '--- ' line only starts the diff if
    the NEXT line is its '+++ ' partner; that way a stray dash-run or a plan
    line beginning with '---' does not swallow the real header."""
    lines = text.splitlines()
    fallback = None
    for i, line in enumerate(lines):
        if line.startswith("diff --git"):
            return "\n".join(lines[i:])
        if line.startswith("--- "):
            if i + 1 < len(lines) and lines[i + 1].startswith("+++ "):
                return "\n".join(lines[i:])
            if fallback is None:
                fallback = i
    return "\n".join(lines[fallback:]) if fallback is not None else None


def _is_valid_diff(diff: str) -> bool:
    return "---" in diff and "+++" in diff and "@@" in diff


def make_diff(old_text: str, new_text: str, path: str) -> str:
    """Unified diff between two full file contents, safe for `patch`.

    Both edit modes that build their own diff go through here.  The subtlety is
    a file whose last line has no newline: difflib then emits an unterminated
    '-' line that runs straight into the following '+' line, producing a patch
    the apply stage rejects as malformed.  Standard unified-diff form marks that
    case explicitly instead, which GNU and BSD patch both accept."""
    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=path,
        tofile=path,
    )
    out = []
    for line in diff:
        out.append(line if line.endswith("\n")
                   else line + "\n\\ No newline at end of file\n")
    return "".join(out)


def normalize_code(text: str) -> str:
    """Strip comments and all whitespace so a 'rewrite' that only reformats or
    re-comments the input is recognised as the no-op it is."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return re.sub(r"\s+", "", text)


_CODE_FENCE_RE = re.compile(r"```(?:cpp|c\+\+|cxx|c)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def _extract_code(text: str) -> Optional[str]:
    """For --edit-mode function: pull the rewritten function out of the response.
    Prefer the LAST fenced ```cpp block (the response may open with a short PLAN,
    and the final block is the code the model was told to end with); otherwise
    use the raw text.  Returns None if it doesn't look like a function (no
    braces)."""
    matches = list(_CODE_FENCE_RE.finditer(text))
    code = (matches[-1].group(1) if matches else text).strip("\n")
    if "{" in code and "}" in code:
        return code
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _make_client(provider: str, api_key: Optional[str], api_base: Optional[str]) -> Any:
    """Create the provider client.  'anthropic' (default) uses the Anthropic SDK;
    'openai-compat' uses the OpenAI SDK pointed at an OpenAI-compatible endpoint
    (e.g. a self-hosted vLLM server) via api_base; 'claude-agent-sdk' has no
    persistent client — each call spins up the local `claude` CLI headlessly via
    the Claude Agent SDK, authenticated through the Claude Code subscription
    login (`claude login`) rather than a billed API key."""
    if provider == "openai-compat":
        try:
            import openai
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "provider 'openai-compat' requires the openai package "
                "(`venv/bin/pip install openai`)."
            ) from e
        return openai.OpenAI(api_key=api_key or "EMPTY", base_url=api_base)
    if provider == "claude-agent-sdk":
        return None
    return anthropic.Anthropic(api_key=api_key)


# One real Claude Code CLI session per region, kept for the life of this
# process: session_key -> the CLI's own session_id.  Populated/consulted by
# _complete_claude_agent_sdk() below.  Keyed on EvidencePackage.region_fingerprint
# (content-based), NOT region_id — DiscoPoP reassigns region_id from a global
# counter after a re-profile, so it can silently point at a different, unrelated
# region; resuming a session under a reused region_id would leak that other
# region's full transcript into this one.
_region_sessions: Dict[str, str] = {}

# --edit-mode direct: one throwaway workspace per region, keyed the same way.
# Each holds a single file — a copy of the source the model is allowed to edit
# — plus the on-disk content it was copied from, so a later call can tell an
# edit the model made from a change the controller made (another region's
# accepted patch, or a revert).
_region_workspaces: Dict[str, Tuple[Path, str]] = {}


def _sync_workspace(session_key: str, source_file: str) -> Tuple[Path, str]:
    """Return (workspace copy of `source_file`, its current on-disk content).

    The workspace is created on the region's first direct-mode call and then
    reused: within one region, retries keep whatever the model already edited,
    so it refines its own attempt against the quality-gate feedback instead of
    starting from the original every time.  It is re-seeded from disk whenever
    the real file changed underneath it (another region's patch was applied, or
    this region's was reverted), because the stale edits no longer apply."""
    disk = Path(source_file).read_text()
    entry = _region_workspaces.get(session_key)
    if entry is not None:
        ws_file, base = entry
        if ws_file.exists() and base == disk:
            return ws_file, disk
    else:
        ws_file = Path(tempfile.mkdtemp(prefix="dp_agent_edit_")) / Path(source_file).name
    ws_file.write_text(disk)
    _region_workspaces[session_key] = (ws_file, disk)
    return ws_file, disk


def _workspace_diff(ws_file: Path, source_file: str, disk: str) -> Optional[str]:
    """Unified diff of the model's edited copy against the real source, ready
    for the L4 gate.  Built from the actual on-disk content, so it always
    applies cleanly.  None when the model changed nothing that matters (no
    edit, or a comment/whitespace-only edit)."""
    edited = ws_file.read_text()
    if normalize_code(edited) == normalize_code(disk):
        return None
    return make_diff(disk, edited, source_file)


def _complete_claude_agent_sdk(
    model: str,
    system: str,
    current: list,
    session_key: str,
    workspace: Optional[Path] = None,
) -> str:
    """Run one turn through the local `claude` CLI headlessly (Claude Agent
    SDK), billed against the Claude Code subscription rather than a per-token
    API key.  `model` accepts Claude Code's own aliases (e.g. "haiku",
    "sonnet", "opus") as well as full model IDs.

    Without `workspace` (edit modes diff/function) tool use is disabled and the
    turn count capped at 1 — the call site wants a single text response, never
    agentic file/bash actions against the profiled source tree.  With
    `workspace` (--edit-mode direct) the model gets Read/Edit/Write confined to
    that directory, which holds nothing but a private COPY of the source file:
    the real, profiled source is not reachable from there, and the answer is
    the copy's final content rather than anything the model prints.

    Unlike the other two providers (stateless HTTP — the full conversation is
    resent on every call), this keeps one real Claude Code session PER REGION:
    the first call for a region starts a fresh session; every later call for
    that same region (a format retry inside call_llm(), or the next budget
    attempt from the controller) resumes it via `resume=<session_id>` and
    sends ONLY the newest message (`current[-1]`, by construction always the
    one new thing to say this turn — see call_llm()'s docstring) — the CLI
    reconstructs everything else from its own on-disk session transcript, so
    the model genuinely remembers prior diff attempts and quality-gate
    feedback for that region instead of having the whole history re-explained
    to it on every call."""
    try:
        from claude_agent_sdk import (  # type: ignore[import-not-found]
            AssistantMessage,
            ClaudeAgentOptions,
            ResultMessage,
            TextBlock,
            query,
        )
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "provider 'claude-agent-sdk' requires the claude-agent-sdk package "
            "(`venv/bin/pip install claude-agent-sdk`) and the `claude` CLI "
            "installed and logged in (`claude login`)."
        ) from e

    prompt = current[-1]["content"]

    def _options(resume: Optional[str]) -> Any:
        return ClaudeAgentOptions(
            system_prompt=system,
            model=model,
            # Direct mode needs several turns (read → edit → …); the text modes
            # want exactly one response and nothing else.
            max_turns=24 if workspace else 1,
            allowed_tools=["Read", "Edit", "Write"] if workspace else [],
            cwd=str(workspace) if workspace else None,
            permission_mode="acceptEdits" if workspace else "dontAsk",
            # Without this, the CLI auto-loads this project's own CLAUDE.md and
            # any user/project settings ("user", "project" are the defaults)
            # into context alongside our system prompt — verified
            # experimentally: the model becomes aware of unrelated
            # dev-guideline instructions. Keep the region-restructuring system
            # prompt uncontaminated.
            setting_sources=[],
            resume=resume,
        )

    async def _run(resume: Optional[str]) -> Tuple[str, Optional[str]]:
        text = ""
        session_id: Optional[str] = None
        async for message in query(prompt=prompt, options=_options(resume)):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text += block.text
            if isinstance(message, ResultMessage):
                session_id = message.session_id
        return text, session_id

    resume_id = _region_sessions.get(session_key)
    try:
        text, session_id = asyncio.run(_run(resume_id))
    except Exception:
        if resume_id is None:
            raise
        # The cached session may have gone stale (its on-disk transcript
        # evicted, etc.) — drop it and retry once as a fresh session rather
        # than aborting the whole run over a resumable hiccup.
        _region_sessions.pop(session_key, None)
        text, session_id = asyncio.run(_run(None))

    if session_id:
        _region_sessions[session_key] = session_id
    return text


class LLMConnectionError(RuntimeError):
    """The LLM endpoint could not be reached (server not running, wrong
    --api-base, or network failure).  Fatal for the whole run — every region
    would hit the same error — so the controller aborts cleanly on it."""


def _complete(
    provider: str, client: Any, model: str, current: list, system: str, session_key: str = "",
    workspace: Optional[Path] = None,
) -> str:
    """Run one completion against the chosen provider and return the raw text.

    Both providers receive the same `system` instructions and the same
    user/assistant conversation; only the wire format differs (Anthropic takes
    `system` separately, OpenAI takes it as the first message).  `session_key`
    is only used by 'claude-agent-sdk', to key its per-region CLI session — it
    must be a content-based identity (EvidencePackage.region_fingerprint), not
    DiscoPoP's region_id, which gets reassigned to unrelated regions after a
    re-profile.  `workspace` (--edit-mode direct, claude-agent-sdk only) is the
    directory the model may edit; passing it turns on its file tools."""
    try:
        if provider == "openai-compat":
            resp = client.chat.completions.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "system", "content": system}] + current,
            )
            return resp.choices[0].message.content or ""
        if provider == "claude-agent-sdk":
            return _complete_claude_agent_sdk(model, system, current, session_key, workspace)
        resp = client.messages.create(
            model=model,
            max_tokens=4096,
            system=[{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=current,
        )
        return str(resp.content[0].text)
    except Exception as e:
        # Both the openai and anthropic SDKs raise an `APIConnectionError`
        # when the endpoint is unreachable; match by name so the openai SDK
        # stays an optional dependency.
        if type(e).__name__ == "APIConnectionError":
            endpoint = getattr(client, "base_url", None) or "the configured endpoint"
            raise LLMConnectionError(
                f"cannot reach the LLM endpoint at {endpoint} — "
                f"is the model server running?"
            ) from e
        if type(e).__name__ in ("CLINotFoundError", "CLIConnectionError", "ProcessError"):
            raise LLMConnectionError(
                f"cannot run the Claude Code CLI for provider 'claude-agent-sdk' — "
                f"is `claude` installed and on PATH, and are you logged in "
                f"(`claude login`)? ({e})"
            ) from e
        raise


def call_llm(
    evidence: EvidencePackage,
    model: str,
    api_key: Optional[str] = None,
    max_format_retries: int = 2,
    messages: Optional[list] = None,
    provider: str = "anthropic",
    api_base: Optional[str] = None,
    edit_mode: str = "diff",
    verbose: bool = False,
) -> tuple[Optional[str], list]:
    """Call the LLM and return (output or None, updated messages).

    In edit_mode="diff" (default) the output is a unified diff.  In
    edit_mode="function" it is the complete rewritten enclosing function (the
    controller splices it in by line range and generates the diff itself), which
    avoids the LLM having to produce a byte-exact diff.  In edit_mode="direct"
    (claude-agent-sdk only) the model EDITS a private copy of the file with its
    own Read/Edit/Write tools and the returned string is the diff of that copy
    against the real source — the model never has to express an edit as text at
    all.  Direct mode returns "" (not None) when the model left the file
    unchanged, so the controller can tell "made no edit" apart from "produced
    no usable answer".

    On the first call for a region pass messages=None — the initial prompt is
    built from evidence.  Pass the list returned by the previous call on
    subsequent budget retries.  Every entry in `messages` is preserved
    (controller.py only ever appends), but by construction the LAST entry is
    always the one genuinely new thing to say this turn: the initial prompt on
    the very first call, a re-prompt on a format retry, or the quality-gate
    feedback on the next budget attempt.  The "anthropic"/"openai-compat"
    providers still resend the full list every call (both are stateless HTTP
    APIs); "claude-agent-sdk" instead sends only that last entry and relies on
    its own real per-region CLI session (keyed by evidence.region_fingerprint —
    a content-based identity, NOT the reassignable region_id) to supply
    everything earlier — see _complete_claude_agent_sdk().

    `provider` selects the backend: "anthropic" (default, billed API key),
    "openai-compat" (any OpenAI-compatible endpoint at `api_base`, e.g. a
    self-hosted vLLM), or "claude-agent-sdk" (runs the local `claude` CLI
    headlessly via the Claude Agent SDK, billed against the Claude Code
    subscription instead of a per-token API key — `model` accepts Claude
    Code's own aliases like "haiku" as well as full model IDs, and `api_key`
    is ignored since auth comes from `claude login`).
    """
    function_mode = edit_mode == "function"
    direct_mode = edit_mode == "direct"
    if direct_mode and provider != "claude-agent-sdk":
        raise RuntimeError(
            "--edit-mode direct requires --provider claude-agent-sdk (it is the "
            "only backend that can edit files itself)."
        )
    system = (_SYSTEM_DIRECT if direct_mode
              else _SYSTEM_FUNCTION if function_mode else _SYSTEM)
    client = _make_client(provider, api_key, api_base)
    session_key = evidence.region_fingerprint or evidence.region_id

    workspace_file: Optional[Path] = None
    disk = ""
    if direct_mode:
        workspace_file, disk = _sync_workspace(session_key, evidence.source_file)

    if messages is None:
        # First attempt for this region — build initial prompt from evidence.
        if direct_mode:
            assert workspace_file is not None
            user_prompt = _build_direct_prompt(evidence, workspace_file)
        elif function_mode:
            user_prompt = _build_function_prompt(evidence)
        else:
            user_prompt = _build_prompt(evidence)
        messages = [{"role": "user", "content": user_prompt}]

    current = list(messages)
    kind = "direct" if direct_mode else "function" if function_mode else "diff"

    for attempt in range(max_format_retries + 1):
        if verbose:
            last_user = next(
                (m["content"] for m in reversed(current) if m["role"] == "user"), ""
            )
            viz.llm_request(model, provider, system, last_user, attempt=attempt)

        text = _complete(provider, client, model, current, system,
                         session_key=session_key,
                         workspace=workspace_file.parent if workspace_file else None)

        if verbose:
            viz.llm_response(text, kind=kind)

        if direct_mode:
            assert workspace_file is not None
            # The answer is the file the model left behind, not its prose.
            out = _workspace_diff(workspace_file, evidence.source_file, disk)
        else:
            out = _extract_code(text) if function_mode else _extract_diff(text)
        valid = (
            out is not None if function_mode or direct_mode
            else bool(out and _is_valid_diff(out))
        )

        if verbose:
            viz.llm_extracted(kind, out if valid else None)

        if valid:
            # Return messages with assistant turn appended so the controller
            # can extend the conversation with quality-gate feedback and retry.
            return out, current + [{"role": "assistant", "content": text}]

        # Free format re-prompt — doesn't consume a budget slot.
        if attempt < max_format_retries:
            reprompt = (
                f"You did not change `{workspace_file}` (comment or formatting "
                "edits do not count). Read the file, then APPLY your rewrite "
                "with the Edit tool — describing it in your reply has no effect."
                if direct_mode else
                "Your response must end with the complete rewritten function as a "
                "single ```cpp code block — signature and full body, no diff. "
                "A short plain-text PLAN before the code block is allowed; "
                "nothing may follow the code block."
                if function_mode else
                "Your response must END with a unified diff.\n"
                "After your short plain-text PLAN, write '--- <original_file>' "
                "on its own line, then '+++ <modified_file>' on the next, then "
                "one or more '@@ … @@' hunks — and stop there.\n"
                "No code fences, and no PLAN line may start with '---', '+++' "
                "or '@@'."
            )
            current = current + [
                {"role": "assistant", "content": text},
                {"role": "user", "content": reprompt},
            ]

    # Direct mode's only failure here is "the model never edited the file" —
    # report it as the no-op ("") the controller feeds back, not as garbage output.
    return ("" if direct_mode else None), current
