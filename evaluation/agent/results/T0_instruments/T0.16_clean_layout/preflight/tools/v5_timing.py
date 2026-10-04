#!/usr/bin/env python3
"""Is the sequential original as fast in the two-file layout as in v4? The timed region (the harness's own
DP_TIMED_REGION_SECONDS), plain -O2 builds, N runs each, alternating.

    python v5_timing.py <v5 root> <SIZE> <runs> names...
"""
import os
import re
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO / "evaluation/agent/tools"))
sys.path.insert(0, str(REPO))
from harness_equivalence import _cc  # noqa: E402

V4 = REPO / "evaluation/agent/prepared/tsvc_b1"
V4_H = REPO / "evaluation/agent/prepared/_harness"
V5 = Path(sys.argv[1]) / "prepared/tsvc_c1"
V5_H = Path(sys.argv[1]) / "_harness"
SIZE, RUNS, names = sys.argv[2], int(sys.argv[3]), sys.argv[4:]


def build(srcs, incs, cpath, exe):
    r = subprocess.run([*_cc(), "-O2", f"-D{SIZE}_DATASET", *incs, *map(str, srcs), "-o", str(exe), "-lm"],
                       capture_output=True, text=True, env=dict(os.environ, CPATH=str(cpath)))
    assert r.returncode == 0, r.stderr[-400:]


def timed(exe):
    p = subprocess.run([str(exe)], capture_output=True, text=True, timeout=900)
    return float(re.search(r"DP_TIMED_REGION_SECONDS ([0-9.]+)", p.stderr).group(1))


with tempfile.TemporaryDirectory(prefix="v5time_") as tmp:
    t = Path(tmp)
    for n in names:
        build([V4 / n / f"{n}.c"], [], V4_H, t / "a4")
        build([V5 / n / f"{n}.c", V5 / n / "main.c"], [f"-I{V5 / n}"], V5_H, t / "a5")
        t4, t5 = [], []
        for _ in range(RUNS):
            t4.append(timed(t / "a4"))
            t5.append(timed(t / "a5"))
        m4, m5 = statistics.median(t4), statistics.median(t5)
        print(f"{n:6s} {SIZE}: v4 {m4:.3f}s (min {min(t4):.3f}, max {max(t4):.3f})   v5 {m5:.3f}s "
              f"(min {min(t5):.3f}, max {max(t5):.3f})   v5/v4 {m5 / m4:.3f}", flush=True)
