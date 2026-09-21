"""
The system prompts, assembled from blocks
-------------------------------------------
Two modes share most of their text and differ in exactly three places: who
writes the pragma, what "success" means, and how the answer is judged.  Writing
them out twice guarantees they drift, so they are composed from named blocks
instead.

The "how it is judged" block is GENERATED from the gate that is configured for
the run (`GateFacts`), not written as a constant: a prompt that promises a
timing step which is switched off, or a byte-for-byte comparison where a measured
tolerance applies, steers the model away from exactly the rewrites the gate would
accept (review P3).

The prompt is sent with `cache_control: ephemeral`, so it must be byte-identical
across every call in a session for the cache to hit.  It still is: the gate facts
are fixed for a run, so the same text is built on every call.
"""
from __future__ import annotations

import textwrap
from typing import Optional, Set

from ..types import GateFacts


# ---------------------------------------------------------------------------
# System prompt (cached across all calls in a session)
# ---------------------------------------------------------------------------

# The system prompt is assembled from blocks rather than written out twice.
# The two modes differ in exactly three places — who writes the pragma, what
# "success" means, and how the answer is judged — and share everything else.

_RULE = "------------------------------------------------------------------\n"

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

    You have succeeded when the annotated code compiles, runs race-free and
    reproduces the original program's results{SPEED_GOAL}.  Nothing downstream adds
    a pragma to the code you rewrite — a loop you leave unannotated stays
    sequential, and a rewrite with no pragma in it has parallelized nothing.

""")
_GIVEN_ITEMS = (
    ("deps", "the dependences observed at run time (RAW / WAR / WAW, grouped per "
             "variable, tagged array or scalar, quoted against the statements they "
             "point at)"),
    ("accesses", "the index expressions each array is written and read with"),
    ("blockers", "DiscoPoP's own Do-All blockers with their origin (static = a "
                 "dependence it could not rule out, dynamic = one it actually observed)"),
    ("loop_nest", "the loop nest with induction variables and iterations per activation"),
    ("inner_patterns", "the loops inside the region DiscoPoP already reports as parallel"),
    ("calls", "any calls in the region"),
)


def _wrap(text: str, indent: str = "") -> str:
    return textwrap.fill(text, width=74, initial_indent=indent, subsequent_indent=indent,
                         break_long_words=False, break_on_hyphens=False)


def _given(include: Optional[Set[str]]) -> str:
    """The "what we give you" block, listing only what the request really carries.

    It used to be a constant describing the full package.  Under `--evidence none`
    the model was therefore told it had been given observed dependences, Do-All
    blockers and a loop nest, and then shown none of them."""
    items = [text for name, text in _GIVEN_ITEMS if include is None or name in include]
    head = _RULE + "WHAT WE GIVE YOU\n" + _RULE
    after = "after a failed attempt, which check failed and why"
    if not items:
        return (head + _wrap(
            "Every request carries the region's source and, " + after + ".  No profiling "
            "data is provided for this region: work from the code itself.") + "\n\n")
    body = _wrap("Every request carries the region's source and, from the profile: "
                 + ", ".join(items) + " — and, " + after + ".")
    advice = "Work from that evidence rather than from what the algorithm is called."
    if include is None or "deps" in include:
        advice = _wrap(
            "Work from that evidence rather than from what the algorithm is called.  Two "
            "things in it are easy to misread on inspection: WAR and WAW usually mean a "
            "location is reused, not that a value travels between iterations; and a "
            "dependence on a loop's own counter is never the blocker, because "
            "privatising the counter removes it.")
    return head + body + "\n\n" + advice + "\n\n"


_CONTRACT_OPEN = textwrap.dedent("""\
    ------------------------------------------------------------------
    THE CONTRACT
    ------------------------------------------------------------------
      - The program's output must stay byte-identical.  Everything else is
        yours: execution order, loop bounds, extra buffers, extra passes.
      - Extra work is fine within a constant factor — a second buffer, one
        more pass.  Work that GROWS with the input is not: recomputing from
        scratch what the original carried forward turns an O(n) loop into
        O(n^2), which passes every check here and loses at full size.
      - A buffer whose size grows with the problem must be HEAP-allocated —
        malloc/free, or whatever allocator this program already uses — never
        a local array.  The stack is 8 MB and this program is verified at
        sizes far larger than the one you are shown: a local `T buf[N][N]`
        is 131 KB at N=128 and 8 MB at N=1024, where it dies before it
        computes anything.  A one-dimensional `T buf[N]` is fine.
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
def _step(text: str) -> str:
    """One numbered step's text, wrapped with the hanging indent the list uses."""
    return _wrap(text, "     ").lstrip()


