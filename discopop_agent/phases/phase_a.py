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

import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .. import project as project_mod
from .. import viz
from ..args import AgentArguments
from ..evidence import assemble
from ..gate import _validate_cached, fix_hunk_headers, measure_marginal, noise_floor
from ..llm import LLMConnectionError, call_llm
from ..llm.diffs import make_diff
from ..llm.dep_review import _llm_dep_review
from ..plan import build_candidates, region_budget, region_fingerprint
from ..plan.impact import ImpactModel, load_hotspots
from ..pragmas import (_added_pragmas, _touched_span, arbitrate_pragmas,
                       changed_span, check_llm_pragmas, existing_parallel_spans,
                       net_new_pragmas)
from ..profiling import _measure_hotspots, _reprofil, _reprofil_fast
from ..profiling import fast_refresh
from ..profiling.tools import _explorer_cmd, _venv_env, run_explorer
from ..sources import (_apply_to_source, _function_edit_to_diff,
                       _restore_profile, _snapshot_profile)
from ..gate.harness_lines import check_protected
from ..types import GateFacts, HotspotCandidate, ValidationResult
from .report import _REGION_LABEL, _record_candidate, _write_record
from .verdicts import (_MARGINAL_NOISE, _OUTCOME_LABEL, D40_SETS_KEY, SPEED_THRESHOLD_KEY, RewriteOutcome, tier1_verdict,
                       _rewrite_feedback, _verify_rewrite, exposed_in, judge_as_shipped)


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
                                impact=self.impact, min_impact=self.args.min_impact,
                                min_runtime_share=self.args.min_runtime_share,
                                exclude_functions=self.args.exclude_functions)


def should_remeasure_runtimes(reprofile_ok: bool, hotspots: bool,
                              impact_available: bool) -> bool:
    """Whether to re-measure runtimes after a kept rewrite.  (Fix 86)

    Note what is NOT a parameter: the restructuring depth.  The regions a rewrite
    creates have no measurement, and something always ranks them — a deeper Tier-2
    level only when one is coming, but PHASE B on every single run.  While this was
    gated on `deeper_coming` it never fired at the default --restructure-depth 0, so
    every exposed loop reached Phase B unmeasured, `predicted_saving` returned None
    for all of them, and --min-runtime-share (0.01 in the campaign) dropped them —
    leaving Phase B nothing to apply and Settle discarding the rewrite as an orphan.
    The whole restructuring path then reported `no-change`.

    Cost of getting it right: one native-speed run, beside the instrumented one the
    re-profile has already paid for.
    """
    return reprofile_ok and hotspots and impact_available


def covered_spans_after(start_line: int, end_line: int, pre_text: str, post_text: str,
                        diff: str, self_annotated: bool) -> List[Tuple[int, int]]:
    """The lines a KEPT rewrite has made parallel, in the rewritten file's coordinates.

    Nothing for a rewrite that carries no pragma.  Such a rewrite has parallelised
    nothing yet: it exists so that DiscoPoP can, and the loops it exposed are exactly
    what Phase B must annotate.  Marking its region covered — as used to happen for
    every kept rewrite — made `build_candidates` drop those loops (a covered region
    predicts no saving), so under --no-llm-pragmas with runtime measurements Phase B
    had nothing to apply and Settle then discarded the rewrite as an orphan.

    For a self-annotated rewrite it is the PARALLEL CONSTRUCTS inside the region as
    it now stands — not the region.  The whole edited span used to be covered (and in
    its OLD line numbers), which hid a sibling loop of the same function from
    Phase B and meant a deeper restructuring level could never see anything a
    rewrite had created.  If no construct can be located the region's span is the
    fallback, so something is always covered."""
    if not self_annotated:
        return []
    lm = fast_refresh.line_map(pre_text, post_text)
    grown = len(post_text.splitlines()) - len(pre_text.splitlines())
    new_start = lm.get(start_line, start_line)
    new_end = lm.get(end_line) or (end_line + grown)
    ch = changed_span(diff)
    if ch is not None:
        new_start, new_end = min(new_start, ch[0]), max(new_end, ch[1])
    new_end = max(new_end, new_start)
    inside = [(a, b) for a, b in existing_parallel_spans(post_text)
              if new_start <= a and b <= new_end + 1]
    return inside or [(new_start, new_end)]


