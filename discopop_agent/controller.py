"""
Agentic Controller — ties L1 → L2 → L3 → L4 together.

Targets any hotspot code region (loop, function body, CU), not just loops.

Main loop (per thesis flowchart, slide 9):

The quality gate (L4) is deliberately Tier-2 only: it exists to prove that
code the LLM restructured is valid.  DiscoPoP's own pragma is trusted and
applied as generated, so a region with an applicable pattern never reaches
the LLM.

  For each candidate (priority order):
    ┌─ Tier-1: DiscoPoP pattern found & applicable?
    │    Yes → apply the pragma as generated → ACCEPT
    │              (no gate, no measurement, no LLM call, no re-profile)
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
  found they are skipped without any LLM call.

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

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List

from . import viz
from .args import AgentArguments
from .l1_planner import build_candidates, region_fingerprint
from .l2_evidence import _brace_match_end, assemble, load_prevented_deps
from .l3_llm import LLMConnectionError, call_llm, fmt_blockers, make_diff, normalize_code
from .l4_validator import capture_reference, fix_hunk_headers, validate
from .types import ValidationResult

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

    Covers three location variants:
      - "Location is heap block allocated by main thread"  (vector data on heap)
      - "Location is stack of main thread"                 (vector object / local var)
      - "Location is global '<name>'"                      (static / file-scope array)
    The location clause only establishes the main-thread-vs-worker shape; the
    reasoning is about WHERE THE ACCESSES RUN, so it holds for any storage
    class.  Omitting globals made the agent escalate correctly-parallel loops
    over `static` arrays to the LLM — caught by the benchmark's Do-All baseline.
    In both cases the main thread's access must be sequential (no .omp_outlined
    in its call stack), confirming it runs outside any parallel region.
    """
    lines = diagnostic.splitlines()

    # Variant 1: OpenMP REDUCTION gather.  libomp combines per-thread partials
    # inside its barrier (`.omp.reduction.reduction_func` called from
    # `__kmp_*barrier_gather`), under runtime-internal synchronization TSan
    # cannot see because libomp is not TSan-instrumented.  Conservative rule:
    # EVERY racing access must sit inside those runtime frames — an access in
    # plain user code (a genuine missing-reduction race) disqualifies.
    access_blocks = []
    for idx, line in enumerate(lines):
        if ("Read" in line or "Write" in line) and (
            "by main thread:" in line or "by thread T" in line
        ):
            frames = []
            for j in range(idx + 1, len(lines)):
                if not lines[j].strip():
                    break
                frames.append(lines[j])
            access_blocks.append(frames)
    if access_blocks and all(
        any(".omp.reduction.reduction_func" in f or
            ("__kmp_" in f and "barrier" in f) for f in frames)
        for frames in access_blocks
    ):
        return True

    # Variant 2: OMP worker vs. the main thread running sequential code after
    # the parallel-for barrier — TSan on macOS does not model that implicit
    # barrier.
    is_heap = (
        "Location is heap block" in diagnostic
        and "allocated by main thread" in diagnostic
    )
    is_stack = "Location is stack of main thread" in diagnostic
    is_global = "Location is global" in diagnostic
    if not (is_heap or is_stack or is_global):
        return False
    if ".omp_outlined" not in diagnostic:
        return False
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


def _venv_env() -> "dict[str, str]":
    """Environment with our venv's bin dir prepended to PATH.

    The agent is typically launched as `venv/bin/python -m discopop_agent`
    WITHOUT activating the venv, so `venv/bin` is not on PATH.  The explorer we
    spawn shells out to a BARE `discopop_patch_generator` (resolved via PATH);
    without this, PATH may resolve it to a stale/global DiscoPoP install
    (e.g. ~/.local/bin) that doesn't understand newer pattern types
    (`ValueError: Unknown task type: PARALLELREGION`) and exits 1, aborting the
    re-profile.  Prepending our venv's bin guarantees the matching tool wins.
    """
    import os

    env = dict(os.environ)
    venv_bin = str(Path(sys.executable).parent)
    env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
    return env


