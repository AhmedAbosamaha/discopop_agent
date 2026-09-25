"""
Phase B — annotate, once, from the final profile
--------------------------------------------------
Phase A leaves the source pragma-free, so the profile in .discopop describes
exactly the code being annotated here.  Interleaving annotation with
restructuring is what used to leave every queued patch racing a file that had
already shifted under it.

Each patch is RE-DERIVED against the current file rather than replayed from
DiscoPoP's stored diff, because applying one pragma moves every line below it.
Order is by predicted time saved (or by workload without measurements), so the
pragma most likely to matter is measured against the cleanest baseline.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .. import project as project_mod
from ..args import AgentArguments
from ..gate import _validate_cached, measure_marginal, noise_floor
from ..llm import make_diff
from ..plan import build_candidates, region_fingerprint
from ..plan import impact as impact_mod
from ..pragmas import (_already_annotated, _read_tier1_patch,
                       _repair_pragma_clauses, check_pragma_clauses,
                       derive_pragma_patch, existing_parallel_spans)
from ..sources import _apply_in_memory, _apply_to_source
from ..types import HotspotCandidate
from .report import _record_candidate, _write_record
from .verdicts import _MARGINAL_NOISE
# The key under which Phase B leaves its measured keep-threshold in the gate cache for Settle.
# Every other key of that cache is a patch digest, so it cannot collide.  Defined in verdicts.py
# since D40, whose Phase A check reads the same threshold; re-exported here for its importers.
from .verdicts import SPEED_THRESHOLD_KEY as SPEED_THRESHOLD_KEY


def _phase_b(
    args: AgentArguments, dp_dir: Path, output_dir: Path,
    reference_output: "str | None", reference_outputs: "List[Tuple[List[str], str]] | None",
    binary_args: "List[str] | None", reference_time: "float | None",
    gate_cache: Dict[str, Any], change_log: List[Any],
    impact: "impact_mod.ImpactModel | None" = None,
) -> List[Dict[str, Any]]:
    """Annotate: apply every DiscoPoP pragma that survives validation.

    Runs ONCE, after all restructuring, and never re-profiles.  That is the
    whole point: the source is pragma-free on entry, so the profile in dp_dir
    describes exactly the code being annotated.  Interleaving this with
    restructuring is what used to leave every queued patch racing a file that
    had already shifted under it.

    Order is by workload, largest first, so the pragma most likely to matter is
    measured against the cleanest baseline.  Each patch is re-derived against
    the CURRENT file rather than replayed from a stored diff, so applying one
    pragma cannot invalidate the next.
    """
    kept: List[Any] = []
    fresh = build_candidates(dp_dir, args.source_file, args.lambda_penalty,
                             args.min_workload, impact=impact, min_impact=args.min_impact,
                             min_runtime_share=args.min_runtime_share,
                             exclude_functions=args.exclude_functions)
    todo = [c for c in fresh
            if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")]
    if impact is not None and impact.available:
        # Annotate the pragma that saves the most time first, so the biggest win
        # is measured against the cleanest baseline.
        todo.sort(key=lambda c: (-(c.impact_seconds or 0.0),
                                 -(c.region.end_line - c.region.start_line)))
    else:
        todo.sort(key=lambda c: c.workload_estimate, reverse=True)

    print(f"\n{'='*60}")
    print(f"  PHASE B — annotate  ({len(todo)} candidate pragma(s))")
    print(f"{'='*60}\n")
    if not todo:
        print("  DiscoPoP proposes no applicable pattern for the final source.\n")
        return kept

    # What counts as "not slower" is whatever this machine's jitter can already
    # produce for an unchanged file.  One compile, then alternating runs.
    threshold = _MARGINAL_NOISE
    if args.require_speedup and not args.dry_run:
        ok_n, floor, ndiag = noise_floor(
            Path(args.source_file).read_text(), args.source_file, binary_args,
            extra_flags=list(args.timing_cflags) or None,
        )
        if ok_n:
            threshold = min(floor - 0.01, 0.99)
            print(f"  Timing noise floor on this machine: {floor:.3f} "
                  f"→ keep anything at or above {threshold:.3f}\n")
        else:
            print(f"  [warn] could not calibrate timing noise ({ndiag[:60]}); "
                  f"falling back to {threshold:.2f}\n")
    # Settle re-asks the speed question about the finished file with the SAME paired
    # measurement and the same threshold (Fix 89); this is how it learns the threshold.
    gate_cache[SPEED_THRESHOLD_KEY] = threshold

    # Spans that already run in parallel: loops annotated by THIS pass, and loops
    # that were parallel on entry — a Phase A rewrite the model annotated itself.
    # `todo` is built once, before the loop, so impact.mark_covered() cannot remove
    # a nested candidate from it, and _already_annotated() only matches the SAME
    # loop header — neither catches an inner loop whose enclosing loop is parallel.
    # The entry scan matters when there are no runtime measurements
    # (--no-hotspots): "covered" is then unknown, and DiscoPoP's pragma for an
    # inner loop went INSIDE the model's parallel loop — a nested region that the
    # safety gate passes and, with the speed check off, nothing removes.
    applied_spans: List[Tuple[Optional[int], int, int]] = []
    if args.project is None:
        applied_spans = [(None, a, b) for a, b in
                         existing_parallel_spans(Path(args.source_file).read_text())]
    else:
        # One scan per project file, each span tied to that file's DiscoPoP id.
        for fid, path in project_mod.load_file_mapping(dp_dir).items():
            if args.project.contains(path) and path.is_file():
                applied_spans += [(fid, a, b) for a, b in
                                  existing_parallel_spans(path.read_text())]
    if applied_spans:
        print(f"  {len(applied_spans)} loop(s) are already parallel in the source; "
              f"nothing is nested inside them.\n")

    # Pragmas that passed every safety stage but measured slower than the noise
    # threshold ON THEIR OWN — judged together after the pass (D33).
    deferred_safe: List[Dict[str, Any]] = []

    def annotate(cand: HotspotCandidate, ptype: Optional[str],
                 pattern: Optional[Dict[str, Any]]) -> str:
        """Try ONE of DiscoPoP's patterns for this loop.

        Returns "kept", "skipped" (nothing about this pattern — an alternative would
        fare the same), "deferred" (safe but slower alone: judged jointly afterwards,
        D33) or "dropped" (this pattern's pragma failed: try the next)."""
        project_mod.work_on(args, cand.source_file)
        rid = cand.region.region_id
        pid = pattern.get("pattern_id", "?") if pattern else "?"
        pragma = (pattern or {}).get("pragma", "")
        lines = f"{cand.region.start_line}–{cand.region.end_line}"
        print(f"┌─ pattern #{pid}  {ptype or 'pattern'} @ lines {lines}"
              f"  (W={cand.workload_estimate:.0f})")
        print(f"│  {pragma}")

        if cand.workload_estimate < args.min_workload:
            print(f"│  workload below --min-workload → not worth a thread")
            print(f"└─ SKIPPED\n")
            return "skipped"

        # Re-derive against the file as it stands: earlier pragmas in this same
        # phase have already moved every line below them.
        diff = _repair_pragma_clauses(
            derive_pragma_patch(
                _read_tier1_patch(dp_dir / "patch_generator" / str(pid)),
                args.source_file,
            ),
            args.source_file,
        )
        if not diff:
            print(f"│  no generated patch on disk")
            print(f"└─ SKIPPED\n")
            return "dropped"

        if _already_annotated(diff, args.source_file):
            print(f"│  this loop is already annotated in the source")
            print(f"└─ SKIPPED (nothing to add)\n")
            return "skipped"

        # Nested inside a loop that already runs in parallel.  Applying it
        # would put one worksharing construct inside another; with nesting off
        # (the OpenMP default) the inner team is a single thread, so it buys
        # nothing and costs the region's own overhead.
        enclosing = next(
            ((f, a, b) for f, a, b in applied_spans
             if (f is None or f == cand.region.file_id)
             and a <= cand.region.start_line and cand.region.end_line <= b),
            None,
        )
        if enclosing is not None:
            print(f"│  nested inside the already-parallelized region at lines "
                  f"{enclosing[1]}–{enclosing[2]}")
            print(f"└─ SKIPPED (enclosing loop is already parallel)\n")
            return "skipped"

        # 1. static — the only check that sees a clause handing back a value it
        #    cannot hand back.
        problem = check_pragma_clauses(diff, args.source_file)
        if problem:
            _record_candidate(output_dir, {
                "phase": "B", "region_id": cand.region.region_id, "passed": False,
                "stage": "clause", "diagnostic": problem[:2000], "pattern_type": ptype,
            }, diff, args.dry_run)
            print(f"│  clause check: {problem}")
            print(f"└─ DROPPED (bad data-sharing clause)\n")
            return "dropped"

        if args.dry_run:
            print(f"└─ DRY RUN — not applied\n")
            return "skipped"

        # 2. does it work?  Everything except the timing.
        res, from_cache, barrier_fp = _validate_cached(
            gate_cache, diff, args, reference_output, binary_args,
            reference_time, reference_outputs=reference_outputs, mode="safety",
            dep_region=(cand.region.file_id, cand.region.start_line,
                        cand.region.end_line),
        )
        _record_candidate(output_dir, {
            "phase": "B", "region_id": cand.region.region_id, "passed": res.passed,
            "stage": res.stage, "diagnostic": (res.diagnostic or "")[:2000],
            "from_cache": from_cache, "barrier_false_positive": barrier_fp,
            "pattern_type": ptype,
        }, diff, args.dry_run)
        if barrier_fp:
            print(f"│  TSan OMP-barrier false positive — re-verified on output")
        if not res.passed:
            print(f"│  gate failed at '{res.stage}': "
                  f"{res.diagnostic[:150].replace(chr(10), ' ')}")
            print(f"└─ DROPPED\n")
            return "dropped"

        # 3. is it worth it?  Only when the user asked for that question.
        marginal = None
        if args.require_speedup:
            before = Path(args.source_file).read_text()
            after = _apply_in_memory(diff, args.source_file)
            if after is None:
                print(f"│  could not stage the patch for measurement")
                print(f"└─ DROPPED\n")
                return "dropped"
            ok_m, marginal, mdiag = measure_marginal(
                before, after, args.source_file, binary_args,
                extra_flags=list(args.timing_cflags) or None,
            )
            if not ok_m:
                # A CRASH during the timing run is not a failure to measure — it is the
                # candidate failing at a size the correctness gate never tried. The gate runs
                # at the agent size; the timing runs at the kernel's measured size, which is
                # where a rewrite that puts an N x N array on the STACK finally overflows it
                # (polybench/floyd-warshall: fine at N=128, 8 MB and dead at N=1024). Saying
                # "measurement failed" hid that behind a timing word.
                crashed = "non-zero exit (-" in mdiag or "signal" in mdiag.lower()
                if crashed:
                    print(f"│  the program CRASHED at the timing size — the correctness gate "
                          f"runs at the agent size and never reached it")
                    print(f"│  {mdiag[:110]}")
                    print(f"└─ DROPPED (unsafe at size)\n")
                else:
                    print(f"│  measurement failed: {mdiag[:120]}")
                    print(f"└─ DROPPED\n")
                return "dropped"
            if marginal < threshold:
                # Safe, but slower ALONE.  Not dropped yet (D33): when a rewrite splits
                # a loop into two or three, each pragma alone can lose while all of them
                # together win — E1: 7 of the 18 trials this line used to end were 1.2-2.8x
                # the original with the set (e1b_marginal_replay).  Judged below, jointly.
                print(f"│  marginal {marginal:.2f}× alone — deferred: judged together with the "
                      f"other pragmas that do not pay alone (D33)")
                print(f"└─ DEFERRED (slower alone)\n")
                deferred_safe.append({"cand": cand, "ptype": ptype, "pid": pid, "pragma": pragma,
                                      "lines": lines, "res": res, "alone": marginal})
                return "deferred"
            print(f"│  marginal {marginal:.2f}×")
            if impact is not None and impact.available:
                impact.observe_speedup(marginal)

        fp_before = region_fingerprint(args.source_file, cand.region.start_line,
                                       cand.region.end_line, cand.region.name)
        if args.apply_patches and not _apply_to_source(diff, args.source_file,
                                                       output_dir, "Phase-B"):
            print(f"└─ DROPPED (patch would not apply)\n")
            return "dropped"
        # Only now is this loop spoken for.  Marking it before the patch had
        # actually gone in left a failed apply "covering" every loop inside it.
        if impact is not None and impact.available:
            impact.mark_covered(cand.region.file_id, cand.region.start_line,
                                cand.region.end_line)
        applied_spans.append((cand.region.file_id, cand.region.start_line,
                              cand.region.end_line))
        record = {
            "region_id": rid,
            "region_type": cand.region.region_type,
            "phase": "B",
            "pattern_id": pid,
            "pattern_type": ptype,
            "pragma": pragma,
            "lines": lines,
            "marginal_speedup": marginal,
            "applied_to_source": bool(args.apply_patches),
            # What the gate actually leaned on: "exact" means byte-identical
            # output, "numeric" means the values moved and were judged against
            # the measured noise floor.  `schedules` lists the thread/schedule
            # configurations the race check covered.
            "evidence": dict(res.evidence),
        }
        kept.append(record)
        if not args.apply_patches:
            # Recorded and validated, but deliberately not written: the patch
            # stays in patch_generator/ and accepted.json describes it.
            print(f"└─ VALIDATED, not written (--no-apply-patches)\n")
            return "kept"
        # Identity of the region this pragma landed on, taken BEFORE the patch
        # went in, so it matches what Phase A recorded as exposed.
        change_log.append({
            "kind": "pragma", "region_id": rid, "diff": diff,
            "fingerprint": fp_before,
            "file": str(Path(args.source_file).resolve()),
        })
        _write_record(output_dir, record, args.dry_run)
        print(f"└─ APPLIED\n")
        return "kept"

    for cand in todo:
        # DiscoPoP can report more than one applicable pattern for a loop (a Do-All
        # and a Reduction on the same line).  They differ in their clauses, so when
        # the first one's pragma does not survive, the next is a different question.
        options: List[Any] = [(cand.pattern_type, cand.pattern)] + list(cand.alternates)
        for n, (ptype, pattern) in enumerate(options):
            if annotate(cand, ptype, pattern) != "dropped":
                break
            if n + 1 < len(options):
                print(f"   DiscoPoP reports another pattern for this loop "
                      f"({options[n + 1][0]}) — trying it\n")
    if deferred_safe and args.require_speedup and not args.dry_run:
        kept += _judge_jointly(args, dp_dir, output_dir, deferred_safe, applied_spans, threshold,
                               reference_output, reference_outputs, binary_args, reference_time,
                               gate_cache, change_log, impact)
    return kept


def _judge_jointly(
    args: AgentArguments, dp_dir: Path, output_dir: Path, deferred: List[Dict[str, Any]],
    applied_spans: List[Tuple[Optional[int], int, int]], threshold: float,
    reference_output: "str | None", reference_outputs: "List[Tuple[List[str], str]] | None",
    binary_args: "List[str] | None", reference_time: "float | None",
    gate_cache: Dict[str, Any], change_log: List[Any],
    impact: "impact_mod.ImpactModel | None",
) -> List[Dict[str, Any]]:
    """D33 — the pragmas that were safe but did not pay ALONE, judged as a set.

    Phase B measures each pragma against the state before it, so a pragma that pays
    only together with another — the two or three loops a rewrite split one loop into —
    loses every single comparison and the set that wins is never built (E1: 7 of 18
    such trials, `e1b_marginal_replay`).  Here, per file: apply the deferred pragmas
    together (outermost first — one nested in another is left out, as in the pass
    above), re-check the SET for safety (TSan, schedules, output), time it against the
    state before it with the same paired measurement and threshold, and, if it pays,
    remove members one at a time while removing one does not make it slower (backward
    elimination: a member that adds nothing is not shipped).  What is kept lands as ONE
    change-log entry, so Settle keeps or drops the set as a unit.
    """
    kept: List[Dict[str, Any]] = []
    print(f"┌─ D33 — {len(deferred)} safe pragma(s) did not pay alone; measuring them together")
    by_file: Dict[str, List[Dict[str, Any]]] = {}
    for d in deferred:
        by_file.setdefault(d["cand"].source_file, []).append(d)
    for source_file, group in by_file.items():
        project_mod.work_on(args, source_file)
        path = Path(args.source_file)
        before = path.read_text()
        members: List[Dict[str, Any]] = []
        spans: List[Tuple[int, int]] = []
        for d in group:
            r = d["cand"].region
            if any((f is None or f == r.file_id) and a <= r.start_line and r.end_line <= b
                   for f, a, b in applied_spans) or \
               any(a <= r.start_line and r.end_line <= b for a, b in spans):
                continue                     # nested in a parallel loop: nothing to add
            members.append(d)
            spans.append((r.start_line, r.end_line))
        if len(members) < 2:
            print(f"│  {Path(source_file).name}: fewer than two to combine — dropped as measured alone")
            continue

        def build(subset: List[Dict[str, Any]]) -> "str | None":
            """The file with exactly these pragmas added, each re-derived against the
            text the previous ones left (they move every line below them)."""
            try:
                for d in subset:
                    diff = _repair_pragma_clauses(derive_pragma_patch(
                        _read_tier1_patch(dp_dir / "patch_generator" / str(d["pid"])),
                        args.source_file), args.source_file)
                    after = _apply_in_memory(diff, args.source_file) if diff else None
                    if after is None:
                        return None
                    path.write_text(after)
                return path.read_text()
            finally:
                path.write_text(before)      # the file itself only changes when the set is kept

        joint = build(members)
        if joint is None:
            print(f"│  {path.name}: the set could not be staged — dropped as measured alone")
            continue
        joint_diff = make_diff(before, joint, args.source_file)
        res, _cached, _fp = _validate_cached(
            gate_cache, joint_diff, args, reference_output, binary_args, reference_time,
            reference_outputs=reference_outputs, mode="safety")
        _record_candidate(output_dir, {
            "phase": "B", "region_id": "joint:" + ",".join(str(d["cand"].region.region_id) for d in members),
            "passed": res.passed, "stage": res.stage if not res.passed else "joint",
            "diagnostic": (res.diagnostic or "")[:2000], "pattern_type": "joint",
            "members": [str(d["cand"].region.region_id) for d in members],
        }, joint_diff, args.dry_run)
        if not res.passed:
            print(f"│  {path.name}: together they fail at '{res.stage}' — all dropped")
            continue
        ok_m, ratio, mdiag = measure_marginal(before, joint, args.source_file, binary_args,
                                              extra_flags=list(args.timing_cflags) or None)
        if not ok_m or ratio < threshold:
            why = f"{ratio:.2f}×" if ok_m else f"not measurable ({mdiag[:60]})"
            print(f"│  {path.name}: {len(members)} together {why} — still costs more than it saves; all dropped")
            continue
        print(f"│  {path.name}: {len(members)} together {ratio:.2f}× — the set pays")
        # Backward elimination: a member whose removal does not slow the set down is dead weight.
        for d in list(reversed(members)):
            if len(members) < 2:
                break
            rest = [m for m in members if m is not d]
            without = build(rest)
            if without is None:
                continue
            ok_r, r_rm, _ = measure_marginal(joint, without, args.source_file, binary_args,
                                             extra_flags=list(args.timing_cflags) or None)
            if ok_r and r_rm >= threshold:
                print(f"│    without {d['lines']}: {r_rm:.2f}× the set — adds nothing, left out")
                members, joint = rest, without
            else:
                print(f"│    without {d['lines']}: " + (f"{r_rm:.2f}× the set" if ok_r else "not measurable")
                      + " — needed")
        joint_diff = make_diff(before, joint, args.source_file)
        fps = [region_fingerprint(args.source_file, d["cand"].region.start_line,
                                  d["cand"].region.end_line, d["cand"].region.name) for d in members]
        if args.apply_patches and not _apply_to_source(joint_diff, args.source_file,
                                                       output_dir, "Phase-B"):
            print(f"│  {path.name}: the set would not apply — dropped")
            continue
        if impact is not None and impact.available:
            impact.observe_speedup(ratio)
        group_id = "joint:" + ",".join(str(d["cand"].region.region_id) for d in members)
        for d, fp in zip(members, fps):
            r = d["cand"].region
            if impact is not None and impact.available:
                impact.mark_covered(r.file_id, r.start_line, r.end_line)
            applied_spans.append((r.file_id, r.start_line, r.end_line))
            record = {"region_id": r.region_id, "region_type": r.region_type, "phase": "B",
                      "pattern_id": d["pid"], "pattern_type": d["ptype"], "pragma": d["pragma"],
                      "lines": d["lines"], "marginal_speedup": d["alone"], "joint_speedup": ratio,
                      "phase_b_mode": "joint", "joint_group": group_id,
                      "applied_to_source": bool(args.apply_patches), "evidence": dict(res.evidence)}
            kept.append(record)
            _write_record(output_dir, record, args.dry_run)
        if args.apply_patches:
            change_log.append({"kind": "pragma", "region_id": group_id, "diff": joint_diff,
                               "fingerprint": fps[0], "fingerprints": fps,
                               "region_ids": [d["cand"].region.region_id for d in members],
                               "file": str(Path(args.source_file).resolve())})
        print(f"│  {path.name}: {len(members)} pragma(s) APPLIED together")
    print(f"└─ D33 done\n")
    return kept