def _how_compared(gate: GateFacts) -> str:
    """How outputs are compared, in the words the gate would use."""
    how = ("floating-point values may differ only by the rounding that reordering "
           "additions legitimately causes; labels, counts and integers must match exactly"
           if gate.numeric else "byte for byte")
    if gate.n_inputs > 1:
        return _step(f"its output is compared with the original program's on {gate.n_inputs} "
                     f"different inputs, not only the one that was profiled — {how}.  A "
                     "rewrite that is right for one input and wrong for another fails here")
    return _step(f"its output is compared with the original program's — {how}")


def _granularity(gate: GateFacts, step: int, verb: str) -> str:
    """The closing paragraph on which loop to make parallel.

    With the speed check off, the old text was actively harmful: the agent profiles
    at a deliberately small size, where EVERY loop of a PolyBench kernel has ~32
    iterations per activation, so "prefer the outermost one that qualifies" named
    no loop at all (review P4)."""
    if gate.require_speedup:
        return (f"Step {step} also decides granularity: each ACTIVATION of a loop is a separate\n"
                "parallel region, so it is the iterations per activation, not the total\n"
                "across activations, that has to cover thread startup.  The evidence marks\n"
                f"which loops qualify; {verb} the outermost one that does, and leave the\n"
                "loops nested inside it alone — one pragma per nest.\n\n")
    return ("Speed is NOT judged here.  The program was profiled on a deliberately\n"
            "small input, so the iteration counts in the evidence are far below what\n"
            "the code runs in practice, and its speed is measured afterwards at full\n"
            "size — which is where your rewrite finally has to win, so keep its work\n"
            "within a constant factor of the original's.  Do not leave a loop\n"
            "sequential because its count looks small:\n"
            f"{verb} the OUTERMOST loop that can be made independent — it has the\n"
            "most work per activation at any size — and leave the loops nested\n"
            "inside it alone, one pragma per nest.\n\n")


def _checked(gate: GateFacts) -> str:
    """"How it is checked" when DiscoPoP writes the pragmas (--no-llm-pragmas)."""
    judged = ["races (ThreadSanitizer)"]
    if gate.stress:
        judged.append("agreement across thread counts and static, dynamic and\n"
                      "     guided schedules")
    judged.append("output")
    if gate.require_speedup:
        judged.append("speed against the same build on one thread")
    steps = [
        "it must compile",
        "it is run sequentially, and " + _how_compared(gate),
        "it is re-profiled, and a pattern must appear IN THE LINES YOU CHANGED,\n"
        "     or the rewrite is reverted — passing 1 and 2 only shows it did no harm",
        "DiscoPoP's pragma is applied, and that build is checked for "
        + ", ".join(judged[:-1]) + " and " + judged[-1],
    ]
    body = "\n".join(f"  {i}. {t}" for i, t in enumerate(steps, 1))
    return (_RULE + "HOW YOUR REWRITE IS CHECKED\n" + _RULE + f"{body}\n\n"
            "Steps 1-2 run your code sequentially, so passing them says nothing about\n"
            "step 4, which runs it with iterations overlapping in arbitrary order.  A\n"
            "loop you intend to be parallel has to give the same result whatever order\n"
            "its iterations run in — that, not merely reproducing the output in serial,\n"
            "is what is being asked for.\n\n"
            + _granularity(gate, 4, "expose"))


