#!/usr/bin/env python3
"""T0.1 — choose each kernel's verification size by measurement.

For every packaged kernel, the serial original is built at increasing PolyBench dataset sizes
and its timed computation (DP_TIMED_REGION_SECONDS) is measured. The verification size is the
smallest size whose median serial kernel time reaches ``--target`` seconds: below that, thread
start-up and timer noise are a large share of the measurement and a real speedup cannot show.
Larger sizes are not tried once the target is met, or after a run exceeds ``--cap``.

Run it pinned to the NUMA node the experiments use, e.g. on the server:

    numactl --cpunodebind=1 --membind=1 ~/discopop_agent/venv/bin/python \
        agent/tools/size_table.py --out agent/runs/t0_1_sizes

A second, smaller target (``--timing-target``) picks the *timing size* for the speed-check
experiment: the size at which the agent's own speed check times the program, while profiling
and correctness checks stay at the agent size. It is kept small because that check runs the
program many times per decision.

Writes ``sizes.csv`` (one row per kernel × size) and ``chosen.json`` (timing and verification
size per kernel, plus host, compiler and load) into ``--out``.
"""
from __future__ import annotations

import argparse
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
import bench  # noqa: E402
import csv
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

AGENT_DIR = Path(__file__).resolve().parent.parent
# Every packaged benchmark, kernels and applications alike: prepared/<suite>/<name>. The
# applications reuse the kernels' dataset names, so one table covers both, and the keys are
# the names the runner looks up in kernel_sizes.json.
PREPARED = AGENT_DIR / "prepared"
SIZES = ["SMALL", "STANDARD", "LARGE", "EXTRALARGE"]
REGION_RE = re.compile(r"^DP_TIMED_REGION_SECONDS\s+([0-9.eE+-]+)", re.M)


def _load() -> str:
    try:
        return " ".join(Path("/proc/loadavg").read_text().split()[:3])
    except OSError:
        return " ".join(f"{x:.2f}" for x in os.getloadavg())