def speed_threshold(args: AgentArguments, gate_cache: Dict[str, Any],
                    binary_args: Optional[List[str]]) -> float:
    """Settle's keep-threshold — the timing noise measured on this machine — for D40's check.

    Phase B measures it, and the floor's Phase B usually has before Phase A starts; but not when
    DiscoPoP alone proposes nothing for the original, which is exactly class R.  Then it is
    measured here, once, the way Phase B does it, and left in the cache for everything after."""
    if SPEED_THRESHOLD_KEY not in gate_cache:
        ok_n, floor, ndiag = noise_floor(Path(args.source_file).read_text(), args.source_file,
                                         binary_args, extra_flags=list(args.timing_cflags) or None)
        gate_cache[SPEED_THRESHOLD_KEY] = min(floor - 0.01, 0.99) if ok_n else _MARGINAL_NOISE
        print(f"│  [Phase-A] timing noise on this machine: "
              + (f"{floor:.3f}" if ok_n else f"not measurable ({ndiag[:50]})")
              + f" → keep at or above {gate_cache[SPEED_THRESHOLD_KEY]:.3f}")
    return float(gate_cache[SPEED_THRESHOLD_KEY])


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
        # In a project each region is worked on in the file it lives in.
        project_mod.work_on(args, candidate.source_file)
        rid = region.region_id
        rtype = _REGION_LABEL.get(region.region_type, region.region_type)
        label = f"{rtype} {rid} (lines {region.start_line}–{region.end_line})"

        # Tier-2 (LLM restructuring) is only allowed up to restructure_depth.
        tier2_allowed = (depth <= args.restructure_depth)

        print(f"┌─ [depth={depth}] {label}  score={candidate.score:.1f}")

        # Already inside a construct that runs in parallel in the file AS IT NOW
        # STANDS — a loop the model annotated a moment ago, typically.  There is
        # nothing left to win there, and asking anyway is what produced a second
        # "rewrite" that only re-spelled the pragma of the first (observed on the
        # two-file end-to-end run).  Read from the source, so it holds with or
        # without runtime measurements; the impact model's covered spans say the
        # same thing only when hotspots were measured, and only from the NEXT queue
        # rebuild on.
        try:
            parallel_now = existing_parallel_spans(Path(args.source_file).read_text())
        except OSError:
            parallel_now = []
        enclosing_par = next(((a, b) for a, b in parallel_now
                              if a <= region.start_line and region.end_line <= b), None)
        if enclosing_par is not None:
            print(f"│  already inside the parallel construct at lines "
                  f"{enclosing_par[0]}–{enclosing_par[1]} — nothing left to win here")
            print(f"└─ COVERED\n")
            continue

        # ── Tier-1 ───────────────────────────────────────────────────────────
        failure_reason = "DiscoPoP found no applicable parallelism pattern for this region"
        if candidate.tier == 1 and candidate.pattern and candidate.pattern.get("applicable_pattern"):
            # PHASE A leaves this alone.  DiscoPoP can already parallelize it,
            # so there is nothing to restructure — and inserting its pragma now
            # is exactly what used to invalidate the profile every later
            # decision depends on.  Phase B collects it from the final profile
            # and applies it there, once, with nothing left to shift underneath.
            requeue = None
            if (getattr(args, "requeue_rejected", False) and tier2_allowed and not args.dry_run
                    and args.budget > 0 and reference_output is not None):
                # v3.1, the re-queue: is DiscoPoP's pattern here real?  Its pragma through the
                # safety gate now (cached for Phase B); if no pattern it offers passes, the region
                # would stay sequential with nobody told why — so the model gets it instead.
                def _t1_safe(t1_diff: str) -> "tuple[bool, str, str]":
                    res_t, _ct, _bt = _validate_cached(
                        gate_cache, t1_diff, args, reference_output, binary_args, reference_time,
                        reference_outputs=reference_outputs, mode="safety",
                        dep_region=(region.file_id, region.start_line, region.end_line))
                    _record_candidate(output_dir, {
                        "phase": "A-tier1", "region_id": rid, "depth": depth,
                        "passed": res_t.passed, "stage": res_t.stage,
                        "diagnostic": (res_t.diagnostic or "")[:2000],
                    }, t1_diff, args.dry_run)
                    return res_t.passed, res_t.stage or "", (res_t.diagnostic or "")
                safe_t1, t1_stage, t1_diag = tier1_verdict(candidate, dp_dir, args.source_file, _t1_safe)
                if not safe_t1:
                    requeue = (t1_stage, t1_diag)
            if requeue is None:
                print(f"│  [Phase-A] DiscoPoP already has a pattern here "
                      f"({candidate.pattern_type or 'pattern'}) — deferred to Phase B")
                print(f"└─ DEFERRED\n")
                deferred.append((rid, depth))
                continue
            print(f"│  [Phase-A] DiscoPoP reports this region parallel "
                  f"({candidate.pattern_type or 'pattern'}), but its pragma fails the gate at "
                  f"'{requeue[0]}' — requeued for the model")
            failure_reason = (
                f"DiscoPoP reports this region parallel (an applicable "
                f"{candidate.pattern_type or 'parallel'} pattern) and observed no dependence that "
                f"prevents it, but its own pragma for it fails the check at '{requeue[0]}': "
                + " ".join(requeue[1].split())[:700]
                + "  So a dependence DiscoPoP did not observe is carried here, and the region stays "
                  "sequential unless it is restructured.")

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

        # Decision D3: under --budget-policy share, attempts follow the region's share
        # of runtime relative to the largest share queued at this moment.
        top_share = max((c.runtime_fraction or 0.0) for _d, c in candidates) if candidates else 0.0
        budget = region_budget(args.budget_policy, args.budget, args.budget_min,
                               candidate.runtime_fraction, top_share)
        if args.budget_policy != "fixed":
            share_txt = (f"{candidate.runtime_fraction * 100:.1f}%"
                         if candidate.runtime_fraction is not None else "unmeasured")
            print(f"│  [Tier-2] Budget {budget} (policy {args.budget_policy}: share {share_txt}, "
                  f"largest queued {top_share * 100:.1f}%)")
        if args.budget_policy != "fixed" and budget <= 0:
            print(f"└─ SKIPPED (no model budget for this region)\n")
            skipped.append((rid, depth))
            continue
        tier2_messages: List[Any] | None = None

        # Any restructuring may need reverting — it is kept only if DiscoPoP can
        # parallelize it afterwards — so the profile is snapshotted and restored by
        # file-copy instead of a full re-profile.  The snapshot is taken LAZILY, the
        # first time a rewrite has passed the gate and is about to touch the file:
        # nothing before that point writes to the profile, and most attempts never
        # get that far.  It used to be taken before the first model call, for every
        # region — a copy of all of .discopop, 7.1 GB on LULESH, usually for nothing.
        # The pre-patch source is identical across retries (revert restores it), so
        # one snapshot serves every attempt for this candidate.
        dp_snapshot: Path | None = None
        pre_patch_src: str | None = None
        pre_patch_src = Path(args.source_file).resolve().read_text()

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
                diff, tier2_messages, reply_text = call_llm(
                    evidence, args.model,
                    api_key=args.api_key,
                    messages=tier2_messages,
                    provider=args.provider,
                    api_base=args.api_base,
                    edit_mode=args.edit_mode,
                    llm_pragmas=args.llm_pragmas,
                    verbose=args.verbose,
                    evidence_sections=args.evidence_sections,
                    llm_recon=(args.llm_recon
                               and args.llm_recon_mode == "folded"),
                    gate=GateFacts(
                        require_speedup=args.require_speedup,
                        n_inputs=1 + len(args.check_inputs or []),
                        numeric=args.noise_floor > 0.0,
                        stress=args.schedule_stress,
                        omit=tuple(getattr(args, "prompt_omit", ()) or ()),
                        external_evidence=getattr(args, "external_evidence", "") or "",
                        protected=tuple(getattr(args, "protected_lines", ()) or ()),
                        protected_note=getattr(args, "protected_note", "") or "",
                        judge_as_shipped=bool(getattr(args, "judge_as_shipped", False))),
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
                diff, tier2_messages, reply_text = None, tier2_messages, ""

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
            # Fix 97 (D39): the lines the file shares with the measurement harness, checked
            # before anything is built — a change there alters what is measured, not what is
            # computed, and its retry is not charged (see the refund below).
            harness_problem = check_protected(diff, args.source_file,
                                              getattr(args, "protected_lines", ()) or ())
            if harness_problem:
                result = ValidationResult(passed=False, stage="harness", diagnostic=harness_problem)
            if result is None and self_annotated:
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
                if ("pragma omp" in diff and args.require_speedup and not args.dry_run
                        and getattr(args, "judge_as_shipped", False)):
                    # D40.1: the gate's performance stage pairs against the run's noise
                    # threshold, which class R's floor never measured (DiscoPoP alone has no
                    # pragma for it) — measured here first, once.
                    speed_threshold(args, gate_cache, binary_args)
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
            _record_candidate(output_dir, {
                "phase": "A", "region_id": rid, "depth": depth,
                "attempt_budget_left": budget, "self_annotated": self_annotated,
                "pragmas": pragmas, "passed": result.passed, "stage": result.stage,
                "diagnostic": (result.diagnostic or "")[:2000],
                "measured_speedup": result.measured_speedup,
                "barrier_false_positive": barrier_fp,
            }, fix_hunk_headers(diff), args.dry_run)
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
                        region_fingerprint(c.source_file, c.region.start_line,
                                     c.region.end_line, c.region.name),
                    )
                    for d, c in candidates[i:]
                ]

                if dp_snapshot is None:
                    dp_snapshot = _snapshot_profile(dp_dir, output_dir)
                if not _apply_to_source(clean_diff, args.source_file, output_dir, "Tier-2"):
                    # The gate applied this very diff to a copy, so this is rare — the
                    # file changed underneath, or `patch` stopped half way.  It used to
                    # be ignored: the run re-profiled the UNPATCHED source and recorded
                    # the rewrite as accepted.  Put the file back exactly, keep nothing.
                    if pre_patch_src is not None:
                        src_abs.write_text(pre_patch_src)
                    patch_file.unlink(missing_ok=True)
                    print(f"│  [Tier-2] the validated rewrite could not be written to "
                          f"{src_abs.name} — source restored, region left unchanged")
                    print(f"└─ SKIPPED (patch did not apply to the real file)\n")
                    skipped.append((rid, depth))
                    break
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
                # Read ONCE.  The refresh, the hotspot remap and the dependence
                # review each used to re-read this file, so the three of them
                # could in principle disagree about what "the new source" is,
                # and the line map got rebuilt each time.
                post_patch_src = Path(args.source_file).read_text()
                remeasured = False
                refreshed_fast = False
                # Taken before anything moves the measurements onto the new file: a
                # reverted rewrite restores source and profile, and the runtimes have
                # to go back with them.  They did not, so after a revert every later
                # region was ranked with lines from a file that no longer existed.
                impact_before = impact.snapshot()
                if use_fast:
                    print(f"│  [Tier-2] Fast refresh (compile only, no instrumented run)...")
                    reprofile_ok, note = _reprofil_fast(
                        args.source_file, dp_dir, pre_patch_src or "",
                        post_patch_src, output_dir,
                    )
                    if reprofile_ok:
                        print(f"│           {note}")
                        refreshed_fast = True
                        if args.llm_recon:
                            # followup: a fresh turn on the SAME session, asked
                            # only now that the rewrite is accepted and the
                            # refreshed instruction mapping exists.  folded: the
                            # claims already rode out on the rewrite reply.
                            if args.llm_recon_mode == "followup":
                                from ..llm.dep_reconstruct import ask_after_gate
                                _lines = post_patch_src.splitlines()
                                _lm = fast_refresh.line_map(
                                    pre_patch_src or "", post_patch_src)
                                _new = {n for n in range(1, len(_lines) + 1)
                                        if n not in set(_lm.values())}
                                if _new:
                                    _lo = max(min(_new) - 6, 1)
                                    _hi = min(max(_new) + 6, len(_lines))
                                    _exc = "\n".join(
                                        f"{n:4d}  {_lines[n - 1]}"
                                        for n in range(_lo, _hi + 1))
                                    _loops = [
                                        str(n) for n in range(_lo, _hi + 1)
                                        if re.match(r"\s*(for|while)\s*\(",
                                                    _lines[n - 1])]
                                    try:
                                        reply_text = ask_after_gate(
                                            _exc, _loops, args.model,
                                            session_key=region_fingerprint(
                                                args.source_file,
                                                region.start_line,
                                                region.end_line, region.name),
                                            messages=tier2_messages,
                                            api_key=args.api_key,
                                            provider=args.provider,
                                            api_base=args.api_base)
                                    except Exception as e:      # never fail the run
                                        print(f"│           reconstruction call "
                                              f"failed: {str(e)[:80]}")
                                        reply_text = ""

                        if args.llm_recon and reply_text:
                            # The claims rode out on the SAME call that produced
                            # this rewrite — no extra request, and the model had
                            # the code in front of it.  They are applied only
                            # HERE, after the refresh has been accepted: a
                            # rewrite that gets reverted takes its claims with
                            # it, so nothing is reconstructed for code that
                            # never lands.
                            from ..llm.dep_reconstruct import reconstruct
                            lmap2 = fast_refresh.line_map(
                                pre_patch_src or "", post_patch_src)
                            nl2 = len(post_patch_src.splitlines())
                            rewritten2 = {n for n in range(1, nl2 + 1)
                                          if n not in set(lmap2.values())}
                            prof2 = (dp_dir / "profiler").resolve()
                            rep = reconstruct(
                                prof2, "", [], rewritten2, args.model,
                                reply=reply_text,
                                audit_path=output_dir / "llm_recon.json",
                                source_file=args.source_file,
                                source_lines=post_patch_src.splitlines())
                            if rep.rows:
                                r2 = run_explorer(dp_dir)
                                if r2.returncode != 0:
                                    print(f"│           reconstruction broke the "
                                          f"explorer — profile left as refreshed")
                            print(f"│           reconstruction: {rep.summary()}")
                            for _ln, _v, _t in rep.contradicted[:3]:
                                # Detected, never acted on: static analysis is
                                # over-approximate, so this is often the model
                                # being right.  It is logged because an omission
                                # is the one direction that can ship a race.
                                print(f"│           [warn] model called loop "
                                      f"{_ln} independent, but static analysis "
                                      f"records a {_t} on {_v} there")

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

                # What this refresh actually WAS — said in one parseable line and kept in
                # the record.  A fast refresh that turns out unusable falls back to a full
                # re-profile so that a correct rewrite is not lost to a hiccup in the cheap
                # path; but an experiment whose variable IS the refresh (E3) must be able
                # to see that a "fast" trial was not one.  0 of 108 archived fast refreshes
                # fell back, which is a rate to report, not a reason to stay blind to it.
                refresh_kind = ("failed" if not reprofile_ok else
                                "fast" if refreshed_fast else
                                "fallback" if use_fast else "full")
                print(f"│  [refresh] kind={refresh_kind}")

                # After EVERY successful refresh (D29) — the full re-profile, the fallback,
                # and the fast refresh too.  The fast refresh exists to skip the
                # INSTRUMENTED run; this is one native-speed run, and without it the fast
                # arm alone could not rank the regions a rewrite created, so E3's arms
                # would have differed in the refresh AND in whether Phase B sees the
                # exposed loops at all (Fixes 86, 87).
                if should_remeasure_runtimes(
                        reprofile_ok, args.hotspots, impact.available):
                    ok_hs, hs_note = _measure_hotspots(args, dp_dir, force=True)
                    fresh = load_hotspots(dp_dir, threads=impact.threads) \
                        if ok_hs else None
                    if fresh is not None and fresh.available:
                        impact.adopt(fresh)
                        remeasured = True
                        print(f"│  [Tier-2] Re-measured runtimes: "
                              f"{len(impact.by_line)} region(s), "
                              f"{impact.total_runtime*1e3:.1f} ms total")
                    else:
                        # Said as it is: with a share floor set an unmeasured region is
                        # not ranked on the proxy, it is not queued at all.
                        print(f"│  [Tier-2] could not re-measure runtimes ({hs_note[:60]}) — "
                              f"regions this rewrite created have no measurement"
                              + (" and, with --min-runtime-share set, will not be queued"
                                 if args.min_runtime_share else ""))

                if reprofile_ok and impact.available:
                    # Runtimes and covered spans are keyed by LINE, so a rewrite that
                    # shifts lines does not merely make them stale — it makes them
                    # point at whatever now sits at that number.  They are translated
                    # the way the dependences are, and what cannot be is dropped.
                    # This used to happen on the fast-refresh path ONLY: after a full
                    # re-profile (the --no-fast-refresh arms, and the fallback when a
                    # refresh is unusable) every region below the rewrite inherited
                    # the runtime of whatever used to sit at its line number.  Fresh
                    # measurements are already in new coordinates — then only the
                    # covered spans move.
                    lost = impact.remap_lines(
                        region.file_id,
                        fast_refresh.line_map(pre_patch_src or "", post_patch_src),
                        measurements=not remeasured)
                    if lost:
                        print(f"│           {lost} runtime measurement(s) dropped — "
                              f"their lines were rewritten")

                now_parallel = covered_spans_after(region.start_line, region.end_line,
                                                   pre_patch_src or "", post_patch_src,
                                                   clean_diff, self_annotated)
                if reprofile_ok and impact.available and now_parallel:
                    # Marked BEFORE the queue is rebuilt below — it used to come
                    # after, so the regions nested in the rewrite just kept were
                    # rebuilt as survivors and attempted anyway.  A revert restores
                    # `impact`, this included.
                    # Each construct is charged its measured share; one whose lines
                    # were rewritten has lost its measurement, and such constructs
                    # split what is left of the region's share between them — so the
                    # region reads as finished unless a measurement says otherwise.
                    shares = {sp: impact.fraction(region.file_id, sp[0], sp[1])
                              for sp in now_parallel}
                    unknown = [sp for sp, v in shares.items() if v is None]
                    residual = max((candidate.runtime_fraction or 0.0)
                                   - sum(v for v in shares.values() if v is not None), 0.0)
                    for sp in now_parallel:
                        known = shares[sp]
                        impact.mark_covered(region.file_id, sp[0], sp[1],
                                            known if known is not None
                                            else residual / max(len(unknown), 1))

                # rebuilt / discovered are computed read-only first; the queue and
                # all_seen_prints are only mutated once we decide to COMMIT.
                rebuilt: List[Any] = []
                discovered: List[Any] = []   # (depth+1, candidate, fingerprint)
                fresh_all: List[Any] = []
                if reprofile_ok:
                    fresh_all = _candidates(dp_dir)
                    fresh_by_print: Dict[Any, List[Any]] = defaultdict(list)
                    for nc in fresh_all:
                        fp = region_fingerprint(nc.source_file, nc.region.start_line,
                                          nc.region.end_line, nc.region.name)
                        fresh_by_print[fp].append(nc)

                    consumed: Set[Any] = set()
                    for old_depth, fp in old_prints:
                        for nc in fresh_by_print.get(fp, []):
                            if id(nc) not in consumed:
                                rebuilt.append((old_depth, nc))
                                consumed.add(id(nc))
                                break

                    for nc in fresh_all:
                        if id(nc) in consumed:
                            continue
                        fp = region_fingerprint(nc.source_file, nc.region.start_line,
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
                    # DiscoPoP's own verdict on the rewrite, before D40 judges it — E4's measure,
                    # which a D40 revert would otherwise hide (D40.1; parsed into the trial record).
                    print(f"│  [Phase-A] exposure verdict: {outcome.status}")
                    # ── D40 — judged as it will ship, while the model can still act ──────
                    # Phase B and Settle would judge DiscoPoP's pragmas for these loops, and
                    # the program with them against the original, after this region's attempts
                    # are over.  Asked here instead (verdicts.judge_as_shipped), with the file
                    # left pragma-free: the pragmas are staged as text and timed in a temporary
                    # directory, so no line number anything reads moves.  A failure takes the
                    # revert below — source, profile snapshot, runtimes and covered spans restored;
                    # the queue and the change log are only touched at COMMIT.  D40.1: at every
                    # depth, but when a deeper level follows only the SAFETY half — an exposed loop
                    # is never restructured again, so its pragma's safety cannot change, while its
                    # speed may still (a later rewrite of another region) and waits for the last level.
                    if (outcome.status == "exposed" and args.require_speedup
                            and getattr(args, "judge_as_shipped", False) and pre_patch_src is not None
                            and not args.dry_run):
                        print(f"│  [Phase-A] D40 — judging it as it will ship: DiscoPoP's pragmas for "
                              f"the exposed loops through the safety gate"
                              + (f"; depth {depth + 1} follows, so the speed half waits for the last level"
                                 if deeper_coming else
                                 ", then the program with them against the program before the rewrite (paired)"))
                        d40_started = time.monotonic()

                        def _safe(d40_diff: str, c: Any) -> "tuple[bool, str]":
                            res_s, _cs, _bs = _validate_cached(
                                gate_cache, d40_diff, args, reference_output, binary_args,
                                reference_time, reference_outputs=reference_outputs, mode="safety",
                                dep_region=((c.region.file_id, c.region.start_line, c.region.end_line)
                                            if c is not None else None))
                            where = (f"pragma for lines {c.region.start_line}–{c.region.end_line}"
                                     if c is not None else "the pragmas together")
                            _record_candidate(output_dir, {
                                "phase": "A-D40", "region_id": rid, "depth": depth,
                                "exposed_region": c.region.region_id if c is not None else "set",
                                "passed": res_s.passed, "stage": res_s.stage,
                                "diagnostic": (res_s.diagnostic or "")[:2000],
                            }, d40_diff, args.dry_run)
                            if res_s.passed:
                                print(f"│  [Phase-A] D40: {where} passes the safety gate")
                                return True, ""
                            print(f"│  [Phase-A] D40: {where} fails at '{res_s.stage}'")
                            return False, f"{res_s.stage}: {res_s.diagnostic or ''}"[:1500]

                        def _time(before_text: str, after_text: str) -> "tuple[bool, float, str]":
                            return measure_marginal(before_text, after_text, args.source_file,
                                                    binary_args,
                                                    extra_flags=list(args.timing_cflags) or None)

                        outcome = judge_as_shipped(
                            exposed_in(fresh_all, _touched_span(clean_diff), args.source_file),
                            pre_patch_src, dp_dir, args.source_file,
                            threshold=(0.0 if deeper_coming else speed_threshold(args, gate_cache, binary_args)),
                            validate=_safe, measure=None if deeper_coming else _time)
                        ratio_txt = f" {outcome.speedup:.2f}×" if outcome.speedup is not None else ""
                        print(f"│  [Phase-A] D40 verdict: {outcome.status}{ratio_txt}"
                              + (" — Phase B and Settle decide, as before" if outcome.status == "exposed"
                                 else " — its pragmas are safe; speed is judged at the last level"
                                 if outcome.status == "safe_deferred" else ""))
                        # D40's own cost, apart from the rest of the agent's time (E5; D40.1).
                        print(f"│  [Phase-A] D40 time: {time.monotonic() - d40_started:.1f} s")
                        if outcome.status == "ok" and outcome.judged_spans:
                            # D41: Phase B applies exactly this set when nothing changed since.
                            gate_cache.setdefault(D40_SETS_KEY, []).append({
                                "region": rid, "on": outcome.judged_on, "spans": outcome.judged_spans,
                                "staged": outcome.judged_text, "ratio": outcome.speedup})

                if outcome.status not in ("ok", "exposed", "safe_deferred", "self_annotated"):
                    # REVERT — the restructuring did not achieve its purpose.
                    # Restore source + the pre-patch profile from the snapshot
                    # (file copy) instead of re-profiling — far cheaper.
                    if pre_patch_src is not None:
                        src_abs.write_text(pre_patch_src)
                    if dp_snapshot is not None:
                        _restore_profile(dp_snapshot, dp_dir, output_dir)
                    impact.restore(impact_before)
                    patch_file.unlink(missing_ok=True)
                    msg = _rewrite_feedback(
                        outcome, dp_dir, region.file_id, _touched_span(clean_diff),
                        deps_shown=(args.evidence_sections is None
                                    or "deps" in args.evidence_sections),
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

                # ── Fix 85: who writes the better pragma here? ───────────────
                # The model may have annotated a loop DiscoPoP had already claimed
                # (it reaches those loops through an enclosing region, even though
                # the loops themselves were deferred).  Phase B will then find
                # nothing to annotate and DiscoPoP's pragma is never measured.
                # Build it, gate it, time the two against each other, keep the
                # faster — arbitration needs a measurement, so it runs only where
                # the run already measures.
                arb_records: List[Dict[str, Any]] = []
                if (self_annotated and args.require_speedup
                        and getattr(args, "pragma_arbitration", True)
                        and getattr(evidence, "inner_patterns", None)
                        and pre_patch_src is not None):
                    timing_flags = list(getattr(args, "timing_cflags", ()) or ()) or None

                    def _gate_alt(alt_text: str) -> "tuple[bool, str]":
                        alt_diff = make_diff(src_abs.read_text(), alt_text, args.source_file)
                        if not alt_diff.strip():
                            return False, "no change"
                        res_alt, _c, _b = _validate_cached(
                            gate_cache, alt_diff, args, reference_output, binary_args,
                            reference_time, reference_outputs=reference_outputs,
                            mode="safety",
                            dep_region=(region.file_id, region.start_line, region.end_line),
                        )
                        return res_alt.passed, (res_alt.diagnostic or res_alt.stage or "")

                    def _time_pair(before_text: str, after_text: str) -> "tuple[bool, float, str]":
                        return measure_marginal(before_text, after_text, args.source_file,
                                                binary_args, extra_flags=timing_flags)

                    kept_text, arb_records = arbitrate_pragmas(
                        src_abs.read_text(), pre_patch_src, evidence.inner_patterns,
                        args.source_file, _gate_alt, _time_pair,
                        min_ratio=args.min_measured_speedup,
                    )
                    if arb_records and kept_text != src_abs.read_text():
                        src_abs.write_text(kept_text)
                        clean_diff = fix_hunk_headers(
                            make_diff(pre_patch_src, kept_text, args.source_file))
                        pragmas = _added_pragmas(clean_diff)
                    if arb_records:
                        record["pragma_arbitration"] = arb_records

                # ── COMMIT ────────────────────────────────────────────────────
                # Without a re-profile nothing describes the file as it now stands:
                # the queued regions' line numbers and evidence belong to the old
                # text.  They are not attempted — and that is SAID, and counted.
                if reprofile_ok:
                    # What the profile on disk now IS: carried-forward data after a
                    # fast refresh, measured data after a full re-profile.  Decided
                    # here, at commit — it used to be set as soon as a refresh ran,
                    # so a rewrite that was then reverted (its snapshot restored)
                    # still cost the run a full re-profile before Phase B, and a full
                    # re-profile never cleared it.
                    profile_is_fast = refreshed_fast
                unreachable = [] if reprofile_ok else list(candidates[i:])
                del candidates[i:]
                if unreachable:
                    print(f"│  [Tier-2] {len(unreachable)} queued region(s) will NOT be "
                          f"attempted: no profile describes the rewritten file")
                    for d_left, c_left in unreachable:
                        skipped.append((c_left.region.region_id, d_left))
                candidates.extend(rebuilt)
                candidates.extend((d, nc) for d, nc, _ in discovered)
                for _d, _nc, fp in discovered:
                    all_seen_prints.add(fp)
                if reprofile_ok:
                    print(f"│  [Tier-2] {len(rebuilt)} survivor(s) rebuilt, "
                          f"{len(discovered)} new at depth {depth + 1}")
                    record["reprofiled"] = True
                record["exposed_pattern"] = outcome.pattern_label
                record["refresh"] = refresh_kind
                if impact.available:
                    if result.measured_speedup:
                        impact.observe_speedup(result.measured_speedup)
                if self_annotated:
                    record["pragmas"] = net_new_pragmas(clean_diff)
                    record["pragma_text"] = pragmas
                    record["self_annotated"] = True
                change_log.append({
                    "kind": "rewrite", "region_id": rid, "diff": clean_diff,
                    "file": str(Path(args.source_file).resolve()),
                    "exposed": outcome.exposed_prints,
                    "self_annotated": self_annotated,
                    "pragmas": net_new_pragmas(clean_diff),
                })
                if self_annotated:
                    print(f"│  [Tier-2] Kept on its own pragmas: {len(pragmas)} "
                          f"annotated loop(s), gate passed end to end")
                else:
                    print(f"│  [Tier-2] DiscoPoP now finds: {outcome.pattern_label}")
                if exposed_speedup is not None:
                    record["exposed_speedup"] = exposed_speedup
                    print(f"│  [Tier-2] Restructuring pays off "
                          f"({'measured' if self_annotated else 'with its pragmas, against the program before it'} "
                          f"{exposed_speedup:.2f}×)")
                elif outcome.status in ("exposed", "safe_deferred"):
                    # An exposed loop is Tier 1 from here on and is never restructured again, so
                    # "deferred to depth N+1" was wrong at every depth: its pragma is Phase B's
                    # (D40.1).  What a deeper level may still do is restructure OTHER regions.
                    print(f"│  [Tier-2] DiscoPoP's pragma for it is applied and judged in Phase B"
                          + (f"; depth {depth + 1} may still restructure other regions" if deeper_coming else ""))

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
                    "schedules": "The parallel build does not give ONE answer: its output "
                            "changed with the thread count or the schedule. Iterations of a "
                            "loop you marked parallel still depend on the order they run in — "
                            "a dependence the sanitizer did not flag (an order-dependent update, "
                            "a value one iteration leaves for the next), or a clause that hands "
                            "threads the wrong starting value.",
                    "dependences": "The pragma sits on a loop for which DiscoPoP OBSERVED a "
                            "loop-carried dependence while profiling this exact code, and the "
                            "code of that loop is unchanged. Annotating it cannot be right: "
                            "remove that dependence by restructuring, or put the pragma on a "
                            "loop that does not carry it.",
                    "harness": "The change touched lines that belong to the program's "
                            "measurement (listed in the task). They decide what is measured, not "
                            "what is computed, so they must stay exactly as they are and where "
                            "they are; nothing was built or run.",
                }
                guidance = _STAGE_GUIDANCE.get(result.stage, "")
                refunded = ""
                if result.stage in ("apply", "compile", "openmp_compile", "harness") and build_retries > 0:
                    build_retries -= 1
                    budget += 1     # a build error — or a touched harness line — must not cost a real attempt
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
                # The instruction has to fit the stage.  One text used to serve every
                # non-build failure: it asked "which of (a) or (b) this was" — options
                # only the correctness guidance defines — and told the model not to
                # resubmit a variation right after the clause guidance had said to
                # keep the strategy and fix only the clause.
                if result.stage in ("apply", "compile", "openmp_compile"):
                    retry_instr = (
                        "Keep your transformation approach and fix ONLY the reported "
                        "error — do not change strategy over a build problem."
                    )
                elif result.stage == "harness":
                    retry_instr = (
                        "Your parallelization is not what failed. Make the same change again, "
                        "leaving the measurement lines exactly as they were."
                    )
                elif result.stage == "clause":
                    retry_instr = (
                        "Keep your restructuring and the loop you chose to parallelize; "
                        "change ONLY the clause named above."
                    )
                elif result.stage == "correctness":
                    retry_instr = (
                        "Do not resubmit a variation of the same code. Say in one line "
                        "which of (a) or (b) this was and what you are changing because "
                        "of it — then make sure the code you write actually differs in "
                        "that way. Stating the right bound and then writing the old one "
                        "is the most common way this retry fails."
                    )
                elif result.stage == "performance":
                    retry_instr = (
                        "Keep what removed the dependence. Give each parallel region more "
                        "work — move the pragma to an enclosing loop, or merge regions — "
                        "and do not fall back to the sequential code."
                    )
                else:
                    retry_instr = (
                        "Do not resubmit a variation of the same code. Say in one line "
                        "which iterations still touch the same location, or depend on "
                        "each other's order, and what you are changing because of it — "
                        "then make sure the code you write actually differs in that way."
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