def _reprofil(source_file: str, discopop_dir: Path, binary_args: list | None = None) -> bool:
    """Re-instrument, run, and re-explore after a Tier-2 patch is accepted."""
    src = Path(source_file).resolve()   # absolute path avoids CWD confusion
    binary = src.parent / "a.out"
    extra = [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"] if Path(_LLVM_LIBCXX).exists() else []
    env = _venv_env()

    r = subprocess.run(
        [_cxx_wrapper(), str(src), "-o", str(binary)] + extra,
        capture_output=True, text=True, cwd=src.parent, env=env,
    )
    if r.returncode != 0:
        print(f"      [re-profile] instrumentation failed:\n{r.stderr[-500:]}")
        return False

    run_cmd = [str(binary)] + (binary_args or [])
    subprocess.run(run_cmd, capture_output=True, text=True, cwd=src.parent, env=env)

    r = subprocess.run(
        [_explorer_cmd()], capture_output=True, text=True,
        cwd=discopop_dir.resolve(), env=env,
    )
    if r.returncode != 0:
        print(f"      [re-profile] explorer failed:\n{r.stderr[-500:]}")
        return False

    return True


def _function_edit_to_diff(
    source_file: str, start_line: int, end_line: int, new_code: str
) -> str | None:
    """--edit-mode function: splice the LLM's rewritten function into the file
    over [start_line, end_line] and return a unified diff of the change.

    The diff is generated from the actual on-disk content, so it always applies
    cleanly — eliminating the diff-apply failure class.  Returns None if the span
    is invalid or the edit is a no-op (ignoring comments and whitespace)."""
    old_text = Path(source_file).read_text()
    old_lines = old_text.splitlines(keepends=True)
    if start_line < 1 or end_line > len(old_lines) or start_line > end_line:
        return None
    new_block = [ln + "\n" for ln in new_code.splitlines()]
    new_lines = old_lines[: start_line - 1] + new_block + old_lines[end_line:]
    old_span = "".join(old_lines[start_line - 1: end_line])
    if normalize_code(new_code) == normalize_code(old_span):
        return None
    return make_diff(old_text, "".join(new_lines), source_file)


def _apply_to_source(diff: str, source_file: str, output_dir: Path, label: str) -> bool:
    """Write a validated patch into the real source file, backing the original
    up first.  Returns True if the file now carries the change.

    Tier-2 rewrites were always written back, but a validated Tier-1 pragma used
    to be recorded and then left on disk in patch_generator/ — so a run that
    proved a 5x parallelization ended with the user's source untouched and
    nothing to show for it.  The agent's output is a parallelized program, so
    accepted patches of either tier land in the file.
    """
    src = Path(source_file).resolve()
    backup = output_dir / f"{src.name}.original"
    if not backup.exists():
        shutil.copy2(src, backup)
        print(f"│  [{label}] Original backed up → {backup.name}")
    patch_path = output_dir / f".apply_{label.lower()}.patch"
    patch_path.write_text(fix_hunk_headers(diff) + "\n")
    r = subprocess.run(
        ["patch", "--quiet", "--no-backup-if-mismatch", str(src), str(patch_path)],
        capture_output=True, text=True,
    )
    patch_path.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"│  [{label}] WARNING: could not apply the validated patch to "
              f"{src.name}: {(r.stdout + r.stderr).strip()[:160]}")
        return False
    print(f"│  [{label}] Applied to {src.name}")
    return True


_PRAGMA_SHARED_RE = re.compile(r"\bshared\s*\(([^)]*)\)")
_HUNK_OLD_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")


def _declared_in(lines: List[str], name: str) -> bool:
    """Is `name` DECLARED anywhere in these lines (not merely used)?"""
    decl = re.compile(
        r"(?:^|[;{}(,]|\s)"                       # statement boundary
        r"(?:const\s+|static\s+|volatile\s+|unsigned\s+|signed\s+)*"
        r"(?:auto|bool|char|short|int|long|float|double|size_t|"
        r"[A-Za-z_]\w*(?:::\w+)*)"                # a type name
        r"[\s*&]+"
        r"(?:[\w\s,*&]*?\b)?"                     # other names in the same decl
        + re.escape(name) + r"\b\s*(?=[=;,\[)])"
    )
    return any(decl.search(ln) for ln in lines)


