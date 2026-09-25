#!/usr/bin/env python3
"""T0.10 — the expert ceiling of the restructuring benchmarks (no model, no DiscoPoP).

For every packaged TSVC loop that has an expert reference solution: build the ORIGINAL
(serial, -O2) and the REFERENCE (-O2 -fopenmp) at each dataset size, run the original once
and the reference at each thread count, and record the timed-region seconds and whether the
two digests agree within the oracle's tolerance. A restructuring benchmark is only useful
for speed claims if its own expert solution is faster: this study says at which size (if
any) that holds on the machine the experiments run on, and sets the ceiling against which
the agent's speedup is reported.

Self-contained on purpose (it must be runnable beside a running experiment without touching
the harness tree): needs only the two source directories.

    python3 tsvc_ceiling.py --packages agent/prepared/tsvc --references agent/reference_solutions/tsvc \\
        --out agent/runs/t0_10_tsvc_ceiling --sizes LARGE,EXTRALARGE --threads 6,12 [--pin 1]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_include  # noqa: E402
harness_include.install()   # every build finds prepared/_harness (D39)

REGION_RE = re.compile(r"^DP_TIMED_REGION_SECONDS\s+([0-9.eE+-]+)", re.M)
TOL = 1e-9


def _run(cmd: List[str], threads: Optional[int], pin: Optional[int], timeout: float) -> Tuple[int, Optional[float], str]:
    env = dict(os.environ)
    if threads:
        env["OMP_NUM_THREADS"] = str(threads)
    prefix = ["numactl", f"--cpunodebind={pin}", f"--membind={pin}"] if pin is not None and shutil.which("numactl") else []
    try:
        p = subprocess.run([*prefix, *cmd], capture_output=True, text=True, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return -9, None, ""
    m = REGION_RE.findall(p.stderr)
    return p.returncode, (sum(float(x) for x in m) if m else None), p.stdout


def _digest(out: str) -> Dict[str, float]:
    return {k: float(v) for k, v in (l.split() for l in out.splitlines() if l.startswith("pb_"))}


def _rel(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or a.keys() != b.keys():
        return float("inf")
    return max(abs(a[k] - b[k]) / max(abs(a[k]), abs(b[k]), 1e-300) for k in a)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--packages", required=True, type=Path)
    ap.add_argument("--references", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--sizes", default="LARGE,EXTRALARGE")
    ap.add_argument("--threads", default="6,12")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--pin", type=int, default=None, help="NUMA node to bind to")
    ap.add_argument("--cc", default=shutil.which("clang-20") or shutil.which("clang") or "cc")
    ap.add_argument("--timeout", type=float, default=600)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    threads = [int(x) for x in a.threads.split(",") if x]
    omp_extra: List[str] = []
    if sys.platform == "darwin" and Path("/usr/local/opt/libomp").exists():
        omp_extra = ["-I/usr/local/opt/libomp/include", "-L/usr/local/opt/libomp/lib"]
    rows: List[dict] = []
    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    for ref in sorted(a.references.glob("*.c")):
        name = ref.stem
        pkg = a.packages / name / f"{name}.c"
        if not pkg.exists():
            continue
        for size in [s for s in a.sizes.split(",") if s]:
            with tempfile.TemporaryDirectory(prefix=f"t010_{name}_") as tmp:
                t = Path(tmp)
                b1 = subprocess.run([a.cc, "-O2", f"-D{size}_DATASET", str(pkg), "-o", str(t / "orig"), "-lm"],
                                    capture_output=True, text=True)
                b2 = subprocess.run([a.cc, "-O2", "-fopenmp", *omp_extra, f"-D{size}_DATASET", str(ref),
                                     "-o", str(t / "ref"), "-lm"], capture_output=True, text=True)
                if b1.returncode or b2.returncode:
                    rows.append({"loop": name, "size": size, "error": "build: " + (b1.stderr + b2.stderr)[-200:]})
                    continue
                seq: List[float] = []
                dig: Dict[str, float] = {}
                for _ in range(a.repeats):
                    rc, secs, out = _run([str(t / "orig")], None, a.pin, a.timeout)
                    if rc == 0 and secs is not None:
                        seq.append(secs)
                        dig = _digest(out)
                if not seq:
                    rows.append({"loop": name, "size": size, "error": "original did not run"})
                    continue
                row: dict = {"loop": name, "size": size, "serial_s": round(statistics.median(seq), 4)}
                for n in threads:
                    par: List[float] = []
                    err = 0.0
                    for _ in range(a.repeats):
                        rc, secs, out = _run([str(t / "ref")], n, a.pin, a.timeout)
                        if rc == 0 and secs is not None:
                            par.append(secs)
                            err = max(err, _rel(dig, _digest(out)))
                    if par:
                        row[f"ref_T{n}_s"] = round(statistics.median(par), 4)
                        row[f"speedup_T{n}"] = round(row["serial_s"] / statistics.median(par), 3)
                        row[f"rel_err_T{n}"] = err
                best = max([row.get(f"speedup_T{n}", 0) for n in threads] or [0])
                row["best_speedup"] = best
                row["correct"] = all(row.get(f"rel_err_T{n}", float("inf")) <= TOL for n in threads)
                rows.append(row)
                print(f"{name:7s} {size:10s} serial {row['serial_s']:8.3f}s  "
                      + "  ".join(f"T{n} {row.get(f'speedup_T{n}', 0):5.2f}x" for n in threads)
                      + f"  correct={row['correct']}", flush=True)
        fields = ["loop", "size", "serial_s", *[f"ref_T{n}_s" for n in threads], *[f"speedup_T{n}" for n in threads],
                  *[f"rel_err_T{n}" for n in threads], "best_speedup", "correct", "error"]
        with open(a.out / "ceiling.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        (a.out / "summary.json").write_text(json.dumps({
            "study": "T0.10 expert ceiling of the TSVC restructuring benchmarks", "host": platform.node(),
            "started": started, "finished": time.strftime("%Y-%m-%dT%H:%M:%S"), "compiler": a.cc,
            "threads": threads, "repeats": a.repeats, "numa_node": a.pin,
            "load": " ".join(Path("/proc/loadavg").read_text().split()[:3]) if Path("/proc/loadavg").exists() else None,
            "rows": rows}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
