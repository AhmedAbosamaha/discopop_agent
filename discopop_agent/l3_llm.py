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
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import anthropic

from . import viz
from .types import EvidencePackage

# ---------------------------------------------------------------------------
# System prompt (cached across all calls in a session)
# ---------------------------------------------------------------------------

# The system prompt is assembled from blocks rather than written out twice.
# The two modes differ in exactly three places — who writes the pragma, what
# "success" means, and how the answer is judged — and share everything else.

_ROLE = textwrap.dedent("""\
    You are the restructuring stage of DiscoPoP, a profiler that finds OpenMP
    parallelism in C/C++ programs.

""")

_ROLE_ANNOTATE = textwrap.dedent("""\
    You are the restructuring and annotation stage of DiscoPoP, a profiler that
    finds OpenMP parallelism in C/C++ programs.

""")

_ASK = textwrap.dedent("""\
    ------------------------------------------------------------------
    WHAT WE ASK OF YOU
    ------------------------------------------------------------------
    DiscoPoP profiled one region and could not extract safe parallelism from
    it.  Rewrite that region's sequential source so the parallelism becomes
    explicit.  You do NOT write pragmas — DiscoPoP re-profiles your rewrite and
    inserts them itself.

    You have succeeded when DiscoPoP finds one of the four patterns it can
    exploit — Do-All, Reduction, Pipeline, Task-parallel — in the lines you
    changed, and the pragma it then generates is race-free, output-preserving,
    and faster than the sequential build.

""")

_ASK_ANNOTATE = textwrap.dedent("""\
    ------------------------------------------------------------------
    WHAT WE ASK OF YOU
    ------------------------------------------------------------------
    DiscoPoP profiled one region and could not extract safe parallelism from
    it.  Rewrite that region's sequential source so the parallelism becomes
    explicit, and annotate it yourself: every loop you intend to run in
    parallel carries its own `#pragma omp`, with its data-sharing clauses
    spelled out.

    You have succeeded when the annotated code compiles, runs race-free,
    reproduces the original output byte for byte, and is measurably faster than
    the same build held to one thread.  Nothing downstream adds a pragma to the
    code you rewrite — a loop you leave unannotated stays sequential, and a
    rewrite with no pragma in it has parallelized nothing.

""")

_GIVEN = textwrap.dedent("""\
    ------------------------------------------------------------------
    WHAT WE GIVE YOU
    ------------------------------------------------------------------
    Every request carries the region's source and, from the profile: the
    dependences observed at run time (RAW / WAR / WAW, grouped per variable,
    tagged array or scalar, quoted against the statements they point at),
    DiscoPoP's own Do-All blockers with their origin (static = a dependence it
    could not rule out, dynamic = one it actually observed), the loop nest with
    induction variables and iterations per activation, any calls in the region,
    and — after a failed attempt — which check failed and what DiscoPoP found
    in YOUR rewrite.

    Work from that evidence rather than from what the algorithm is called.  Two
    things in it are easy to misread on inspection: WAR and WAW usually mean a
    location is reused, not that a value travels between iterations; and a
    dependence on an induction variable is never the blocker, because OpenMP
    handles those itself.

""")

_CONTRACT_OPEN = textwrap.dedent("""\
    ------------------------------------------------------------------
    THE CONTRACT
    ------------------------------------------------------------------
      - The program's output must stay byte-identical.  Everything else is
        yours: execution order, operation count, loop bounds, extra buffers,
        extra passes.  Doing more work than the original is fine.
      - Do not rename the function or change its signature, and do not touch
        I/O or its formatting.
""")

_CONTRACT_NO_PRAGMA = "  - Do not write `#pragma omp` yourself.\n"

_CONTRACT_PRAGMA = """\
  - Annotate what you parallelize: a rewrite with no `#pragma omp` in it is
    still a sequential program, however independent its iterations are.
  - Say what every variable does.  `reduction(op:var)` for an accumulator,
    `private` for per-iteration scratch declared OUTSIDE the loop,
    `firstprivate` for a value read in and not needed after.  Two rules
    decide the cases that go wrong silently:
      · a variable DECLARED inside the loop body is already per-iteration —
        it must not appear in any clause at all
      · a variable the loop WRITES and code after the loop READS must never
        be `private` or `firstprivate`.  Those discard the writes, so the
        later read sees a stale value and the program keeps running with a
        wrong answer.  Use `reduction`, or `lastprivate`, or leave it shared
        and make the write itself safe.
"""