def _repair_pragma_clauses(diff: "str | None", source_file: str) -> "str | None":
    """Drop names from a generated pragma's `shared()` clause when they are not
    in scope at the pragma.

    DiscoPoP sometimes lists a loop-BODY local in `shared()`.  Observed on
    example4: for a loop whose body opens `int tmp = arr[i];` it emitted
    `shared(tmp,arr)`, and the -fopenmp build then fails outright with
    "use of undeclared identifier 'tmp'".  The gate correctly rejects that
    pattern, but the only recovery was Tier-2 — an LLM call, gated by
    --restructure-depth — for what is a one-token defect in a generated clause.
    Deleting the name is not restructuring, so it happens here instead: at any
    depth, for free, before the gate.

    Only `shared()` is touched, and that makes the repair semantically free:
    a variable from an enclosing scope is shared by DEFAULT in a `parallel for`,
    so removing it from the clause cannot change the meaning — it is either
    redundant or (the bug case) not in scope at all.  `private`, `firstprivate`,
    `lastprivate` and `reduction` are left alone, since removing a name there
    WOULD change semantics.  A pragma carrying `default(none)` is skipped
    entirely, because there the clause is load-bearing.

    Returns the diff unchanged (same object) when there is nothing to fix, so
    the gate cache key is unaffected.
    """
    if not diff or "#pragma omp" not in diff:
        return diff

    try:
        src_lines = Path(source_file).read_text().splitlines()
    except OSError:
        return diff

    out: List[str] = []
    old_line = 0           # 1-based line in the ORIGINAL file
    changed = False

    for line in diff.splitlines():
        m = _HUNK_OLD_RE.match(line)
        if m:
            old_line = int(m.group(1))
            out.append(line)
            continue

        if line.startswith("+") and "#pragma omp" in line and "default(none)" not in line:
            # The pragma is inserted BEFORE original line `old_line`, which is
            # the loop it applies to.  Its body is that loop's brace span.
            body: List[str] = []
            if 0 < old_line <= len(src_lines):
                end = _brace_match_end(source_file, old_line)
                if end >= old_line:
                    body = src_lines[old_line - 1:end]
            if body:
                def _strip(mm: "re.Match") -> str:
                    names = [n.strip() for n in mm.group(1).split(",") if n.strip()]
                    kept = [n for n in names if not _declared_in(body, n)]
                    if len(kept) == len(names):
                        return str(mm.group(0))
                    dropped = [n for n in names if n not in kept]
                    print(f"│  [Tier-1] Repairing the generated pragma: "
                          f"{', '.join(dropped)} "
                          f"{'is' if len(dropped) == 1 else 'are'} declared inside "
                          f"the loop body, so cannot appear in shared()")
                    return f"shared({','.join(kept)})" if kept else ""

                fixed = str(_PRAGMA_SHARED_RE.sub(_strip, line))
                if fixed != line:
                    changed = True
                    line = fixed.rstrip() + " "
            out.append(line)
            continue

        if not line.startswith("+"):
            # context and removed lines both advance the original-file position
            if not line.startswith("---") and not line.startswith("\\"):
                old_line += 1
        out.append(line)

    return "\n".join(out) + ("\n" if diff.endswith("\n") else "") if changed else diff


def _read_tier1_patch(patch_dir: Path) -> str | None:
    """Return the content of the first .patch file DiscoPoP generated for a
    pattern, or None if the patch_generator directory is missing / empty."""
    if not patch_dir.exists():
        return None
    for f in sorted(patch_dir.glob("*.patch")):
        return f.read_text()
    return None


def _snapshot_profile(dp_dir: Path, output_dir: Path) -> Path:
    """Copy the current DiscoPoP profile (.discopop) to a snapshot under the
    agent's output dir (kept inside the project, not the OS temp dir), excluding
    the output dir itself when it lives inside .discopop.  Restoring this snapshot
    is far cheaper than re-running instrument+run+explore to rebuild the same
    pre-patch state on a revert."""
    snap_root = output_dir / ".profile_snapshots"
    snap_root.mkdir(parents=True, exist_ok=True)
    snap = Path(tempfile.mkdtemp(prefix="snap_", dir=snap_root))
    ignore = None
    if output_dir.resolve().parent == dp_dir.resolve():
        # output_dir (and thus the snapshot under it) lives inside .discopop —
        # exclude it so we never copy the snapshot into itself.
        ignore = shutil.ignore_patterns(output_dir.name)
    shutil.copytree(dp_dir, snap, dirs_exist_ok=True, ignore=ignore)
    return snap


def _restore_profile(snap: Path, dp_dir: Path, output_dir: Path) -> None:
    """Restore the profile from a snapshot taken by _snapshot_profile, preserving
    the agent's output dir (accepted.json, patches, backups) when it lives inside
    .discopop.  Replaces re-profiling on a revert."""
    keep = output_dir.name if output_dir.resolve().parent == dp_dir.resolve() else None
    for item in dp_dir.iterdir():
        if item.name == keep:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for item in snap.iterdir():
        dst = dp_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)


