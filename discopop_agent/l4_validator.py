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

def run_patch(target: Path, patch_path: Path) -> Tuple[bool, str]:
    """Apply `patch_path` to `target`, without any way to hang.

    GNU patch goes INTERACTIVE whenever it cannot work out what to do — "File
    to patch:", "Reversed (or previously applied) patch detected!  Assume -R?"
    — and reads the answer from stdin.  Under subprocess.run(capture_output=True)
    stdout and stderr are piped but stdin is inherited, so those prompts are
    invisible and the call blocks forever.  That really happened: a run sat on
    an unanswerable prompt for six minutes before it was killed.

    Three guards, each closing a different route to a hang:
      --batch            never ask; take the default for every question
      --forward          skip a patch that looks already applied instead of
                         asking about it (the case that hung: an earlier pragma
                         had already changed the lines this patch expected)
      stdin=DEVNULL      any prompt that still appears reads EOF and gives up
      timeout            a backstop — patch works in milliseconds, so anything
                         approaching a minute is pathological
    """
    try:
        r = subprocess.run(
            # --no-backup-if-mismatch: suppress <file>.orig backups on fuzzy apply.
            ["patch", "--batch", "--forward", "--quiet",
             "--no-backup-if-mismatch", str(target), str(patch_path)],
            capture_output=True, text=True,
            stdin=subprocess.DEVNULL, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, "patch timed out after 60 s (it should take milliseconds)"
    if r.returncode != 0:
        return False, (r.stdout + r.stderr).strip() or f"patch exited {r.returncode}"
    return True, ""


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

    ok, diag = run_patch(dst, patch_path)
    if not ok:
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

    Both the correctness and performance stages want the SAME `-O2 -fopenmp`
    binary, and `validate()` builds it once and memoises it.  The speedup
    comparison no longer builds a second, non-OpenMP variant: it varies
    OMP_NUM_THREADS on this one binary instead, so identical machine code sits
    on both sides of the ratio (see `_measure_speedup`).  `openmp=False` is
    therefore unused by the gate today and kept only for callers that want a
    genuinely sequential build.
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
    par_bin: Path, work_dir: Path, binary_args: Optional[List[str]],
    pairs: int = 5, min_pairs: int = 3, threshold: Optional[float] = None,
) -> Tuple[bool, float, float, float, str]:
    """Measure parallel scaling of ONE binary: 1 thread vs all threads.

    This used to compare two different builds — the source without `-fopenmp`
    against the source with it — and that made the ratio unattributable.
    `-fopenmp` changes codegen and layout, so part of any difference came from
    the compiler rather than from the parallelism, and near the 1.1x accept
    threshold that mattered: the same pragma on the same case measured 0.89x on
    one run and 1.10x on the next, straddling the cutoff.

    Running the SAME binary under `OMP_NUM_THREADS=1` and then unrestricted
    removes the compiler from the comparison entirely — identical machine code,
    identical layout, so whatever changes IS the parallelism.  It also drops one
    of the two builds the gate used to do.

    Interleaving the two settings pairwise and taking the MEDIAN of the per-pair
    ratios cancels machine-load drift: whatever the load was during a pair, it
    affected both sides of that pair's ratio.  Runs up to `pairs` pairs but
    stops after `min_pairs` once the running median sits well clear of
    `threshold` — a rewrite that is 3x faster or 3x slower does not need five
    pairs to prove it; only borderline ratios spend the full budget.

    Returns (ok, median_ratio, best_1_thread_seconds, best_n_thread_seconds, diag).
    """
    import os
    import statistics
    import time as _time

    base_env = dict(os.environ)
    one_thread = dict(base_env, OMP_NUM_THREADS="1")
    all_threads = {k: v for k, v in base_env.items() if k != "OMP_NUM_THREADS"}

    ratios: List[float] = []
    best_seq = best_par = float("inf")
    for done in range(max(1, pairs)):
        if (threshold is not None and done >= min_pairs and ratios
                and not (0.75 * threshold < statistics.median(ratios) < 1.35 * threshold)):
            break
        pair_times = []
        for env in (one_thread, all_threads):
            args = [str(par_bin)] + (binary_args or [])
            try:
                t0 = _time.perf_counter()
                r = subprocess.run(args, capture_output=True, text=True,
                                   timeout=120, cwd=work_dir, env=env)
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
    source_file: str, binary_args: Optional[list] = None,
    extra_inputs: Optional[List[List[str]]] = None,
) -> Tuple[Optional[str], Optional[float], Optional[List[Tuple[List[str], str]]]]:
    """Compile the unmodified source (-O2, no OpenMP/TSan) and record what it
    does, as the golden reference every rewrite is judged against.

    Returns (primary stdout, best wall seconds, [(argv, stdout), ...]).

    The time is the baseline for the performance gate's net check: the patched
    program at full threads must beat the ORIGINAL program, not merely its own
    single-thread run.

    `extra_inputs` are additional argument vectors to record.  One input proves
    very little about semantic equivalence — a rewrite can be right for the
    profiled size and wrong at 0, 1, or an odd count, which is exactly where
    re-derived loop bounds break — so each extra input becomes another output
    the rewrite must reproduce.  Inputs the ORIGINAL program cannot run cleanly
    are dropped with a warning rather than failing the run.
    """
    clangpp = _find_clangpp()
    if clangpp is None:
        return None, None, None
    with tempfile.TemporaryDirectory(prefix="dp_agent_ref_") as tmp:
        work_dir = Path(tmp)
        dst = work_dir / Path(source_file).name
        shutil.copy2(source_file, dst)
        ok, _, binary = _compile_variant(dst, clangpp, work_dir, "ref_binary", openmp=False)
        if not ok or binary is None:
            return None, None, None
        ok, stdout, best_t, _ = _run_timed(binary, work_dir, binary_args, repeats=3)
        if not ok:
            return None, None, None
        pairs: List[Tuple[List[str], str]] = [(list(binary_args or []), stdout)]
        for argv in extra_inputs or []:
            ok_i, out_i, _, diag_i = _run_timed(binary, work_dir, argv, repeats=1)
            if ok_i:
                pairs.append((list(argv), out_i))
            else:
                print(f"  [warn] check input {argv!r} does not run on the ORIGINAL "
                      f"program ({diag_i.splitlines()[0] if diag_i else 'failed'}) "
                      f"— dropped")
        return stdout, best_t, pairs


