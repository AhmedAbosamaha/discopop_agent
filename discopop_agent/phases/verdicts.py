"""
Did a rewrite achieve what it exists to achieve?
--------------------------------------------------
Passing the gate proves a rewrite is HARMLESS — it compiles and reproduces the
output.  That is necessary and nowhere near sufficient: a rename, a reordering,
or an early-exit shortcut all pass it while parallelizing nothing.

So after a rewrite is applied and re-profiled, this asks the question the whole
exercise is about: can DiscoPoP now parallelize the lines that changed?  Under
--llm-pragmas the answer is already in the diff and the gate has judged it, but
otherwise DiscoPoP's verdict is what decides, and `_rewrite_feedback` turns a
refusal into something the model can act on — including re-reading
doall_prevented.json from the FRESH profile so it sees the blockers for its own
rewrite rather than for the original.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from ..args import AgentArguments
from ..evidence import load_prevented_deps
from ..gate import _validate_cached, check_pragma_compiles
from ..llm import fmt_blockers
from ..plan import region_fingerprint
from ..pragmas import check_pragma_clauses, derive_pragma_patch, _read_tier1_patch


@dataclass
class RewriteOutcome:
    """Did the restructuring achieve what it exists to achieve?

    status:
      "ok"             — DiscoPoP found a pattern in the rewritten code and its
                         pragma passed the gate (and was fast enough, if required)
      "exposed"        — a pattern was found; validating it is deferred to the
                         next depth, which is allowed to restructure it further
      "self_annotated" — --llm-pragmas: the rewrite carries its own pragmas and
                         has already passed the full gate, so DiscoPoP's opinion
                         of it is not what decides
      "no_pattern"     — DiscoPoP re-profiled the rewrite and still found nothing
      "pattern_broken" — a pattern was found but its pragma fails the gate
      "no_speedup"     — the pragma is correct but not faster
    """
    status: str
    speedup: "float | None" = None
    pattern_label: str = ""
    diagnostic: str = ""
    # Content fingerprints of the regions this rewrite exposed.  A rewrite is
    # justified at the end only if Phase B applied a pragma to one of them —
    # matched on identity, not on line numbers, which drift as later changes
    # land above them.
    exposed_prints: List[str] = field(default_factory=list)
def _verify_rewrite(
    fresh: list,
    touched: "tuple[int, int] | None",
    dp_dir: Path,
    args: AgentArguments,
    reference_output: "str | None",
    binary_args: "list | None",
    reference_time: "float | None",
    validate_patterns: bool,
    gate_cache: dict,
    reference_outputs: "list | None" = None,
) -> RewriteOutcome:
    """Decide whether an accepted-by-the-gate rewrite actually did its job.

    A rewrite exists for exactly one reason: to let DiscoPoP parallelize code it
    previously could not.  Compiling and preserving output is necessary but says
    nothing about that — so after re-profiling we check what DiscoPoP now
    reports for the rewritten lines, and (when this is the last chance to act on
    it) run its generated pragma through the full gate.

    Patterns are tried largest-workload-first and the FIRST qualifying one wins:
    the decision is "did anything pay off", so validating the rest only burns
    time on a question already answered.
    """
    exposed = [
        c for c in fresh
        if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")
        and (touched is None
             or not (c.region.end_line < touched[0] or c.region.start_line > touched[1]))
    ]
    if not exposed:
        return RewriteOutcome("no_pattern")

    exposed.sort(key=lambda c: c.workload_estimate, reverse=True)
    label = ", ".join(
        f"{c.pattern_type or 'pattern'} @ lines {c.region.start_line}–{c.region.end_line}"
        for c in exposed[:3]
    )
    prints = [
        region_fingerprint(args.source_file, c.region.start_line,
                           c.region.end_line, c.region.name)
        for c in exposed
    ]
    if not validate_patterns:
        # "A pattern appeared" is a weaker claim than "a pragma works", and
        # DiscoPoP makes the first one for loops clang rejects outright — a
        # runtime bound, a surviving `break`.  Keeping such a rewrite spends an
        # LLM call and a re-profile on something that can never pay off, so
        # check the cheap half now: the clauses, and one -fopenmp build.
        for c in exposed:
            cpid = c.pattern.get("pattern_id", "?") if c.pattern else "?"
            patch = derive_pragma_patch(
                _read_tier1_patch(dp_dir / "patch_generator" / str(cpid)),
                args.source_file,
            )
            if not patch or check_pragma_clauses(patch, args.source_file):
                continue
            ok_c, _diag = check_pragma_compiles(patch, args.source_file)
            if ok_c:
                return RewriteOutcome("exposed", pattern_label=label,
                                      exposed_prints=prints)
        return RewriteOutcome(
            "no_usable_pragma", pattern_label=label, exposed_prints=prints,
            diagnostic="DiscoPoP reports a pattern for the rewritten lines, but "
                       "every pragma it generates for them is rejected before it "
                       "can run — the clauses are wrong, or the loop is not in a "
                       "form OpenMP accepts.",
        )

    worst = RewriteOutcome("pattern_broken", pattern_label=label)
    for cand in exposed:
        pid = cand.pattern.get("pattern_id", "?") if cand.pattern else "?"
        patch = _read_tier1_patch(dp_dir / "patch_generator" / str(pid))
        if not patch:
            continue
        res, _cached, _fp = _validate_cached(
            gate_cache, patch, args, reference_output, binary_args, reference_time,
            reference_outputs=reference_outputs,
        )
        if res.passed:
            return RewriteOutcome("ok", res.measured_speedup, label)
        # "no speedup" is closer to success than "still racing": prefer to
        # report it, so the retry prompt talks about granularity, not correctness.
        if res.stage == "performance":
            worst = RewriteOutcome("no_speedup", res.measured_speedup, label, res.diagnostic)
        elif worst.status != "no_speedup":
            worst = RewriteOutcome("pattern_broken", None, label, res.diagnostic)
    return worst
_OUTCOME_LABEL = {
    "no_pattern": "DiscoPoP still finds no parallelism in the rewritten lines",
    "pattern_broken": "DiscoPoP found a pattern, but its pragma fails validation",
    "no_speedup": "DiscoPoP parallelized it, but it is not faster",
    "reprofile_failed": "the rewrite broke DiscoPoP's profiling run",
    "no_usable_pragma": "DiscoPoP sees a pattern, but no pragma it generates for it can run",
}
# Fallback only.  The real threshold is measured per run by noise_floor() — an
# unchanged program does not measure 1.000, and how far off it lands depends on
# the host and the program, not on a number chosen here.  This value is used
# only when that calibration cannot run.
_MARGINAL_NOISE = 0.97
def _rewrite_feedback(
    outcome: RewriteOutcome, dp_dir: Path, file_id: int,
    touched: "tuple[int, int] | None",
) -> str:
    """Turn a failed post-restructuring verdict into the message the LLM sees.

    This is the only place DiscoPoP's own opinion of the model's rewrite reaches
    the model.  Each verdict gets a different instruction, because they mean
    opposite things: "no pattern" means the dependence is still there, while
    "no speedup" means it is gone and only granularity is wrong — telling the
    model to keep hunting for dependences in that case sends it backwards.
    """
    if outcome.status == "no_pattern":
        msg = (
            "DiscoPoP re-profiled your rewrite. Your code compiles and its output is "
            "correct, but DiscoPoP STILL finds no parallel pattern in the lines you "
            "changed — so the rewrite achieved nothing and has been reverted.\n\n"
            "The blocking dependence is therefore still present. Do not re-submit a "
            "variation of the same structure — the blockers below are DiscoPoP's "
            "analysis OF YOUR REWRITE, not of the original code, so read them as a "
            "description of what you just wrote."
        )
        blockers = fmt_blockers(
            load_prevented_deps(dp_dir, file_id, *(touched or (1, 10**9)))[:12]
        )
        if blockers:
            msg += (
                "\n\nWhat DiscoPoP reports about YOUR REWRITTEN CODE:\n" + blockers
            )
        else:
            msg += (
                "\n\nDiscoPoP reported no specific Do-All blocker for those lines, "
                "which usually means the loop is not in a form it analyses at all: "
                "check that the loop you intended to be parallel has a computable "
                "trip count, a simple `i < bound` condition, and no break/continue/"
                "return in its body."
            )
        return msg

    if outcome.status == "pattern_broken":
        return (
            f"Progress: after your rewrite DiscoPoP DID detect parallelism "
            f"({outcome.pattern_label}).\n\n"
            f"Your rewrite is correct on its own — it already passed the sequential "
            f"output check. What failed is running it in parallel: DiscoPoP added "
            f"its `#pragma omp` to your code and that build broke. The rewrite has "
            f"been reverted.\n\n"
            f"So the thing to find is not a bug in your logic but an ordering "
            f"assumption — something in the body that only holds when iterations run "
            f"one after another. Keep the structure that made the loop detectable.\n\n"
            f"Reading the diagnostic: it comes from validating YOUR CODE PLUS THAT "
            f"PRAGMA, so a complaint that the program is not semantically equivalent "
            f"is not about your rewrite alone. And if the outputs differ only in the "
            f"last digits of floating-point values, a parallel reduction reassociated "
            f"the arithmetic — that is not a dependence.\n\n"
            f"Diagnostic:\n{outcome.diagnostic[:1200]}"
        )

    if outcome.status == "no_usable_pragma":
        return (
            f"Close: after your rewrite DiscoPoP DOES report parallelism "
            f"({outcome.pattern_label}). But every pragma it generates for those "
            f"lines is rejected before it can run, so the rewrite cannot lead to "
            f"a parallel build and has been reverted.\n\n"
            f"That is almost always the loop's SHAPE. OpenMP needs the trip count "
            f"known before the loop starts: the condition has to compare the loop "
            f"variable directly against a bound that does not change inside the "
            f"loop, and the body must contain no break, continue, return or goto. "
            f"A bound computed at run time — `for (i = start; ...)` where `start` "
            f"is set inside an enclosing loop — reads as parallel to the profiler "
            f"and is rejected by the compiler.\n\n"
            f"Rewrite the loop so its bounds are plain expressions of the loop "
            f"variable and loop-invariant values.\n\n"
            f"{outcome.diagnostic}"
        )

    if outcome.status == "no_speedup":
        got = f"{outcome.speedup:.2f}x" if outcome.speedup else "no measurable gain"
        return (
            f"Your rewrite worked in every respect except the one that matters: "
            f"DiscoPoP parallelized it ({outcome.pattern_label}) and the parallel "
            f"build is CORRECT, but it is not faster ({got}). It has been reverted.\n\n"
            f"The dependence is already gone, so do not go looking for one again. "
            f"The parallel work is too fine-grained to cover thread startup: each "
            f"iteration needs to do more, or the parallelism needs to move to a "
            f"level that has more work per activation.\n\n"
            f"Diagnostic:\n{outcome.diagnostic[:800]}"
        )

    return (
        "Your rewrite compiled and produced correct output, but DiscoPoP could not "
        "instrument or profile it, so it cannot be parallelized at all. It has been "
        "reverted. Avoid constructs that change the program's structure in ways the "
        "profiler cannot follow (unusual templates, macros, computed control flow); "
        "prefer a plain loop rewrite.\n\n"
        f"{outcome.diagnostic}"
    )
