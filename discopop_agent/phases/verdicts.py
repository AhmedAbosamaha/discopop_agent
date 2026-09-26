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

import difflib
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..args import AgentArguments
from ..evidence import load_prevented_deps
from ..gate import _validate_cached, check_pragma_compiles
from ..llm import fmt_blockers
from ..llm.diffs import make_diff
from ..plan import region_fingerprint
from ..pragmas import (_read_tier1_patch, _repair_pragma_clauses, check_pragma_clauses,
                       derive_pragma_patch)
from ..sources import _apply_in_memory

from ..gate.timing import SPEED_THRESHOLD_KEY as SPEED_THRESHOLD_KEY   # defined with the timing code


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
    fresh: List[Any],
    touched: "tuple[int, int] | None",
    dp_dir: Path,
    args: AgentArguments,
    reference_output: "str | None",
    binary_args: "List[str] | None",
    reference_time: "float | None",
    validate_patterns: bool,
    gate_cache: Dict[str, Any],
    reference_outputs: "List[Tuple[List[str], str]] | None" = None,
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
    exposed = exposed_in(fresh, touched, args.source_file)
    if not exposed:
        return RewriteOutcome("no_pattern")

    exposed.sort(key=lambda c: c.workload_estimate, reverse=True)
    label = ", ".join(
        f"{c.pattern_type or 'pattern'} @ lines {c.region.start_line}–{c.region.end_line}"
        for c in exposed[:3]
    )
    prints = [
        region_fingerprint(c.source_file, c.region.start_line,
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
            # With Phase B's clause repair: without it a generated clause that names a
            # loop-local variable fails the -fopenmp build here, and the rewrite was
            # reverted as `no_usable_pragma` although Phase B would have repaired and
            # applied the pragma (the chart audit of 26 Sep, finding 5).
            patch = pragma_patch(c, dp_dir, args.source_file)
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
            dep_region=(cand.region.file_id, cand.region.start_line,
                        cand.region.end_line),
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


def exposed_in(fresh: List[Any], touched: "tuple[int, int] | None", source_file: str) -> List[Any]:
    """The loops DiscoPoP now reports as parallel IN THE LINES THAT CHANGED — and in the
    file that changed."""
    return [
        c for c in fresh
        if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")
        and Path(c.source_file).resolve() == Path(source_file).resolve()
        and (touched is None
             or not (c.region.end_line < touched[0] or c.region.start_line > touched[1]))
    ]


def pragma_patch(c: Any, dp_dir: Path, source_file: str) -> "str | None":
    """DiscoPoP's pragma for candidate `c`, re-derived against `source_file` as it stands and
    with loop-local names repaired out of its clauses — exactly as Phase B derives it, so the
    gate cache serves one verdict to both."""
    pid = c.pattern.get("pattern_id", "?") if c.pattern else "?"
    return _repair_pragma_clauses(
        derive_pragma_patch(_read_tier1_patch(dp_dir / "patch_generator" / str(pid)), source_file),
        source_file)


def stage_pragmas(text: str, members: List[Any], dp_dir: Path, source_file: str) -> "str | None":
    """`text` with DiscoPoP's pragma for every member added — as TEXT.  The real file is never
    written: each pragma is re-derived by its loop header (as Phase B does) against a scratch
    copy holding what the previous ones left, since every inserted pragma moves the lines below
    it.  None when one of them cannot be staged."""
    with tempfile.TemporaryDirectory(prefix="dp_agent_d40_") as tmp:
        scratch = Path(tmp) / Path(source_file).name
        scratch.write_text(text)
        for c in members:
            diff = pragma_patch(c, dp_dir, str(scratch))
            staged = _apply_in_memory(diff, str(scratch)) if diff else None
            if staged is None:
                return None
            scratch.write_text(staged)
        return scratch.read_text()


_LOOP_RE = re.compile(r"^\s*(for|while)\s*\(")
_ALLOC_RE = re.compile(r"\b(malloc|calloc|realloc|aligned_alloc|posix_memalign)\s*\(|\bnew\s+\w")
_COPY_RE = re.compile(r"\b(memcpy|memmove|std::copy)\b")


def rewrite_additions(before: str, after: str) -> str:
    """What a rewrite added, in words the model can act on — loops, allocations, bulk copies,
    counted from the diff as added minus removed."""
    plus: List[str] = []
    minus: List[str] = []
    for ln in difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="", n=0):
        if ln.startswith("+") and not ln.startswith("+++"):
            plus.append(ln[1:])
        elif ln.startswith("-") and not ln.startswith("---"):
            minus.append(ln[1:])

    def net(rx: "re.Pattern[str]") -> int:
        return sum(1 for s in plus if rx.search(s)) - sum(1 for s in minus if rx.search(s))
    loops, allocs, copies = net(_LOOP_RE), net(_ALLOC_RE), net(_COPY_RE)
    parts = []
    if loops > 0:
        parts.append(f"{loops} more loop{'s' if loops > 1 else ''} than the code it replaced")
    if allocs > 0:
        parts.append(f"{allocs} allocation{'s' if allocs > 1 else ''}")
    if copies > 0:
        parts.append(f"{copies} bulk cop{'ies' if copies > 1 else 'y'} (memcpy/memmove)")
    return ", ".join(parts) if parts else "no extra loop, allocation or bulk copy that the diff shows"


def judge_as_shipped(
    exposed: List[Any], before: str, dp_dir: Path, source_file: str, *,
    threshold: float,
    validate: Callable[[str, Any], Tuple[bool, str]],
    measure: Callable[[str, str], Tuple[bool, float, str]],
) -> RewriteOutcome:
    """D40 — judge a kept rewrite the way it will ship, while the model can still act on it.

    Phase A used to ask only whether DiscoPoP now finds a pattern in the rewritten lines; the
    pragma's safety and the program's speed were Phase B's and Settle's questions, answered after
    the region's attempts were over — so a correct rewrite that ran slower than the original was
    dropped at the end and the model never heard why (E1c/E2: 21–29 trials per arm, Settle's
    ratio a median 0.53x).  Until 22 Aug (`3657447b`) this was asked here, pragma by pragma
    against a reference time taken at start-up; the two-phase rebuild moved every pragma
    insertion to Phase B, so that an inserted pragma stops shifting the lines Phase A reads, and
    the question went with it.

    Asked again, and still without writing a pragma into the file: DiscoPoP's pragma for each
    exposed loop, outermost first (a loop inside one judged safe gets none, as in Phase B),
    through the safety gate (`validate`; mode safety, cached — Phase B does not pay again); the
    safe ones staged together as TEXT and, as a set, through the gate again; then the rewrite with
    them timed against `before` with Settle's paired measurement and threshold (`measure`).  So
    a rewrite kept here is one Settle keeps, and one reverted here is one Settle would have
    dropped — reverted now, while the region's budget can pay for another attempt.

    `before` is the text before THIS rewrite (earlier kept rewrites in it, pragma-free like this
    one), so the ratio is this region's contribution alone.  A timing that fails without a crash
    leaves the verdict to Phase B and Settle, as before ("exposed")."""
    label = ", ".join(f"{c.pattern_type or 'pattern'} @ lines {c.region.start_line}–{c.region.end_line}"
                      for c in exposed[:3])
    prints = [region_fingerprint(c.source_file, c.region.start_line, c.region.end_line, c.region.name)
              for c in exposed]
    after = Path(source_file).read_text()
    members: List[Any] = []
    spans: List[Tuple[int, int]] = []
    first_fail = ""
    for c in sorted(exposed, key=lambda c: (c.region.start_line, c.region.start_line - c.region.end_line)):
        r = c.region
        if any(a <= r.start_line and r.end_line <= b for a, b in spans):
            continue                              # inside a loop already judged safe: one pragma per nest
        diff = pragma_patch(c, dp_dir, source_file)
        if not diff:
            continue
        problem = check_pragma_clauses(diff, source_file)
        ok, why = (False, f"clause: {problem}") if problem else validate(diff, c)
        if not ok:
            first_fail = first_fail or why
            continue
        members.append(c)
        spans.append((r.start_line, r.end_line))
    if not members:
        return RewriteOutcome("pattern_broken", pattern_label=label, exposed_prints=prints,
                              diagnostic=first_fail or "no pragma DiscoPoP generates for these lines passes")
    staged = stage_pragmas(after, members, dp_dir, source_file)
    if staged is not None and len(members) > 1:
        ok, _why = validate(make_diff(after, staged, source_file), None)
        if not ok:
            # Together they fail where each alone passed: judge the outermost one alone.
            members = members[:1]
            staged = stage_pragmas(after, members, dp_dir, source_file)
    if staged is None:
        return RewriteOutcome("exposed", pattern_label=label, exposed_prints=prints)
    ok_m, ratio, mdiag = measure(before, staged)
    if not ok_m:
        if "non-zero exit (-" in mdiag or "signal" in mdiag.lower():
            return RewriteOutcome("pattern_broken", pattern_label=label, exposed_prints=prints,
                                  diagnostic="the program with DiscoPoP's pragmas CRASHED at the timing "
                                             "size, which the correctness checks never reach: " + mdiag[:300])
        return RewriteOutcome("exposed", pattern_label=label, exposed_prints=prints)
    if ratio < threshold:
        return RewriteOutcome("not_faster", speedup=ratio, pattern_label=label, exposed_prints=prints,
                              diagnostic=rewrite_additions(before, after))
    return RewriteOutcome("ok", speedup=ratio, pattern_label=label, exposed_prints=prints)


_OUTCOME_LABEL = {
    "no_pattern": "DiscoPoP still finds no parallelism in the rewritten lines",
    "pattern_broken": "DiscoPoP found a pattern, but its pragma fails validation",
    "no_speedup": "DiscoPoP parallelized it, but it is not faster",
    "reprofile_failed": "the rewrite broke DiscoPoP's profiling run",
    "no_usable_pragma": "DiscoPoP sees a pattern, but no pragma it generates for it can run",
    "not_faster": "DiscoPoP parallelized it, but the program is not faster than before the rewrite",
}
# Fallback only.  The real threshold is measured per run by noise_floor() — an
# unchanged program does not measure 1.000, and how far off it lands depends on
# the host and the program, not on a number chosen here.  This value is used
# only when that calibration cannot run.
_MARGINAL_NOISE = 0.97
def _rewrite_feedback(
    outcome: RewriteOutcome, dp_dir: Path, file_id: int,
    touched: "tuple[int, int] | None", deps_shown: bool = True,
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

    if outcome.status == "not_faster":
        # D40.  The cause measured in E1c/E2 was what the rewrite ADDED — a copy of an array on
        # every repetition, a second pass, an allocation — not the dependence and not, mostly,
        # granularity, so that is what this names first.  DiscoPoP's dependences are pointed to
        # only in arms that showed them.
        return (
            f"Your rewrite is correct, DiscoPoP parallelized it ({outcome.pattern_label}), and its "
            f"pragmas passed every safety check. But with those pragmas the program runs at "
            f"{(outcome.speedup or 0.0):.2f}x the speed of the program as it stood before your "
            f"rewrite (the two timed interleaved, at the timing size). It has to be FASTER than "
            f"before, not only parallel, so the rewrite has been reverted.\n\n"
            f"The dependence is gone — do not look for one again. Look at what your rewrite "
            f"ADDED: {outcome.diagnostic}. Every extra pass over an array, every copy and every "
            f"allocation inside the repeated loop is paid on every repetition, and here it costs "
            f"more than the parallel loops save. Copy only what a loop-carried dependence forces "
            f"(an array no iteration writes needs no copy"
            + ("; DiscoPoP's dependences above name the arrays that carry one" if deps_shown else "")
            + "), keep the passes over memory as close to the original's as you can, and allocate "
            "outside the repeated loop. If your rewrite adds nothing of that kind, the parallel "
            "loop has too little work per activation to cover thread startup: make the loop with "
            "the most work per activation the parallel one."
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
