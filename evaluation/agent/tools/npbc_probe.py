#!/usr/bin/env python3
"""E11 feasibility probe (no model): can DiscoPoP analyse RepoOMP's serial NPB-C inputs?

For each of the eight NPB 3.0 C kernels in `benchmarks/RepoOMP` (the `<k>_#_omp.c` files —
the OpenMP version with every pragma removed, the exact inputs of RepoOMP's paper), the
probe generates `npbparams.h` with NPB's own `setparams` for the chosen class, compiles the
kernel plus NPB's `common/` sources through DiscoPoP's wrapper as ONE unity unit (as the
harness profiles a multi-file program), runs the instrumented binary and the explorer, and
records the three times, NPB's own verification verdict and the pattern counts.

    ~/discopop_agent/venv/bin/python agent/tools/npbc_probe.py --out agent/runs/e11_probe [--class S]

Output: `probe.csv`, `summary.json`, one directory per kernel with the logs.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_include  # noqa: E402
harness_include.install()   # every build finds prepared/_harness (D39)

HARNESS = Path(__file__).resolve().parents[2]
NPB = HARNESS / "benchmarks" / "RepoOMP" / "benchmark" / "NPB3.0-omp-C"
KERNELS = ["EP", "IS", "CG", "FT", "MG", "BT", "SP", "LU"]
COMMON = ["c_print_results.c", "c_randdp.c", "c_timers.c", "wtime.c"]
# which kernels link NPB's random-number unit (their Makefiles' OBJS); IS, BT, SP, LU carry their own or none
USES_RANDDP = {"CG", "EP", "FT", "MG"}


def _run(cmd: List[str], cwd: Path, env: Dict[str, str], timeout: float, log: Path) -> Tuple[int, float]:
    t0 = time.perf_counter()
    with open(log, "w") as f:
        try:
            rc = subprocess.run(cmd, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            rc = -9
    return rc, time.perf_counter() - t0


def probe(kernel: str, cls: str, out: Path, timeout: float) -> dict:
    k = kernel.lower()
    d = out / kernel
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    env = dict(os.environ)
    env["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{env.get('PATH', '')}"
    rec: dict = {"kernel": kernel, "class": cls, "lines": len((NPB / kernel / f"{k}_#_omp.c").read_text(errors="replace").splitlines())}
    # the program: the serial kernel under a plain name, its headers, NPB's common sources
    shutil.copy2(NPB / kernel / f"{k}_#_omp.c", d / f"{k}.c")
    for h in (NPB / kernel).glob("*.h"):
        shutil.copy2(h, d / h.name)
    (d / "common").mkdir()
    for f in [*COMMON, "npb-C.h", "wtime.h"]:
        shutil.copy2(NPB / "common" / f, d / "common" / f)
    # NPB's own parameter generator
    cc = shutil.which("clang-20") or shutil.which("clang") or "cc"
    subprocess.run([cc, "-O1", "-w", "-o", str(d / "setparams"), str(NPB / "sys" / "setparams.c")], check=False)
    # setparams reads ../config/make.def (compiler strings it echoes into npbparams.h)
    shutil.copytree(NPB / "config", out / "config", dirs_exist_ok=True)
    sp = subprocess.run([str(d / "setparams"), k, cls], cwd=d, capture_output=True, text=True)
    if not (d / "npbparams.h").exists():
        rec["error"] = f"setparams failed: {(sp.stdout + sp.stderr)[-200:]}"
        return rec
    unity = d / "unity.c"
    commons = [c for c in COMMON if c != "c_randdp.c" or kernel in USES_RANDDP]
    # common units FIRST: NPB 3.0 is pre-C99 (implicit declarations), and in one unit a call
    # seen before its definition would otherwise conflict with it
    unity.write_text("".join(f'#include "common/{c}"\n' for c in commons) + f'#include "{k}.c"\n')
    # The pragma-free files still call the OpenMP runtime API (omp_get_num_threads), so they
    # are built with -fopenmp as RepoOMP's Makefile does; with no pragma left they run serially.
    omp = ["-fopenmp", "-std=gnu89", "-w"]
    if platform.system() == "Darwin" and Path("/usr/local/opt/libomp").exists():
        omp += ["-I/usr/local/opt/libomp/include", "-L/usr/local/opt/libomp/lib"]
    rc, rec["instrument_s"] = _run(["discopop_cc", str(unity.resolve()), f"-I{d.resolve()}", f"-I{(d / 'common').resolve()}",
                                    *omp, "-o", "a.out", "-lm"], d, env, timeout, d / "instrument.log")
    unity.unlink(missing_ok=True)
    if rc != 0:
        rec["error"] = f"instrument rc={rc}"
        return rec
    rc, rec["run_s"] = _run(["./a.out"], d, env, timeout, d / "run.log")
    text = (d / "run.log").read_text(errors="replace")
    rec["npb_verification"] = ("SUCCESSFUL" if "SUCCESSFUL" in text else "UNSUCCESSFUL" if "UNSUCCESSFUL" in text else "?")
    if rc != 0:
        rec["error"] = f"profiled run rc={rc}"
        return rec
    rc, rec["explore_s"] = _run(["discopop_explorer"], d / ".discopop", env, timeout, d / "explore.log")
    if rc != 0:
        tail = [l for l in (d / "explore.log").read_text(errors="replace").splitlines() if l.strip()]
        rec["error"] = f"explorer rc={rc}: {tail[-1][:160] if tail else ''}"
        return rec
    pats = json.loads((d / ".discopop" / "explorer" / "patterns.json").read_text())["patterns"]
    rec["patterns"] = {kk: len(v) for kk, v in pats.items() if v}
    mapping = d / ".discopop" / "profiler" / "stateID_to_callpath_mapping.txt"
    rec["callpath_states"] = sum(1 for _ in open(mapping)) if mapping.exists() else None
    shutil.rmtree(d / ".discopop" / "profiler", ignore_errors=True)      # MBs; the probe keeps the verdicts
    for p in (d / "a.out", d / "setparams"):
        p.unlink(missing_ok=True)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--class", dest="cls", default="S")
    ap.add_argument("--kernels", default=",".join(KERNELS))
    ap.add_argument("--timeout", type=float, default=3600)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for kernel in [x for x in a.kernels.split(",") if x]:
        rec = probe(kernel, a.cls, out, a.timeout)
        rows.append(rec)
        print(f"{kernel:3s} {rec.get('lines', 0):5d} lines  instrument {rec.get('instrument_s', 0):7.1f}s  run {rec.get('run_s', 0):7.1f}s  "
              f"explore {rec.get('explore_s', 0):7.1f}s  states {rec.get('callpath_states')}  {rec.get('npb_verification', '')}  "
              f"{rec.get('patterns') or rec.get('error')}", flush=True)
        (out / "summary.json").write_text(json.dumps({"study": "E11 probe: DiscoPoP on RepoOMP's serial NPB-C inputs",
                                                        "host": platform.node(), "class": a.cls, "rows": rows}, indent=2) + "\n")
        with open(out / "probe.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["kernel", "class", "lines", "instrument_s", "run_s", "explore_s",
                                              "callpath_states", "npb_verification", "patterns", "error"], extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
