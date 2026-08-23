"""
ThreadSanitizer: running it, and knowing when to believe it
-------------------------------------------------------------
The stage and the report analysis live together because neither is much use
without the other on this platform.

TSan only reports accesses it cannot order, and it learns the order from
synchronization it can see.  It cannot see OpenMP's: the barrier ending every
`parallel for` is inside libomp, which is not instrumented unless libarcher is
loaded.  Without archer a program whose second parallel loop reads what the
first one wrote — bit-identical over 20 runs at 1/2/4/8/16 threads — is reported
as a data race.

So `_is_omp_barrier_false_positive` reads the report itself.  The discriminator
is exact rather than statistical: both accesses inside the SAME `.omp_outlined`
function means one parallel region and a genuine race; DIFFERENT outlined
functions means a barrier separates them and they cannot overlap.  It is
disabled when the code uses `nowait` or tasks, which genuinely remove the
barrier — and nothing is ever accepted on it alone, since the caller re-runs the
gate with the race check off and the patch must still reproduce the output.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from .toolchain import (_LIBOMP_DIR, _LLVM_LIBCXX, _macos_sysroot_flag,
                        _tsan_env)


_OUTLINED_RE = re.compile(r"\.omp_outlined[A-Za-z0-9_.]*")
# Constructs that remove the barrier this reasoning depends on.  `nowait` drops
# the implicit barrier at the end of a worksharing region outright; a task can
# outlive the region that spawned it.  Either makes two distinct outlined
# regions genuinely concurrent, so Variant 3 must not fire.
_NO_BARRIER_RE = re.compile(r"\bnowait\b|#\s*pragma\s+omp\s+(?:task|taskloop)\b")
# TSan opens the first access with "Write of size 4 at 0x... by thread T1:" and
# the second with "Previous write of size 4 ... by main thread:" — capitalised
# only on the first.  Matching on "Read"/"Write" therefore saw ONE of the two
# accesses, which silently weakened every rule phrased as "all racing accesses".
_ACCESS_RE = re.compile(
    r"^\s*(?:Previous\s+)?(?:atomic\s+)?(?:read|write)\s+of size\s+\d+.*"
    r"\bby (?:main thread|thread T\d+):\s*$",
    re.IGNORECASE,
)


def _access_blocks(lines: List[str]) -> List[List[str]]:
    """The stack frames of each racing access in a TSan report, in order.

    An access line opens the block and the next blank line closes it; everything
    between is that access's stack.
    """
    blocks: List[List[str]] = []
    for idx, line in enumerate(lines):
        if _ACCESS_RE.search(line):
            frames = []
            for j in range(idx + 1, len(lines)):
                if not lines[j].strip():
                    break
                frames.append(lines[j])
            blocks.append(frames)
    return blocks


def _is_omp_barrier_false_positive(diagnostic: str, code: str = "") -> bool:
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
    access_blocks = _access_blocks(lines)

    # Variant 1: OpenMP REDUCTION gather.  libomp combines per-thread partials
    # inside its barrier (`.omp.reduction.reduction_func` called from
    # `__kmp_*barrier_gather`), under runtime-internal synchronization TSan
    # cannot see because libomp is not TSan-instrumented.  Conservative rule:
    # EVERY racing access must sit inside those runtime frames — an access in
    # plain user code (a genuine missing-reduction race) disqualifies.
    if access_blocks and all(
        any(".omp.reduction.reduction_func" in f or
            ("__kmp_" in f and "barrier" in f) for f in frames)
        for frames in access_blocks
    ):
        return True

    # Variant 3: two DIFFERENT parallel regions.  Every racing access sits
    # inside an outlined region, but not the SAME one — so a barrier separates
    # them and they cannot overlap.  Verified on this host: a program whose
    # second `parallel for` reads what the first one wrote (indices reversed, so
    # a different thread reads each element) is reported as a race, while being
    # bit-deterministic over 20 runs at 1/2/4/8/16 threads.  The distinction is
    # exact rather than statistical:
    #   same outlined function on both sides  -> one region, genuinely concurrent
    #   different outlined functions          -> a barrier between them
    # (Homebrew's libomp carries no TSan annotations — there is no libarcher —
    # so TSan sees none of OpenMP's synchronization.)  `code` is the source this
    # patch produces; when it uses `nowait` or tasks the barrier is not there to
    # reason about and this variant is skipped.
    if not (code and _NO_BARRIER_RE.search(code)):
        outlined: List[str] = []
        for frames in access_blocks:
            hit = next((_OUTLINED_RE.search(f) for f in frames
                        if ".omp_outlined" in f), None)
            if hit is None:
                outlined = []
                break
            outlined.append(hit.group(0))
        if len(outlined) >= 2 and len(set(outlined)) >= 2:
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