def _run_once(binary: Path, cap: float) -> Optional[Dict[str, float]]:
    t0 = time.perf_counter()
    try:
        p = subprocess.run([str(binary)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                           text=True, timeout=cap)
    except subprocess.TimeoutExpired:
        return None
    wall = time.perf_counter() - t0
    m = REGION_RE.search(p.stderr)
    if p.returncode != 0 or not m:
        raise RuntimeError(f"{binary.name}: exit {p.returncode}, timer line {'found' if m else 'missing'}")
    return {"kernel": float(m.group(1)), "program": wall}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--kernels", default="", help="comma list (default: every packaged kernel not excluded)")
    ap.add_argument("--exclude", default="cholesky,trmm,durbin", help="kernels left out (weak oracles, §2)")
    ap.add_argument("--sizes", default=",".join(SIZES))
    ap.add_argument("--target", type=float, default=1.0, help="serial kernel seconds the verification size must reach")
    ap.add_argument("--timing-target", type=float, default=0.25,
                    help="serial kernel seconds the timing size (agent speed check) must reach")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--cap", type=float, default=300.0, help="seconds per run before giving up on larger sizes")
    ap.add_argument("--cc", default=os.environ.get("DP_CC", "clang-20"))
    ap.add_argument("--cxx", default=os.environ.get("DP_CXX", "clang++-20"),
                    help="compiler for the C++ benchmarks (the applications)")
    a = ap.parse_args()

    cc = shutil.which(a.cc) or a.cc
    cxx = shutil.which(a.cxx) or a.cxx
    excluded = {k for k in a.exclude.split(",") if k}
    # Keyed by the FULL name (suite/benchmark), because bare names collide: `lu` is both
    # polybench/lu and npb/lu, and a table keyed on the bare name silently gives one of them
    # the other's sizes. A bare name is still accepted on the command line when unambiguous.
    available = {f"{m.parent.parent.name}/{m.parent.name}": m.parent
                 for m in sorted(PREPARED.glob("*/*/meta.json"))}
    short: Dict[str, List[str]] = {}
    for full in available:
        short.setdefault(full.split("/")[1], []).append(full)
    asked: List[str] = ([k for k in a.kernels.split(",") if k] if a.kernels else sorted(available))
    kernels: List[str] = []
    for k in asked:
        if k in available:
            kernels.append(k)
        elif len(short.get(k, [])) == 1:
            kernels.append(short[k][0])
        elif short.get(k):
            raise SystemExit(f"{k!r} is ambiguous: {', '.join(short[k])} — name it in full")
        else:
            raise SystemExit(f"not packaged: {k} — see agent/prepared/")
    kernels = [k for k in kernels if k not in excluded]
    sizes = [s for s in a.sizes.split(",") if s]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    load_start = _load()
    rows: List[Dict[str, object]] = []
    chosen: Dict[str, Dict[str, object]] = {}
    with tempfile.TemporaryDirectory() as tmp:
        for k in kernels:
            bench_dir = available[k]          # prepared/<suite>/<name>, not prepared/<name>
            meta = json.loads((bench_dir / "meta.json").read_text())
            # One file, or a project's units and include directories (bench.py).
            inputs, tail_flags = bench.build_inputs(bench_dir, meta)
            # The applications are C++; the kernels are C. One table covers both, so the
            # compiler follows the benchmark rather than the command line.
            compiler = cc if meta.get("language", "c") == "c" else cxx
            pick: Optional[str] = None
            timing_pick: Optional[str] = None
            longest = ("", 0.0)
            for s in sizes:
                # The key is the full name (suite/benchmark); a filename cannot carry its "/".
                binary = Path(tmp) / f"{k.replace('/', '_')}.{s}"
                subprocess.run([compiler, "-O3", f"-D{s}_DATASET", *inputs, "-o", str(binary),
                                *tail_flags, "-lm"], check=True, capture_output=True)
                runs = []
                timed_out = False
                failure = ""
                for _ in range(a.repeats):
                    try:
                        r = _run_once(binary, a.cap)
                    except RuntimeError as e:      # e.g. a crash at a size the machine cannot hold
                        failure = str(e)
                        break
                    if r is None:
                        timed_out = True
                        break
                    runs.append(r)
                if failure:
                    rows.append({"kernel": k, "size": s, "runs": 0, "timed_out": False,
                                 "kernel_s_median": None, "program_s_median": None,
                                 "kernel_share": None, "failure": failure})
                    print(f"{k:18s} {s:10s} FAILED {failure}", flush=True)
                    break
                kern = statistics.median(r["kernel"] for r in runs) if runs else None
                prog = statistics.median(r["program"] for r in runs) if runs else None
                rows.append({"kernel": k, "size": s, "runs": len(runs), "timed_out": timed_out,
                             "kernel_s_median": kern, "program_s_median": prog,
                             "kernel_share": (kern / prog) if kern and prog else None})
                print(f"{k:18s} {s:10s} kernel {kern if kern is not None else 'timeout':>12} s", flush=True)
                if kern is not None and kern > longest[1]:
                    longest = (s, kern)
                if timed_out:
                    break
                if kern is not None and timing_pick is None and kern >= a.timing_target:
                    timing_pick = s
                if kern is not None and kern >= a.target:
                    pick = s
                    break
            chosen[k] = {"timing_size": timing_pick, "verification_size": pick,
                         "longest_measured": {"size": longest[0], "kernel_s": longest[1]}}

    with (out / "sizes.csv").open("w", newline="") as f:
        fields: List[str] = []
        for row in rows:                   # a failed size adds a `failure` column
            fields += [key for key in row if key not in fields]
        w = csv.DictWriter(f, fieldnames=fields or ["kernel"])
        w.writeheader()
        w.writerows(rows)
    cc_version = subprocess.run([cc, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    (out / "chosen.json").write_text(json.dumps({
        "study": "T0.1 verification size per kernel",
        "target_kernel_seconds": a.target, "repeats": a.repeats, "cap_seconds": a.cap,
        "host": platform.node(), "compiler": cc_version, "flags": "-O3 -D<SIZE>_DATASET",
        "numa_binding": subprocess.run(["numactl", "--show"], capture_output=True, text=True).stdout
        if shutil.which("numactl") else "numactl not available",
        "started": started, "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "load_start": load_start, "load_end": _load(), "kernels": chosen,
    }, indent=2))
    print(f"wrote {out / 'sizes.csv'} and {out / 'chosen.json'}")


if __name__ == "__main__":
    main()
