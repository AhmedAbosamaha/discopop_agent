"""
The orchestrator — setup, then the three phases, then the summary
===================================================================
This module owns the SHAPE of a run and nothing else; every step it calls lives
in its own package.  What happens, in order:

  1. Capture a golden reference: the unmodified program's stdout, and its
     runtime.  Every later version has to reproduce that output exactly.
  2. Measure where the time goes (`plan/impact.py`, from DiscoPoP's own hotspot
     detection) so candidates can be ranked by the time parallelizing them would
     SAVE rather than by an instruction count.
  3. Establish the baseline to beat — counted honestly as patterns whose pragma
     passes the clause check AND compiles, not merely patterns DiscoPoP claims.
  4. PHASE A (`phases/phase_a.py`) — restructure, with the source kept
     pragma-free.  Regions DiscoPoP can already parallelize are DEFERRED here.
     NOT because a pragma corrupts the profile — the instrumented build carries
     no -fopenmp, so DiscoPoP reads pragmas as comments and re-analysing after
     one returns identical data.  What an insertion really breaks is LINE
     NUMBERS: `assemble()` takes a region's span from the profile and then reads
     the SOURCE at those numbers, so a pragma inserted above a queued region
     would show the next LLM call the wrong lines.
  5. PHASE B (`phases/phase_b.py`) — annotate, once, from the final profile.
     The structural reason this is a second pass: Phase A's queue GROWS while it
     runs (each kept rewrite appends newly discovered regions at depth+1), so
     the full set of annotatable regions — and therefore a global ordering by
     predicted time saved — is not knowable until Phase A has finished.
     Every patch is re-derived against the file as it currently stands, since
     each applied pragma shifts every line below it.
  6. SETTLE (`phases/settle.py`) — the only step that judges the FILE.  Drop
     rewrites no kept pragma justified, rebuild by re-applying the survivors
     onto the original, and re-gate the result; if it still fails, drop the
     newest pragma and try again, reverting the whole run if nothing survives.

Two invariants worth knowing before reading the code:

  * Nothing is trusted because an earlier stage approved it.  Every gate before
    SETTLE judged a candidate patch against a temp copy; the file that ends up
    on disk is a reconstruction, and it earns its own verdict.
  * Region identity is content-based (`plan/regions.py`), never the region id.
    DiscoPoP hands ids out from one global counter, so patching one function
    renumbers everything after it — and an id can be reassigned to a completely
    unrelated region.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from . import viz
from .args import AgentArguments
from .gate import (capture_reference, check_pragma_compiles,
                   numerical_noise_floor)
from .phases import (RunState, _phase_b, _print_banner, _print_candidates,
                     _settle, phase_a)
from .plan import build_candidates, region_fingerprint
from .plan import impact as impact_mod
from .pragmas import _read_tier1_patch, check_pragma_clauses, derive_pragma_patch
from .profiling import _measure_hotspots, _reprofil
from .types import HotspotCandidate

def run(args: AgentArguments) -> None:
    dp_dir = Path(args.discopop_dir)
    profiler_dir = dp_dir / "profiler"
    output_dir = Path(args.output_dir)
    # A dry run promises no file changes, so don't even create the output dir.
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    viz.enable(args.verbose)
    _print_banner(args)

    # Golden reference output: the unmodified program's stdout.  Every patched
    # version must reproduce it (semantic-equivalence gate).  None if the program
    # can't be built/run cleanly up front, in which case correctness is skipped.
    binary_args = args.reprofil_args or None
    reference_output, reference_time, reference_outputs = capture_reference(
        args.source_file, binary_args, extra_inputs=args.check_inputs or None
    )
    if reference_output is None and not args.allow_unverified:
        # Failing OPEN here is the worst available outcome: the run continues and
        # accepts patches whose output was never compared to anything, while the
        # summary reports them as accepted.  If the original program cannot be
        # built or run there is nothing to compare against, and the honest
        # response to that is to stop.
        print("  [FATAL] Could not build or run the ORIGINAL program, so there is no\n"
              "          reference output and the correctness gate cannot run.\n"
              "          Fix the program (or its --reprofil-args), or pass\n"
              "          --allow-unverified to accept patches that were never checked\n"
              "          for semantic equivalence.\n")
        sys.exit(1)
    if reference_output is None:
        print("  [warn] --allow-unverified: no reference output — the correctness gate\n"
              "         is OFF for this run. Nothing below is checked against the\n"
              "         original program's behaviour.\n")
    else:
        rt = f", {reference_time*1e3:.1f} ms baseline" if reference_time else ""
        n = len(reference_outputs or [])
        extra = f" on {n} inputs" if n > 1 else " on 1 input"
        print(f"  [ok] Captured reference output{extra} ({len(reference_output)} bytes{rt}) "
              f"for the correctness/performance gates.")
        if n == 1:
            print("  [note] one input only — a rewrite that is wrong for other sizes "
                  "would still pass. Add --check-input to widen the check.")
        print()

    # Numerical calibration, once per run.  The counterpart of the timing noise
    # floor: before disbelieving a rewrite whose digits moved, find out how far
    # this program's own digits already move between builds that mean the same
    # thing.  A program printing no floating point measures 0.0 and stays under
    # byte-exact comparison, which is where every integer-output case lands.
    if args.numeric_tolerance and reference_output is not None and not args.dry_run:
        nf = numerical_noise_floor(args.source_file, binary_args)
        args.noise_floor = nf.value
        if nf.value > 0.0:
            print(f"  [ok] Numerical noise floor {nf.value:.2e} of output scale "
                  f"({nf.diagnostic}).")
            print("  [note] values may move that far without failing the correctness "
                  "gate; labels, line structure and integers must still match exactly.")
        else:
            print(f"  [ok] Numerical noise floor 0 — {nf.diagnostic}; "
                  f"output is compared byte-for-byte.")
        print()

    # Gate results for this run, keyed by (patch, source text).
    # A pattern measured by the post-rewrite verification is normally measured
    # again by the Tier-1 pass that applies it, one queue position later; this
    # lets the second ask reuse the first answer.  Scoped to the run rather than
    # module-global so nothing leaks between runs.
    gate_cache: dict = {}

    # Set only when a kept rewrite could not be re-profiled (--llm-pragmas keeps
    # such a rewrite because the gate, not DiscoPoP, judged it).  Phase B has no
    # profile it can trust after that, so it does not run.
    profile_stale = False
    # True once a fast refresh has left carried-forward dependence data in the
    # profile.  Phase B annotates from measured data, so this is settled with one
    # full re-profile before it runs rather than being allowed to accumulate.
    profile_is_fast = False

    accepted: List[dict] = []
    # Regions DiscoPoP can already parallelize: Phase A skips them, Phase B
    # picks them up from the final profile.
    deferred: List[tuple] = []
    original_text = Path(args.source_file).read_text()
    # Ordered record of every change written to the source, so the end of the
    # run can rebuild from the original keeping only what earned its place.
    change_log: List[dict] = []
    # Each entry is (region_id, discovery_depth).  A region ID can appear more
    # than once (different content versions across re-profiles reuse IDs); the
    # summary de-duplicates and drops IDs that were ultimately accepted.
    skipped: List[tuple] = []

    # Tracks the CONTENT fingerprint of every region ever enqueued across all
    # re-profile cycles.  Region IDs drift after a patch (global counter), so
    # identity is keyed on source text instead — see region_fingerprint() in plan/regions.py.
    all_seen_prints: set = set()

    # Measure before ranking.  One extra instrumented run, once, and it is what
    # lets the queue be ordered by time saved instead of instruction count.
    impact = impact_mod.ImpactModel(threads=os.cpu_count() or 1)
    if not args.hotspots:
        hs_note = "disabled (--no-hotspots)"
    elif args.dry_run:
        # A dry run promises to change nothing, so it never RUNS the program —
        # but it will happily use a measurement that is already there, which is
        # what makes `--dry-run` useful for inspecting the queue order.
        hs_note = "not measured on a dry run; using whatever is already in .discopop"
    else:
        ok_hs, hs_note = _measure_hotspots(args, dp_dir)
        if not ok_hs:
            print(f"  [warn] hotspot detection unavailable: {hs_note}")
    if args.hotspots:
        impact = impact_mod.load_hotspots(dp_dir, threads=os.cpu_count() or 1)
    if impact.available:
        print(f"  Hotspots       : {hs_note} — {len(impact.by_line)} region(s) measured, "
              f"{impact.total_runtime*1e3:.1f} ms total, ranking by predicted time saved "
              f"at {impact.threads} threads\n")
    else:
        print(f"  Hotspots       : {hs_note} — falling back to the static workload proxy "
              f"for ranking\n")

    def _candidates(dd: Path) -> List[HotspotCandidate]:
        return build_candidates(dd, args.source_file, args.lambda_penalty,
                                args.min_workload, impact=impact,
                                min_impact=args.min_impact)

    initial = _candidates(dp_dir)
    if not initial:
        print("No hotspot regions found. Run discopop_explorer first.")
        return

    # candidates: list of (discovery_depth, HotspotCandidate)
    # depth=0 → initial profile; depth=N → discovered after N Tier-2 re-profiles
    # P0 — what DiscoPoP achieves unaided.  Counted to the SAME standard the
    # run's own output is held to: a pattern DiscoPoP merely claims is not a
    # working pragma.  On example4 the one "applicable" pattern is
    # `private(ok)` on the sortedness check, which compiles into a program that
    # reports success even with the sort deleted — so the honest baseline there
    # is 0, and counting it as 1 made every run look like a regression.
    claimed = [c for c in initial
               if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")]
    baseline_pragmas = 0
    for c in claimed:
        cpid = c.pattern.get("pattern_id", "?") if c.pattern else "?"
        d = derive_pragma_patch(
            _read_tier1_patch(dp_dir / "patch_generator" / str(cpid)),
            args.source_file,
        )
        if not d or check_pragma_clauses(d, args.source_file):
            continue
        ok_c, _diag = check_pragma_compiles(d, args.source_file)
        baseline_pragmas += 1 if ok_c else 0
    dropped_baseline = len(claimed) - baseline_pragmas
    print(f"  Baseline       : DiscoPoP proposes {len(claimed)} applicable "
          f"pattern(s) unaided; {baseline_pragmas} of them produce a usable pragma"
          + (f" ({dropped_baseline} rejected before it could run)"
             if dropped_baseline else ""))
    print(f"                   → the run beats DiscoPoP by ending with more than "
          f"{baseline_pragmas}\n")

    candidates: list = [(0, c) for c in initial]
    all_seen_prints.update(
        region_fingerprint(args.source_file, c.region.start_line, c.region.end_line, c.region.name)
        for c in initial
    )

    print("  Initial candidates")
    _print_candidates(candidates)

    print(f"{'='*60}")
    print(f"  PHASE A — restructure  (the source stays pragma-free)")
    print(f"{'='*60}\n")

    state = RunState(
        args=args, dp_dir=dp_dir, profiler_dir=profiler_dir, output_dir=output_dir,
        impact=impact, reference_output=reference_output,
        reference_outputs=reference_outputs, reference_time=reference_time,
        binary_args=binary_args, original_text=original_text,
        gate_cache=gate_cache, accepted=accepted, deferred=deferred,
        skipped=skipped, change_log=change_log, all_seen_prints=all_seen_prints,
        candidates=candidates,
    )
    phase_a(state)
    profile_is_fast, profile_stale = state.profile_is_fast, state.profile_stale

    # ── Phase B: annotate ────────────────────────────────────────────────────
    # Everything above only restructured code.  Now, once, from the profile the
    # last kept rewrite produced, apply every pragma that survives validation.
    if profile_is_fast and not profile_stale and not args.dry_run:
        print(f"\n  One full re-profile before Phase B — it annotates from measured "
              f"dependences, not carried-forward ones.")
        if not _reprofil(args.source_file, dp_dir, args.reprofil_args or None):
            print(f"  [warn] that re-profile failed; Phase B will be skipped.")
            profile_stale = True

    if profile_stale:
        print(f"\n{'='*60}")
        print(f"  PHASE B — skipped (no profile describes the current source)")
        print(f"{'='*60}\n")
        annotated: List[Dict[str, Any]] = []
    else:
        annotated = _phase_b(
            args, dp_dir, output_dir, reference_output, reference_outputs,
            binary_args, reference_time, gate_cache, change_log, impact,
        )
    accepted.extend(annotated)

    # ── Settle: drop orphans, rebuild, verify the result, repair ─────────────
    # This is the only check against the program the user actually started with,
    # and the only one that looks at the file as it finally exists rather than
    # at a candidate patch on a temp copy.
    if not args.dry_run and change_log:
        print(f"{'='*60}")
        print(f"  SETTLING — verify the finished source, drop what does not hold up")
        print(f"{'='*60}")
        survivors, notes = _settle(
            original_text, change_log, args, output_dir, reference_output,
            reference_outputs, binary_args, reference_time,
        )
        if notes:
            print(f"  Dropped {len(notes)} change(s):")
            for n in notes:
                print(f"    · {n}")
        print()

        # accepted.json must describe the file on disk, not everything that was
        # ever provisionally accepted.
        kept_pragma_ids = {c["region_id"] for c in survivors if c["kind"] == "pragma"}
        kept_rewrite_ids = {c["region_id"] for c in survivors if c["kind"] == "rewrite"}
        accepted = [
            r for r in accepted
            if (r.get("phase") == "B" and r["region_id"] in kept_pragma_ids)
            or (r.get("tier") == 2 and r["region_id"] in kept_rewrite_ids)
        ]
        f = output_dir / "accepted.json"
        f.write_text(json.dumps(accepted, indent=2))

    # ── Summary ──────────────────────────────────────────────────────────────
    # De-duplicate skipped IDs and drop any that were ultimately accepted in
    # some version (e.g. a loop skipped at depth 0 but accepted at depth 1 after
    # an enclosing region's restructuring made it parallelisable).  Keep the
    # lowest depth at which each remaining ID was skipped.
    accepted_ids = {r["region_id"] for r in accepted}
    skipped_by_id: dict = {}
    for rid, d in skipped:
        if rid in accepted_ids:
            continue
        if rid not in skipped_by_id or d < skipped_by_id[rid]:
            skipped_by_id[rid] = d

    # The metric is pragmas that survive in the finished file, whoever wrote
    # them: Phase B's, plus the ones an --llm-pragmas rewrite carries itself.
    n_dp_pragmas = len([r for r in accepted if r.get("phase") == "B"])
    n_llm_pragmas = sum(r.get("pragmas", 0) for r in accepted if r.get("tier") == 2)
    n_pragmas = n_dp_pragmas + n_llm_pragmas
    n_rewrites = len([r for r in accepted if r.get("tier") == 2])
    print(f"\n{'='*60}")
    breakdown = (f" ({n_dp_pragmas} DiscoPoP + {n_llm_pragmas} LLM)"
                 if n_llm_pragmas else "")
    print(f"  SUMMARY: {n_rewrites} rewrite(s) kept  |  {n_pragmas} pragma(s) applied"
          f"{breakdown}  |  {len(skipped_by_id)} skipped")
    verdict = ("BEAT" if n_pragmas > baseline_pragmas
               else "MATCHED" if n_pragmas == baseline_pragmas else "BELOW")
    print(f"  DiscoPoP unaided: {baseline_pragmas} usable pragma(s)  →  this run: "
          f"{n_pragmas}   [{verdict}]")
    for r in accepted:
        d = r.get("discovery_depth", 0)
        # Phase-B records carry "phase", Phase-A ones carry "tier".
        kind = "Phase-B pragma" if r.get("phase") == "B" else f"Tier-{r.get('tier', '?')}"
        extra = ""
        if r.get("marginal_speedup") is not None:
            extra = f"  marginal {r['marginal_speedup']:.2f}×"
        elif r.get("self_annotated"):
            extra = f"  {r.get('pragmas', 0)} own pragma(s)"
            if r.get("exposed_speedup") is not None:
                extra += f", {r['exposed_speedup']:.2f}×"
        print(f"    ✓  {r.get('region_type', '?')} {r['region_id']}  "
              f"[{kind}]  depth={d}{extra}")
    for rid, d in skipped_by_id.items():
        print(f"    ✗  {rid}  [skipped]  depth={d}")
    print(f"\n  Results → {output_dir}/accepted.json")
    print(f"{'='*60}\n")
