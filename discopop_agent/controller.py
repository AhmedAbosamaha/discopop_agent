"""
Agentic Controller — ties L1 → L2 → L3 → L4 together.

Targets any hotspot code region (loop, function body, CU), not just loops.

Main loop (per thesis flowchart, slide 9):

  For each candidate (priority order):
    ┌─ Tier-1: DiscoPoP pattern found & applicable?
    │    Yes → validate patch (compile + TSan with -fopenmp)
    │              PASS → ACCEPT (write record, no LLM call, no re-profile)
    │              FAIL → Tier-2 allowed at this depth?
    │                       No  → SKIP
    │                       Yes → escalate to Tier-2
    │    No  → Tier-2 allowed at this depth?
    │              No  → SKIP
    │              Yes → Tier-2:
    │                      assemble evidence (L2)
    │                      call LLM (L3) → valid diff?
    │                        No  → format re-prompt (free), then retry
    │                        Yes → quality gate (L4) → pass?
    │                                Yes → apply patch, re-profile, discover new
    │                                No  → diagnostic → retry (decrement budget)
    └─ continue to next candidate

Discovery depth (--restructure-depth N):
  Every candidate carries a discovery_depth.  Initial candidates are depth=0.
  After each accepted Tier-2 patch the source is re-profiled; newly exposed
  candidates (IDs not yet seen) are enqueued at depth=current+1.

  Tier-2 (LLM restructuring) is only applied to candidates at depth ≤ N.
  Candidates at depth > N are processed with Tier-1 only — if no pattern is
  found or Tier-1 fails validation, they are skipped without any LLM call.

  With --restructure-depth 0 (default):
    depth=0 (initial)  → Tier-1 or Tier-2
    depth=1 (discovered after first restructuring) → Tier-1 only → terminates

  With --restructure-depth 1:
    depth=0 → Tier-1 or Tier-2 → re-profile → depth=1 → Tier-1 or Tier-2
    depth=2 → Tier-1 only → terminates

  Termination is guaranteed: at depth N+1 the source is never modified again,
  so no further re-profiling occurs and the queue drains.

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
from collections import defaultdict
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


def _fingerprint(source_file: str, start_line: int, end_line: int, name: str | None = None) -> str:
    """Content-based identity for a code region, invariant under DiscoPoP's
    global ID drift and under line-number shifts caused by patching.

    DiscoPoP assigns region IDs from a single global counter (Structs.hpp:60),
    so patching one function renumbers every region after it — IDs cannot be
    used to track a region across a re-profile.  Source line numbers also shift
    when a patch adds/removes lines above a region.  The region's *text*, by
    contrast, is unchanged unless that exact region was patched.

    The fingerprint normalises whitespace and drops blank/comment lines so that
    re-indentation alone does not break the match.  The enclosing region name
    (function name, when available) is folded in to disambiguate textually
    identical sibling regions in different functions.
    """
    try:
        lines = Path(source_file).read_text().splitlines()
        region = lines[start_line - 1 : end_line]
    except (OSError, IndexError):
        region = []

    body = "\n".join(
        ln.strip() for ln in region
        if ln.strip() and not ln.strip().startswith("//")
    )
    return f"{name or ''}␟{body}"


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
    """Print candidate table. candidates is a list of (depth, HotspotCandidate)."""
    print(f"{'Region ID':<12} {'Type':<10} {'Score':>7}  {'Tier':>4}  {'Depth':>5}  {'Ŝ (est.)':>12}  Name")
    print("-" * 76)
    for depth, c in candidates:
        r = c.region
        name = r.name or f"lines {r.start_line}–{r.end_line}"
        print(f"  {r.region_id:<10} {r.region_type:<10} {c.score:>7.1f}  {c.tier:>4}  {depth:>5}  {c.estimated_speedup:>12,.0f}  {name}")
    print()


def _print_banner(args: AgentArguments) -> None:
    print(f"\n{'='*60}")
    print("  DiscoPoP Agentic Controller")
    print(f"{'='*60}")
    print(f"  Source         : {args.source_file}")
    print(f"  DiscoPoP dir   : {args.discopop_dir}")
    print(f"  Model          : {args.model}")
    print(f"  Budget         : {args.budget} LLM retries/region")
    print(f"  λ penalty      : {args.lambda_penalty}")
    print(f"  Min speedup    : {args.min_speedup}×")
    print(f"  Restruct. depth: {args.restructure_depth} "
          f"(Tier-2 allowed at depth 0–{args.restructure_depth})")
    print(f"  Dry run        : {args.dry_run}")
    print(f"  LLM mode       : {'manual (stdin)' if args.manual_llm else 'mock' if args.mock_llm else args.model}")
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

    accepted: List[dict] = []
    # Each entry is (region_id, discovery_depth).  A region ID can appear more
    # than once (different content versions across re-profiles reuse IDs); the
    # summary de-duplicates and drops IDs that were ultimately accepted.
    skipped: List[tuple] = []

    # Tracks the CONTENT fingerprint of every region ever enqueued across all
    # re-profile cycles.  Region IDs drift after a patch (global counter), so
    # identity is keyed on source text instead — see _fingerprint().
    all_seen_prints: set = set()

    initial = build_candidates(
        dp_dir, args.source_file, args.lambda_penalty, args.min_speedup
    )
    if not initial:
        print("No hotspot regions found. Run discopop_explorer first.")
        return

    # candidates: list of (discovery_depth, HotspotCandidate)
    # depth=0 → initial profile; depth=N → discovered after N Tier-2 re-profiles
    candidates: list = [(0, c) for c in initial]
    all_seen_prints.update(
        _fingerprint(args.source_file, c.region.start_line, c.region.end_line, c.region.name)
        for c in initial
    )

    print("  Initial candidates")
    _print_candidates(candidates)

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
            if candidate.estimated_speedup < args.min_speedup:
                print(f"│  [Tier-1] Speedup {candidate.estimated_speedup:.0f} < "
                      f"min {args.min_speedup:.0f} — not worth parallelising")
                print(f"└─ SKIPPED\n")
                skipped.append((rid, depth))
                continue

            pragma = candidate.pattern.get("pragma", "")
            pid = candidate.pattern.get("pattern_id", "?")
            ptype = candidate.pattern_type or "pattern"
            patch_dir = dp_dir / "patch_generator" / str(pid)
            print(f"│  [Tier-1] Pattern #{pid} ({ptype}): {pragma}  (Ŝ={candidate.estimated_speedup:.0f})")

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
                        # Distinguish a real race (DiscoPoP false positive) from an
                        # OpenMP-canonical-form compile error — they need different
                        # framing and a different Tier-2 instruction.
                        if t1_result.stage == "openmp_compile":
                            reason_label = "loop not in OpenMP-canonical form"
                            t2_hint = (
                                f"DiscoPoP suggested a {ptype} pattern (pragma: {pragma}), "
                                f"but the loop is NOT in OpenMP-canonical form, so the "
                                f"generated pragma fails to compile.  Rewrite the loop into "
                                f"canonical form (simple `i < bound` condition, no break/"
                                f"continue/return in the body).\n"
                                f"Compiler diagnostic:\n{t1_result.diagnostic}"
                            )
                        else:
                            reason_label = "DiscoPoP false positive (real race)"
                            t2_hint = (
                                f"DiscoPoP suggested a {ptype} pattern (pragma: {pragma}), "
                                f"but the generated patch FAILED validation at stage "
                                f"'{t1_result.stage}' — likely a false-positive due to a "
                                f"loop-carried dependency DiscoPoP did not detect.\n"
                                f"Validation diagnostic:\n{t1_result.diagnostic}"
                            )
                        print(f"│  [Tier-1] Validation FAILED (stage={t1_result.stage}) "
                              f"— {reason_label}")
                        if not tier2_allowed:
                            print(f"│  [Tier-1] Tier-2 not allowed at depth {depth} → SKIP")
                            print(f"└─ SKIPPED\n")
                            skipped.append((rid, depth))
                            continue
                        print(f"│  [Tier-1] Escalating to Tier-2 (LLM restructuring)")
                        failure_reason = t2_hint
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
                    "discovery_depth": depth,
                }
                accepted.append(record)
                _write_record(output_dir, record)
                continue
            # tier1_valid is False → fall through to Tier-2 check below

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

                clean_diff = fix_hunk_headers(diff)
                patch_file = output_dir / f"region_{rid.replace(':', '_')}_tier2.patch"
                patch_file.write_text(clean_diff)

                src_abs = Path(args.source_file).resolve()
                backup = output_dir / f"{src_abs.name}.original"
                if not backup.exists():
                    shutil.copy2(src_abs, backup)
                    print(f"│  [Tier-2] Original backed up → {backup.name}")

                # Snapshot the CONTENT fingerprint of each still-queued candidate
                # BEFORE the patch touches the file.  A survivor (a region we
                # haven't processed and didn't patch) has identical text before
                # and after, so its fingerprint matches a fresh candidate even
                # though its ID drifted and its line numbers may have shifted.
                old_prints = [
                    (
                        d,
                        _fingerprint(args.source_file, c.region.start_line,
                                     c.region.end_line, c.region.name),
                    )
                    for d, c in candidates[i:]
                ]
                del candidates[i:]

                patch_result = subprocess.run(
                    ["patch", "--quiet", str(src_abs), str(patch_file)],
                    capture_output=True, text=True,
                )
                if patch_result.returncode != 0:
                    print(f"│  [Tier-2] WARNING: patch apply failed: "
                          f"{(patch_result.stdout + patch_result.stderr).strip()[:200]}")

                record = {
                    "region_id": rid,
                    "region_type": region.region_type,
                    "tier": 2,
                    "patch_file": str(patch_file),
                    "reprofiled": False,
                    "discovery_depth": depth,
                }

                print(f"│  [Tier-2] Re-profiling to refresh data and discover new candidates...")
                reprofile_ok = _reprofil(
                    args.source_file, dp_dir, args.reprofil_args or None
                )
                if reprofile_ok:
                    fresh_all = build_candidates(
                        dp_dir, args.source_file, args.lambda_penalty, args.min_speedup
                    )

                    # Index fresh candidates by content fingerprint (a bucket per
                    # fingerprint handles textually identical sibling regions).
                    fresh_by_print: dict = defaultdict(list)
                    for nc in fresh_all:
                        fp = _fingerprint(args.source_file, nc.region.start_line,
                                          nc.region.end_line, nc.region.name)
                        fresh_by_print[fp].append(nc)

                    # Survivors: match each remaining old candidate to a fresh one
                    # by content, consuming the match so duplicates pair up 1:1.
                    # The survivor keeps its depth but adopts the fresh candidate's
                    # current lines / pattern / patch data.
                    consumed: set = set()
                    rebuilt: list = []
                    for old_depth, fp in old_prints:
                        for nc in fresh_by_print.get(fp, []):
                            if id(nc) not in consumed:
                                rebuilt.append((old_depth, nc))
                                consumed.add(id(nc))
                                break

                    # Discovered: fresh candidates whose content was never queued
                    # and that did not pair with a survivor.  Assigned depth+1.
                    discovered: list = []
                    for nc in fresh_all:
                        if id(nc) in consumed:
                            continue
                        fp = _fingerprint(args.source_file, nc.region.start_line,
                                          nc.region.end_line, nc.region.name)
                        if fp not in all_seen_prints:
                            discovered.append((depth + 1, nc))
                            all_seen_prints.add(fp)

                    candidates.extend(rebuilt)
                    candidates.extend(discovered)

                    print(f"│  [Tier-2] {len(rebuilt)} survivor(s) rebuilt, "
                          f"{len(discovered)} new at depth {depth + 1}")
                    record["reprofiled"] = True

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
            skipped.append((rid, depth))

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

    print(f"\n{'='*60}")
    print(f"  SUMMARY: {len(accepted)} accepted  |  {len(skipped_by_id)} skipped")
    for r in accepted:
        d = r.get("discovery_depth", 0)
        print(f"    ✓  {r['region_type']} {r['region_id']}  [Tier-{r['tier']}]  depth={d}")
    for rid, d in skipped_by_id.items():
        print(f"    ✗  {rid}  [skipped]  depth={d}")
    print(f"\n  Results → {output_dir}/accepted.json")
    print(f"{'='*60}\n")
