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

import re
import textwrap
from typing import Any, Dict, List, Optional, Set, Tuple

import anthropic

from . import viz
from .types import EvidencePackage

# ---------------------------------------------------------------------------
# System prompt (cached across all calls in a session)
# ---------------------------------------------------------------------------

_SYSTEM_CORE = textwrap.dedent("""\
    You are an expert in C/C++ parallelization and compiler dependency analysis,
    acting as the restructuring stage of DiscoPoP, an automatic OpenMP parallelism
    profiler.

    ------------------------------------------------------------------
    HOW YOUR OUTPUT IS USED
    ------------------------------------------------------------------
    DiscoPoP profiled ONE code region and could not extract safe parallelism from
    it: either it found no pattern, or the pattern it found produced an OpenMP
    pragma that failed validation (did not compile, raced under ThreadSanitizer,
    changed the program's output, or gave no speedup).

    You rewrite the region's SEQUENTIAL source so that the parallelism becomes
    explicit and safe.  You do NOT insert OpenMP pragmas — DiscoPoP re-profiles
    your rewrite and inserts them itself.

    ------------------------------------------------------------------
    THE ONE CONTRACT (verified automatically)
    ------------------------------------------------------------------
    Your rewrite is compiled, run sequentially, and its printed OUTPUT is
    compared BYTE-FOR-BYTE with the original program's.  Any difference is an
    automatic rejection.  That is the whole contract:
      - The OUTPUT must be identical.  Execution order, operation count, loop
        bounds, extra buffers, extra passes — all of these are YOURS TO CHANGE
        whenever the new schedule needs it.  Doing MORE comparisons or updates
        than the original is fine; a rewrite is judged by its output, never by
        how closely its code resembles the original.
      - Do not rename the function or change its signature; do not add, remove,
        or reorder I/O or change output formatting.

    ------------------------------------------------------------------
    WHAT COUNTS AS SUCCESS
    ------------------------------------------------------------------
    DiscoPoP can only exploit these patterns, so your rewrite must expose at
    least one of them:
      - Do-All        — loop iterations are fully independent.
      - Reduction     — iterations combine into an associative/commutative accumulator.
      - Pipeline      — ordered producer -> consumer stages with no back-edges.
      - Task-parallel — independent regions connected by explicit data flow.
    Aim for a rewrite that not only is detectable but actually pays off: coarse
    enough that thread-spawn overhead is amortised.

    Your job is to EXPOSE PARALLELISM, not to speed up the sequential version.
    A faster serial algorithm is NOT a valid answer.  In particular, do NOT:
      - add an early-termination / "did anything change this pass" shortcut,
      - substitute a lower-complexity but still-serial algorithm,
      - return the original code (or a renamed/reordered copy of it) unchanged.
    None of these remove the blocking dependence.  Every rewrite must make some
    loop's iterations genuinely independent (Do-All / Reduction) or split it
    into independent stages/tasks.

    ------------------------------------------------------------------
    READ THE EVIDENCE FIRST — REASON FROM IT, NOT FROM THE ALGORITHM'S NAME
    ------------------------------------------------------------------
    Each request gives you the region source, the runtime dependences observed
    (RAW / WAR / WAW with line and variable), any reduction variables, DiscoPoP's
    exact Do-All blockers, and — when a pragma was already tried — why it failed.
    Do not guess from what the code "looks like"; decide from this evidence.
      - RAW (read-after-write) across iterations is the real blocker: some
        iteration reads a value another iteration wrote.  Removing these is the job.
      - WAR / WAW are usually STORAGE conflicts (a variable reused across
        iterations), not true data flow — they typically dissolve under
        privatization or renaming.
      - A blocker marked STATIC origin may be a dependence DiscoPoP could not rule
        out rather than one that truly occurs — often removable by privatizing or
        first-writing the variable inside the loop.  A DYNAMIC origin blocker was
        actually observed at run time and must be genuinely broken.
      - Loop INDUCTION VARIABLES (listed per loop in the evidence) are handled by
        OpenMP automatically: dependences on them are never the real blocker.
        Never restructure to "fix" an induction variable.

    ------------------------------------------------------------------
    METHOD — CLASSIFY EACH BLOCKING DEPENDENCE BY ITS CAUSE, THEN FIX THE CAUSE
    ------------------------------------------------------------------
    For every RAW / blocker, decide which cause below it is; the cause dictates
    the fix.  Match on the DATA FLOW, not on the surface syntax or algorithm.

      1. STORAGE / FALSE DEPENDENCE — a scalar or buffer is REUSED across
         iterations (a temp, an index, scratch space) but carries no real value
         from one iteration to the next.
         Fix: give each iteration its own instance — declare the variable inside
              the loop body (privatize) or rename to break the reuse.  No
              algorithmic change.

      2. ACCUMULATION / REDUCTION — every iteration reads AND writes the same
         variable through an associative, commutative operator
         (+, *, min, max, count, logical and/or).
         Fix: isolate it as a clean reduction — one accumulation per iteration
              into one variable, with no other writes to shared state in the body.
              Strip unrelated work that hides the reduction (see cause 6).

      3. IN-PLACE COUPLING — within ONE sweep, an iteration reads array elements
         that another iteration of the SAME sweep writes (updates that touch an
         element and its neighbour, a compare-and-swap of adjacent items, or
         writing back into the array being read).

         DECIDE FIRST — the same-sweep read-back question: can a value WRITTEN
         during one sweep be READ again later in the SAME sweep?
           - NO — every new value depends only on the PREVIOUS sweep (a pure
             map / stencil, e.g. new[i] = f(old[i-1], old[i], old[i+1]))
             -> use (a).
           - YES — the update propagates / cascades along the array within the
             sweep (e.g. a swap whose result the next iteration compares)
             -> (a) is INVALID; you MUST use (b).

         Fix:
           a) DOUBLE-BUFFER: allocate a separate output array; read every input
              exclusively from the previous-sweep buffer, write every result into
              the new buffer, then swap the buffers after the sweep.
           b) PARTITION / COLOUR: keep the updates in place, but split each sweep
              into ordered sub-passes whose iterations touch DISJOINT,
              non-adjacent elements (e.g. even-indexed pairs, then odd-indexed
              pairs; or "red" cells, then "black").  Within one sub-pass every
              iteration is independent -> Do-All; running the sub-passes in
              order reproduces the sequential result.  Under the new schedule a
              value moves a SHORTER distance per sweep than the old cascade
              carried it, so RE-DERIVE every loop bound: each sub-pass must
              cover every element of its class on every sweep — a bound copied
              from the old code that shrinks with progress (assuming part of
              the array is already settled) is WRONG here, and covering the
              full range (more comparisons than the original) is exactly what
              correctness requires.

         WRONG (removes NOTHING): copying the array into a renamed buffer and
              then performing the SAME order-dependent, in-place updates on the
              copy.  A rename is not a decoupling — the loop-carried dependence
              is unchanged, and the rewrite will be rejected.

      4. TRUE RECURRENCE / SCAN — iteration i's result is defined in terms of
         iteration i-1's result (running total, propagation, chained state).
         Fix: reformulate, do not privatize.  Options: a closed-form expression
              of i, a parallel prefix-scan, or a blocked / recursive-doubling
              formulation.  If the recurrence is genuinely serial and cannot be
              reassociated, leave it unparallelized rather than emit an unsafe
              rewrite.

      5. NON-CANONICAL CONTROL FLOW — the loop can't be parallelized because its
         trip count is not known up front: break, continue, return, goto, or a
         non-affine bound.
         Fix: convert to a fixed-trip-count loop with IDENTICAL output — replace
              early exit with a flag/mask evaluated every iteration and tested
              after the loop; move compound conditions into the bound.

      6. SERIALIZATION BY MIXED CONCERNS — the body fuses independent
         computations, or repeats loop-invariant work, hiding the parallel part.
         Fix: hoist invariant work out of the loop; SPLIT (fission) a loop whose
              statements are independent across iterations into separate loops,
              each parallelizable on its own; conversely FUSE trivially small
              parallel loops to raise granularity.

    ------------------------------------------------------------------
    WORKED EXAMPLE (method applied end-to-end)
    ------------------------------------------------------------------
    Evidence given: RAW on scalar `t` (lines 3→4), RAW on scalar `norm`
    (line 5→5, also listed as reduction candidate `norm (+)`), induction
    variable `i`, no array-element RAW.

        1  double t; double norm = 0;
        2  for (int i = 0; i < n; i++) {
        3      t = a[i] * s;
        4      b[i] = t + c[i];
        5      norm += t * t;
        6  }

    Reasoning: `t` is written before it is read in EVERY iteration — no value
    flows between iterations, so the RAW on `t` is cause 1 (storage reuse):
    declare it inside the body.  `norm` is read-modify-write through `+`, cause
    2 (reduction): keep exactly one accumulation.  No array-element RAW, so no
    buffering or partitioning is needed.

    Rewrite (iterations now fully independent Do-All + reduction):

        1  double norm = 0;
        2  for (int i = 0; i < n; i++) {
        3      double t = a[i] * s;
        4      b[i] = t + c[i];
        5      norm += t * t;
        6  }

    Byte-identical output — the change removes the reported dependences and
    touches nothing else.

    ------------------------------------------------------------------
    SCOPE OF CHANGE
    ------------------------------------------------------------------
    Change what the diagnosed cause requires and nothing else: statements
    unrelated to the blocking dependences, I/O, and code outside the region
    stay as they are.  But when the cause requires an algorithm-level reshaping
    (double-buffering, coloured sub-passes, fission, a scan reformulation),
    carry it out COMPLETELY — including re-derived bounds and initial values.
    A timid half-measure that keeps the old schedule's bounds or ordering is
    the most common way to fail.
    When the reported failure was "no speedup" (not a race), the dependence is
    already gone — restructure for GRANULARITY (coarsen, fuse, hoist, move
    parallelism to an outer level), not for correctness.

    ------------------------------------------------------------------
    OPENMP-CANONICAL FORM (every loop you intend to be parallel must satisfy ALL)
    ------------------------------------------------------------------
      - Condition compares the loop variable DIRECTLY against a loop-invariant
        bound:  RIGHT `i < n - 1`   WRONG `i + 1 < n`  (compound left-hand side).
      - Increment is i++, i--, i += c, or i -= c with loop-invariant c.
      - Body has NO break, continue, return, or goto.
      - Trip count is computable before the loop begins.
    NEVER INTRODUCE new break, continue, return, or goto as part of a
    transformation — not in the target loop and not in any enclosing loop you
    touch.  If the existing code has such control flow, convert it to canonical
    form (cause 5); do not add more.
""")

