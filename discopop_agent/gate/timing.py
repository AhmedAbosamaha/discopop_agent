"""
Measuring whether a parallelization is actually faster
-------------------------------------------------------
All wall-clock measurement lives here, and it is all interleaved and
median-based for one reason: single-shot timings on a loaded machine flapped
between 1.12x and 0.52x for the same binary, which caused both false reverts and
false accepts.

The speedup is measured on ONE binary at `OMP_NUM_THREADS=1` against the same
binary unrestricted.  Comparing two builds instead — one with `-fopenmp`, one
without — made an unchanged program measure 0.89x and then 1.10x, because the
two builds differ by more than the pragma.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from .toolchain import _find_clangpp
from .patching import _compile_variant


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


def time_source(
    source_text: str, source_file: str, work_dir: Path, name: str,
    binary_args: Optional[list] = None, repeats: int = 5,
) -> Tuple[bool, float, str, str]:
    """Build `source_text` with -O2 -fopenmp; return (ok, best time, stdout, diag).

    Used by the marginal measurement, which needs to time two states of the same
    file.  Both sides are -fopenmp builds differing only by one pragma, so the
    compiler is out of the comparison — the mistake `_measure_speedup` documents
    (comparing an -fopenmp build against a non-fopenmp one) is not repeated here.
    """
    clangpp = _find_clangpp()
    if clangpp is None:
        return False, 0.0, "", "no supported clang++ found"
    src = work_dir / f"{name}_{Path(source_file).name}"
    src.write_text(source_text)
    ok, diag, binary = _compile_variant(src, clangpp, work_dir, name, openmp=True)
    if not ok or binary is None:
        return False, 0.0, "", f"build failed:\n{diag}"
    best = float("inf")
    out = ""
    for _ in range(max(1, repeats)):
        ok_r, out, dt, rdiag = _run_timed(binary, work_dir, binary_args, repeats=1)
        if not ok_r:
            return False, 0.0, "", f"run failed: {rdiag}"
        best = min(best, dt)
    return True, best, out, ""


def noise_floor(
    source_text: str, source_file: str, binary_args: Optional[list] = None,
    pairs: int = 5, trials: int = 3,
) -> Tuple[bool, float, str]:
    """Worst marginal ratio an UNCHANGED program produces on this machine.

    `measure_marginal` compares two states of a file; run it on two IDENTICAL
    states and every ratio should be 1.0.  It is not — on the development
    machine an unchanged example4 measured between 0.981 and 1.030 across six
    trials.  The keep/drop threshold has to sit below that floor, or run-to-run
    jitter alone starts discarding pragmas that cost nothing.

    Measured rather than assumed, because the floor is a property of the host
    and the program, not a constant: a hardcoded 0.97 happens to clear 0.981
    here and would be wrong on a noisier machine.

    Builds ONCE and times the same binary on both sides of each pair, so this
    costs one compile rather than the fourteen a full marginal run would.

    Critically it computes the SAME statistic the decision uses — the median of
    `pairs` ratios — repeated `trials` times, and returns the worst of those
    medians.  Taking the minimum of raw pair ratios instead measures a much
    wider distribution (0.88 vs 0.98 on the same machine) and would set a
    threshold loose enough to accept a real 12% regression.
    """
    import statistics
    clangpp = _find_clangpp()
    if clangpp is None:
        return False, 0.0, "no supported clang++ found"
    with tempfile.TemporaryDirectory(prefix="dp_agent_noise_") as tmp:
        work = Path(tmp)
        src = work / Path(source_file).name
        src.write_text(source_text)
        ok, diag, binary = _compile_variant(src, clangpp, work, "noise", openmp=True)
        if not ok or binary is None:
            return False, 0.0, f"build failed:\n{diag}"
        medians: List[float] = []
        for _ in range(max(1, trials)):
            ratios: List[float] = []
            for _ in range(max(1, pairs)):
                ok_a, _oa, ta, da = _run_timed(binary, work, binary_args, repeats=1)
                ok_b, _ob, tb, db = _run_timed(binary, work, binary_args, repeats=1)
                if not (ok_a and ok_b):
                    return False, 0.0, f"run failed: {da or db}"
                if tb > 0:
                    ratios.append(ta / tb)
            if ratios:
                medians.append(statistics.median(ratios))
    if not medians:
        return False, 0.0, "no valid timing samples"
    return True, min(medians), ""


def measure_marginal(
    before_text: str, after_text: str, source_file: str,
    binary_args: Optional[list] = None, pairs: int = 5,
) -> Tuple[bool, float, str]:
    """How much does the one change between these two states cost or save?

    Returns (ok, ratio, diag) where ratio = before / after — above 1.0 means the
    change made the program faster.  Both states are timed in the SAME temp dir,
    interleaved pair by pair so machine-load drift hits both sides of each pair,
    and the median of the per-pair ratios is taken.

    This is the per-region number that actually matters: what a pragma is worth
    in the program it will ship in, not in isolation.
    """
    import statistics
    ratios: List[float] = []
    with tempfile.TemporaryDirectory(prefix="dp_agent_marg_") as tmp:
        work_dir = Path(tmp)
        for i in range(max(1, pairs)):
            ok_b, tb, _ob, diag_b = time_source(before_text, source_file, work_dir,
                                                f"before{i}", binary_args, repeats=1)
            if not ok_b:
                return False, 0.0, diag_b
            ok_a, ta, _oa, diag_a = time_source(after_text, source_file, work_dir,
                                                f"after{i}", binary_args, repeats=1)
            if not ok_a:
                return False, 0.0, diag_a
            if ta > 0:
                ratios.append(tb / ta)
    if not ratios:
        return False, 0.0, "no valid timing samples"
    return True, statistics.median(ratios), ""
