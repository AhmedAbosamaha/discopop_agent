"""
The system prompts, assembled from blocks
-------------------------------------------
Two modes share most of their text and differ in exactly three places: who
writes the pragma, what "success" means, and how the answer is judged.  Writing
them out twice guarantees they drift, so they are composed from named blocks
instead.

The prompt is sent with `cache_control: ephemeral`, so it must be byte-identical
across every call in a session for the cache to hit — which is why these are
module-level constants rather than something built per call.
"""
from __future__ import annotations

import textwrap


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


def _system_prompt(edit_mode: str, llm_pragmas: bool,
                   llm_recon: bool = False) -> str:
    """The system prompt for one (edit mode, who-writes-the-pragma) pair.

    Kept as module-level constants rather than built per call: the prompt is
    sent with `cache_control: ephemeral`, so it has to be byte-identical across
    every call in a session for the cache to hit.
    """
    core = _SYSTEM_CORE_ANNOTATE if llm_pragmas else _SYSTEM_CORE
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