# Output-format instruction appended per edit mode.
_OUTPUT_DIFF = textwrap.dedent("""\

    >>> OUTPUT A UNIFIED DIFF ONLY. <<<
    No prose, no explanation, no markdown, no code fences. Your ENTIRE response
    must be the diff itself, beginning with '--- ' and containing '+++ ' and
    '@@ ' markers. Any text that is not part of the diff causes the response to
    be rejected.
""")

_OUTPUT_FUNCTION = textwrap.dedent("""\

    >>> OUTPUT FORMAT: PLAN, THEN THE COMPLETE REWRITTEN FUNCTION. <<<
    First write PLAN — plain text, no code block, in exactly this shape:
      Line 1: "Same-sweep read-back: YES/NO/N-A — <one line why>"  (can a value
              written during one sweep be read again later in the SAME sweep?
              YES means double-buffering is invalid — you must partition.
              N-A when the region has no in-place array update at all.)
      Lines 2-5: for each blocking dependence, its cause (1-6) and the fix.
      Last line: "Loop headers: <the exact for(...) header text of every loop
              you changed or added>" — the code block must contain these
              headers verbatim; re-derive any bound the old schedule assumed.
    Then output the ENTIRE rewritten function — its signature and full body,
    from the opening `{` to the closing `}` — as ONE ```cpp code block, and end
    your response there.  Do NOT output a diff, line numbers, or markers.
    Rewrite only this one function; do not rename it or change its signature.
    The agent applies the code block verbatim in place, so it must compile as-is.
""")