def _write_record(output_dir: Path, record: dict, dry_run: bool = False) -> None:
    """Append one accepted region to accepted.json.

    A dry run still evaluates Tier-1 patches for real (it only skips the LLM),
    so its verdicts belong in the printed summary — but --dry-run promises no
    file changes, so nothing is written."""
    if dry_run:
        return
    f = output_dir / "accepted.json"
    records: List[dict] = json.loads(f.read_text()) if f.exists() else []
    records.append(record)
    f.write_text(json.dumps(records, indent=2))


def _print_candidates(candidates: list) -> None:
    """Print candidate table. candidates is a list of (depth, HotspotCandidate)."""
    print(f"{'Region ID':<12} {'Type':<10} {'Score':>7}  {'Tier':>4}  {'Depth':>5}  {'Workload':>12}  Name")
    print("-" * 76)
    for depth, c in candidates:
        r = c.region
        name = r.name or f"lines {r.start_line}–{r.end_line}"
        print(f"  {r.region_id:<10} {r.region_type:<10} {c.score:>7.1f}  {c.tier:>4}  {depth:>5}  {c.workload_estimate:>12,.0f}  {name}")
    print()


def _print_banner(args: AgentArguments) -> None:
    print(f"\n{'='*60}")
    print("  DiscoPoP Agentic Controller")
    print(f"{'='*60}")
    print(f"  Source         : {args.source_file}")
    print(f"  DiscoPoP dir   : {args.discopop_dir}")
    print(f"  Model          : {args.model}")
    print(f"  Budget         : {args.budget} LLM retries/region "
          f"(+{args.build_retries} free build fixes)")
    print(f"  λ penalty      : {args.lambda_penalty}")
    print(f"  Min workload   : {args.min_workload}")
    print(f"  Restruct. depth: {args.restructure_depth} "
          f"(Tier-2 allowed at depth 0–{args.restructure_depth})")
    print(f"  Quality gate   : Tier-2 only (LLM rewrites); "
          f"Tier-1 pragmas applied unvalidated")
    print(f"  Speedup gate   : "
          + (f"require ≥ {args.min_measured_speedup}× measured"
             if args.require_speedup else "OFF (--no-require-speedup)"))
    print(f"  Dry run        : {args.dry_run}")
    if args.provider == "openai-compat":
        llm_mode = f"{args.model} @ {args.api_base} (openai-compat)"
    else:
        llm_mode = args.model
    print(f"  LLM mode       : {llm_mode}")
    print(f"  Edit mode      : {args.edit_mode}")
    print(f"{'='*60}\n")


_HUNK_NEW_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _touched_span(diff: str) -> "tuple[int, int] | None":
    """Line range the patch rewrote, in NEW-file coordinates, from its @@ headers.

    Used to ask the post-restructuring question precisely: did DiscoPoP find a
    pattern *in the code the model actually changed*?  A pattern somewhere else
    in the file proves nothing about this rewrite.  Returns None when no hunk
    header parses (then the caller falls back to file scope).
    """
    lo = hi = None
    for line in diff.splitlines():
        m = _HUNK_NEW_RE.match(line)
        if not m:
            continue
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) is not None else 1
        end = start + max(count, 1) - 1
        lo = start if lo is None else min(lo, start)
        hi = end if hi is None else max(hi, end)
    return (lo, hi) if lo is not None and hi is not None else None


def _gate_key(diff: str, source_file: str) -> str:
    """Identity of one gate run: this patch, against this exact source text.

    The source hash is what makes reuse safe — a patch validated before another
    region's pragma was applied says nothing about the file afterwards, and that
    case really happens (a rewrite exposes two loops; applying the first one's
    pragma changes the file the second is measured against).
    """
    h = hashlib.sha1()
    h.update(Path(source_file).read_bytes())
    h.update(b"\0")
    h.update(diff.encode())
    return h.hexdigest()


