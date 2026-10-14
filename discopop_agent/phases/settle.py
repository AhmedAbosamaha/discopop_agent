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
line spans drift) and no kept rewrite was built on, rebuild by RE-APPLYING
survivors rather than un-applying anything, and re-gate the result — dropping
the newest pragma and rebuilding while it fails, reverting the whole run if
nothing is left.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .. import project as project_mod
from ..args import AgentArguments
from ..gate import validate
from ..gate.tsan import barrier_artefact_possible
from ..gate.timing import measure_marginal
from ..llm import make_diff, normalize_code
from .verdicts import _MARGINAL_NOISE
from ..sources import _apply_change_log
from ..types import ValidationResult


def _check_final_source(
    args: AgentArguments, originals: "Dict[str, str] | str", reference_output: "str | None",
    reference_outputs: "List[Tuple[List[str], str]] | None", binary_args: "List[str] | None",
    reference_time: "float | None", speed_threshold: float = _MARGINAL_NOISE,
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
    if isinstance(originals, str):
        # The single-file form: the one file's text as it stood at the start.
        originals = {str(Path(args.source_file).resolve()): originals}
    changed = [p for p, text in originals.items()
               if normalize_code(Path(p).read_text()) != normalize_code(text)]
    if not changed:
        return True, "source unchanged"
    # One file is handed to the gate as "original + cumulative diff"; in a project
    # the staged tree already holds every OTHER file in its final state, so the
    # program that gets built and judged is the finished one either way.  The file
    # chosen is one whose diff carries a pragma, when any does, because that is
    # what switches the gate to its parallel track (-fopenmp, the sanitizer, the
    # schedule matrix) — and those then cover every pragma in the program.
    def _adds_pragma(p: str) -> bool:
        return "#pragma omp" in Path(p).read_text() and "#pragma omp" not in originals[p]
    target = next((p for p in changed if _adds_pragma(p)), changed[0])
    project_mod.work_on(args, target)
    original_text = originals[target]
    final_text = Path(target).read_text()

    with tempfile.TemporaryDirectory(prefix="dp_agent_check_") as tmp:
        base = Path(tmp) / Path(target).name
        base.write_text(original_text)
        cumulative = make_diff(original_text, final_text, str(base))
        def _run(skip: bool) -> ValidationResult:
            return validate(
                cumulative, str(base), reference_output=reference_output,
                reference_outputs=reference_outputs, binary_args=binary_args,
                require_speedup=False, reference_time=reference_time,
                skip_race_check=skip, mode="safety",
                # The SAME tolerance and stress settings every earlier gate used.
                # Without them this re-check compared byte-for-byte, so a reduction
                # accepted under the measured noise floor failed here and the whole
                # run was reverted (review F9).
                noise_floor=getattr(args, "noise_floor", 0.0),
                stress=getattr(args, "schedule_stress", True),
                stress_threads=tuple(getattr(args, "stress_threads", None) or ()) or None,
            )

        res = _run(False)
        # The macOS OMP-barrier artefact applies here exactly as it does to a
        # single pragma, and forgetting it is worse at this end: every pragma
        # would pass its own gate (which does re-check) and then be thrown away
        # by this one, so the run could never keep anything on this platform.
        if (not res.passed and res.stage == "tsan"
                and barrier_artefact_possible(res.diagnostic, final_text)):
            print(f"  [note] TSan OMP-barrier false positive on the finished file "
                  f"— re-verifying on output instead")
            res = _run(True)
        if not res.passed:
            return False, (f"the finished file fails at '{res.stage}': "
                           f"{res.diagnostic[:160].replace(chr(10), ' ')}")

        if args.require_speedup and reference_time is not None:
            # PAIRED, like every speed decision before it (Fix 89).  This used to
            # time the finished program alone (best-of-5, -fopenmp) against the
            # reference captured at the START of the run (best-of-3, no -fopenmp)
            # and call the program slower when the two differed by more than the
            # noise allowance.  Two states of the machine minutes apart on a
            # shared host are not a comparison: in E1's class-R run 15 of 90 TSVC
            # trials had a program Phase B had just measured at 1.02-1.84x per
            # pragma, interleaved, and this check then reported it 1.1-8x SLOWER
            # than a number taken before the model was even called, and threw the
            # whole run away.  The same interleaved original-vs-final measurement
            # Phase B uses, both sides -fopenmp builds of the same file, median of
            # the per-pair ratios, and the same "not slower beyond the noise"
            # threshold, cannot be fooled by drift.  `reference_time` is now only
            # the switch that says the original could be timed at all.
            ok_m, ratio, mdiag = measure_marginal(
                original_text, final_text, target, binary_args, pairs=5,
                extra_flags=list(args.timing_cflags) or None,
            )
            if not ok_m:
                return False, f"could not time the finished program: {mdiag[:120]}"
            if ratio < speed_threshold:
                return False, (f"slower than the original: {ratio:.2f}x, paired "
                               f"(kept at or above {speed_threshold:.3f})")
            return True, f"output matches, {ratio:.2f}x the original, paired"
    return True, "output matches the original"


def _region_text_in(fingerprint: str, text: str) -> bool:
    """Is the region a fingerprint names still in `text`, as a run of whole lines?

    `region_fingerprint` is the region's lines stripped, blank and comment lines
    dropped, behind the enclosing name and a separator; the file is normalised the
    same way, and only whole lines may match.
    """
    body = fingerprint.split("␟", 1)[-1]
    if not body:
        return False
    lines = [ln.strip() for ln in text.splitlines()
             if ln.strip() and not ln.strip().startswith("//")]
    return f"\n{body}\n" in "\n" + "\n".join(lines) + "\n"


def _orphans_to_drop(originals: "Dict[str, str]", keep: List[Any], orphans: List[Any],
                     args: AgentArguments) -> List[Any]:
    """The orphans that go: those no rewrite that stays was built on.  (Fix 106)

    A deeper level restructures what the level before it produced, and a region
    sent back to the model is rewritten on top of the rewrite that exposed it, so
    DiscoPoP's pragmas land on the LAST rewrite's regions and every earlier rewrite
    of the chain looks as if it achieved nothing.  Dropping one took the chain with
    it: the later rewrites, and the pragmas on them, no longer applied to the
    original (E8's smoke, 14 Oct: both trials ended with nothing).

    A later rewrite is built on an orphan when it changed a region the orphan
    exposed — that region's text is in its file just before the rewrite and gone
    just after it — or when it does not apply without the orphan, the replay's
    own test of dependence.  Newest first, so an orphan that only a later orphan
    was built on goes once that one has gone.  An orphan nothing was built on goes
    as before.
    """
    if not orphans:
        return []
    states: Dict[int, Tuple[str, str]] = {}
    base = _apply_change_log(originals, keep, args, states=states)
    staying = list(keep)
    gone: List[Any] = []
    for orphan in reversed(orphans):
        at = next(i for i, c in enumerate(staying) if c is orphan)
        later = [c for c in staying[at + 1:] if c["kind"] != "pragma"]
        prints = orphan.get("exposed", [])
        changed = next((c for c in later
                        if id(c) in states and c.get("file") == orphan.get("file")
                        and any(_region_text_in(fp, states[id(c)][0])
                                and not _region_text_in(fp, states[id(c)][1]) for fp in prints)),
                       None)
        if changed is not None:
            by, how = changed, "changed a region it exposed"
        else:
            without = [c for c in staying if c is not orphan]
            landed = _apply_change_log(originals, without, args)
            needs = next((c for c in later if any(c is b for b in base)
                          and not any(c is ld for ld in landed)), None)
            if needs is None:
                staying, base = without, landed
                gone.append(orphan)
                continue
            by, how = needs, "does not apply without it"
        print(f"  [keep] rewrite of {orphan['region_id']} — no kept pragma targets a region it "
              f"exposed, but the rewrite of {by['region_id']} kept after it {how}")
    return gone


def _settle(
    originals: "Dict[str, str] | str", change_log: List[Any], args: AgentArguments,
    output_dir: Path, reference_output: "str | None",
    reference_outputs: "List[Tuple[List[str], str]] | None", binary_args: "List[str] | None",
    reference_time: "float | None", speed_threshold: float = _MARGINAL_NOISE,
) -> "Tuple[List[Any], List[Any]]":
    """Reduce the run to a set of changes that is sound AND worth keeping.

    Three things happen here, in one loop, because they are the same operation:

      1. ORPHANS.  A Phase-A rewrite exists to let DiscoPoP parallelize
         something.  If no kept pragma targets a region it exposed, it achieved
         nothing — and it is not free, so it goes.  Justification is by region
         FINGERPRINT, not line containment: regions nest, and their line spans
         drift as changes land above them.  A rewrite that carries its OWN
         pragmas (--llm-pragmas) is its own justification and is never an
         orphan — the parallelism is in the change itself, not in what DiscoPoP
         made of it afterwards.  Nor is one that a kept rewrite was built on
         (Fix 106, `_orphans_to_drop`): the pragmas of a chain land on its LAST
         rewrite's regions, and what the chain stands on has to stay with it.

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
    notes: List[Any] = []
    keep = list(change_log)
    if isinstance(originals, str):
        # The single-file form: the one file's text as it stood at the start.
        originals = {str(Path(args.source_file).resolve()): originals}

    while True:
        # A D33 set is one entry covering several regions: each of its fingerprints counts.
        applied_prints = {fp for c in keep if c["kind"] == "pragma"
                          for fp in (c.get("fingerprints") or [c.get("fingerprint")]) if fp}
        orphans = [ch for ch in keep
                   if ch["kind"] != "pragma" and not ch.get("self_annotated")
                   and not applied_prints & set(ch.get("exposed", []))]
        gone = _orphans_to_drop(originals, keep, orphans, args)
        for ch in orphans:
            if any(ch is g for g in gone):
                notes.append(f"rewrite of {ch['region_id']} — exposed "
                             f"{len(ch.get('exposed', []))} region(s), none kept a pragma")
        keep = [ch for ch in keep if not any(ch is g for g in gone)]

        landed = _apply_change_log(originals, keep, args)
        for ch in keep:
            if ch not in landed:
                notes.append(f"{ch['kind']} for {ch['region_id']} — depended on a "
                             f"change that was dropped, so it no longer applies")
        keep = landed

        ok, why = _check_final_source(args, originals, reference_output,
                                      reference_outputs, binary_args, reference_time,
                                      speed_threshold)
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
            for path, text in originals.items():
                if Path(path).read_text() != text:
                    Path(path).write_text(text)
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
