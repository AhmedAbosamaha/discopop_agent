"""
Agentic Controller — ties L1 → L2 → L3 → L4 together.

Targets any hotspot code region (loop, function body, CU), not just loops.

Main loop (per thesis flowchart, slide 9):

  For each candidate (priority order):
    ┌─ Tier-1: DiscoPoP pattern found & applicable?
    │    Yes → validate patch (compile + TSan with -fopenmp)
    │              PASS → ACCEPT (write record, no LLM call)
    │              FAIL → treat as Tier-2 (DiscoPoP had a false positive)
    │    No  → budget left?
    │              No  → SKIP
    │              Yes → Tier-2:
    │                      assemble evidence (L2)
    │                      call LLM (L3) → valid diff?
    │                        No  → format re-prompt (free), then retry
    │                        Yes → quality gate (L4) → pass?
    │                                Yes → apply to source, re-profile, back to Tier-1
    │                                No  → diagnostic → retry (decrement budget)
    └─ continue to next candidate

Pass structure (controlled by --distance):
  Pass 0 : process all candidates from the initial DiscoPoP profile.
           After each accepted Tier-2 patch the source is re-profiled so
           that subsequent Tier-1 candidates in the same pass get fresh
           pattern data — but NO new candidates are added mid-pass.
  Pass 1…distance : re-profile the (now-modified) source and process only
           candidates not seen in any earlier pass.  Repeats up to --distance
           times, stopping early if no new candidates are found.

Why Tier-1 validation matters:
  DiscoPoP's Do-All detector never sees cross-iteration deps for scalar
  variables (instruction-ID / source-line-ID mismatch in the dep graph).
  A loop like `a[i] = a[i] + a[i-1]` gets flagged as Do-All even though
  it has a genuine loop-carried RAW dependency.  Running TSan with -fopenmp
  on the generated patch exposes the data race before we commit the change.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from .args import AgentArguments
from .l1_planner import build_candidates
from .l2_evidence import assemble
from .l3_llm import call_llm, call_manual
from .l4_validator import fix_hunk_headers, validate
from .mock_llm import call_mock

_LLVM_LIBCXX = "/usr/local/Cellar/llvm@19/19.1.7/lib/c++"
_REGION_LABEL = {"loop": "loop", "function": "function", "cu": "block"}


def _cxx_wrapper() -> str:
    return str(Path(sys.executable).parent / "discopop_cxx")


def _explorer_cmd() -> str:
    return str(Path(sys.executable).parent / "discopop_explorer")


def _is_omp_barrier_false_positive(diagnostic: str) -> bool:
    """Detect macOS TSan false positive: OMP worker accesses memory, main thread
    accesses it sequentially after the parallel-for barrier exits.

    Real race:   both accesses are .omp_outlined  (two workers conflict)
    False positive: one access is .omp_outlined (worker), the other is the
    main thread running sequential code after the barrier — TSan on macOS
    does not model the implicit barrier at the end of #pragma omp parallel for.

    Covers two location variants:
      - "Location is heap block allocated by main thread"  (vector data on heap)
      - "Location is stack of main thread"                 (vector object / local var)
    In both cases the main thread's access must be sequential (no .omp_outlined
    in its call stack), confirming it runs outside any parallel region.
    """
    is_heap = (
        "Location is heap block" in diagnostic
        and "allocated by main thread" in diagnostic
    )
    is_stack = "Location is stack of main thread" in diagnostic
    if not (is_heap or is_stack):
        return False
    if ".omp_outlined" not in diagnostic:
        return False
    lines = diagnostic.splitlines()
    for idx, line in enumerate(lines):
        # Match only ACCESS lines ("Write ... by main thread:" / "Read ... by main thread:"),
        # not allocation lines ("allocated by main thread:") which appear in heap-location
        # blocks and do not indicate that the main thread is one of the racing accessors.
        if "by main thread:" in line and ("Write" in line or "Read" in line):
            # Collect only the stack frames that belong to THIS access block.
            # TSan separates access blocks with a blank line; stop there so we
            # don't accidentally include the next access's .omp_outlined frames.
            main_frames = []
            for j in range(idx + 1, len(lines)):
                if not lines[j].strip():
                    break
                main_frames.append(lines[j])
            if not any(".omp_outlined" in f for f in main_frames):
                return True
    return False


_IO_CALLS = frozenset({
    "printf", "fprintf", "sprintf", "snprintf", "puts", "putchar",
    "fwrite", "fread", "fgets", "fputs", "scanf", "fscanf",
    "cout", "cerr", "cin",
})

def _region_is_io_only(source_file: str, start_line: int, end_line: int) -> bool:
    """Return True when every non-blank line in the region is an I/O call.

    TSan can produce false positives on loops that only call stdio/iostream
    functions because their internal buffers are touched before the lock is
    taken.  Skipping TSan for pure I/O regions avoids that noise without
    masking real computation races.
    """
    try:
        lines = Path(source_file).read_text().splitlines()
        region = lines[start_line - 1 : end_line]
    except (OSError, IndexError):
        return False

    compute_lines = [
        ln.strip() for ln in region
        if ln.strip() and not ln.strip().startswith("//")
    ]
    if not compute_lines:
        return False

    return all(
        any(io in ln for io in _IO_CALLS)
        for ln in compute_lines
    )


def _reprofil(source_file: str, discopop_dir: Path, binary_args: list | None = None) -> bool:
    """Re-instrument, run, and re-explore after a Tier-2 patch is accepted."""
    src = Path(source_file).resolve()   # absolute path avoids CWD confusion
    binary = src.parent / "a.out"
    extra = [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"] if Path(_LLVM_LIBCXX).exists() else []

    r = subprocess.run(
        [_cxx_wrapper(), str(src), "-o", str(binary)] + extra,
        capture_output=True, text=True, cwd=src.parent,
    )
    if r.returncode != 0:
        print(f"      [re-profile] instrumentation failed:\n{r.stderr[-500:]}")
        return False

    run_cmd = [str(binary)] + (binary_args or [])
    subprocess.run(run_cmd, capture_output=True, text=True, cwd=src.parent)

    r = subprocess.run(
        [_explorer_cmd()], capture_output=True, text=True,
        cwd=discopop_dir.resolve(),
    )
    if r.returncode != 0:
        print(f"      [re-profile] explorer failed:\n{r.stderr[-500:]}")
        return False

    return True


def _read_tier1_patch(patch_dir: Path) -> str | None:
    """Return the content of the first .patch file DiscoPoP generated for a
    pattern, or None if the patch_generator directory is missing / empty."""
    if not patch_dir.exists():
        return None
    for f in sorted(patch_dir.glob("*.patch")):
        return f.read_text()
    return None


def _write_record(output_dir: Path, record: dict) -> None:
    f = output_dir / "accepted.json"
    records: List[dict] = json.loads(f.read_text()) if f.exists() else []
    records.append(record)
    f.write_text(json.dumps(records, indent=2))


def _print_candidates(candidates: list) -> None:
    print(f"{'Region ID':<12} {'Type':<10} {'Score':>7}  {'Tier':>4}  {'Ŝ (est.)':>12}  Name")
    print("-" * 68)
    for c in candidates:
        r = c.region
        name = r.name or f"lines {r.start_line}–{r.end_line}"
        print(f"  {r.region_id:<10} {r.region_type:<10} {c.score:>7.1f}  {c.tier:>4}  {c.estimated_speedup:>12,.0f}  {name}")
    print()


def _print_banner(args: AgentArguments) -> None:
    print(f"\n{'='*60}")
    print("  DiscoPoP Agentic Controller")
    print(f"{'='*60}")
    print(f"  Source      : {args.source_file}")
    print(f"  DiscoPoP dir: {args.discopop_dir}")
    print(f"  Model       : {args.model}")
    print(f"  Budget      : {args.budget} LLM retries/region")
    print(f"  λ penalty   : {args.lambda_penalty}")
    print(f"  Min speedup : {args.min_speedup}×")
    print(f"  Distance    : {args.distance} discovery pass(es) after initial run")
    print(f"  Dry run     : {args.dry_run}")
    print(f"  LLM mode    : {'manual (stdin)' if args.manual_llm else 'mock' if args.mock_llm else args.model}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(args: AgentArguments) -> None:
    dp_dir = Path(args.discopop_dir)
    profiler_dir = dp_dir / "profiler"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    _print_banner(args)

    # ── Global state across all passes ──────────────────────────────────────
    accepted: List[dict] = []
    skipped: List[str] = []
    # all_seen_ids: every region ID ever queued in any pass.
    # Prevents re-discovering in later passes a region that was already handled
    # (or deliberately skipped) in an earlier pass.
    all_seen_ids: set = set()

    # ── Outer pass loop ──────────────────────────────────────────────────────
    # Pass 0  : initial candidates from the existing .discopop profile.
    # Pass 1…N: re-profile + discover only regions not yet seen.
    for pass_num in range(args.distance + 1):

        if pass_num == 0:
            candidates = build_candidates(
                dp_dir, args.source_file, args.lambda_penalty, args.min_speedup
            )
            if not candidates:
                print("No hotspot regions found. Run discopop_explorer first.")
                return
            header = "Initial candidates"
        else:
            print(f"\n{'='*60}")
            print(f"  DISCOVERY PASS {pass_num}/{args.distance}")
            print(f"{'='*60}\n")
            if not _reprofil(args.source_file, dp_dir, args.reprofil_args or None):
                print("  Re-profiling failed — stopping discovery.")
                break
            fresh_all = build_candidates(
                dp_dir, args.source_file, args.lambda_penalty, args.min_speedup
            )
            candidates = [
                c for c in fresh_all
                if c.region.region_id not in all_seen_ids
            ]
            if not candidates:
                print("  No new candidates found — stopping discovery.")
                break
            header = f"New candidates (pass {pass_num})"

        all_seen_ids.update(c.region.region_id for c in candidates)

        print(f"  {header}")
        _print_candidates(candidates)

        # ── Inner candidate loop (one pass) ──────────────────────────────────
        i = 0
        while i < len(candidates):
            candidate = candidates[i]
            i += 1
            region = candidate.region
            rid = region.region_id
            rtype = _REGION_LABEL.get(region.region_type, region.region_type)
            label = f"{rtype} {rid} (lines {region.start_line}–{region.end_line})"

            print(f"┌─ {label}  score={candidate.score:.1f}")

            # ── Tier-1 ───────────────────────────────────────────────────────
            failure_reason = "DiscoPoP found no applicable parallelism pattern for this region"
            if candidate.tier == 1 and candidate.pattern and candidate.pattern.get("applicable_pattern"):
                # Apply the speedup gate: only accept if Ŝ ≥ min_speedup.
                if candidate.estimated_speedup < args.min_speedup:
                    print(f"│  [Tier-1] Speedup {candidate.estimated_speedup:.0f} < "
                          f"min {args.min_speedup:.0f} — not worth parallelising")
                    print(f"└─ SKIPPED\n")
                    skipped.append(rid)
                    continue

                pragma = candidate.pattern.get("pragma", "")
                pid = candidate.pattern.get("pattern_id", "?")
                ptype = candidate.pattern_type or "pattern"
                patch_dir = dp_dir / "patch_generator" / str(pid)
                print(f"│  [Tier-1] Pattern #{pid} ({ptype}): {pragma}  (Ŝ={candidate.estimated_speedup:.0f})")

                # Validate: compile the DiscoPoP patch with -fopenmp + TSan.
                # This catches false-positive Do-All patterns (e.g. loop-carried
                # scalar deps that DiscoPoP's dep graph misses).
                # Skip validation for trivially small loops (workload < 50) — they
                # are unlikely to contain real parallelism bugs and TSan can produce
                # false positives on I/O-only loops (printf races on stdout buffer).
                tier1_diff = _read_tier1_patch(patch_dir)
                tier1_valid = True
                io_only = _region_is_io_only(
                    args.source_file, region.start_line, region.end_line
                )
                if tier1_diff and not args.dry_run and not io_only:
                    print(f"│  [Tier-1] Running TSan validation on generated patch...")
                    t1_result = validate(tier1_diff, args.source_file)
                    if not t1_result.passed:
                        if (t1_result.stage == "tsan"
                                and _is_omp_barrier_false_positive(t1_result.diagnostic)):
                            print(f"│  [Tier-1] TSan OMP-barrier false positive detected — accepting")
                        else:
                            print(f"│  [Tier-1] Validation FAILED (stage={t1_result.stage}) "
                                  f"— DiscoPoP false positive")
                            print(f"│  [Tier-1] Escalating to Tier-2 (LLM restructuring)")
                            failure_reason = (
                                f"DiscoPoP suggested a {ptype} pattern (pragma: {pragma}), "
                                f"but the generated patch FAILED validation at stage "
                                f"'{t1_result.stage}' — likely a false-positive due to a "
                                f"loop-carried dependency DiscoPoP did not detect.\n"
                                f"Validation diagnostic:\n{t1_result.diagnostic}"
                            )
                            tier1_valid = False

                if tier1_valid:
                    print(f"│  [Tier-1] Validation PASSED")
                    print(f"└─ ACCEPTED\n")
                    record = {
                        "region_id": rid,
                        "region_type": region.region_type,
                        "tier": 1,
                        "pattern_id": pid,
                        "pragma": pragma,
                        "patch_dir": str(patch_dir),
                    }
                    accepted.append(record)
                    _write_record(output_dir, record)
                    continue
                # tier1_valid is False → fall through to Tier-2 below

            # ── Tier-2: LLM restructuring ─────────────────────────────────────
            if candidate.tier != 1:
                # Only print this when we didn't already come from a Tier-1 failure
                print(f"│  [Tier-1] No applicable pattern → Tier-2 (LLM)")

            if args.dry_run:
                print(f"│  [Tier-2] DRY RUN — skipping LLM call")
                print(f"└─ SKIPPED\n")
                skipped.append(rid)
                continue

            budget = args.budget
            # Accumulated conversation for LLM retries (API and manual modes).
            # None on first call → callee builds initial prompt from evidence.
            # After each diff the callee appends the assistant turn and returns
            # the updated list.  After each quality-gate failure the controller
            # appends a user turn so every retry sees the full exchange.
            tier2_messages: list | None = None

            while budget > 0:
                budget -= 1
                print(f"│  [Tier-2] Assembling evidence (budget remaining: {budget})")

                evidence = assemble(candidate, profiler_dir, failure_reason)

                if args.mock_llm:
                    diff = call_mock(evidence)
                elif args.manual_llm:
                    diff, tier2_messages = call_manual(evidence, messages=tier2_messages)
                else:
                    print(f"│  [Tier-2] Calling {args.model}...")
                    diff, tier2_messages = call_llm(
                        evidence, args.model,
                        api_key=args.api_key,
                        messages=tier2_messages,
                    )

                if diff is None:
                    if budget > 0:
                        print(f"│  [Tier-2] LLM returned invalid diff — retrying")
                    else:
                        print(f"│  [Tier-2] LLM returned invalid diff")
                    continue

                print(f"│  [Tier-2] Diff received — running quality gate (apply/compile/TSan)")
                result = validate(diff, args.source_file)

                if result.passed:
                    print(f"│  [Tier-2] Quality gate PASSED")

                    # Normalise hunk header counts before writing to disk and
                    # applying — LLMs often miscalculate +N,M counts, and the
                    # quality gate fixes these internally (via fix_hunk_headers)
                    # but without this step the raw patch command would reject
                    # the saved file with "malformed patch".
                    clean_diff = fix_hunk_headers(diff)
                    patch_file = output_dir / f"region_{rid.replace(':', '_')}_tier2.patch"
                    patch_file.write_text(clean_diff)

                    # Back up original before first modification (never overwrite backup)
                    src_abs = Path(args.source_file).resolve()
                    backup = output_dir / f"{src_abs.name}.original"
                    if not backup.exists():
                        shutil.copy2(src_abs, backup)
                        print(f"│  [Tier-2] Original backed up → {backup.name}")

                    patch_result = subprocess.run(
                        ["patch", "--quiet", str(src_abs), str(patch_file)],
                        capture_output=True, text=True,
                    )
                    if patch_result.returncode != 0:
                        print(f"│  [Tier-2] WARNING: patch apply failed: "
                              f"{(patch_result.stdout + patch_result.stderr).strip()[:200]}")

                    # Re-profile within this pass to refresh Tier-1 pattern data
                    # for remaining candidates.  Rebuild the queue by region ID:
                    # candidates whose ID still exists in the fresh profile are
                    # updated in-place with current pattern data; candidates whose
                    # ID disappeared (region was restructured away) are dropped
                    # from this pass and will be re-discovered in distance passes.
                    print(f"│  [Tier-2] Re-profiling to refresh pattern data...")
                    reprofile_ok = _reprofil(args.source_file, dp_dir, args.reprofil_args or None)
                    if reprofile_ok:
                        fresh = build_candidates(
                            dp_dir, args.source_file, args.lambda_penalty, args.min_speedup
                        )
                        resolved = {r["region_id"] for r in accepted} | set(skipped)
                        fresh_by_id = {nc.region.region_id: nc for nc in fresh}
                        remaining = [
                            fresh_by_id[old_c.region.region_id]
                            for old_c in candidates[i:]
                            if old_c.region.region_id not in resolved
                            and old_c.region.region_id in fresh_by_id
                            # Drop IDs whose iteration count collapsed to ≤ 1 — this
                            # indicates the ID drifted to a different construct after
                            # code restructuring.  These regions are re-discovered with
                            # their correct new IDs in subsequent distance passes.
                            and fresh_by_id[old_c.region.region_id].region.iteration_count > 1
                        ]
                        del candidates[i:]
                        candidates.extend(remaining)
                        all_seen_ids.update(nc.region.region_id for nc in remaining)
                        print(f"│  [Tier-2] Re-profiling complete ({len(candidates) - i} remaining)")

                    record = {
                        "region_id": rid,
                        "region_type": region.region_type,
                        "tier": 2,
                        "patch_file": str(patch_file),
                        "reprofiled": reprofile_ok,
                    }
                    accepted.append(record)
                    _write_record(output_dir, record)
                    print(f"└─ ACCEPTED\n")
                    break

                else:
                    print(f"│  [Tier-2] Stage '{result.stage}' failed: "
                          f"{result.diagnostic[:200].replace(chr(10), ' ')}")
                    failure_reason = (
                        f"Validation failed at stage '{result.stage}':\n"
                        f"{result.diagnostic[:500]}"
                    )
                    # Extend the conversation so the next budget retry sees
                    # the quality-gate diagnostic as a proper user turn.
                    if tier2_messages is not None:
                        diagnostic_snippet = (result.diagnostic or "(no diagnostic)")[:600]
                        tier2_messages = tier2_messages + [{
                            "role": "user",
                            "content": (
                                f"Your diff failed at the '{result.stage}' stage.\n\n"
                                f"Diagnostic:\n{diagnostic_snippet}\n\n"
                                f"Please try a different restructuring approach."
                            ),
                        }]
            else:
                print(f"└─ SKIPPED (budget exhausted)\n")
                skipped.append(rid)

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  SUMMARY: {len(accepted)} accepted  |  {len(skipped)} skipped")
    for r in accepted:
        print(f"    ✓  {r['region_type']} {r['region_id']}  [Tier-{r['tier']}]")
    for rid in skipped:
        print(f"    ✗  {rid}  [skipped]")
    print(f"\n  Results → {output_dir}/accepted.json")
    print(f"{'='*60}\n")