_CONTRACT_CLOSE = """\
  - The original code returned unchanged — renamed, reordered, unrolled, or
    wrapped in an early-exit shortcut — is not an answer, and neither is a
    faster serial algorithm.  The blocking dependence has to be gone.

"""

_CHECKED = textwrap.dedent("""\
    ------------------------------------------------------------------
    HOW YOUR REWRITE IS CHECKED
    ------------------------------------------------------------------
      1. it must compile
      2. it is run, and its output compared byte-for-byte
      3. it is re-profiled, and a pattern must appear IN THE LINES YOU CHANGED,
         or the rewrite is reverted — passing 1 and 2 only shows it did no harm
      4. DiscoPoP's pragma is applied, and that build is checked for races,
         output, and speed

    Steps 1-2 run your code sequentially, so passing them says nothing about
    step 4, which runs it with iterations overlapping in arbitrary order.  A
    loop you intend to be parallel has to give the same result whatever order
    its iterations run in — that, not merely reproducing the output in serial,
    is what is being asked for.

    Step 4 also decides granularity: each ACTIVATION of a loop is a separate
    parallel region, so it is the iterations per activation, not the total
    across activations, that has to cover thread startup.  The evidence marks
    which loops qualify; prefer the outermost one that does.

""")

_CHECKED_ANNOTATE = textwrap.dedent("""\
    ------------------------------------------------------------------
    HOW YOUR REWRITE IS CHECKED
    ------------------------------------------------------------------
      1. the clauses on every pragma you wrote are read statically and held to
         the two rules above — a clause that breaks one is rejected before
         anything is built
      2. it must compile, plain and again with -fopenmp
      3. ThreadSanitizer runs the parallel build: any real race fails it
      4. the parallel build is run and its output compared byte-for-byte
      5. that same build is timed against itself pinned to one thread, and has
         to be faster

    Steps 3-5 run your loops with iterations overlapping in arbitrary order.  A
    loop you marked parallel has to give the same result whatever order its
    iterations run in — reproducing the output in serial proves nothing about
    that.  Nothing here re-profiles your code: this list is the whole judgement,
    and a pragma you did not write is a loop that was never parallelized.

    Step 5 also decides granularity: each ACTIVATION of a loop is a separate
    parallel region, so it is the iterations per activation, not the total
    across activations, that has to cover thread startup.  The evidence marks
    which loops qualify; annotate the outermost one that does, and leave the
    loops nested inside it alone — one pragma per nest.

""")

_OMP_RULES = textwrap.dedent("""\
    ------------------------------------------------------------------
    WHAT OPENMP REQUIRES OF A PARALLEL LOOP
    ------------------------------------------------------------------
      - the condition compares the loop variable directly against a
        loop-invariant bound: `i < n - 1`, not `i + 1 < n`
      - the increment is i++, i--, i += c, or i -= c
      - no break, continue, return, or goto in the body — and do not introduce
        one anywhere you touch
    A loop whose trip count is not known before it starts cannot be
    parallelized at all.  Turning an existing early exit into a flag tested
    after the loop is a valid way to fix that, but only when the iterations it
    now runs have no side effects and cannot fault.
""")

_PRAGMA_FORMS = textwrap.dedent("""\

    Stay with the worksharing forms: `#pragma omp parallel for`, plus
    `reduction(...)`, `schedule(...)` or `collapse(n)` where they earn their
    place.  No nested parallel regions, no `#pragma omp parallel` around a loop
    you then hand-partition by thread id, and nothing that needs a runtime call
    to be correct.
""")

_SYSTEM_CORE = (_ROLE + _ASK + _GIVEN + _CONTRACT_OPEN + _CONTRACT_NO_PRAGMA
                + _CONTRACT_CLOSE + _CHECKED + _OMP_RULES)

_SYSTEM_CORE_ANNOTATE = (_ROLE_ANNOTATE + _ASK_ANNOTATE + _GIVEN + _CONTRACT_OPEN
                         + _CONTRACT_PRAGMA + _CONTRACT_CLOSE + _CHECKED_ANNOTATE
                         + _OMP_RULES + _PRAGMA_FORMS)

# Asked for before the code in every edit mode.  Deliberately not a form: the
# point is to make the model commit to which dependence it is removing before
# it writes, not to fill in fields.
_PLAN_SPEC = """\
Before the code, a short plain-text plan: which dependence you are removing and
how, and any bound or initial value you had to re-derive because the new
schedule visits the data in a different order.  A few lines is enough."""


