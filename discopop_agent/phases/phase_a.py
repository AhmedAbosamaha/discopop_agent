"""
Phase A — restructure, with the source kept pragma-free
---------------------------------------------------------
Regions DiscoPoP can already parallelize are DEFERRED, not processed.  The
reason is line numbers, not profile validity: the instrumented build carries no
-fopenmp, so a pragma is a comment to DiscoPoP and re-analysing after one returns
the same dependences.  But `assemble()` reads a region's span from the profile
and the TEXT from the source file, so a pragma inserted above a still-queued
region would hand the next LLM call the wrong lines.  Deferring also lets Phase B
order every pragma globally by predicted time saved, which is impossible here
because this queue is still growing.  A region with no pattern goes to the LLM,
and what comes back is gated, written, and re-profiled.

What decides whether the rewrite stays depends on who wrote the pragmas.  Under
--llm-pragmas the diff carries them and the gate has already judged them —
sanitizer, output from the parallel build, clock.  Otherwise the question is
DiscoPoP's: did a pattern appear in the lines that changed, and does the pragma
it generates for them actually work?  Anything else reverts, restoring source
AND profile from a snapshot rather than re-profiling.

The loop is index-based on purpose: a kept rewrite re-profiles, and the regions
that appear as a result are appended and picked up in the same pass.
"""
from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .. import viz
from ..args import AgentArguments
from ..evidence import assemble
from ..gate import _validate_cached, fix_hunk_headers
from ..llm import LLMConnectionError, call_llm
from ..llm.dep_review import _llm_dep_review
from ..plan import build_candidates, region_fingerprint
from ..plan.impact import ImpactModel, load_hotspots
from ..pragmas import _added_pragmas, _touched_span, check_llm_pragmas
from ..profiling import _measure_hotspots, _reprofil, _reprofil_fast
from ..profiling import fast_refresh
from ..sources import (_apply_to_source, _function_edit_to_diff,
                       _restore_profile, _snapshot_profile)
from ..types import HotspotCandidate, ValidationResult
from .report import _REGION_LABEL, _write_record
from .verdicts import (_OUTCOME_LABEL, RewriteOutcome, _rewrite_feedback,
                       _verify_rewrite)


@dataclass
class RunState:
    """Everything Phase A reads and writes, in one place.

    Passing this rather than eighteen parameters is what makes the loop
    extractable at all.  The containers are mutated in place — the queue, the
    accepted records, the change log — so only the two profile flags have to be
    written back explicitly.
    """
    args: AgentArguments
    dp_dir: Path
    profiler_dir: Path
    output_dir: Path
    impact: ImpactModel
    reference_output: Optional[str] = None
    reference_outputs: Optional[List[Any]] = None
    reference_time: Optional[float] = None
    binary_args: Optional[List[str]] = None
    original_text: str = ""
    gate_cache: Dict[str, Any] = field(default_factory=dict)
    accepted: List[Dict[str, Any]] = field(default_factory=list)
    deferred: List[Tuple[Any, ...]] = field(default_factory=list)
    skipped: List[Tuple[Any, ...]] = field(default_factory=list)
    change_log: List[Dict[str, Any]] = field(default_factory=list)
    all_seen_prints: Set[str] = field(default_factory=set)
    candidates: List[Tuple[int, HotspotCandidate]] = field(default_factory=list)
    # Set when a fast refresh leaves carried-forward dependence data in the
    # profile, and when a kept rewrite could not be re-profiled at all.
    profile_is_fast: bool = False
    profile_stale: bool = False

    def candidates_for(self, dd: Path) -> List[HotspotCandidate]:
        return build_candidates(dd, self.args.source_file,
                                self.args.lambda_penalty, self.args.min_workload,
                                impact=self.impact, min_impact=self.args.min_impact)


