"""
L4 Execution & Validation Layer
---------------------------------
Three-stage quality gate for every LLM-generated patch:

  Stage 1 — Apply   : patch must apply cleanly to an isolated copy
  Stage 2 — Compile : patched file must compile (plain clang++, not instrumented)
  Stage 3 — TSan    : compile with -fopenmp -fsanitize=thread and run; no races

Stage 3 has two distinct failure stages in the result:
  - "openmp_compile" : the -fopenmp build failed because a loop is not in
                       OpenMP-canonical form (e.g. `i + 1 < n` condition, or a
                       `break` in the body).  Plain stage-2 compile ignores
                       `#pragma omp`, so this only surfaces here.  It is a form
                       error, not a data race.
  - "tsan"           : the build ran and ThreadSanitizer reported a real race.

On any failure the diagnostic text is returned so L3 can include it in
the next retry prompt.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Tuple

from .types import ValidationResult

# Prefer LLVM 19 clang++ (same toolchain used for the profiler)
_CLANGPP_CANDIDATES = [
    "/usr/local/Cellar/llvm@19/19.1.7/bin/clang++",
    "/usr/local/bin/clang++-19",
    "clang++-19",
    "clang++",
]
_LLVM_LIBCXX = "/usr/local/Cellar/llvm@19/19.1.7/lib/c++"
# macOS: libomp is keg-only (brew install libomp); add its lib dir if present
_LIBOMP_DIR = "/usr/local/opt/libomp/lib"

def _macos_sysroot_flag() -> list:
    """Return -isysroot flag pointing at the available macOS SDK, or []."""
    import subprocess, platform
    if platform.system() != "Darwin":
        return []
    try:
        sdk = subprocess.check_output(["xcrun", "--show-sdk-path"],
                                      text=True, stderr=subprocess.DEVNULL).strip()
        return ["-isysroot", sdk] if sdk else []
    except Exception:
        return []


def _find_clangpp() -> Optional[str]:
    for candidate in _CLANGPP_CANDIDATES:
        p = Path(candidate)
        if p.is_absolute() and p.exists():
            return str(p)
        if shutil.which(candidate):
            return shutil.which(candidate)
    return None


# ---------------------------------------------------------------------------
# Diff normalisation: fix off-by-one line counts in @@ headers
# ---------------------------------------------------------------------------

import re as _re

_HUNK_RE = _re.compile(r"^(@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@)(.*)")


def fix_hunk_headers(diff: str) -> str:
    """Re-derive old/new line counts from the diff body and rewrite @@ headers.

    LLMs frequently miscalculate the line counts in unified-diff hunk headers
    (e.g. write +21,20 when the body actually provides 18 new lines).  The GNU
    patch utility is strict about these counts and fails with 'malformed patch'
    when they are wrong.  This function fixes the headers so minor counting
    errors don't discard an otherwise correct patch.
    """
    lines = diff.splitlines()
    out: list = []
    i = 0
    while i < len(lines):
        m = _HUNK_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue

        old_start = int(m.group(2))
        new_start = int(m.group(4))
        suffix = m.group(6)  # anything after the closing @@

        # Scan the body of this hunk to recount
        j = i + 1
        old_count = 0
        new_count = 0
        while j < len(lines):
            ln = lines[j]
            if ln.startswith("@@") or ln.startswith("--- ") or ln.startswith("+++ "):
                break
            if ln.startswith("\\"):
                # "\ No newline at end of file" annotates the preceding line;
                # it is not itself a line of either file, so it must not be
                # counted — doing so would corrupt the header we're fixing.
                j += 1
                continue
            if ln.startswith("-"):
                old_count += 1
            elif ln.startswith("+"):
                new_count += 1
            else:
                old_count += 1
                new_count += 1
            j += 1

        out.append(f"@@ -{old_start},{old_count} +{new_start},{new_count} @@{suffix}")
        i += 1
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Stage 1: apply patch
# ---------------------------------------------------------------------------

def _apply(diff: str, source_file: str, work_dir: Path) -> Tuple[bool, str, Optional[Path]]:
    src = Path(source_file)
    dst = work_dir / src.name
    shutil.copy2(src, dst)

    diff = fix_hunk_headers(diff)

    # Rewrite --- / +++ paths to point at our working copy
    fixed_lines = []
    for line in diff.splitlines():
        if line.startswith("--- "):
            fixed_lines.append(f"--- {dst}")
        elif line.startswith("+++ "):
            fixed_lines.append(f"+++ {dst}")
        else:
            fixed_lines.append(line)
    patch_path = work_dir / "llm.patch"
    patch_path.write_text("\n".join(fixed_lines) + "\n")

    result = subprocess.run(
        # --no-backup-if-mismatch: suppress <file>.orig backups on fuzzy apply.
        ["patch", "--quiet", "--no-backup-if-mismatch", str(dst), str(patch_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        diag = (result.stdout + result.stderr).strip()
        return False, f"patch failed:\n{diag}", None
    return True, "", dst


# ---------------------------------------------------------------------------
# Stage 2: compile
# ---------------------------------------------------------------------------

def _compile(source: Path, clangpp: str, work_dir: Path) -> Tuple[bool, str]:
    binary = work_dir / "validate_binary"
    extra = (
        [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"]
        if Path(_LLVM_LIBCXX).exists() else []
    ) + _macos_sysroot_flag()
    cmd = [clangpp, str(source), "-o", str(binary), "-g", "-O1"] + extra
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    if result.returncode != 0:
        return False, result.stderr[-2000:]
    return True, ""


def _compile_variant(
    source: Path, clangpp: str, work_dir: Path, name: str, openmp: bool, optimize: str = "-O2"
) -> Tuple[bool, str, Optional[Path]]:
    """Compile `source` to a runnable binary, with or without OpenMP.

    Used by the correctness and performance stages: the same source compiled
    without -fopenmp runs sequentially (pragmas ignored), with -fopenmp runs
    in parallel.  Comparing the two isolates the effect of the pragma.
    """
    binary = work_dir / name
    extra = (
        [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"]
        if Path(_LLVM_LIBCXX).exists() else []
    ) + (
        [f"-L{_LIBOMP_DIR}", f"-Wl,-rpath,{_LIBOMP_DIR}"]
        if (openmp and Path(_LIBOMP_DIR).exists()) else []
    ) + _macos_sysroot_flag()
    cmd = [clangpp, str(source), "-o", str(binary), optimize]
    if openmp:
        cmd.append("-fopenmp")
    cmd += extra
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    if result.returncode != 0:
        return False, result.stderr[-1500:], None
    return True, "", binary


def _run_timed(
    binary: Path, work_dir: Path, binary_args: Optional[list], repeats: int = 3
) -> Tuple[bool, str, float, str]:
    """Run `binary` `repeats` times; return (ok, stdout, best_wall_seconds, diag).

    Uses the minimum wall time across runs — the least noise-inflated sample.
    """
    import time as _time
    args = [str(binary)] + (binary_args or [])
    best = float("inf")
    stdout = ""
    for _ in range(max(1, repeats)):
        try:
            t0 = _time.perf_counter()
            r = subprocess.run(args, capture_output=True, text=True, timeout=120, cwd=work_dir)
            dt = _time.perf_counter() - t0
        except subprocess.TimeoutExpired:
            return False, "", 0.0, "run timed out (120 s)"
        if r.returncode != 0:
            return False, r.stdout, 0.0, f"non-zero exit ({r.returncode}):\n{r.stderr[-500:]}"
        stdout = r.stdout
        best = min(best, dt)
    return True, stdout, best, ""


def _measure_speedup(
    seq_bin: Path, par_bin: Path, work_dir: Path, binary_args: Optional[List[str]],
    pairs: int = 5, min_pairs: int = 3, threshold: Optional[float] = None,
) -> Tuple[bool, float, float, float, str]:
    """Measure the parallel-over-sequential speedup with interleaved A/B pairs.

    Timing the two binaries in separate blocks lets a machine-load change during
    one block skew the ratio arbitrarily (observed: the same rewrite measuring
    1.12x on one run and 0.52x on the next while an LLM server loaded the box).
    Interleaving seq/par runs pairwise and taking the MEDIAN of the per-pair
    ratios cancels load drift: whatever the load was during a pair, it affected
    both sides of that pair's ratio.

    Runs up to `pairs` pairs but stops after `min_pairs` once the verdict is no
    longer in doubt — the running median sits well clear of `threshold` (the
    accept cutoff) in either direction.  Measurement is the single most
    expensive part of the gate (2 program runs per pair), and a rewrite that is
    3x faster or 3x slower does not need five pairs to prove it; only genuinely
    borderline ratios spend the full budget.

    Returns (ok, median_ratio, best_seq_seconds, best_par_seconds, diag).
    """
    import statistics
    import time as _time

    ratios: List[float] = []
    best_seq = best_par = float("inf")
    for done in range(max(1, pairs)):
        if (threshold is not None and done >= min_pairs and ratios
                and not (0.75 * threshold < statistics.median(ratios) < 1.35 * threshold)):
            break
        pair_times = []
        for binary in (seq_bin, par_bin):
            args = [str(binary)] + (binary_args or [])
            try:
                t0 = _time.perf_counter()
                r = subprocess.run(args, capture_output=True, text=True,
                                   timeout=120, cwd=work_dir)
                dt = _time.perf_counter() - t0
            except subprocess.TimeoutExpired:
                return False, 0.0, 0.0, 0.0, "speedup measurement timed out (120 s)"
            if r.returncode != 0:
                return False, 0.0, 0.0, 0.0, (
                    f"speedup measurement: non-zero exit ({r.returncode}):\n"
                    f"{r.stderr[-500:]}"
                )
            pair_times.append(dt)
        seq_t, par_t = pair_times
        best_seq, best_par = min(best_seq, seq_t), min(best_par, par_t)
        if par_t > 0:
            ratios.append(seq_t / par_t)
    if not ratios:
        return False, 0.0, 0.0, 0.0, "speedup measurement produced no valid samples"
    return True, statistics.median(ratios), best_seq, best_par, ""


# ---------------------------------------------------------------------------
# Stage 3: ThreadSanitizer
# ---------------------------------------------------------------------------

def _tsan_env() -> dict:
    """Environment for the ThreadSanitizer run.

    TSan is by far the most expensive stage of the gate: on a 0.2 s benchmark
    kernel the sanitized parallel build took 37 s (185x).  Almost all of that is
    spent AFTER the first race is found — the default is to report and keep
    going, unwinding a stack for every further racing access.  We only ever use
    the first warning block, so `halt_on_error=1` stops at exactly the point
    where the rest of the run stopped mattering: measured on the same kernel,
    37 s -> 0.7 s with the race still reported on 3 runs out of 3.

    Deliberately NOT set here: OMP_NUM_THREADS.  Capping it to 4 on this
    8-thread machine was even faster, but the race then went undetected on 2
    runs out of 2 — a gate that passes because it looked less hard is worse
    than a slow one.  Detection is probabilistic; keep every thread the machine
    would really use.  (Set OMP_NUM_THREADS yourself and it is respected.)
    """
    import os

    env = dict(os.environ)
    existing = env.get("TSAN_OPTIONS", "")
    env["TSAN_OPTIONS"] = (existing + ":" if existing else "") + "halt_on_error=1"
    return env


def _tsan(
    source: Path, clangpp: str, work_dir: Path, skip_race_check: bool = False,
    binary_args: Optional[List[str]] = None,
) -> Tuple[bool, str, str]:
    """Compile with -fopenmp + TSan and run.

    Returns (ok, diagnostic, stage).  The stage distinguishes the two very
    different failure modes of this step:
      - "openmp_compile" : the OpenMP build failed.  Enabling -fopenmp activates
                           the `#pragma omp parallel for`, and the compiler then
                           enforces OpenMP-canonical loop form.  A loop the plain
                           (stage-2) compile accepted — e.g. `for(i; i+1<n; ...)`
                           or one containing `break` — is rejected here.  This is
                           NOT a data race; it means the loop is not in a form
                           OpenMP can parallelize.
      - "tsan"           : the build ran and ThreadSanitizer reported a real race.

    When `skip_race_check` is set, the OpenMP build is still compiled (so an
    openmp_compile error is still caught) but a reported race is IGNORED — used
    to re-verify a suspected OMP-barrier false positive against the correctness
    and performance gates instead of rejecting it on the race alone.
    """
    binary = work_dir / "tsan_binary"
    extra = (
        [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"]
        if Path(_LLVM_LIBCXX).exists() else []
    ) + (
        [f"-L{_LIBOMP_DIR}", f"-Wl,-rpath,{_LIBOMP_DIR}"]
        if Path(_LIBOMP_DIR).exists() else []
    ) + _macos_sysroot_flag()
    # -fopenmp is required so that #pragma omp parallel for actually runs in
    # parallel; without it TSan never sees cross-thread access on loop vars.
    cmd = [
        clangpp, str(source), "-o", str(binary),
        "-fsanitize=thread", "-fopenmp", "-g", "-O1",
    ] + extra
    compile_result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    if compile_result.returncode != 0:
        return (
            False,
            f"OpenMP compile failed (loop not in OpenMP-canonical form):\n"
            f"{compile_result.stderr[-1000:]}",
            "openmp_compile",
        )

    if skip_race_check:
        # Compile succeeded; deliberately do not run TSan / inspect for races.
        return True, "", "tsan"

    try:
        # Sanitized builds run 5-15x slower than native, so this timeout must
        # exceed the native run timeout (120 s), not undercut it.
        run_result = subprocess.run(
            [str(binary)] + (binary_args or []),
            capture_output=True, text=True, timeout=300, cwd=work_dir,
            env=_tsan_env(),
        )
    except subprocess.TimeoutExpired:
        return False, (
            "TSan run timed out (300 s) — the sanitized build is too slow to "
            "check this workload for races"
        ), "tsan"

    stderr = run_result.stderr
    if "WARNING: ThreadSanitizer" in stderr or "DATA RACE" in stderr:
        # Extract just the first warning block (up to and including the first SUMMARY line)
        warning_idx = stderr.find("WARNING: ThreadSanitizer")
        if warning_idx >= 0:
            snippet = stderr[warning_idx:]
            summary_idx = snippet.find("SUMMARY: ThreadSanitizer")
            if summary_idx >= 0:
                newline_after = snippet.find("\n", summary_idx)
                snippet = snippet[: newline_after + 1 if newline_after >= 0 else summary_idx + 200]
        else:
            snippet = stderr[-1000:]
        return False, f"Race detected:\n{snippet}", "tsan"
    if run_result.returncode != 0:
        # No race reported but the sanitized binary crashed — that is not a
        # pass; surface it instead of silently treating it as race-free.
        return False, (
            f"TSan run exited non-zero ({run_result.returncode}) without a race "
            f"report:\n{stderr[-500:]}"
        ), "tsan"
    return True, "", "tsan"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def capture_reference(
    source_file: str, binary_args: Optional[list] = None
) -> Tuple[Optional[str], Optional[float]]:
    """Compile the unmodified source (-O2, no OpenMP/TSan) and run it to capture
    (stdout, best wall seconds) as the golden reference.  The time is the
    baseline for the performance gate's net check: a restructured program's
    parallel build must beat the ORIGINAL sequential program, not merely its own
    (possibly overhead-slowed) sequential build.  Returns (None, None) if the
    program cannot be built or run, in which case both checks are skipped for
    the session.
    """
    clangpp = _find_clangpp()
    if clangpp is None:
        return None, None
    with tempfile.TemporaryDirectory(prefix="dp_agent_ref_") as tmp:
        work_dir = Path(tmp)
        dst = work_dir / Path(source_file).name
        shutil.copy2(source_file, dst)
        ok, _, binary = _compile_variant(dst, clangpp, work_dir, "ref_binary", openmp=False)
        if not ok or binary is None:
            return None, None
        ok, stdout, best_t, _ = _run_timed(binary, work_dir, binary_args, repeats=3)
        return (stdout, best_t) if ok else (None, None)


def validate(
    diff: str,
    source_file: str,
    reference_output: Optional[str] = None,
    binary_args: Optional[list] = None,
    require_speedup: bool = False,
    min_speedup: float = 1.0,
    skip_race_check: bool = False,
    reference_time: Optional[float] = None,
) -> ValidationResult:
    """Run the quality-gate stages. Return the first failure or success.

    Stages: apply → compile → tsan/openmp_compile → correctness → performance.

    - tsan (only when the diff carries a `#pragma omp`): a pragma-less rewrite
      is single-threaded, so there is nothing to race — running the sanitizer
      on it would only cost time.
    - correctness (when `reference_output` is given): the patched program,
      compiled WITH -fopenmp, must reproduce the reference stdout exactly.
      Catches restructurings that change observable results.
    - performance (when `require_speedup` and the diff adds a `#pragma omp`):
      interleaved A/B measurement; the parallel build must run at least
      `min_speedup`× faster than the same source built sequentially AND —
      when `reference_time` is given — must not be slower than the ORIGINAL
      program (guards against a rewrite whose own sequential build is
      overhead-slowed making the ratio look good on a losing patch).
    """
    clangpp = _find_clangpp()
    if clangpp is None:
        return ValidationResult(
            passed=False, stage="compile",
            diagnostic="No supported clang++ found (checked 19-based paths)",
        )

    with tempfile.TemporaryDirectory(prefix="dp_agent_val_") as tmp:
        work_dir = Path(tmp)

        # Stage 1
        ok, diag, patched = _apply(diff, source_file, work_dir)
        if not ok:
            return ValidationResult(passed=False, stage="apply", diagnostic=diag)
        assert patched is not None  # _apply returns the path when ok is True

        # Stage 2
        ok, diag = _compile(patched, clangpp, work_dir)
        if not ok:
            return ValidationResult(passed=False, stage="compile", diagnostic=diag)

        # Track stages this diff's own gating rules never attempt, independent
        # of pass/fail, so the terminal renderer doesn't show a false "passed"
        # for a check that literally never ran.
        skipped_stages: List[str] = []

        # Stage 3 — only pragma-bearing patches can race
        if "pragma omp" in diff:
            ok, diag, stage = _tsan(
                patched, clangpp, work_dir,
                skip_race_check=skip_race_check, binary_args=binary_args,
            )
            if not ok:
                return ValidationResult(passed=False, stage=stage, diagnostic=diag,
                                        skipped_stages=skipped_stages)
        else:
            skipped_stages += ["openmp_compile", "tsan"]

        # Stage 4 — semantic correctness (observable output must be unchanged)
        if reference_output is not None:
            ok, diag, par_bin = _compile_variant(
                patched, clangpp, work_dir, "correctness_par", openmp=True
            )
            if not ok or par_bin is None:
                return ValidationResult(passed=False, stage="correctness",
                                        diagnostic=f"parallel build failed:\n{diag}",
                                        skipped_stages=skipped_stages)
            ok, out, _, rdiag = _run_timed(par_bin, work_dir, binary_args, repeats=1)
            if not ok:
                return ValidationResult(passed=False, stage="correctness",
                                        diagnostic=f"parallel run failed: {rdiag}",
                                        skipped_stages=skipped_stages)
            if out != reference_output:
                return ValidationResult(
                    passed=False, stage="correctness",
                    diagnostic=(
                        "Program output changed — restructuring is NOT semantically "
                        "equivalent.\n"
                        f"--- expected (original) ---\n{reference_output[:600]}\n"
                        f"--- got (patched) ---\n{out[:600]}"
                    ),
                    skipped_stages=skipped_stages,
                )

        # Stage 5 — measured speedup (only for patches that add a pragma)
        measured: Optional[float] = None
        if not (require_speedup and "pragma omp" in diff):
            skipped_stages.append("performance")
        if require_speedup and "pragma omp" in diff:
            # The two builds are independent (different binaries, same input) —
            # compile them concurrently rather than one after another. Safe:
            # subprocess.run releases the GIL while the child runs, so this is
            # genuine OS-level parallelism, not GIL-limited. The actual TIMED
            # runs later (_measure_speedup) must stay strictly sequential —
            # running them concurrently would have them compete for the CPU
            # and corrupt the very wall-clock comparison we're measuring.
            with ThreadPoolExecutor(max_workers=2) as pool:
                fut_seq = pool.submit(
                    _compile_variant, patched, clangpp, work_dir, "perf_seq", False
                )
                fut_par = pool.submit(
                    _compile_variant, patched, clangpp, work_dir, "perf_par", True
                )
                ok_s, diag_s, seq_bin = fut_seq.result()
                ok_p, diag_p, par_bin = fut_par.result()
            if not (ok_s and ok_p and seq_bin and par_bin):
                # A failed measurement must not count as a pass.
                return ValidationResult(
                    passed=False, stage="performance",
                    diagnostic=f"speedup measurement build failed:\n{diag_s or diag_p}",
                    skipped_stages=skipped_stages,
                )
            m_ok, measured, seq_t, par_t, m_diag = _measure_speedup(
                seq_bin, par_bin, work_dir, binary_args, threshold=min_speedup
            )
            if not m_ok:
                return ValidationResult(passed=False, stage="performance",
                                        diagnostic=m_diag, skipped_stages=skipped_stages)
            if measured < min_speedup:
                return ValidationResult(
                    passed=False, stage="performance",
                    diagnostic=(
                        f"No speedup from parallelization: measured "
                        f"{measured:.2f}× (median of interleaved pairs; best "
                        f"sequential {seq_t*1e3:.1f} ms vs best parallel "
                        f"{par_t*1e3:.1f} ms), below the required "
                        f"{min_speedup:.2f}×."
                    ),
                    measured_speedup=measured,
                    skipped_stages=skipped_stages,
                )
            if reference_time is not None and par_t > reference_time:
                return ValidationResult(
                    passed=False, stage="performance",
                    diagnostic=(
                        f"Net regression vs the ORIGINAL program: parallel build "
                        f"{par_t*1e3:.1f} ms vs original sequential "
                        f"{reference_time*1e3:.1f} ms (the rewrite's own "
                        f"sequential baseline is slower than the original, so "
                        f"its {measured:.2f}× ratio does not translate into a "
                        f"real gain)."
                    ),
                    measured_speedup=measured,
                    skipped_stages=skipped_stages,
                )

    return ValidationResult(passed=True, stage="accepted", measured_speedup=measured,
                            skipped_stages=skipped_stages)
