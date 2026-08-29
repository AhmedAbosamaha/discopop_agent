"""
Settle — the only step that judges the FILE
---------------------------------------------
Every gate before this validated a candidate patch against a temp copy.  What
ends up on disk is a RECONSTRUCTION — the survivors re-applied onto the original
— and that is not automatically the thing any gate looked at.  Trusting the
reconstruction is how a pragma the gate rejects deterministically ended up in
the source.

Three things happen here, in one loop, because they are the same operation:
drop rewrites no kept pragma justified (matched by region FINGERPRINT, since
line spans drift), rebuild by RE-APPLYING survivors rather than un-applying
anything, and re-gate the result — dropping the newest pragma and rebuilding
while it fails, reverting the whole run if nothing is left.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from ..args import AgentArguments
from ..gate import validate
from ..gate.tsan import _is_omp_barrier_false_positive
from ..gate.timing import time_source
from ..llm import make_diff, normalize_code
from .verdicts import _MARGINAL_NOISE
from ..sources import _apply_change_log
from ..types import ValidationResult


def _check_final_source(
    args: AgentArguments, original_text: str, reference_output: "str | None",
    reference_outputs: "list | None", binary_args: "list | None",
    reference_time: "float | None",
) -> "tuple[bool, str]":
    """Is the file ON DISK sound, and is it better than what the user started with?

    Every gate before this validated a candidate patch against a temp copy.  The
    file that ends up on disk is a RECONSTRUCTION — the survivors re-applied
    onto the original — and that is not automatically the thing any gate looked
    at.  Trusting the reconstruction is how a pragma the gate rejects
    deterministically ended up in the source.

    So this re-runs the real gate against the actual final content: compile, the
    -fopenmp build, ThreadSanitizer, and output.  Speed is asked only under
    --require-speedup, and separately, because it is the user's switch for
    whether that question is asked at all.
    """
    final_text = Path(args.source_file).read_text()
    if normalize_code(final_text) == normalize_code(original_text):
        return True, "source unchanged"

    with tempfile.TemporaryDirectory(prefix="dp_agent_check_") as tmp:
        base = Path(tmp) / Path(args.source_file).name
        base.write_text(original_text)
        cumulative = make_diff(original_text, final_text, str(base))
        def _run(skip: bool) -> ValidationResult:
            return validate(
                cumulative, str(base), reference_output=reference_output,
                reference_outputs=reference_outputs, binary_args=binary_args,
                require_speedup=False, reference_time=reference_time,
                skip_race_check=skip, mode="safety",
            )

        res = _run(False)
        # The macOS OMP-barrier artefact applies here exactly as it does to a
        # single pragma, and forgetting it is worse at this end: every pragma
        # would pass its own gate (which does re-check) and then be thrown away
        # by this one, so the run could never keep anything on this platform.
        if (not res.passed and res.stage == "tsan"
                and _is_omp_barrier_false_positive(res.diagnostic)):
            print(f"  [note] TSan OMP-barrier false positive on the finished file "
                  f"— re-verifying on output instead")
            res = _run(True)
        if not res.passed:
            return False, (f"the finished file fails at '{res.stage}': "
                           f"{res.diagnostic[:160].replace(chr(10), ' ')}")

        if args.require_speedup and reference_time is not None:
            ok_t, t_final, _out, tdiag = time_source(
                final_text, args.source_file, Path(tmp), "final", binary_args, repeats=5
            )
            if not ok_t:
                return False, f"could not time the finished program: {tdiag[:120]}"
            # NOT a bare `>`.  Two things make a bare comparison a coin flip
            # here, and it decides whether a whole run survives:
            #   * whole-program wall-time carries a few tenths of a percent of
            #     noise even at best-of-5 (measured: an UNCHANGED file failed
            #     this check in 4 of 8 trials, ratios 0.991-1.006);
            #   * the two sides are not even the same build — reference_time
            #     comes from a NON-fopenmp compile (capture_reference) while
            #     t_final comes from an -fopenmp one (time_source), which is the
            #     mismatch `_measure_speedup` documents avoiding.
            # So the same tolerance the rest of the gate uses for "not slower"
            # applies: a real regression has to clear the noise, not tie with it.
            if t_final > reference_time / _MARGINAL_NOISE:
                return False, (f"slower than the original: {t_final*1e3:.1f} ms vs "
                               f"{reference_time*1e3:.1f} ms "
                               f"(beyond the {1/_MARGINAL_NOISE - 1:.0%} noise allowance)")
            return True, (f"output matches, {t_final*1e3:.1f} ms vs "
                          f"{reference_time*1e3:.1f} ms original")
    return True, "output matches the original"
def _settle(
    original_text: str, change_log: list, args: AgentArguments,
    output_dir: Path, reference_output: "str | None",
    reference_outputs: "list | None", binary_args: "list | None",
    reference_time: "float | None",
) -> "tuple[list, list]":
    """Reduce the run to a set of changes that is sound AND worth keeping.

    Three things happen here, in one loop, because they are the same operation:

      1. ORPHANS.  A Phase-A rewrite exists to let DiscoPoP parallelize
         something.  If no kept pragma targets a region it exposed, it achieved
         nothing — and it is not free, so it goes.  Justification is by region
         FINGERPRINT, not line containment: regions nest, and their line spans
         drift as changes land above them.  A rewrite that carries its OWN
         pragmas (--llm-pragmas) is its own justification and is never an
         orphan — the parallelism is in the change itself, not in what DiscoPoP
         made of it afterwards.

      2. RECONSTRUCTION.  Rebuild by re-applying survivors onto a fresh copy of
         the original rather than un-applying anything, so no patch is ever
         reversed and dependence is discovered instead of computed.

      3. VERIFICATION.  Re-gate the RESULT.  Every earlier gate judged a
         candidate patch against a temp copy; the reconstruction is a different
         artifact and has to earn its own verdict.  While it fails, drop the
         most recently applied pragma and rebuild again — newest first, because
         later pragmas are the least likely to be load-bearing and the most
         likely to be the interaction that broke it.

    Returns (surviving change log, human-readable notes about what was dropped).
    """
    notes: list = []
    keep = list(change_log)

    while True:
        applied_prints = {c["fingerprint"] for c in keep
                          if c["kind"] == "pragma" and c.get("fingerprint")}
        pruned: list = []
        for ch in keep:
            if ch["kind"] == "pragma":
                pruned.append(ch)
            elif ch.get("self_annotated"):
                pruned.append(ch)
            elif applied_prints & set(ch.get("exposed", [])):
                pruned.append(ch)
            else:
                notes.append(f"rewrite of {ch['region_id']} — exposed "
                             f"{len(ch.get('exposed', []))} region(s), none kept a pragma")
        keep = pruned

        landed = _apply_change_log(original_text, keep, args)
        for ch in keep:
            if ch not in landed:
                notes.append(f"{ch['kind']} for {ch['region_id']} — depended on a "
                             f"change that was dropped, so it no longer applies")
        keep = landed

        ok, why = _check_final_source(args, original_text, reference_output,
                                      reference_outputs, binary_args, reference_time)
        if ok:
            if why != "source unchanged":
                print(f"  [ok] finished source verified — {why}")
            return keep, notes

        # Newest first, and DiscoPoP's pragmas before the LLM's own: a pragma
        # applied on top of finished code is the cheaper thing to lose than a
        # restructuring that carries its parallelism with it.
        droppable = ([c for c in keep if c["kind"] == "pragma"]
                     or [c for c in keep if c.get("self_annotated")])
        if not droppable:
            # Nothing left to drop and it still does not hold up: the rewrites
            # alone are the problem, so put the user back where they started.
            Path(args.source_file).write_text(original_text)
            notes.append(f"everything reverted — {why}")
            print(f"  [revert] {why}")
            return [], notes

        victim = droppable[-1]
        what = ("pragma" if victim["kind"] == "pragma"
                else "self-annotated rewrite")
        keep.remove(victim)
        notes.append(f"{what} for {victim['region_id']} — dropped because {why}")
        print(f"  [repair] {why}")
        print(f"           → dropping the {what} for {victim['region_id']} and re-checking")
