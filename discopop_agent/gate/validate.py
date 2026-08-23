"""
The quality gate — stage order, and the one place results are reused
----------------------------------------------------------------------
Stages, in order: apply -> compile -> openmp_compile/tsan -> correctness ->
performance.  Two of them are conditional on the diff carrying a `#pragma omp`,
because a pragma-less rewrite is single-threaded: there is nothing to race and
nothing to speed up.

`mode="safety"` runs everything except the timing — "is this change safe to
insert?" without "is it worth inserting?".

`_validate_cached` is the entry point every caller should use rather than
`validate` directly.  It reuses a verdict already computed for the same patch
against the same source bytes, and it re-verifies a suspected OMP-barrier
artefact with the race check off instead of trusting the heuristic.  Calling
`validate` raw skips both — which is how Phase A ran for a while without the
barrier re-check applying to LLM rewrites at all.
"""
from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from ..args import AgentArguments
from ..types import ValidationResult
from .patching import _apply, _compile, _compile_variant
from .timing import _measure_speedup, _run_timed
from .toolchain import _find_clangpp
from .tsan import _is_omp_barrier_false_positive, _tsan


def check_pragma_compiles(diff: str, source_file: str) -> Tuple[bool, str]:
    """Does this generated pragma survive an -fopenmp build?  One compile, no run.

    DiscoPoP reports `do_all` for loops whose generated pragma clang then
    rejects — a loop whose bound is a runtime value, or one still containing a
    `break`.  Phase A needs to know that BEFORE it keeps a rewrite, because
    "a pattern appeared" is not the same claim as "a pragma works", and the
    difference costs an LLM call and a re-profile to discover later.
    """
    clangpp = _find_clangpp()
    if clangpp is None:
        return False, "no supported clang++ found"
    with tempfile.TemporaryDirectory(prefix="dp_agent_pc_") as tmp:
        work = Path(tmp)
        ok, diag, patched = _apply(diff, source_file, work)
        if not ok or patched is None:
            return False, f"patch did not apply: {diag[:160]}"
        ok, diag, _b = _compile_variant(patched, clangpp, work, "pc", openmp=True)
        if not ok:
            return False, diag[:400]
    return True, ""


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


def _gate_key(diff: str, source_file: str, mode: str) -> str:
    """Identity of one gate run: this patch, against this exact source text,
    asking this set of questions.

    The source hash is what makes reuse safe — a patch validated before another
    region's pragma was applied says nothing about the file afterwards, and that
    case really happens (a rewrite exposes two loops; applying the first one's
    pragma changes the file the second is measured against).

    `mode` is in the key because the modes are not interchangeable: "safety"
    skips the timing runs, so serving one of its results to a "full" caller
    would silently report an unmeasured patch as fast enough.
    """
    h = hashlib.sha1()
    h.update(Path(source_file).read_bytes())
    h.update(b"\0")
    h.update(diff.encode())
    h.update(b"\0")
    h.update(mode.encode())
    return h.hexdigest()


def _validate_cached(
    cache: dict,
    diff: str,
    args: AgentArguments,
    reference_output: "str | None",
    binary_args: "list | None",
    reference_time: "float | None",
    reference_outputs: "list | None" = None,
    mode: str = "full",
) -> "tuple[ValidationResult, bool, bool]":
    """Run the gate on `diff`, or return the answer already computed for it.

    Returns (result, served_from_cache, barrier_false_positive_suspected).

    Both gate sites come through here: Tier-1 in mode="safety", the post-rewrite
    verification in mode="full".  Two reasons it is worth the indirection.

    The cache: one verification measures every pattern a rewrite exposed, and a
    later region can present an identical patch against identical source bytes —
    a full duplicate gate run (three compiles, a sanitizer run, a correctness
    run, and up to five timing pairs) for a verdict already known.

    The macOS OMP-barrier false-positive re-check: TSan reports a race between a
    write inside `.omp_outlined` and the main thread's read after the region,
    with no barrier edge it can see.  Legitimate pragmas trip it, so a `tsan`
    failure carrying that signature is re-verified with the race check off
    rather than being trusted.  Any caller that skips this wrapper rejects
    correct pragmas on macOS.
    """
    key = _gate_key(diff, args.source_file, mode)
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
            mode=mode,
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