def _validate_cached(
    cache: dict,
    diff: str,
    args: AgentArguments,
    reference_output: "str | None",
    binary_args: "list | None",
    reference_time: "float | None",
    reference_outputs: "list | None" = None,
) -> "tuple[ValidationResult, bool, bool]":
    """Run the gate on `diff`, or return the answer already computed for it.

    Returns (result, served_from_cache, barrier_false_positive_suspected).

    Only the post-rewrite verification calls this now — the Tier-1 pass applies
    DiscoPoP's pragma without gating it.  The cache still earns its place: one
    verification measures every pattern the rewrite exposed, and a later region
    can present an identical patch against identical source bytes — a full
    duplicate gate run (three compiles, a sanitizer run, a correctness run, and
    up to five timing pairs) for a verdict already known.

    The macOS OMP-barrier false-positive re-check lives here too.
    """
    key = _gate_key(diff, args.source_file)
    hit = cache.get(key)
    if hit is not None:
        return hit, True, False

    def _run(skip: bool) -> ValidationResult:
        return validate(
            diff, args.source_file,
            reference_output=reference_output,
            reference_outputs=reference_outputs,
            binary_args=binary_args,
            require_speedup=args.require_speedup,
            min_speedup=args.min_measured_speedup,
            skip_race_check=skip,
            reference_time=reference_time,
        )

    res = _run(False)
    barrier_fp = (
        not res.passed and res.stage == "tsan"
        and _is_omp_barrier_false_positive(res.diagnostic)
    )
    if barrier_fp:
        # Suspected macOS barrier artefact: re-verify against the correctness
        # and performance gates rather than accepting on the heuristic alone.
        res = _run(True)
    cache[key] = res
    return res, False, barrier_fp


@dataclass
class RewriteOutcome:
    """Did the restructuring achieve what it exists to achieve?

    status:
      "ok"             — DiscoPoP found a pattern in the rewritten code and its
                         pragma passed the gate (and was fast enough, if required)
      "exposed"        — a pattern was found; validating it is deferred to the
                         next depth, which is allowed to restructure it further
      "no_pattern"     — DiscoPoP re-profiled the rewrite and still found nothing
      "pattern_broken" — a pattern was found but its pragma fails the gate
      "no_speedup"     — the pragma is correct but not faster
    """
    status: str
    speedup: "float | None" = None
    pattern_label: str = ""
    diagnostic: str = ""


def _verify_rewrite(
    fresh: list,
    touched: "tuple[int, int] | None",
    dp_dir: Path,
    args: AgentArguments,
    reference_output: "str | None",
    binary_args: "list | None",
    reference_time: "float | None",
    validate_patterns: bool,
    gate_cache: dict,
    reference_outputs: "list | None" = None,
) -> RewriteOutcome:
    """Decide whether an accepted-by-the-gate rewrite actually did its job.

    A rewrite exists for exactly one reason: to let DiscoPoP parallelize code it
    previously could not.  Compiling and preserving output is necessary but says
    nothing about that — so after re-profiling we check what DiscoPoP now
    reports for the rewritten lines, and (when this is the last chance to act on
    it) run its generated pragma through the full gate.

    Patterns are tried largest-workload-first and the FIRST qualifying one wins:
    the decision is "did anything pay off", so validating the rest only burns
    time on a question already answered.
    """
    exposed = [
        c for c in fresh
        if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")
        and (touched is None
             or not (c.region.end_line < touched[0] or c.region.start_line > touched[1]))
    ]
    if not exposed:
        return RewriteOutcome("no_pattern")

    exposed.sort(key=lambda c: c.workload_estimate, reverse=True)
    label = ", ".join(
        f"{c.pattern_type or 'pattern'} @ lines {c.region.start_line}–{c.region.end_line}"
        for c in exposed[:3]
    )
    if not validate_patterns:
        # A deeper Tier-2 pass may still restructure this loop; requiring its
        # first-cut pragma to be perfect now would revert genuine progress.
        return RewriteOutcome("exposed", pattern_label=label)

    worst = RewriteOutcome("pattern_broken", pattern_label=label)
    for cand in exposed:
        pid = cand.pattern.get("pattern_id", "?") if cand.pattern else "?"
        patch = _read_tier1_patch(dp_dir / "patch_generator" / str(pid))
        if not patch:
            continue
        res, _cached, _fp = _validate_cached(
            gate_cache, patch, args, reference_output, binary_args, reference_time,
            reference_outputs=reference_outputs,
        )
        if res.passed:
            return RewriteOutcome("ok", res.measured_speedup, label)
        # "no speedup" is closer to success than "still racing": prefer to
        # report it, so the retry prompt talks about granularity, not correctness.
        if res.stage == "performance":
            worst = RewriteOutcome("no_speedup", res.measured_speedup, label, res.diagnostic)
        elif worst.status != "no_speedup":
            worst = RewriteOutcome("pattern_broken", None, label, res.diagnostic)
    return worst


