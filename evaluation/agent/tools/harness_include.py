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


def install() -> Path:
    """Put the harness directory first on ``CPATH`` (idempotent) and return it."""
    parts = [p for p in os.environ.get("CPATH", "").split(os.pathsep) if p]
    if str(HARNESS_INCLUDE) not in parts:
        os.environ["CPATH"] = os.pathsep.join([str(HARNESS_INCLUDE)] + parts)
    return HARNESS_INCLUDE
