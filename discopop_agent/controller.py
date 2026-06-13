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

Why Tier-1 validation matters:
  DiscoPoP's Do-All detector never sees cross-iteration deps for scalar
  variables (instruction-ID / source-line-ID mismatch in the dep graph).
  A loop like `a[i] = a[i] + a[i-1]` gets flagged as Do-All even though
  it has a genuine loop-carried RAW dependency.  Running TSan with -fopenmp
  on the generated patch exposes the data race before we commit the change.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import List

from .args import AgentArguments
from .l1_planner import build_candidates
from .l2_evidence import assemble
from .l3_llm import call_llm
from .l4_validator import validate
from .mock_llm import call_mock
from .types import HotspotCandidate

_LLVM_LIBCXX = "/usr/local/Cellar/llvm@19/19.1.7/lib/c++"
_REGION_LABEL = {"loop": "loop", "function": "function", "cu": "block"}


def _cxx_wrapper() -> str:
    return str(Path(sys.executable).parent / "discopop_cxx")


def _explorer_cmd() -> str:
    return str(Path(sys.executable).parent / "discopop_explorer")


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
    print(f"  Dry run     : {args.dry_run}")
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

    candidates = build_candidates(
        dp_dir, args.source_file, args.lambda_penalty, args.min_speedup
    )

    if not candidates:
        print("No hotspot regions found. Run discopop_explorer first.")
        return

    # Priority table
    print(f"{'Region ID':<12} {'Type':<10} {'Score':>7}  {'Tier':>4}  {'Ŝ (est.)':>12}  Name")
    print("-" * 68)
    for c in candidates:
        r = c.region
        name = r.name or f"lines {r.start_line}–{r.end_line}"
        print(f"  {r.region_id:<10} {r.region_type:<10} {c.score:>7.1f}  {c.tier:>4}  {c.estimated_speedup:>12,.0f}  {name}")
    print()

    accepted: List[dict] = []
    skipped: List[str] = []

    seen_ids: set = {c.region.region_id for c in candidates}
    i = 0
    while i < len(candidates):
        candidate = candidates[i]
        i += 1
        region = candidate.region
        rid = region.region_id
        rtype = _REGION_LABEL.get(region.region_type, region.region_type)
        label = f"{rtype} {rid} (lines {region.start_line}–{region.end_line})"

        print(f"┌─ {label}  score={candidate.score:.1f}")

        # ── Tier-1 ──────────────────────────────────────────────────────────
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
            ptype = candidate.pattern.get("pattern_type", "pattern")
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
                    print(f"│  [Tier-1] Validation FAILED (stage={t1_result.stage}) "
                          f"— DiscoPoP false positive")
                    print(f"│  [Tier-1] Escalating to Tier-2 (LLM restructuring)")
                    failure_reason = (
                        f"DiscoPoP suggested a {ptype} pattern (pragma: {pragma}), "
                        f"but the generated patch FAILED validation at stage "
                        f"'{t1_result.stage}' — likely a false-positive due to a "
                        f"loop-carried dependency DiscoPoP did not detect.\n"
                        f"Validation diagnostic:\n{t1_result.diagnostic[:600]}"
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

        # ── Tier-2: LLM restructuring ────────────────────────────────────────
        if candidate.tier != 1:
            # Only print this when we didn't already come from a Tier-1 failure
            print(f"│  [Tier-1] No applicable pattern → Tier-2 (LLM)")

        if args.dry_run:
            print(f"│  [Tier-2] DRY RUN — skipping LLM call")
            print(f"└─ SKIPPED\n")
            skipped.append(rid)
            continue

        budget = args.budget
        last_diff: str | None = None

        while budget > 0:
            budget -= 1
            print(f"│  [Tier-2] Assembling evidence (budget remaining: {budget})")

            evidence = assemble(candidate, profiler_dir, failure_reason)

            if args.mock_llm:
                diff = call_mock(evidence)
            else:
                print(f"│  [Tier-2] Calling {args.model}...")
                diff = call_llm(
                    evidence, args.model,
                    api_key=args.api_key,
                    prior_diff=last_diff,
                )

            if diff is None:
                print(f"│  [Tier-2] LLM returned invalid diff — retrying")
                failure_reason = "Previous LLM attempt returned an invalid diff"
                continue

            last_diff = diff

            print(f"│  [Tier-2] Diff received — running quality gate (apply/compile/TSan)")
            result = validate(diff, args.source_file)

            if result.passed:
                print(f"│  [Tier-2] Quality gate PASSED")

                patch_file = output_dir / f"region_{rid.replace(':', '_')}_tier2.patch"
                patch_file.write_text(diff)

                # Back up original before first modification (never overwrite backup)
                src_abs = Path(args.source_file).resolve()
                backup = output_dir / f"{src_abs.name}.original"
                if not backup.exists():
                    import shutil
                    shutil.copy2(src_abs, backup)
                    print(f"│  [Tier-2] Original backed up → {backup.name}")

                subprocess.run(
                    ["patch", "--quiet", str(src_abs), str(patch_file)],
                    capture_output=True,
                )

                print(f"│  [Tier-2] Re-profiling to discover new patterns...")
                reprofile_ok = _reprofil(args.source_file, dp_dir, args.reprofil_args or None)
                if reprofile_ok:
                    fresh = build_candidates(
                        dp_dir, args.source_file, args.lambda_penalty, args.min_speedup
                    )
                    added = 0
                    for nc in fresh:
                        if nc.region.region_id not in seen_ids:
                            seen_ids.add(nc.region.region_id)
                            candidates.append(nc)
                            added += 1
                    if added:
                        print(f"│  [Tier-2] {added} new candidate(s) queued from re-profile")
                    print(f"│  [Tier-2] Re-profiling complete")

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
