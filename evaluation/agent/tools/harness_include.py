"""Where every build finds the measurement harness (D39, 25 Sep 2026).

From packaging v4 a benchmark's files hold only the benchmark's own code; our measurement —
sizes, input, perturbation, timing, output — lives in a header under ``prepared/_harness/``,
OUTSIDE every benchmark directory. That is what keeps it out of sight: DiscoPoP instruments
only functions defined inside the project root (``DP_PROJECT_ROOT_DIR``, the directory it is
run in — `profiler/DiscoPoP/llvm_hooks/runOnFunction.cpp`, and the same rule in hotspot
detection), and no model's working copy holds a file from outside the package.

The header is found through ``CPATH``, which clang reads for every compile: the harness's own
builds, DiscoPoP's wrappers, the agent's gate (it inherits the environment) — one setting,
no change to any command line and no agent argument that could differ between arms.

Every tool that builds a package imports this module and calls ``install()`` before its
first build.
"""
from __future__ import annotations

import os
from pathlib import Path

HARNESS_INCLUDE = Path(__file__).resolve().parent.parent / "prepared" / "_harness"

# The allocator of every program a tool runs (E1-v5's smoke run, 4 Oct 2026; record §6).
# In packaging v5 the loop's function is CALLED once per repetition (48 times). A solution that allocates
# its scratch array inside the function and frees it again gets, from glibc, a fresh mapping on every call
# (a block above 32 MB is always mmap'ed and unmapped): every element page-faults anew, which costs more
# than the loop itself — Opus's and Sonnet's correct split of s211 ran at 0.69x and 0.73x of the sequential
# original for this reason alone, Fable's (a static buffer) at 2.2x. With the allocator told to serve every
# block from the heap and to keep freed memory (the three variables below — a common setting on HPC
# installations), the same two programs run at 1.85x and 2.07x and the others are unchanged. It is a
# property of how the program is RUN, the same for the original and every candidate, for the harness's
# verification and the agent's own speed check alike; no file and no prompt changes. glibc only: without
# effect on macOS, and under ThreadSanitizer (its own allocator).
# OFF until the author decides (`KEEP_FREED_MEMORY`); `DP_KEEP_FREED_MEMORY=1|0` overrides for a check.
KEEP_FREED_MEMORY = False
ALLOCATOR_ENV = {"MALLOC_MMAP_MAX_": "0", "MALLOC_TRIM_THRESHOLD_": "68719476736", "MALLOC_TOP_PAD_": "268435456"}


def allocator_env() -> dict:
    """The allocator variables in force ({} = glibc's defaults)."""
    on = os.environ.get("DP_KEEP_FREED_MEMORY", "1" if KEEP_FREED_MEMORY else "0") == "1"
    return dict(ALLOCATOR_ENV) if on else {}


def install() -> Path:
    """Put the harness directory first on ``CPATH`` (idempotent), set the allocator every program is run
    with (see above), and return the harness directory. Everything a tool starts inherits both."""
    parts = [p for p in os.environ.get("CPATH", "").split(os.pathsep) if p]
    if str(HARNESS_INCLUDE) not in parts:
        os.environ["CPATH"] = os.pathsep.join([str(HARNESS_INCLUDE)] + parts)
    os.environ.update(allocator_env())
    return HARNESS_INCLUDE