# Diff mode keeps the original system prompt verbatim; function mode swaps the
# trailing output instruction.
_SYSTEM = _SYSTEM_CORE + _OUTPUT_DIFF
_SYSTEM_FUNCTION = _SYSTEM_CORE + _OUTPUT_FUNCTION

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
        f"## Region: {evidence.region_id}  type={region_label}  ({exec_info})\n",
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
        "### Runtime data dependences (observed across all executions)\n"
        "(grouped per variable; each is tagged [array element] or [scalar]: an "
        "array-element dep is on the DATA and is usually algorithmic; a scalar "
        "dep is usually a storage conflict removable by privatization/renaming)",
        _fmt_deps(evidence.raw_deps, "RAW — read-after-write (the blocking ones)",
                  evidence.line_text, (evidence.start_line, evidence.end_line)),
        _fmt_deps(evidence.war_deps, "WAR — write-after-read",
                  region=(evidence.start_line, evidence.end_line)),
        _fmt_deps(evidence.waw_deps, "WAW — write-after-write",
                  region=(evidence.start_line, evidence.end_line)),
    ]

    if evidence.reduction_vars:
        parts.append(
            f"### Reduction variables: {', '.join(evidence.reduction_vars)}\n"
        )

    classification = _fmt_classification(evidence)
    if classification:
        parts.append(classification)

    extra_vars = _fmt_extra_vars(evidence)
    if extra_vars:
        parts.append(extra_vars)

    array_note = _array_dep_note(evidence)
    if array_note:
        parts.append(array_note)

    loop_nest = _fmt_loop_nest(evidence)
    if loop_nest:
        parts.append(loop_nest)

    calls = _fmt_calls(evidence)
    if calls:
        parts.append(calls)

    blockers = _fmt_blockers(evidence.prevented_deps)
    if blockers:
        parts.append(blockers)

    if evidence.tier1_failure_reason:
        parts.append(
            f"### What went wrong\n{evidence.tier1_failure_reason}\n"
        )

    parts.append(
        f"### Task\n"
        f"Restructure the {region_label} at lines "
        f"{evidence.region_id} in {evidence.source_file} "
        f"so that after re-profiling DiscoPoP detects a genuinely parallel "
        f"pattern (Do-All, Reduction, Pipeline, or Task-Parallel) that compiles "
        f"cleanly, is race-free under ThreadSanitizer, and achieves measurable "
        f"speedup.\n"
        f"\n"
        f"Work through this checklist before writing the diff:\n"
        f"  1. Classify each variable under 'RAW' above into causes 1-6 "
        f"(induction variables and loop-local temps are cause 1; an "
        f"array-element RAW is cause 3 or 4 — decide with the same-sweep "
        f"read-back question).\n"
        f"  2. Apply the matching fix COMPLETELY — including loop bounds "
        f"re-derived for the new schedule, in canonical form.\n"
        f"  3. Parallelize at a level with enough iterations x work to beat "
        f"thread overhead (see the loop structure above).\n"
        f"\n"
        f"IMPORTANT: diff context lines (lines beginning with a single space) must match "
        f"the actual file content exactly — use only the raw code indentation, "
        f"not the `NNNN >>>` display prefix shown in the Source section above.\n"
        f"\n"
        f">>> OUTPUT A UNIFIED DIFF ONLY. <<<\n"
        f"No prose, no explanation, no markdown, no code fences. Your entire "
        f"response must be the diff itself, beginning with '--- ' and containing "
        f"'+++ ' and '@@ ' markers. Any text that is not part of the diff will "
        f"cause the response to be rejected."
    )
    return "\n".join(parts)


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
            "— algorithmic; cannot be removed by privatizing/renaming."
        )
    if scalar_raw:
        out.append(
            f"  - RAW on SCALARS: {', '.join(scalar_raw)} — usually storage reuse "
            "or a reduction; check each against the loop's induction variables."
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
        out.append(
            f"  {'  ' * lp['depth']}- loop at lines {lp['start']}–{lp['end']}  "
            f"induction variable(s): {idx}  |  {lp['entries']} activation(s) "
            f"× ~{lp['avg']} iterations = {lp['total']:,} total (max {lp['max']})"
        )
    out.append(
        "  Induction variables are managed by OpenMP automatically — dependences "
        "on them are NEVER the real blocker; do not restructure to 'fix' them.\n"
        "  A loop with few iterations per activation but many activations is "
        "fine-grained: prefer parallelizing an outer loop or coarsening the work "
        "per iteration."
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
        out.append(
            f"  loop at line {lc['line']}: {lc['entries']} activation(s) "
            f"× ~{lc['avg']} iterations each = {lc['total']:,} total "
            f"(max {lc['max']}/activation)"
        )
    out.append(
        "  A loop with FEW iterations per activation but MANY activations is "
        "fine-grained: parallelizing it directly rarely beats thread overhead — "
        "prefer coarser parallelism (parallelize an outer level, or make each "
        "parallel iteration do more work)."
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
    """If the blocking RAW deps are on array elements, state plainly that copying
    or renaming the array cannot remove them.  Returns '' when the blocking deps
    are all scalar (where privatization is the right move)."""
    array_vars = sorted({d.variable for d in ev.raw_deps if getattr(d, "kind", "scalar") == "array"})
    if not array_vars:
        return ""
    return (
        "### Nature of the blocking dependence (read this before choosing a fix)\n"
        f"The loop-carried RAW dependence is on ARRAY ELEMENTS ({', '.join(array_vars)}), "
        "not on a scalar — this is cause 3 (in-place coupling) or cause 4 "
        "(recurrence); copying or renaming the array removes nothing.  Answer "
        "the same-sweep read-back question first: can a value WRITTEN during "
        "one sweep be READ again later in the SAME sweep (e.g. a swapped "
        "element the next iteration compares)?  If YES -> partition into "
        "coloured sub-passes (cause 3b, bounds re-derived for the new "
        "schedule); only if NO -> double-buffer (3a).\n"
    )


def _fmt_blockers(prevented: list) -> str:
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
        "### Runtime data dependences in the target region (observed)\n"
        "(grouped per variable; each is tagged [array element] or [scalar]: an "
        "array-element dep is on the DATA and is usually algorithmic; a scalar "
        "dep is usually a storage conflict removable by privatization/renaming)",
        _fmt_deps(evidence.raw_deps, "RAW — read-after-write (the blocking ones)",
                  evidence.line_text, (evidence.start_line, evidence.end_line)),
        _fmt_deps(evidence.war_deps, "WAR — write-after-read",
                  region=(evidence.start_line, evidence.end_line)),
        _fmt_deps(evidence.waw_deps, "WAW — write-after-write",
                  region=(evidence.start_line, evidence.end_line)),
    ]
    if evidence.reduction_vars:
        parts.append(f"### Reduction variables: {', '.join(evidence.reduction_vars)}\n")
    classification = _fmt_classification(evidence)
    if classification:
        parts.append(classification)
    extra_vars = _fmt_extra_vars(evidence)
    if extra_vars:
        parts.append(extra_vars)
    array_note = _array_dep_note(evidence)
    if array_note:
        parts.append(array_note)
    loop_nest = _fmt_loop_nest(evidence)
    if loop_nest:
        parts.append(loop_nest)
    calls = _fmt_calls(evidence)
    if calls:
        parts.append(calls)
    blockers = _fmt_blockers(evidence.prevented_deps)
    if blockers:
        parts.append(blockers)
    if evidence.tier1_failure_reason:
        parts.append(f"### What went wrong\n{evidence.tier1_failure_reason}\n")

    parts.append(
        "### Task\n"
        f"Restructure the {region_label} (lines {evidence.start_line}–"
        f"{evidence.end_line}) inside `{fname}` so that after re-profiling "
        "DiscoPoP detects a genuinely parallel pattern (Do-All, Reduction, "
        "Pipeline, or Task-Parallel) that compiles cleanly, is race-free under "
        "ThreadSanitizer, and achieves measurable speedup.\n"
        "\n"
        "Work through this checklist:\n"
        "  1. Classify each variable under 'RAW' above into causes 1-6 "
        "(induction variables and loop-local temps are cause 1; an "
        "array-element RAW is cause 3 or 4 — decide with the same-sweep "
        "read-back question).\n"
        "  2. Apply the matching fix COMPLETELY — including loop bounds "
        "re-derived for the new schedule, in canonical form.\n"
        "  3. Parallelize at a level with enough iterations x work to beat "
        "thread overhead (see the loop structure above).\n"
        "\n"
        ">>> OUTPUT exactly as specified in the system instructions: the PLAN "
        "(same-sweep line, causes + fixes, loop headers), then the ENTIRE "
        "rewritten function as ONE ```cpp code block, and end the response "
        "there. Keep the same function name and signature."
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Diff validation
# ---------------------------------------------------------------------------

def _extract_diff(text: str) -> Optional[str]:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("--- ") or line.startswith("diff --git"):
            start = i
            break
    return "\n".join(lines[start:]) if start is not None else None


def _is_valid_diff(diff: str) -> bool:
    return "---" in diff and "+++" in diff and "@@" in diff


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
    (e.g. a self-hosted vLLM server) via api_base."""
    if provider == "openai-compat":
        try:
            import openai
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "provider 'openai-compat' requires the openai package "
                "(`venv/bin/pip install openai`)."
            ) from e
        return openai.OpenAI(api_key=api_key or "EMPTY", base_url=api_base)
    return anthropic.Anthropic(api_key=api_key)


class LLMConnectionError(RuntimeError):
    """The LLM endpoint could not be reached (server not running, wrong
    --api-base, or network failure).  Fatal for the whole run — every region
    would hit the same error — so the controller aborts cleanly on it."""


def _complete(provider: str, client: Any, model: str, current: list, system: str) -> str:
    """Run one completion against the chosen provider and return the raw text.

    Both providers receive the same `system` instructions and the same
    user/assistant conversation; only the wire format differs (Anthropic takes
    `system` separately, OpenAI takes it as the first message)."""
    try:
        if provider == "openai-compat":
            resp = client.chat.completions.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "system", "content": system}] + current,
            )
            return resp.choices[0].message.content or ""
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
    avoids the LLM having to produce a byte-exact diff.

    On the first call for a region pass messages=None — the initial prompt is
    built from evidence.  Pass the list returned by the previous call on
    subsequent budget retries so the model sees the full conversation history.

    `provider` selects the backend: "anthropic" (default) or "openai-compat"
    (any OpenAI-compatible endpoint at `api_base`, e.g. a self-hosted vLLM).
    """
    function_mode = edit_mode == "function"
    system = _SYSTEM_FUNCTION if function_mode else _SYSTEM
    client = _make_client(provider, api_key, api_base)

    if messages is None:
        # First attempt for this region — build initial prompt from evidence.
        user_prompt = _build_function_prompt(evidence) if function_mode else _build_prompt(evidence)
        messages = [{"role": "user", "content": user_prompt}]

    current = list(messages)
    kind = "function" if function_mode else "diff"

    for attempt in range(max_format_retries + 1):
        if verbose:
            last_user = next(
                (m["content"] for m in reversed(current) if m["role"] == "user"), ""
            )
            viz.llm_request(model, provider, system, last_user, attempt=attempt)

        text = _complete(provider, client, model, current, system)

        if verbose:
            viz.llm_response(text, kind=kind)

        out = _extract_code(text) if function_mode else _extract_diff(text)
        valid = out is not None if function_mode else bool(out and _is_valid_diff(out))

        if verbose:
            viz.llm_extracted(kind, out if valid else None)

        if valid:
            # Return messages with assistant turn appended so the controller
            # can extend the conversation with quality-gate feedback and retry.
            return out, current + [{"role": "assistant", "content": text}]

        # Free format re-prompt — doesn't consume a budget slot.
        if attempt < max_format_retries:
            reprompt = (
                "Your response must end with the complete rewritten function as a "
                "single ```cpp code block — signature and full body, no diff. "
                "A short plain-text PLAN before the code block is allowed; "
                "nothing may follow the code block."
                if function_mode else
                "Your response must be a unified diff only.\n"
                "Start with '--- <original_file>' on its own line,\n"
                "then '+++ <modified_file>', then one or more '@@ … @@' hunks.\n"
                "No prose, no code fences."
            )
            current = current + [
                {"role": "assistant", "content": text},
                {"role": "user", "content": reprompt},
            ]

    return None, current
