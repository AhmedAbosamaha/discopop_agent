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
from pathlib import Path
from typing import Optional, Tuple

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


# ---------------------------------------------------------------------------
# Stage 3: ThreadSanitizer
# ---------------------------------------------------------------------------

def _tsan(
    source: Path, clangpp: str, work_dir: Path, skip_race_check: bool = False
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
        run_result = subprocess.run(
            [str(binary)], capture_output=True, text=True, timeout=60, cwd=work_dir
        )
    except subprocess.TimeoutExpired:
        return False, "TSan run timed out (60 s)", "tsan"

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
    return True, "", "tsan"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def capture_reference_output(source_file: str, binary_args: Optional[list] = None) -> Optional[str]:
    """Compile the unmodified source (-O2, no OpenMP/TSan) and run it once to
    capture its stdout as the golden reference.  Returns None if it cannot be
    built or run, in which case correctness checking is skipped for the session.
    """
    clangpp = _find_clangpp()
    if clangpp is None:
        return None
    with tempfile.TemporaryDirectory(prefix="dp_agent_ref_") as tmp:
        work_dir = Path(tmp)
        dst = work_dir / Path(source_file).name
        shutil.copy2(source_file, dst)
        ok, _, binary = _compile_variant(dst, clangpp, work_dir, "ref_binary", openmp=False)
        if not ok or binary is None:
            return None
        ok, stdout, _, _ = _run_timed(binary, work_dir, binary_args, repeats=1)
        return stdout if ok else None


def validate(
    diff: str,
    source_file: str,
    reference_output: Optional[str] = None,
    binary_args: Optional[list] = None,
    require_speedup: bool = False,
    min_speedup: float = 1.0,
    skip_race_check: bool = False,
) -> ValidationResult:
    """Run the quality-gate stages. Return the first failure or success.

    Stages: apply → compile → tsan/openmp_compile → correctness → performance.

    - correctness (when `reference_output` is given): the patched program,
      compiled WITH -fopenmp, must reproduce the reference stdout exactly.
      Catches restructurings that change observable results.
    - performance (when `require_speedup` and the diff adds a `#pragma omp`):
      the parallel build must run at least `min_speedup`× faster than the same
      source built sequentially.  Only meaningful for pragma-bearing patches.
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

        # Stage 3
        ok, diag, stage = _tsan(patched, clangpp, work_dir, skip_race_check=skip_race_check)
        if not ok:
            return ValidationResult(passed=False, stage=stage, diagnostic=diag)

        # Stage 4 — semantic correctness (observable output must be unchanged)
        if reference_output is not None:
            ok, diag, par_bin = _compile_variant(
                patched, clangpp, work_dir, "correctness_par", openmp=True
            )
            if not ok or par_bin is None:
                return ValidationResult(passed=False, stage="correctness",
                                        diagnostic=f"parallel build failed:\n{diag}")
            ok, out, _, rdiag = _run_timed(par_bin, work_dir, binary_args, repeats=1)
            if not ok:
                return ValidationResult(passed=False, stage="correctness",
                                        diagnostic=f"parallel run failed: {rdiag}")
            if out != reference_output:
                return ValidationResult(
                    passed=False, stage="correctness",
                    diagnostic=(
                        "Program output changed — restructuring is NOT semantically "
                        "equivalent.\n"
                        f"--- expected (original) ---\n{reference_output[:600]}\n"
                        f"--- got (patched) ---\n{out[:600]}"
                    ),
                )

        # Stage 5 — measured speedup (only for patches that add a pragma)
        measured: Optional[float] = None
        if require_speedup and "pragma omp" in diff:
            ok_s, _, seq_bin = _compile_variant(
                patched, clangpp, work_dir, "perf_seq", openmp=False
            )
            ok_p, _, par_bin = _compile_variant(
                patched, clangpp, work_dir, "perf_par", openmp=True
            )
            if ok_s and ok_p and seq_bin and par_bin:
                s_ok, _, seq_t, _ = _run_timed(seq_bin, work_dir, binary_args)
                p_ok, _, par_t, _ = _run_timed(par_bin, work_dir, binary_args)
                if s_ok and p_ok and par_t > 0:
                    measured = seq_t / par_t
                    if measured < min_speedup:
                        return ValidationResult(
                            passed=False, stage="performance",
                            diagnostic=(
                                f"No speedup from parallelization: measured "
                                f"{measured:.2f}× (sequential {seq_t*1e3:.1f} ms vs "
                                f"parallel {par_t*1e3:.1f} ms), below the required "
                                f"{min_speedup:.2f}×."
                            ),
                            measured_speedup=measured,
                        )

    return ValidationResult(passed=True, stage="accepted", measured_speedup=measured)