# Output-format instruction appended per edit mode.
_OUTPUT_DIFF = (
    "\n>>> OUTPUT: a short plan, then a unified diff. <<<\n"
    + _PLAN_SPEC
    + "\n"
    "Then the diff, and stop there — no markdown, no code fences, nothing after\n"
    "it.  The diff starts with a '--- ' line, then '+++ ', then one or more\n"
    "'@@ ' hunks.  No line of the plan may begin with those markers.\n"
)

_OUTPUT_FUNCTION = (
    "\n>>> OUTPUT: a short plan, then the complete rewritten function. <<<\n"
    + _PLAN_SPEC
    + "\n"
    "Then the whole function — signature and full body — as ONE ```cpp block,\n"
    "and end there.  No diff, no line numbers.  Keep the function's name and\n"
    "signature; the block is spliced in verbatim, so it must compile as-is.\n"
)

_OUTPUT_DIRECT = (
    "\n>>> OUTPUT: edit the file yourself. <<<\n"
    "You have Read / Edit / Write on a private working copy of the source; its\n"
    "path is in the request.  Read it, write the short plan in your reply, then\n"
    "apply the rewrite with Edit.  Only the file's final content is used —\n"
    "pasting code into the reply does nothing.\n"
    + _PLAN_SPEC
    + "\n"
    "Edit only the file named in the request, keep the change inside the target\n"
    "region and the function containing it, and leave the file compiling — you\n"
    "have no compiler here, so re-read anything you are unsure of.  If you\n"
    "edited this file on an earlier turn those edits are still there: build on\n"
    "them or replace them, but never restore the original code.\n"
)

_SYSTEM = _SYSTEM_CORE + _OUTPUT_DIFF
_SYSTEM_FUNCTION = _SYSTEM_CORE + _OUTPUT_FUNCTION
_SYSTEM_DIRECT = _SYSTEM_CORE + _OUTPUT_DIRECT


def _system_prompt(edit_mode: str, llm_pragmas: bool) -> str:
    """The system prompt for one (edit mode, who-writes-the-pragma) pair.

    Kept as module-level constants rather than built per call: the prompt is
    sent with `cache_control: ephemeral`, so it has to be byte-identical across
    every call in a session for the cache to hit.
    """
    core = _SYSTEM_CORE_ANNOTATE if llm_pragmas else _SYSTEM_CORE
    tail = (_OUTPUT_DIRECT if edit_mode == "direct"
            else _OUTPUT_FUNCTION if edit_mode == "function" else _OUTPUT_DIFF)
    return core + tail

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
        f"Worth settling before you write:\n"
        f"{_TASK_CHECKLIST}\n"
        f"IMPORTANT: diff context lines (lines beginning with a single space) must match "
        f"the actual file content exactly — use only the raw code indentation, "
        f"not the `NNNN >>>` display prefix shown in the Source section above.\n"
        f"\n"
        f">>> OUTPUT as specified in the system instructions: the short plan, "
        f"then the unified diff, and end the response there."
    )
    return "\n".join(parts)


# The three analysis steps every edit mode asks for, verbatim.
_TASK_CHECKLIST = (
    "  - Which dependence is actually blocking this, and is it a value moving\n"
    "    between iterations or just a location being reused?\n"
    "  - Does the loop you are making parallel have enough work per activation\n"
    "    to be worth it?  The loop structure above says which do.\n"
    "  - Re-derive any bound the old execution order made safe.\n"
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
        "Worth settling before you write:\n"
        f"{_TASK_CHECKLIST}"
        "\n"
        ">>> OUTPUT as specified in the system instructions: the short plan, "
        "then the ENTIRE rewritten function as ONE ```cpp code block, and end "
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
        "Worth settling before you write:\n"
        f"{_TASK_CHECKLIST}"
        "\n"
        ">>> Read the file, give the short plan, then APPLY the rewrite with the "
        "Edit tool. Do not print a diff or the rewritten code — the file's "
        "content is what is used. Keep the function's name and signature."
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
        # Two different hiccups land here, and neither is worth losing a run
        # over.  A cached session can go stale (its on-disk transcript evicted),
        # and the CLI itself can fail a call transiently — observed once as
        # `Claude Code returned an error result: success`, with the identical
        # call succeeding immediately afterwards.  Either way: drop any session
        # we were resuming and try once more from scratch.  A real problem
        # (not logged in, no CLI) fails the same way twice and still raises.
        _region_sessions.pop(session_key, None)
        time.sleep(2)
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
    llm_pragmas: bool = False,
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

    `llm_pragmas` switches the system prompt: off (default) the model is told
    DiscoPoP will insert the pragmas, on it is told to write them itself and
    that nothing downstream will add one for it.

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
    system = _system_prompt(edit_mode, llm_pragmas)
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