_OUTCOME_LABEL = {
    "no_pattern": "DiscoPoP still finds no parallelism in the rewritten lines",
    "pattern_broken": "DiscoPoP found a pattern, but its pragma fails validation",
    "no_speedup": "DiscoPoP parallelized it, but it is not faster",
    "reprofile_failed": "the rewrite broke DiscoPoP's profiling run",
}


def _rewrite_feedback(
    outcome: RewriteOutcome, dp_dir: Path, file_id: int,
    touched: "tuple[int, int] | None",
) -> str:
    """Turn a failed post-restructuring verdict into the message the LLM sees.

    This is the only place DiscoPoP's own opinion of the model's rewrite reaches
    the model.  Each verdict gets a different instruction, because they mean
    opposite things: "no pattern" means the dependence is still there, while
    "no speedup" means it is gone and only granularity is wrong — telling the
    model to keep hunting for dependences in that case sends it backwards.
    """
    if outcome.status == "no_pattern":
        msg = (
            "DiscoPoP re-profiled your rewrite. Your code compiles and its output is "
            "correct, but DiscoPoP STILL finds no parallel pattern in the lines you "
            "changed — so the rewrite achieved nothing and has been reverted.\n\n"
            "The blocking dependence is therefore still present. Do not re-submit a "
            "variation of the same structure: re-read the blockers below (they are "
            "DiscoPoP's own analysis OF YOUR REWRITE, not of the original code), name "
            "which cause (1-6) each one is, and apply the fix for that cause."
        )
        blockers = fmt_blockers(
            load_prevented_deps(dp_dir, file_id, *(touched or (1, 10**9)))[:12]
        )
        if blockers:
            msg += (
                "\n\nWhat DiscoPoP reports about YOUR REWRITTEN CODE:\n" + blockers
            )
        else:
            msg += (
                "\n\nDiscoPoP reported no specific Do-All blocker for those lines, "
                "which usually means the loop is not in a form it analyses at all: "
                "check that the loop you intended to be parallel has a computable "
                "trip count, a simple `i < bound` condition, and no break/continue/"
                "return in its body."
            )
        return msg

    if outcome.status == "pattern_broken":
        return (
            f"Progress: after your rewrite DiscoPoP DID detect parallelism "
            f"({outcome.pattern_label}). But when its generated `#pragma omp` is "
            f"applied, the result fails validation — so the rewrite has been "
            f"reverted.\n\n"
            f"Keep the structure that made the loop detectable and fix only what "
            f"the diagnostic below reports. A pattern that is detected but wrong "
            f"means some iterations still interfere: find the remaining shared "
            f"state and make each iteration's work independent of the others.\n\n"
            f"Diagnostic:\n{outcome.diagnostic[:1200]}"
        )

    if outcome.status == "no_speedup":
        got = f"{outcome.speedup:.2f}x" if outcome.speedup else "no measurable gain"
        return (
            f"Your rewrite worked in every respect except the one that matters: "
            f"DiscoPoP parallelized it ({outcome.pattern_label}) and the parallel "
            f"build is CORRECT, but it is not faster ({got}). It has been reverted.\n\n"
            f"The dependence is already gone — this is purely a granularity problem "
            f"(cause 6), so do NOT go looking for dependences again. Make each "
            f"parallel iteration do MORE work: parallelize an outer loop instead of "
            f"an inner one, fuse adjacent tiny parallel loops into one, hoist "
            f"loop-invariant work out, or block/tile the iteration space so threads "
            f"get large contiguous chunks.\n\n"
            f"Diagnostic:\n{outcome.diagnostic[:800]}"
        )

    return (
        "Your rewrite compiled and produced correct output, but DiscoPoP could not "
        "instrument or profile it, so it cannot be parallelized at all. It has been "
        "reverted. Avoid constructs that change the program's structure in ways the "
        "profiler cannot follow (unusual templates, macros, computed control flow); "
        "prefer a plain loop rewrite.\n\n"
        f"{outcome.diagnostic}"
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

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
    if reference_output is None:
        print("  [warn] Could not capture reference output — correctness gate disabled.\n")
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

    # Gate results for this run, keyed by (patch, source text).
    # A pattern measured by the post-rewrite verification is normally measured
    # again by the Tier-1 pass that applies it, one queue position later; this
    # lets the second ask reuse the first answer.  Scoped to the run rather than
    # module-global so nothing leaks between runs.
    gate_cache: dict = {}

    accepted: List[dict] = []
    # Each entry is (region_id, discovery_depth).  A region ID can appear more
    # than once (different content versions across re-profiles reuse IDs); the
    # summary de-duplicates and drops IDs that were ultimately accepted.
    skipped: List[tuple] = []

    # Tracks the CONTENT fingerprint of every region ever enqueued across all
    # re-profile cycles.  Region IDs drift after a patch (global counter), so
    # identity is keyed on source text instead — see region_fingerprint() in l1_planner.py.
    all_seen_prints: set = set()

    initial = build_candidates(
        dp_dir, args.source_file, args.lambda_penalty, args.min_workload
    )
    if not initial:
        print("No hotspot regions found. Run discopop_explorer first.")
        return

    # candidates: list of (discovery_depth, HotspotCandidate)
    # depth=0 → initial profile; depth=N → discovered after N Tier-2 re-profiles
    candidates: list = [(0, c) for c in initial]
    all_seen_prints.update(
        region_fingerprint(args.source_file, c.region.start_line, c.region.end_line, c.region.name)
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
            if candidate.workload_estimate < args.min_workload:
                print(f"│  [Tier-1] Workload {candidate.workload_estimate:.0f} < "
                      f"min {args.min_workload:.0f} — too small to bother")
                print(f"└─ SKIPPED\n")
                skipped.append((rid, depth))
                continue

            pragma = candidate.pattern.get("pragma", "")
            pid = candidate.pattern.get("pattern_id", "?")
            ptype = candidate.pattern_type or "pattern"
            patch_dir = dp_dir / "patch_generator" / str(pid)
            print(f"│  [Tier-1] Pattern #{pid} ({ptype}): {pragma}  (W={candidate.workload_estimate:.0f})")

            tier1_diff = _repair_pragma_clauses(
                _read_tier1_patch(patch_dir), args.source_file
            )
            # Tier-1 applies DiscoPoP's own pragma exactly as generated.  The
            # quality gate is reserved for code the LLM restructured, so nothing
            # is measured here — and because escalation to Tier-2 used to be
            # driven by a Tier-1 gate FAILURE, a region with an applicable
            # pattern now always ends here.  The LLM sees only regions where
            # DiscoPoP found no pattern at all.
            print(f"│  [Tier-1] Applying DiscoPoP's pragma as generated "
                  f"(quality gate is Tier-2 only)")
            applied = False
            if args.apply_patches and tier1_diff and not args.dry_run:
                applied = _apply_to_source(
                    tier1_diff, args.source_file, output_dir, label="Tier-1"
                )
            print(f"└─ ACCEPTED\n")
            record = {
                "region_id": rid,
                "region_type": region.region_type,
                "tier": 1,
                "pattern_id": pid,
                "pragma": pragma,
                "patch_dir": str(patch_dir),
                "discovery_depth": depth,
                "measured_speedup": None,
                "applied_to_source": applied,
            }
            accepted.append(record)
            _write_record(output_dir, record, args.dry_run)
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
                    verbose=args.verbose,
                )
            except LLMConnectionError as e:
                # Fatal for the whole run: every region needs the endpoint.
                print(f"│  [Tier-2] FATAL: {e}")
                print(f"└─ aborting — start the LLM server (or fix --api-base) and re-run\n")
                sys.exit(1)

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
                            f"{what} (comment or "
                            "formatting edits do not count). That is not a valid "
                            "answer: the task is to restructure the code so the "
                            "blocking dependence is gone. If your previous "
                            "transformation attempt failed validation, do not fall "
                            "back to the original — apply the OTHER applicable fix "
                            "for the diagnosed cause and adjust every loop bound "
                            "and sweep count to match the new schedule."
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

            print(f"│  [Tier-2] Diff received — running quality gate "
                  f"(apply/compile/correctness)")
            result = validate(
                diff, args.source_file,
                reference_output=reference_output,
                reference_outputs=reference_outputs,
                binary_args=binary_args,
                require_speedup=args.require_speedup,
                min_speedup=args.min_measured_speedup,
                reference_time=reference_time,
            )
            viz.gate_result(result.passed, result.stage, result.diagnostic,
                            result.measured_speedup, skipped_stages=result.skipped_stages)

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
                }

                print(f"│  [Tier-2] Re-profiling to refresh data and discover new candidates...")
                reprofile_ok = _reprofil(
                    args.source_file, dp_dir, args.reprofil_args or None
                )

                # rebuilt / discovered are computed read-only first; the queue and
                # all_seen_prints are only mutated once we decide to COMMIT.
                rebuilt: list = []
                discovered: list = []   # (depth+1, candidate, fingerprint)
                fresh_all: list = []
                if reprofile_ok:
                    fresh_all = build_candidates(
                        dp_dir, args.source_file, args.lambda_penalty, args.min_workload
                    )
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
                if not reprofile_ok:
                    outcome = RewriteOutcome(
                        "reprofile_failed",
                        diagnostic="DiscoPoP could not instrument, run, or analyse the "
                                   "rewritten program (see the log above).",
                    )
                else:
                    # Validating the exposed pragma is deferred only when a deeper
                    # Tier-2 pass is still allowed to work on it.
                    terminal = (depth + 1) > args.restructure_depth
                    print(f"│  [Tier-2] Asking DiscoPoP what it now finds in the "
                          f"rewritten lines"
                          f"{' (and validating its pragma)' if terminal else ''}...")
                    outcome = _verify_rewrite(
                        fresh_all, _touched_span(clean_diff), dp_dir, args,
                        reference_output, binary_args, reference_time,
                        validate_patterns=terminal, gate_cache=gate_cache,
                        reference_outputs=reference_outputs,
                    )

                if outcome.status not in ("ok", "exposed"):
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
                print(f"│  [Tier-2] DiscoPoP now finds: {outcome.pattern_label}")
                if exposed_speedup is not None:
                    record["exposed_speedup"] = exposed_speedup
                    print(f"│  [Tier-2] Restructuring pays off "
                          f"(best exposed loop {exposed_speedup:.2f}×)")
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
                    "apply": "The diff did not apply — its context lines must match the "
                             "current file exactly (raw indentation, no line-number prefix).",
                    "compile": "The patched code does not compile. Fix the C/C++ error "
                             "without changing what the code computes.",
                    "openmp_compile": "A loop you want parallelized is not in OpenMP-canonical "
                             "form (cause 5): use a simple `i < bound` condition and no "
                             "break/continue/return in the body.",
                    "tsan": "ThreadSanitizer found a REAL data race — the loop still carries a "
                            "cross-iteration dependence. Identify its cause (in-place coupling, "
                            "hidden reduction, storage reuse, or a true recurrence) and make the "
                            "iterations independent — do not merely rename storage.",
                    "correctness": "The program's output CHANGED — your restructuring is not "
                            "semantically equivalent. Diagnose WHICH kind of error this is "
                            "before rewriting:\n"
                            "(a) WRONG TRANSFORMATION for the dependence — you assumed an "
                            "independence the code does not have, or reordered operations "
                            "whose order affects the result. Re-check the cause you "
                            "diagnosed against the evidence, then switch to the other fix "
                            "that cause allows.\n"
                            "(b) RIGHT TRANSFORMATION, carried-over detail — the strategy is "
                            "sound but some bound, initial value, or boundary handling was "
                            "copied from the old schedule. Re-derive each such detail for the "
                            "new schedule instead of copying it: a loop bound or skipped "
                            "element that was safe because of the OLD update order is not "
                            "automatically safe under the new one. Keep the strategy and fix "
                            "only that.",
                    "performance": "The parallel build was correct but NOT faster than sequential. "
                            "The dependence is already gone; restructure for granularity (cause 6) "
                            "— coarsen iterations, fuse tiny loops, or hoist invariant work.",
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
                        "Do NOT resubmit a variation of the same code. Your next PLAN "
                        "must open by stating what your previous attempt did, whether "
                        "the failure was (a) the wrong transformation for this "
                        "dependence — then name the different one you are switching "
                        "to — or (b) a detail copied from the old schedule (a bound, "
                        "boundary, or initial value) — then name that exact detail "
                        "and its corrected form.\n"
                        "Then give the OLD -> NEW loop header pairs as usual, and make "
                        "the code you emit match those NEW headers character for "
                        "character. Stating the right bound and then writing the old "
                        "one is the single most common way this retry fails."
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
