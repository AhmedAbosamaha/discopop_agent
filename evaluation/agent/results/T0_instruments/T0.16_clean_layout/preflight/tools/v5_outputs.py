#!/usr/bin/env python3
"""Pre-flight (1): is the program the same? v4 package against the v5 prototype, plain builds:
digest on the shipped input, digest on the perturbed input (seed 7), full dump — byte for byte."""
import hashlib
import os
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
SIZES = sys.argv[2].split(",") if len(sys.argv) > 2 else ["SMALL"]
names = sys.argv[3:] or sorted(p.name for p in V5.iterdir())


def run(srcs, incs, cpath, flags, args, exe):
    env = dict(os.environ, CPATH=str(cpath))
    r = subprocess.run([*_cc(), "-O2", *flags, *incs, *map(str, srcs), "-o", str(exe), "-lm"],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return "BUILD FAILED: " + r.stderr[-400:]
    p = subprocess.run([str(exe), *args], capture_output=True, text=True, timeout=900)
    return p.stdout if p.returncode == 0 else f"RUN FAILED rc={p.returncode}: {p.stderr[-200:]}"


bad = 0
with tempfile.TemporaryDirectory(prefix="v5out_") as tmp:
    t = Path(tmp)
    for n in names:
        row = []
        for size in SIZES:
            for tag, flags, args in (("digest", [], []), ("seed7", [], ["7"]), ("dump", ["-DPB_FULL_DUMP"], [])):
                f = [f"-D{size}_DATASET", *flags]
                o4 = run([V4 / n / f"{n}.c"], [], V4_H, f, args, t / "a4")
                o5 = run([V5 / n / f"{n}.c", V5 / n / "main.c"], [f"-I{V5 / n}"], V5_H, f, args, t / "a5")
                ok = o4 == o5 and not o4.startswith(("BUILD FAILED", "RUN FAILED")) and len(o4) > 0
                row.append(f"{size}/{tag}:{'same' if ok else 'DIFF'}"
                           + ("" if ok else f" [{o4[:120]!r} | {o5[:120]!r}]")
                           + (f" ({hashlib.sha256(o4.encode()).hexdigest()[:8]})" if ok and tag == 'dump' else ""))
                bad += not ok
        print(f"{n:6s} " + "  ".join(row), flush=True)
print(f"\n{len(names)} loops, sizes {SIZES}: {'ALL IDENTICAL' if not bad else str(bad) + ' DIFFERENCES'}")