def _checked_annotate(gate: GateFacts) -> str:
    """"How it is checked" when the model writes the pragmas (the default).

    It used to be a constant, and it described a gate that was not the one in use:
    a timing step that is switched off in the whole campaign, "byte-for-byte" where
    a measured numeric tolerance applies, and no mention of the two checks that
    catch most wrong rewrites — the schedule matrix and the second input.  A model
    told its loop must beat one thread at a deliberately tiny profiling size has a
    reason not to parallelise at all (review P3).
    """
    steps = [
        "the clauses on every pragma you wrote are read statically and held to\n"
        "     the two rules above — a clause that breaks one is rejected before\n"
        "     anything is built",
        "it must compile, plain and again with -fopenmp",
        "ThreadSanitizer runs the parallel build: any real race fails it",
    ]
    if gate.stress:
        steps.append(
            "the parallel build is run repeatedly at one thread count, then at\n"
            "     other thread counts and under static, dynamic and guided schedules:\n"
            "     every run has to agree with the others")
    steps.append(_how_compared(gate))
    if gate.require_speedup:
        steps.append("that same build is timed against itself pinned to one thread, and\n"
                     "     has to be faster")
    body = "\n".join(f"  {i}. {t}" for i, t in enumerate(steps, 1))
    return (_RULE + "HOW YOUR REWRITE IS CHECKED\n" + _RULE + f"{body}\n\n"
            f"Steps 3-{len(steps)} run your loops with iterations overlapping in arbitrary order.  A\n"
            "loop you marked parallel has to give the same result whatever order its\n"
            "iterations run in — reproducing the output in serial proves nothing about\n"
            "that.  Nothing here re-profiles your code: this list is the whole judgement,\n"
            "and a pragma you did not write is a loop that was never parallelized.\n\n"
            + _granularity(gate, len(steps), "annotate"))


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
def _contract_open(gate: GateFacts) -> str:
    """The contract's first line promised byte-identical output; under a measured
    numeric tolerance that is not what is enforced, and a model that believes it will
    refuse the reduction that reorders a sum."""
    if not gate.numeric:
        return _CONTRACT_OPEN
    # Only the FIRST bullet changes; everything after it stays as written.
    start = _CONTRACT_OPEN.index("  - The program's output")
    end = _CONTRACT_OPEN.index("\n  - ", start + 1) + 1
    bullet = _wrap(
        "The program's results must stay the same: every label, count and integer "
        "exactly, floating-point values up to the rounding a reordered sum causes.  "
        "Everything else is yours: execution order, loop bounds, extra buffers, extra "
        "passes.", "    ")
    return _CONTRACT_OPEN[:start] + "  - " + bullet.lstrip() + "\n" + _CONTRACT_OPEN[end:]


def _system_core(gate: GateFacts, include: Optional[Set[str]]) -> str:
    ask = _ASK if gate.require_speedup else _ASK.replace(
        "race-free, output-preserving,\nand faster than the sequential build.",
        "race-free and output-preserving.")
    return (_ROLE + ask + _given(include) + _contract_open(gate) + _CONTRACT_NO_PRAGMA
            + _CONTRACT_CLOSE + _checked(gate) + _OMP_RULES)


def _system_core_annotate(gate: GateFacts, include: Optional[Set[str]]) -> str:
    goal = (", and is measurably faster than the same build held to one thread"
            if gate.require_speedup else "")
    return (_ROLE_ANNOTATE + _ASK_ANNOTATE.replace("{SPEED_GOAL}", goal) + _given(include)
            + _contract_open(gate) + _CONTRACT_PRAGMA + _CONTRACT_CLOSE
            + _checked_annotate(gate) + _OMP_RULES + _PRAGMA_FORMS)


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
def _system_prompt(edit_mode: str, llm_pragmas: bool, llm_recon: bool = False,
                   gate: GateFacts = GateFacts(),
                   evidence_sections: Optional[Set[str]] = None) -> str:
    """The system prompt for one (edit mode, who-writes-the-pragma) pair.

    `gate` describes the gate that will judge the rewrite and `evidence_sections`
    the evidence the requests will carry (None = all of it), so the prompt tells the
    model what is actually checked and what it is actually given.  Both are constant
    for a run, so the text stays byte-identical across every call in a session and
    the prompt cache still hits.
    """
    core = (_system_core_annotate(gate, evidence_sections) if llm_pragmas
            else _system_core(gate, evidence_sections))
    tail = (_OUTPUT_DIRECT if edit_mode == "direct"
            else _OUTPUT_FUNCTION if edit_mode == "function" else _OUTPUT_DIFF)
    return core + tail + (_RECON_ADDENDUM if llm_recon else "")


# ---------------------------------------------------------------------------
# Dependence review (--llm-deps)
# ---------------------------------------------------------------------------

