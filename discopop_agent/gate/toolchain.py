"""
Finding the tools the gate needs, and the environment they run in
------------------------------------------------------------------
Three things that are all "where is X on this machine": the clang that can build
with `-fopenmp` and ThreadSanitizer, the macOS SDK it needs to find system
headers, and libarcher — the OMPT tool without which TSan cannot see OpenMP's
barriers and reports every pair of parallel regions as a race.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional


# Prefer LLVM 19 clang++ (same toolchain used for the profiler)
_CLANGPP_CANDIDATES = [
    "/usr/local/Cellar/llvm@19/19.1.7/bin/clang++",
    "/usr/local/bin/clang++-19",
    "clang++-19",
    "clang++",
]
# LLVM's own libc++ — named explicitly on macOS or the link fails with
# "library 'c++' not found".
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
# Stage 3: ThreadSanitizer
# ---------------------------------------------------------------------------


def find_archer() -> Optional[str]:
    """The libarcher OMPT tool, if this machine has one.

    ThreadSanitizer only reports accesses it cannot order, and it learns the
    order from synchronization it can see.  It cannot see OpenMP's: the barrier
    ending every `parallel for` is inside libomp, which is not instrumented.
    Archer bridges that — it subscribes to the runtime's OMPT callbacks and
    calls TSan's AnnotateHappensBefore/After on each one.

    Without it TSan reports a race between ANY two parallel regions touching the
    same data.  Measured here: a program whose second parallel loop reads what
    the first one wrote is bit-identical over 20 runs at 1/2/4/8/16 threads, and
    is reported as a race; with archer loaded it is clean, while a genuine race
    inside a single region is still caught.

    Homebrew builds libomp with -DOPENMP_ENABLE_OMPT_TOOLS=OFF, so no archer
    ships with it — build one with `discopop_agent/tools/build_archer.sh`.
    When there is none, the gate falls back to the _is_omp_barrier_false_positive
    heuristic in gate/tsan.py, which covers the barrier shape but not `nowait`
    or tasks.
    """
    import os

    explicit = os.environ.get("DP_ARCHER_LIB")
    if explicit:
        return explicit if Path(explicit).exists() else None
    for cand in (
        Path.home() / ".local/lib/libarcher.dylib",
        Path("/usr/local/opt/libomp/lib/libarcher.dylib"),
        Path("/opt/homebrew/opt/libomp/lib/libarcher.dylib"),
        Path.home() / ".local/lib/libarcher.so",
        Path("/usr/lib/llvm/lib/libarcher.so"),
    ):
        if cand.exists():
            return str(cand)
    return None


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
    opts = [env["TSAN_OPTIONS"]] if env.get("TSAN_OPTIONS") else []
    opts.append("halt_on_error=1")

    # Load archer when we have one, so TSan can see OpenMP's barriers instead of
    # reporting every pair of parallel regions as a race.  `ignore_noninstrumented_modules`
    # is archer's own recommendation, and it is only correct WITH archer: it
    # silences reports raised from inside the uninstrumented runtime, which is
    # exactly where the barrier artefacts surface.  Never set it on its own —
    # that would hide reports without adding the ordering that makes them wrong.
    archer = find_archer()
    if archer:
        env["OMP_TOOL_LIBRARIES"] = archer
        env["OMP_TOOL"] = "enabled"
        opts.append("ignore_noninstrumented_modules=1")

    env["TSAN_OPTIONS"] = ":".join(opts)
    return env