def validate(
    diff: str,
    source_file: str,
    reference_output: Optional[str] = None,
    reference_outputs: Optional[List[Tuple[List[str], str]]] = None,
    binary_args: Optional[list] = None,
    require_speedup: bool = False,
    min_speedup: float = 1.0,
    skip_race_check: bool = False,
    reference_time: Optional[float] = None,
    mode: str = "full",
) -> ValidationResult:
    """Run the quality-gate stages. Return the first failure or success.

    Stages: apply → compile → openmp_compile/tsan → correctness → performance.

    - openmp_compile / tsan (only when the diff carries a `#pragma omp`): a
      pragma-less rewrite is single-threaded, so there is nothing to race, and
      there is no pragma for clang to reject as non-canonical either.
    - correctness (when `reference_output` is given): the patched program,
      compiled WITH -fopenmp, must reproduce the reference stdout exactly.
      Catches restructurings that change observable results.  Note this is the
      PARALLEL binary — the stage that catches a race corrupting the output.
    `mode="safety"` runs everything except the timing: apply, compile, the
    -fopenmp build, ThreadSanitizer, and correctness.  It answers "is this
    change safe to insert?" and skips only the stage that asks whether it is
    WORTH inserting.  Tier-1 uses it, and the sanitizer is not optional there:
    correctness alone cannot catch a falsely-detected Do-All, because a racy
    pragma can still print the right answer on a small profiled input and be
    wrong at every other size.

    - performance (when `require_speedup` and the diff adds a `#pragma omp`):
      interleaved A/B on ONE binary, OMP_NUM_THREADS=1 against unrestricted;
      the median ratio must reach `min_speedup`× AND — when `reference_time` is
      given — the parallel run must not be slower than the ORIGINAL program
      (guards against a rewrite whose own single-threaded build is
      overhead-slowed making the ratio look flattering).
    """
    if mode not in ("safety", "full"):
        raise ValueError(f"validate(mode=): unknown mode {mode!r}")
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
            if skip_race_check:
                skipped_stages.append("tsan")
        else:
            skipped_stages += ["openmp_compile", "tsan"]

        # One -O2 -fopenmp build serves BOTH remaining stages: the correctness
        # run and, since the speedup measurement now varies OMP_NUM_THREADS
        # rather than the build, the timed runs too.  The gate used to compile
        # this same source three times.
        check_bin: Optional[Path] = None

        def _check_build() -> Tuple[bool, str]:
            nonlocal check_bin
            if check_bin is not None:
                return True, ""
            ok_b, diag_b, binary = _compile_variant(
                patched, clangpp, work_dir, "check_par", openmp=True
            )
            check_bin = binary
            return (ok_b and binary is not None), diag_b

        # Stage 4 — semantic correctness (observable output must be unchanged),
        # checked on EVERY recorded input, not just the profiled one.
        if reference_output is not None:
            ok, diag = _check_build()
            par_bin = check_bin
            if not ok or par_bin is None:
                return ValidationResult(passed=False, stage="correctness",
                                        diagnostic=f"parallel build failed:\n{diag}",
                                        skipped_stages=skipped_stages)
            cases = reference_outputs or [(list(binary_args or []), reference_output)]
            for argv, expected in cases:
                ok, out, _, rdiag = _run_timed(par_bin, work_dir, argv, repeats=1)
                where = f" for input {' '.join(argv)!r}" if argv else ""
                if not ok:
                    return ValidationResult(
                        passed=False, stage="correctness",
                        diagnostic=f"parallel run failed{where}: {rdiag}",
                        skipped_stages=skipped_stages)
                if out != expected:
                    return ValidationResult(
                        passed=False, stage="correctness",
                        diagnostic=(
                            f"Program output changed{where} — the patched "
                            "program is NOT semantically equivalent to the "
                            "original.\n"
                            + ("This input differs from the one the profile was taken "
                               "on: the rewrite is right for the profiled size but "
                               "wrong here, which usually means a loop bound, an "
                               "initial value, or a boundary case was carried over "
                               "from the old schedule instead of re-derived.\n"
                               if argv != list(binary_args or []) else "")
                            + f"--- expected (original) ---\n{expected[:600]}\n"
                            f"--- got (patched) ---\n{out[:600]}"
                        ),
                        skipped_stages=skipped_stages,
                    )

        # Stage 5 — measured speedup (only for patches that add a pragma)
        measured: Optional[float] = None
        want_perf = (
            mode != "safety" and require_speedup and "pragma omp" in diff
        )
        if not want_perf:
            skipped_stages.append("performance")
        if want_perf:
            ok_b, diag_b = _check_build()
            if not ok_b or check_bin is None:
                # A failed measurement must not count as a pass.
                return ValidationResult(
                    passed=False, stage="performance",
                    diagnostic=f"speedup measurement build failed:\n{diag_b}",
                    skipped_stages=skipped_stages,
                )
            # Same binary, 1 thread vs all — the compiler is out of the
            # comparison, so the ratio is attributable to the parallelism.
            m_ok, measured, seq_t, par_t, m_diag = _measure_speedup(
                check_bin, work_dir, binary_args, threshold=min_speedup
            )
            if not m_ok:
                return ValidationResult(passed=False, stage="performance",
                                        diagnostic=m_diag, skipped_stages=skipped_stages)
            if measured < min_speedup:
                return ValidationResult(
                    passed=False, stage="performance",
                    diagnostic=(
                        f"No speedup from parallelization: measured "
                        f"{measured:.2f}× (same binary, median of interleaved "
                        f"pairs; best at 1 thread {seq_t*1e3:.1f} ms vs best at "
                        f"all threads {par_t*1e3:.1f} ms), below the required "
                        f"{min_speedup:.2f}×."
                    ),
                    measured_speedup=measured,
                    skipped_stages=skipped_stages,
                )
            if reference_time is not None and par_t > reference_time:
                return ValidationResult(
                    passed=False, stage="performance",
                    diagnostic=(
                        f"Net regression vs the ORIGINAL program: this build at "
                        f"full threads takes {par_t*1e3:.1f} ms, the untouched "
                        f"original {reference_time*1e3:.1f} ms. The {measured:.2f}× "
                        f"scaling is real but starts from a slower baseline, so "
                        f"the user ends up with a slower program."
                    ),
                    measured_speedup=measured,
                    skipped_stages=skipped_stages,
                )

    return ValidationResult(passed=True, stage="accepted", measured_speedup=measured,
                            skipped_stages=skipped_stages)