def phase_a(state: RunState) -> None:
    """Run the restructuring pass over the candidate queue."""
    args = state.args
    dp_dir = state.dp_dir
    profiler_dir = state.profiler_dir
    output_dir = state.output_dir
    reference_output = state.reference_output
    reference_outputs = state.reference_outputs
    reference_time = state.reference_time
    binary_args = state.binary_args
    impact = state.impact
    gate_cache = state.gate_cache
    accepted = state.accepted
    deferred = state.deferred
    skipped = state.skipped
    change_log = state.change_log
    all_seen_prints = state.all_seen_prints
    candidates = state.candidates
    _candidates = state.candidates_for
    profile_is_fast = state.profile_is_fast
    profile_stale = state.profile_stale

    # ── Candidate loop ────────────────────────────────────────────────────────
    # Index-based so candidates appended mid-run (from re-profiling) are
    # picked up automatically.
    i = 0
    while i < len(candidates):
        depth, candidate = candidates[i]
        i += 1
        region = candidate.region
        rid = region.region_id
        rtype = _REGION_LABEL.get(region.region_type, region.region_type)
        label = f"{rtype} {rid} (lines {region.start_line}–{region.end_line})"

        # Tier-2 (LLM restructuring) is only allowed up to restructure_depth.
        tier2_allowed = (depth <= args.restructure_depth)

        print(f"┌─ [depth={depth}] {label}  score={candidate.score:.1f}")

        # ── Tier-1 ───────────────────────────────────────────────────────────
        failure_reason = "DiscoPoP found no applicable parallelism pattern for this region"
        if candidate.tier == 1 and candidate.pattern and candidate.pattern.get("applicable_pattern"):
            # PHASE A leaves this alone.  DiscoPoP can already parallelize it,
            # so there is nothing to restructure — and inserting its pragma now
            # is exactly what used to invalidate the profile every later
            # decision depends on.  Phase B collects it from the final profile
            # and applies it there, once, with nothing left to shift underneath.
            print(f"│  [Phase-A] DiscoPoP already has a pattern here "
                  f"({candidate.pattern_type or 'pattern'}) — deferred to Phase B")
            print(f"└─ DEFERRED\n")
            deferred.append((rid, depth))
            continue

        # ── Tier-2: LLM restructuring ─────────────────────────────────────────
        if candidate.tier != 1:
            print(f"│  [Tier-1] No applicable pattern → Tier-2 (LLM)")

        if not tier2_allowed:
            print(f"│  [Tier-2] Restructuring not allowed at depth {depth} "
                  f"(--restructure-depth={args.restructure_depth}) → SKIP")
            print(f"└─ SKIPPED\n")
            skipped.append((rid, depth))
            continue

        if args.dry_run:
            print(f"│  [Tier-2] DRY RUN — skipping LLM call")
            print(f"└─ SKIPPED\n")
            skipped.append((rid, depth))
            continue

        budget = args.budget
        tier2_messages: list | None = None

        # Any restructuring may need reverting — it is kept only if DiscoPoP can
        # parallelize it afterwards — so snapshot the profile ONCE up front and
        # restore by file-copy instead of a full re-profile.  The pre-patch
        # source is identical across retries (revert restores it), so one
        # snapshot serves every attempt for this candidate.
        dp_snapshot: Path | None = None
        pre_patch_src: str | None = None
        pre_patch_src = Path(args.source_file).resolve().read_text()
        dp_snapshot = _snapshot_profile(dp_dir, output_dir)

        # Build errors (bad syntax, non-canonical loop) are mechanical fixes that
        # say nothing about the model's parallelization idea; spending a whole
        # budget slot on one wastes the region's real attempts.  They get their
        # own small allowance instead, capped so a model that cannot produce
        # compiling code still terminates.
        build_retries = args.build_retries

        while budget > 0:
            budget -= 1
            print(f"│  [Tier-2] Assembling evidence (budget remaining: {budget})")

            evidence = assemble(candidate, profiler_dir, failure_reason)

            print(f"│  [Tier-2] Calling {args.model}...")
            try:
                diff, tier2_messages = call_llm(
                    evidence, args.model,
                    api_key=args.api_key,
                    messages=tier2_messages,
                    provider=args.provider,
                    api_base=args.api_base,
                    edit_mode=args.edit_mode,
                    llm_pragmas=args.llm_pragmas,
                    verbose=args.verbose,
                )
            except LLMConnectionError as e:
                # Fatal for the whole run: every region needs the endpoint.
                print(f"│  [Tier-2] FATAL: {e}")
                print(f"└─ aborting — start the LLM server (or fix --api-base) and re-run\n")
                sys.exit(1)
            except Exception as e:                   # noqa: BLE001 - reported below
                # The backend failed this call even after its own retries.  That
                # is a bad attempt, not a broken run: everything already accepted
                # stays, and the next region still gets its chance.  Losing an
                # entire run to one flaky call is how a 20-minute job ends with
                # nothing to show.
                print(f"│  [Tier-2] LLM call failed: {str(e)[:120]}")
                print(f"│           counting it as a failed attempt and moving on")
                diff, tier2_messages = None, tier2_messages

            # In function mode the LLM returns the rewritten enclosing function;
            # splice it in and turn it into a guaranteed-apply diff.  In direct
            # mode it edited a copy of the file itself and call_llm already
            # returned that copy's diff ("" if it changed nothing).
            unchanged = False
            if diff is not None and args.edit_mode == "function":
                diff = _function_edit_to_diff(
                    args.source_file,
                    evidence.enclosing_function_start,
                    evidence.enclosing_function_end,
                    diff,
                )
                unchanged = diff is None
            elif diff == "":
                diff, unchanged = None, True

            if unchanged:
                what = ("You left the file UNCHANGED"
                        if args.edit_mode == "direct"
                        else "You returned the function UNCHANGED")
                print(f"│  [Tier-2] LLM produced no change"
                      f"{' — retrying' if budget > 0 else ''}")
                # Without feedback the next call would replay the same
                # conversation and get the same null answer — tell the model
                # explicitly that returning the input is not a valid move.
                if tier2_messages is not None:
                    tier2_messages = tier2_messages + [{
                        "role": "user",
                        "content": (
                            f"{what} (comment or formatting edits do not count). "
                            "That is not an answer: the blocking dependence has to be "
                            "gone. If your last attempt failed validation, do not fall "
                            "back to the original — restructure it a different way."
                        ),
                    }]

            if diff is None:
                if unchanged:
                    pass  # already reported above
                elif budget > 0:
                    print(f"│  [Tier-2] LLM returned invalid output — retrying")
                else:
                    print(f"│  [Tier-2] LLM returned invalid output")
                continue

            # Under --llm-pragmas a diff that carries a pragma is a finished
            # parallelization, not a step towards one: validate() then runs its
            # -fopenmp build, ThreadSanitizer, the output check against the
            # PARALLEL binary and (with --require-speedup) the timing — all of
            # which it skips for a pragma-less diff, because there is nothing
            # there to race or to speed up.
            pragmas = _added_pragmas(diff) if args.llm_pragmas else []
            self_annotated = bool(pragmas)
            if self_annotated:
                stages = ("apply/compile/openmp/TSan/output"
                          + ("/speed" if args.require_speedup else ""))
                print(f"│  [Tier-2] Diff received with {len(pragmas)} pragma(s) — "
                      f"running quality gate ({stages})")
                for pr in pragmas[:4]:
                    print(f"│           {pr}")
            else:
                print(f"│  [Tier-2] Diff received — running quality gate "
                      f"(apply/compile/correctness)")

            # Cheapest stage first, and the only one that can see a clause which
            # compiles, races nowhere, prints the right answer, and still throws
            # the loop's results away.
            result = None
            barrier_fp = False
            if self_annotated:
                problem = check_llm_pragmas(diff, args.source_file)
                if problem:
                    result = ValidationResult(passed=False, stage="clause",
                                              diagnostic=problem)
            if result is None:
                # Through _validate_cached, not validate() directly: this is
                # where a suspected OMP-barrier false positive is re-verified
                # against output instead of being trusted.  Phase A used to call
                # validate() raw, so that re-check never applied to an LLM
                # rewrite — which only started to matter once the rewrite could
                # carry pragmas of its own, and TSan on this platform reports a
                # race between any two parallel regions.
                result, _cached, barrier_fp = _validate_cached(
                    gate_cache, diff, args, reference_output, binary_args,
                    reference_time, reference_outputs=reference_outputs,
                    dep_region=(region.file_id, region.start_line, region.end_line),
                )
            if barrier_fp:
                print(f"│  [Tier-2] TSan flagged two DIFFERENT parallel regions — a "
                      f"barrier separates them, so this is the libomp/TSan artefact. "
                      f"Re-verified on output instead.")
            # The clause check is the controller's stage, not validate()'s, so
            # it has to declare itself skipped when it does not apply — the
            # renderer would otherwise show a green tick for a check that never ran.
            gate_skipped = list(result.skipped_stages)
            if not self_annotated:
                gate_skipped.insert(0, "clause")
            viz.gate_result(result.passed, result.stage, result.diagnostic,
                            result.measured_speedup, skipped_stages=gate_skipped)

            if result.passed:
                print(f"│  [Tier-2] Quality gate PASSED")

                clean_diff = fix_hunk_headers(diff)
                patch_file = output_dir / f"region_{rid.replace(':', '_')}_tier2.patch"
                patch_file.write_text(clean_diff)

                src_abs = Path(args.source_file).resolve()

                # Snapshot the CONTENT fingerprint of each still-queued candidate
                # BEFORE the patch touches the file.  A survivor (a region we
                # haven't processed and didn't patch) has identical text before
                # and after, so its fingerprint matches a fresh candidate even
                # though its ID drifted and its line numbers may have shifted.
                # NOTE: candidates[i:] is NOT deleted yet — if the restructuring
                # turns out not to pay off we revert and keep the queue intact.
                old_prints = [
                    (
                        d,
                        region_fingerprint(args.source_file, c.region.start_line,
                                     c.region.end_line, c.region.name),
                    )
                    for d, c in candidates[i:]
                ]

                if _apply_to_source(clean_diff, args.source_file, output_dir, "Tier-2"):
                    viz.panel(f"APPLIED PATCH -> {src_abs.name}", clean_diff,
                              color=viz.GREEN, colorize=viz._color_diff_line, max_lines=60)

                record = {
                    "region_id": rid,
                    "region_type": region.region_type,
                    "tier": 2,
                    "patch_file": str(patch_file),
                    "reprofiled": False,
                    "discovery_depth": depth,
                    # See phase_b: how the gate reached this verdict, not just
                    # what it was.
                    "evidence": dict(result.evidence),
                }

                # A deeper Tier-2 pass restructures from this profile, so it
                # gets measured data; a refresh that only has to relocate the
                # queue and find new regions does not.  Phase B is covered
                # separately, by one full re-profile before it runs.
                deeper_coming = (depth + 1) <= args.restructure_depth
                use_fast = args.fast_refresh and not deeper_coming
                if use_fast:
                    print(f"│  [Tier-2] Fast refresh (compile only, no instrumented run)...")
                    # Read ONCE.  The refresh, the hotspot remap and the
                    # dependence review each used to re-read this file, so the
                    # three of them could in principle disagree about what "the
                    # new source" is, and the line map got rebuilt each time.
                    post_patch_src = Path(args.source_file).read_text()
                    reprofile_ok, note = _reprofil_fast(
                        args.source_file, dp_dir, pre_patch_src or "",
                        post_patch_src, output_dir,
                    )
                    if reprofile_ok:
                        print(f"│           {note}")
                        profile_is_fast = True
                        if impact.available:
                            # Hotspots are keyed by LINE, so a rewrite that
                            # shifts lines does not merely make them stale — it
                            # makes them point at whatever now sits at that
                            # number.  Translate them the way the dependences
                            # were translated, and drop what cannot be.
                            lost = impact.remap_lines(
                                region.file_id,
                                fast_refresh.line_map(pre_patch_src or "",
                                                      post_patch_src),
                            )
                            if lost:
                                print(f"│           {lost} runtime measurement(s) "
                                      f"dropped — their lines were rewritten")
                        if args.llm_deps:
                            gaps = _llm_dep_review(
                                args, dp_dir, pre_patch_src or "",
                                post_patch_src, output_dir, region.file_id,
                            )
                            if gaps:
                                print(f"│           {gaps}")
                    else:
                        print(f"│           fast refresh not usable ({note}) "
                              f"— falling back to a full re-profile")
                        reprofile_ok = _reprofil(
                            args.source_file, dp_dir, args.reprofil_args or None
                        )
                else:
                    if args.fast_refresh and deeper_coming:
                        print(f"│  [Tier-2] Full re-profile — depth {depth + 1} will "
                              f"restructure from this data")
                    else:
                        print(f"│  [Tier-2] Re-profiling to refresh data and discover new candidates...")
                    reprofile_ok = _reprofil(
                        args.source_file, dp_dir, args.reprofil_args or None
                    )
                    if (reprofile_ok and deeper_coming and args.hotspots
                            and impact.available):
                        # The next level ranks by time saved, and the regions it
                        # will rank are the ones this rewrite just created —
                        # which have no measurement at all.  Measuring again is
                        # one native-speed run, next to the instrumented one
                        # already paid for here.
                        ok_hs, hs_note = _measure_hotspots(args, dp_dir, force=True)
                        fresh = load_hotspots(dp_dir, threads=impact.threads) \
                            if ok_hs else None
                        if fresh is not None and fresh.available:
                            impact.adopt(fresh)
                            print(f"│  [Tier-2] Re-measured runtimes: "
                                  f"{len(impact.by_line)} region(s), "
                                  f"{impact.total_runtime*1e3:.1f} ms total")
                        else:
                            print(f"│  [Tier-2] could not re-measure runtimes — "
                                  f"new regions will rank on the workload proxy")

                # rebuilt / discovered are computed read-only first; the queue and
                # all_seen_prints are only mutated once we decide to COMMIT.
                rebuilt: list = []
                discovered: list = []   # (depth+1, candidate, fingerprint)
                fresh_all: list = []
                if reprofile_ok:
                    fresh_all = _candidates(dp_dir)
                    fresh_by_print: dict = defaultdict(list)
                    for nc in fresh_all:
                        fp = region_fingerprint(args.source_file, nc.region.start_line,
                                          nc.region.end_line, nc.region.name)
                        fresh_by_print[fp].append(nc)

                    consumed: set = set()
                    for old_depth, fp in old_prints:
                        for nc in fresh_by_print.get(fp, []):
                            if id(nc) not in consumed:
                                rebuilt.append((old_depth, nc))
                                consumed.add(id(nc))
                                break

                    for nc in fresh_all:
                        if id(nc) in consumed:
                            continue
                        fp = region_fingerprint(args.source_file, nc.region.start_line,
                                          nc.region.end_line, nc.region.name)
                        if fp not in all_seen_prints:
                            discovered.append((depth + 1, nc, fp))

                # ── THE POINT OF THE WHOLE EXERCISE ───────────────────────────
                # Compiling and preserving output only makes the rewrite HARMLESS.
                # It is WORTH keeping only if DiscoPoP can now parallelize the
                # lines that changed.  Ask it, every time — never assume.
                if self_annotated:
                    # The question Phase A normally asks DiscoPoP — "can you
                    # parallelize this now?" — has already been answered, by the
                    # model, in the diff.  The gate above judged that answer the
                    # hard way: sanitizer, output from the parallel build, clock.
                    # Re-profiling still runs, but only to refresh line numbers
                    # and find new candidates; its verdict no longer decides.
                    outcome = RewriteOutcome(
                        "self_annotated", speedup=result.measured_speedup,
                        pattern_label=f"{len(pragmas)} LLM pragma(s): "
                                      + "; ".join(pragmas[:2]),
                    )
                    if not reprofile_ok:
                        # The parallelization is validated and stays.  What is
                        # unusable is the PROFILE, so put the coherent one back
                        # and stop trusting DiscoPoP for the rest of this run.
                        if dp_snapshot is not None:
                            _restore_profile(dp_snapshot, dp_dir, output_dir)
                        profile_stale = True
                        print(f"│  [Tier-2] Re-profiling failed — the rewrite is kept "
                              f"(it passed the whole gate), but Phase B is skipped: "
                              f"there is no profile that describes this file")
                elif not reprofile_ok:
                    outcome = RewriteOutcome(
                        "reprofile_failed",
                        diagnostic="DiscoPoP could not instrument, run, or analyse the "
                                   "rewritten program (see the log above).",
                    )
                else:
                    # Validating the exposed pragma is deferred only when a deeper
                    # Tier-2 pass is still allowed to work on it.
                    # Phase A asks one question: did the rewrite expose a
                    # pattern in the lines it changed?  Whether the resulting
                    # pragma works is Phase B's question, asked once, later.
                    print(f"│  [Phase-A] Asking DiscoPoP what it now finds in the "
                          f"rewritten lines...")
                    outcome = _verify_rewrite(
                        fresh_all, _touched_span(clean_diff), dp_dir, args,
                        reference_output, binary_args, reference_time,
                        validate_patterns=False, gate_cache=gate_cache,
                        reference_outputs=reference_outputs,
                    )

                if outcome.status not in ("ok", "exposed", "self_annotated"):
                    # REVERT — the restructuring did not achieve its purpose.
                    # Restore source + the pre-patch profile from the snapshot
                    # (file copy) instead of re-profiling — far cheaper.
                    if pre_patch_src is not None:
                        src_abs.write_text(pre_patch_src)
                    if dp_snapshot is not None:
                        _restore_profile(dp_snapshot, dp_dir, output_dir)
                    patch_file.unlink(missing_ok=True)
                    msg = _rewrite_feedback(
                        outcome, dp_dir, region.file_id, _touched_span(clean_diff)
                    )
                    print(f"│  [Tier-2] {_OUTCOME_LABEL[outcome.status]} — reverting "
                          f"(snapshot restore)")
                    viz.panel("DISCOPOP → LLM FEEDBACK", msg, color=viz.YELLOW, max_lines=30)
                    failure_reason = msg
                    if tier2_messages is not None:
                        tier2_messages = tier2_messages + [
                            {"role": "user", "content": msg}
                        ]
                    print(f"└─ retry (budget remaining: {budget})\n")
                    continue  # budget already decremented at loop top

                exposed_speedup = outcome.speedup

                # ── COMMIT ────────────────────────────────────────────────────
                del candidates[i:]
                candidates.extend(rebuilt)
                candidates.extend((d, nc) for d, nc, _ in discovered)
                for _d, _nc, fp in discovered:
                    all_seen_prints.add(fp)
                if reprofile_ok:
                    print(f"│  [Tier-2] {len(rebuilt)} survivor(s) rebuilt, "
                          f"{len(discovered)} new at depth {depth + 1}")
                    record["reprofiled"] = True
                record["exposed_pattern"] = outcome.pattern_label
                if impact.available:
                    # Stage 3: this region's time is now spoken for, so anything
                    # nested inside it has nothing left to win.
                    impact.mark_covered(region.file_id, region.start_line, region.end_line)
                    if result.measured_speedup:
                        impact.observe_speedup(result.measured_speedup)
                if self_annotated:
                    record["pragmas"] = len(pragmas)
                    record["pragma_text"] = pragmas
                    record["self_annotated"] = True
                change_log.append({
                    "kind": "rewrite", "region_id": rid, "diff": clean_diff,
                    "exposed": outcome.exposed_prints,
                    "self_annotated": self_annotated,
                    "pragmas": len(pragmas),
                })
                if self_annotated:
                    print(f"│  [Tier-2] Kept on its own pragmas: {len(pragmas)} "
                          f"annotated loop(s), gate passed end to end")
                else:
                    print(f"│  [Tier-2] DiscoPoP now finds: {outcome.pattern_label}")
                if exposed_speedup is not None:
                    record["exposed_speedup"] = exposed_speedup
                    print(f"│  [Tier-2] Restructuring pays off "
                          f"({'measured' if self_annotated else 'best exposed loop'} "
                          f"{exposed_speedup:.2f}×)")
                elif outcome.status == "exposed":
                    print(f"│  [Tier-2] Pragma validation deferred to depth "
                          f"{depth + 1} (still allowed to restructure)")

                accepted.append(record)
                _write_record(output_dir, record, args.dry_run)
                print(f"└─ ACCEPTED\n")
                break

            else:
                # A failure-stage → plain-English instruction for the LLM, so the
                # next prompt always says WHY (apply/compile/openmp_compile/tsan/
                # correctness/performance) and what to do about it.
                _STAGE_GUIDANCE = {
                    "clause": "A data-sharing clause on a pragma YOU wrote cannot be "
                             "right. Fix the clause — this is not a reason to change "
                             "the parallelization strategy. A name declared inside the "
                             "loop body belongs in no clause at all; a name the loop "
                             "writes and later code reads needs reduction or "
                             "lastprivate, never private or firstprivate.",
                    "apply": "The diff did not apply — its context lines must match the "
                             "current file exactly (raw indentation, no line-number prefix).",
                    "compile": "The patched code does not compile. Fix the C/C++ error "
                             "without changing what the code computes.",
                    "openmp_compile": "A loop you want parallelized is not in OpenMP-canonical "
                             "form: it needs a simple `i < bound` condition and no "
                             "break/continue/return in the body.",
                    "tsan": "ThreadSanitizer found a REAL data race — the loop still carries a "
                            "cross-iteration dependence. Identify its cause (in-place coupling, "
                            "hidden reduction, storage reuse, or a true recurrence) and make the "
                            "iterations independent — do not merely rename storage.",
                    "correctness": "The program's output CHANGED — your restructuring is not "
                            "semantically equivalent. Diagnose WHICH kind of error this is "
                            "before rewriting:\n"
                            "(a) WRONG TRANSFORMATION — you assumed an independence the "
                            "code does not have, or reordered operations whose order affects "
                            "the result. Re-check that against the evidence and restructure "
                            "differently.\n"
                            "(b) RIGHT TRANSFORMATION, carried-over detail — the strategy is "
                            "sound but some bound, initial value, or boundary handling was "
                            "copied from the old schedule. Re-derive each such detail for the "
                            "new schedule instead of copying it: a loop bound or skipped "
                            "element that was safe because of the OLD update order is not "
                            "automatically safe under the new one. Keep the strategy and fix "
                            "only that.",
                    "performance": "The parallel build was correct but NOT faster than "
                            "sequential. The dependence is already gone; the parallel work is "
                            "just too fine-grained to cover thread startup.",
                }
                guidance = _STAGE_GUIDANCE.get(result.stage, "")
                refunded = ""
                if result.stage in ("apply", "compile", "openmp_compile") and build_retries > 0:
                    build_retries -= 1
                    budget += 1     # a build error must not cost a real attempt
                    refunded = f" (build fix — budget not charged, {build_retries} left)"
                print(f"│  [Tier-2] Stage '{result.stage}' failed{refunded}: "
                      f"{result.diagnostic[:200].replace(chr(10), ' ')}")
                # Keep enough of the diagnostic that the correctness expected-vs-got
                # comparison survives (it can run ~1.3 KB).
                diag_full = (result.diagnostic or "(no diagnostic)")[:1400]
                failure_reason = (
                    f"Validation failed at stage '{result.stage}'. {guidance}\n\n"
                    f"Diagnostic:\n{diag_full}"
                )
                # Build failures need the same approach with the error fixed;
                # semantic failures need an explicit decision about whether the
                # STRATEGY or a DETAIL was wrong (a blanket "switch strategy"
                # pushes the model off correct-but-buggy transformations).
                if result.stage in ("apply", "compile", "openmp_compile"):
                    retry_instr = (
                        "Keep your transformation approach and fix ONLY the reported "
                        "error — do not change strategy over a build problem."
                    )
                else:
                    retry_instr = (
                        "Do not resubmit a variation of the same code. Say in one line "
                        "which of (a) or (b) this was and what you are changing because "
                        "of it — then make sure the code you write actually differs in "
                        "that way. Stating the right bound and then writing the old one "
                        "is the most common way this retry fails."
                    )
                if tier2_messages is not None:
                    tier2_messages = tier2_messages + [{
                        "role": "user",
                        "content": (
                            f"Your diff failed at the '{result.stage}' stage. {guidance}\n\n"
                            f"Diagnostic:\n{diag_full}\n\n"
                            f"{retry_instr}"
                        ),
                    }]
        else:
            print(f"└─ SKIPPED (budget exhausted)\n")
            skipped.append((rid, depth))

        # Clean up the per-candidate profile snapshot (commit or skip — either way
        # we no longer need it).
        if dp_snapshot is not None and dp_snapshot.exists():
            shutil.rmtree(dp_snapshot, ignore_errors=True)

    # Only the flags need carrying back; every container above was mutated in place.
    state.profile_is_fast = profile_is_fast
    state.profile_stale = profile_stale
