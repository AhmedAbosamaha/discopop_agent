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
from typing import Any, Dict, List

from ..args import AgentArguments
from ..gate import _validate_cached, measure_marginal, noise_floor
from ..plan import build_candidates, region_fingerprint
from ..plan import impact as impact_mod
from ..pragmas import (_already_annotated, _read_tier1_patch,
                       _repair_pragma_clauses, check_pragma_clauses,
                       derive_pragma_patch)
from ..sources import _apply_in_memory, _apply_to_source
from .report import _write_record
from .verdicts import _MARGINAL_NOISE


def _phase_b(
    args: AgentArguments, dp_dir: Path, output_dir: Path,
    reference_output: "str | None", reference_outputs: "list | None",
    binary_args: "list | None", reference_time: "float | None",
    gate_cache: dict, change_log: list,
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
    kept: list = []
    fresh = build_candidates(dp_dir, args.source_file, args.lambda_penalty,
                             args.min_workload, impact=impact, min_impact=args.min_impact)
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
            Path(args.source_file).read_text(), args.source_file, binary_args
        )
        if ok_n:
            threshold = min(floor - 0.01, 0.99)
            print(f"  Timing noise floor on this machine: {floor:.3f} "
                  f"→ keep anything at or above {threshold:.3f}\n")
        else:
            print(f"  [warn] could not calibrate timing noise ({ndiag[:60]}); "
                  f"falling back to {threshold:.2f}\n")

    for cand in todo:
        rid = cand.region.region_id
        pid = cand.pattern.get("pattern_id", "?") if cand.pattern else "?"
        pragma = (cand.pattern or {}).get("pragma", "")
        lines = f"{cand.region.start_line}–{cand.region.end_line}"
        print(f"┌─ pattern #{pid}  {cand.pattern_type or 'pattern'} @ lines {lines}"
              f"  (W={cand.workload_estimate:.0f})")
        print(f"│  {pragma}")

        if cand.workload_estimate < args.min_workload:
            print(f"│  workload below --min-workload → not worth a thread")
            print(f"└─ SKIPPED\n")
            continue

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
            continue

        if _already_annotated(diff, args.source_file):
            print(f"│  this loop is already annotated in the source")
            print(f"└─ SKIPPED (nothing to add)\n")
            continue

        # 1. static — the only check that sees a clause handing back a value it
        #    cannot hand back.
        problem = check_pragma_clauses(diff, args.source_file)
        if problem:
            print(f"│  clause check: {problem}")
            print(f"└─ DROPPED (bad data-sharing clause)\n")
            continue

        if args.dry_run:
            print(f"└─ DRY RUN — not applied\n")
            continue

        # 2. does it work?  Everything except the timing.
        res, from_cache, barrier_fp = _validate_cached(
            gate_cache, diff, args, reference_output, binary_args,
            reference_time, reference_outputs=reference_outputs, mode="safety",
            dep_region=(cand.region.file_id, cand.region.start_line,
                        cand.region.end_line),
        )
        if barrier_fp:
            print(f"│  TSan OMP-barrier false positive — re-verified on output")
        if not res.passed:
            print(f"│  gate failed at '{res.stage}': "
                  f"{res.diagnostic[:150].replace(chr(10), ' ')}")
            print(f"└─ DROPPED\n")
            continue

        # 3. is it worth it?  Only when the user asked for that question.
        marginal = None
        if args.require_speedup:
            before = Path(args.source_file).read_text()
            after = _apply_in_memory(diff, args.source_file)
            if after is None:
                print(f"│  could not stage the patch for measurement")
                print(f"└─ DROPPED\n")
                continue
            ok_m, marginal, mdiag = measure_marginal(
                before, after, args.source_file, binary_args
            )
            if not ok_m:
                print(f"│  measurement failed: {mdiag[:120]}")
                print(f"└─ DROPPED\n")
                continue
            if marginal < threshold:
                print(f"│  marginal {marginal:.2f}× — costs more than it saves")
                print(f"└─ DROPPED (slower)\n")
                continue
            print(f"│  marginal {marginal:.2f}×")
            if impact is not None and impact.available:
                impact.observe_speedup(marginal)

        if impact is not None and impact.available:
            impact.mark_covered(cand.region.file_id, cand.region.start_line,
                                cand.region.end_line)
        fp_before = region_fingerprint(args.source_file, cand.region.start_line,
                                       cand.region.end_line, cand.region.name)
        if not _apply_to_source(diff, args.source_file, output_dir, "Phase-B"):
            print(f"└─ DROPPED (patch would not apply)\n")
            continue

        record = {
            "region_id": rid,
            "region_type": cand.region.region_type,
            "phase": "B",
            "pattern_id": pid,
            "pragma": pragma,
            "lines": lines,
            "marginal_speedup": marginal,
            "applied_to_source": True,
            # What the gate actually leaned on: "exact" means byte-identical
            # output, "numeric" means the values moved and were judged against
            # the measured noise floor.  `schedules` lists the thread/schedule
            # configurations the race check covered.
            "evidence": dict(res.evidence),
        }
        # Identity of the region this pragma landed on, taken BEFORE the patch
        # went in, so it matches what Phase A recorded as exposed.
        change_log.append({
            "kind": "pragma", "region_id": rid, "diff": diff,
            "fingerprint": fp_before,
        })
        kept.append(record)
        _write_record(output_dir, record, args.dry_run)
        print(f"└─ APPLIED\n")
    return kept