_SYSTEM_DEPS = textwrap.dedent("""\
    You are reviewing DiscoPoP's STATIC dependence analysis of C/C++ code.

    Static analysis is over-approximate by construction: it reports a dependence
    whenever it cannot PROVE the absence of one.  For code that was just
    rewritten there is no profiling data to settle the question, so each
    reported dependence is either real or an artefact of what the analysis
    could not prove.

    Every dependence below is one DiscoPoP names as the reason it will not
    parallelize a loop, and every one comes from STATIC analysis — anything it
    actually observed running is not shown to you and is not up for discussion.
    You are given the variable, the loop it blocks, and the two source lines.
    Decide:

      REAL      the dependence genuinely occurs at run time — a value written in
                one iteration is read in another, so the loop cannot run its
                iterations in parallel
      SPURIOUS  it cannot occur — the accesses are to disjoint memory, or they
                never overlap between iterations, or the "dependence" is on a
                location each iteration writes before reading (which
                privatization handles)

    Two things are already handled and will not be asked about, so do not reason
    as if they were the issue: the loop's own induction variable, and variables
    declared inside the loop body.

    Judge only what the code shows.  If you cannot tell, answer REAL: a
    dependence wrongly called spurious produces a racy parallel loop, while one
    wrongly called real only costs a missed parallelization.

    Answer with one line per dependence and nothing else:

        <number>: REAL|SPURIOUS - <at most 15 words of reason>
""")


# ---------------------------------------------------------------------------
# Dependence reconstruction (harness arm: fast-llm)
# ---------------------------------------------------------------------------
# The fast refresh cannot carry a dependence whose endpoint sits in code the
# rewrite created — the previous run predates that code, so it was never
# observed.  Measured across two cases, 39 of 39 dependences the full profile
# has and a refresh lacks have an endpoint on a rewritten line, and NONE were
# carryable.  That is the whole remaining gap, and it is the one thing a model
# that just wrote the code is in a position to know.
#
# What is asked for is deliberately narrow and in SOURCE terms only: the model
# never sees or invents an instruction id or a memory region.  It names lines
# and variables; the agent resolves those against the fresh instruction mapping
# and the static analysis, so a claim that cannot be resolved is dropped rather
# than guessed at.
_SYSTEM_RECONSTRUCT = textwrap.dedent("""\
    You are reporting the DATA DEPENDENCES in C/C++ code that was just rewritten.

    A profiler would normally observe these by running the program.  That run has
    been skipped, so for the lines below there is no measurement — you are being
    asked what a run WOULD have observed, because you have the code in front of
    you.

    Report only dependences carried BETWEEN ITERATIONS of a loop, and only for
    the lines shown.  A dependence within one iteration does not constrain
    parallelism and must not be reported.

      RAW  an iteration reads a location an earlier iteration wrote
      WAR  an iteration writes a location an earlier iteration read
      WAW  two iterations write the same location

    Do NOT report the loop's own induction variable: it is handled separately and
    is never a blocker.

    Completeness matters more than precision here.  A dependence you omit makes a
    sequential loop look parallel, which is a race.  A dependence you add that is
    not real only costs a missed parallelization.  When you are unsure whether
    iterations touch the same location, REPORT IT.

    Answer with one line per dependence and nothing else:

        LOOP <loop-header-line> <RAW|WAR|WAW> <variable> <writer-line> <reader-line>

    and for a loop whose iterations are genuinely independent, exactly:

        LOOP <loop-header-line> NONE
""")


# Appended to the restructuring system prompt under --llm-recon.  Asking in the
# SAME call is the whole point: a separate request costs more than the
# instrumented run the fast refresh exists to skip, and the model has more
# context here than it will ever have again.  The format is the one
# dep_reconstruct.parse_claims already reads, so the claims ride out on the
# reply text in every edit mode — including `direct`, where the edited file is
# the answer and the reply would otherwise be discarded.
_RECON_ADDENDUM = textwrap.dedent("""\

    ALSO REPORT THE DEPENDENCES IN THE CODE YOU WRITE.

    The profiler will not be re-run on your rewrite, so nothing will be measured
    there.  Only you know what the new code does.  After your edit, list the
    dependences a run WOULD have observed, carried BETWEEN ITERATIONS of a loop:

        LOOP <loop-header-line> <RAW|WAR|WAW> <variable> <writer-line> <reader-line>

    and for a loop whose iterations are genuinely independent, exactly:

        LOOP <loop-header-line> NONE

    Use the line numbers of the code AFTER your edit.  Skip the loop's own
    induction variable.  Report anything you are unsure about: a dependence you
    omit makes a sequential loop look parallel, which is a race, while one you
    add that is not real costs only a missed parallelization.  These lines go
    after your edit, not instead of it.
""")
