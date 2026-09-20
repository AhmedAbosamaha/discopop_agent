#!/usr/bin/env python3
"""T0.4 — what speedup can the shared host resolve, and do concurrent lanes interfere?

One benchmark, two binaries built as the harness builds them (serial `-O3`; and, for a
parallel program without a model, the same source with Polly's auto-parallelisation), each
run `--repeats` times in three conditions:

  alone      one process, pinned to `--lane-cores` cores of one NUMA node (as a campaign job)
  lanes      `--lanes` copies at once, each pinned to its own disjoint set of cores
  unpinned   one process, no pinning (what a naive run gets)

For every condition the tool records the timed-region seconds of every run (the number the
harness's speedup is made of), their median, IQR, min/max and coefficient of variation, and
the ratio of two medians a run-to-run spread of that size can still distinguish: with
`--repeats` runs per side, a speedup below 1 + 2·CV is within the noise. Host load before
and after is recorded, since other users' jobs share the machine.

Output: `runs.csv` (one row per run), `summary.json`, `run.log`.

    ~/discopop_agent/venv/bin/python agent/tools/timing_noise.py --out agent/runs/t0_4_timing \\
        --benchmarks polybench/2mm,rodinia-3.1/hotspot --repeats 10 --lanes 4 --threads 12
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

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "shared")]
import bench as bench_tools  # noqa: E402
import cli  # noqa: E402

AGENT_DIR = HERE.parent
REGION_RE = re.compile(r"^DP_TIMED_REGION_SECONDS\s+([0-9.eE+-]+)", re.M)
POLLY = ["-mllvm", "-polly", "-mllvm", "-polly-parallel", "-mllvm", "-polly-process-unprofitable"]


def _load() -> str:
    try:
        return " ".join(Path("/proc/loadavg").read_text().split()[:3])
    except OSError:
        return " ".join(f"{x:.2f}" for x in os.getloadavg())


def _numa_nodes() -> List[List[int]]:
    """CPU ids per NUMA node, from /sys; one node holding every CPU when unknown."""
    nodes: List[List[int]] = []
    for d in sorted(Path("/sys/devices/system/node").glob("node[0-9]*")):
        cpus: List[int] = []
        for part in (d / "cpulist").read_text().strip().split(","):
            a, _, b = part.partition("-")
            cpus.extend(range(int(a), int(b or a) + 1))
        nodes.append(cpus)
    return nodes or [list(range(os.cpu_count() or 1))]


def _lane_sets(lane_cores: int, lanes: int, first_node: int = 0) -> List[Tuple[List[int], int]]:
    """`lanes` disjoint core sets of `lane_cores` cores, filling one NUMA node before the next,
    starting at `first_node` and wrapping — so the study can be placed on the node that is free."""
    out: List[Tuple[List[int], int]] = []
    nodes = _numa_nodes()
    order = list(range(first_node, len(nodes))) + list(range(0, first_node))
    for node_id in order:
        cpus = nodes[node_id]
        for i in range(0, len(cpus) - lane_cores + 1, lane_cores):
            out.append((cpus[i:i + lane_cores], node_id))
            if len(out) == lanes:
                return out
    raise SystemExit(f"cannot form {lanes} lanes of {lane_cores} cores on this host")


def _pin(cores: List[int], node: int) -> List[str]:
    if shutil.which("numactl"):
        return ["numactl", f"--physcpubind={','.join(map(str, cores))}", f"--membind={node}"]
    if shutil.which("taskset"):
        return ["taskset", "-c", ",".join(map(str, cores))]
    return []


def _build(root: Path, meta: dict, size: str, extra: List[str], openmp: bool, cc: str, cxx: str,
           out: Path) -> Tuple[bool, str]:
    inputs, tail = bench_tools.build_inputs(root, meta)
    compiler = cc if bench_tools.is_c(meta) else cxx
    cmd = [compiler, "-O3", f"-D{size}_DATASET", *extra, *inputs, "-o", str(out), *tail,
           *cli._toolchain_flags(openmp, bench_tools.is_c(meta)), *(["-lm"] if bench_tools.is_c(meta) else [])]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    return p.returncode == 0, (p.stdout + p.stderr)[-600:]


def _run_once(prefix: List[str], binary: Path, threads: Optional[int], timeout: float) -> Tuple[float, Optional[float], int]:
    env = dict(os.environ)
    if threads is not None:
        env["OMP_NUM_THREADS"] = str(threads)
    t0 = time.perf_counter()
    try:
        p = subprocess.run([*prefix, str(binary)], capture_output=True, text=True, env=env, timeout=timeout,
                           cwd=binary.parent)
    except subprocess.TimeoutExpired:
        return time.perf_counter() - t0, None, -9
    m = REGION_RE.findall(p.stderr)
    return time.perf_counter() - t0, (sum(float(x) for x in m) if m else None), p.returncode


def _stats(vals: List[float]) -> dict:
    if not vals:
        return {"n": 0}
    q = statistics.quantiles(vals, n=4) if len(vals) >= 2 else [vals[0]] * 3
    med = statistics.median(vals)
    cv = (statistics.pstdev(vals) / statistics.mean(vals)) if len(vals) > 1 and statistics.mean(vals) else 0.0
    return {"n": len(vals), "median_s": med, "iqr_s": q[2] - q[0], "min_s": min(vals), "max_s": max(vals),
            "cv": cv, "max_over_min": max(vals) / min(vals) if min(vals) else None,
            "resolvable_speedup": 1 + 2 * cv}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--benchmarks", default="polybench/2mm,rodinia-3.1/hotspot")
    ap.add_argument("--repeats", type=int, default=10)
    ap.add_argument("--lanes", type=int, default=4)
    ap.add_argument("--lane-cores", type=int, default=12)
    ap.add_argument("--first-node", type=int, default=0,
                   help=("NUMA node the first lane sits on (default 0). Set it to the free "
                         "node when the other one is busy: this tool pins each lane itself, "
                         "so running it UNDER `numactl --cpunodebind=N` makes every inner "
                         "pin to another node fail and the `alone` condition collects no "
                         "samples at all — which is how the 20 Sep pass was lost."))
    ap.add_argument("--threads", type=int, default=12, help="OMP threads for the parallel binary")
    ap.add_argument("--size", default="per_kernel", help="dataset size, or per_kernel (verification size)")
    ap.add_argument("--timeout", type=float, default=900)
    ap.add_argument("--serial-only", action="store_true",
                   help=("Measure the serial binary only. Polly's parallel build of `hotspot` "
                         "runs minutes per execution (it parallelises the stencil at the wrong "
                         "level), which is what stopped the first pass of this study; the "
                         "question the study asks — how much does a timed measurement vary on "
                         "this host — is answered by the serial binary alone."))
    ap.add_argument("--cc", default=None)
    ap.add_argument("--cxx", default=None)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    log = open(out / "run.log", "a")
    cxx = cli._find_tool(a.cxx, "AGENT_CXX", cli._CXX_CANDIDATES, "clang++")
    cc = cli._find_tool(a.cc, "AGENT_CC", cli._CC_CANDIDATES, "clang")
    lanes = _lane_sets(a.lane_cores, a.lanes, a.first_node)
    started, load0 = time.strftime("%Y-%m-%dT%H:%M:%S"), _load()
    rows: List[dict] = []
    summary: Dict[str, dict] = {}
    for name in [b for b in a.benchmarks.split(",") if b]:
        bench_dir = AGENT_DIR / "prepared" / name
        meta = bench_tools.load_meta(bench_dir)
        size = a.size if a.size != "per_kernel" else cli._verify_size("per_kernel", name)[0]
        print(f"== {name} at {size}", flush=True)
        with tempfile.TemporaryDirectory(prefix="t04_") as tmp:
            root = bench_tools.stage(bench_dir, Path(tmp) / "src", meta)
            binaries: Dict[str, Tuple[Path, Optional[int]]] = {}
            ok, err = _build(root, meta, size, [], False, cc, cxx, root / "serial")
            if not ok:
                print(f"   serial build failed: {err}", flush=True)
                continue
            binaries["serial"] = (root / "serial", None)
            if not a.serial_only:
                ok, err = _build(root, meta, size, POLLY, True, cc, cxx, root / "polly")
                if ok:
                    binaries["polly_parallel"] = (root / "polly", a.threads)
                else:
                    print(f"   polly build failed (serial only): {err[-200:]}", file=log, flush=True)
            summary[name] = {"size": size}
            for label, (binary, threads) in binaries.items():
                conds: Dict[str, List[float]] = {}
                # alone, pinned to the first lane
                cores, node = lanes[0]
                vals = []
                for i in range(a.repeats):
                    wall, region, rc = _run_once(_pin(cores, node), binary, threads, a.timeout)
                    rows.append({"benchmark": name, "binary": label, "condition": "alone", "lane": 0, "run": i + 1,
                                 "rc": rc, "wall_s": round(wall, 4), "region_s": region, "load": _load()})
                    if region is not None and rc == 0:
                        vals.append(region)
                conds["alone"] = vals
                # unpinned
                vals = []
                for i in range(a.repeats):
                    wall, region, rc = _run_once([], binary, threads, a.timeout)
                    rows.append({"benchmark": name, "binary": label, "condition": "unpinned", "lane": -1,
                                 "run": i + 1, "rc": rc, "wall_s": round(wall, 4), "region_s": region, "load": _load()})
                    if region is not None and rc == 0:
                        vals.append(region)
                conds["unpinned"] = vals
                # lanes: every lane runs its repeats concurrently
                procs = []
                for li, (cores, node) in enumerate(lanes):
                    script = (f"for i in $(seq {a.repeats}); do "
                              f"{' '.join(_pin(cores, node))} {binary} 2>&1 >/dev/null | grep DP_TIMED_REGION_SECONDS; done")
                    env = dict(os.environ)
                    if threads is not None:
                        env["OMP_NUM_THREADS"] = str(threads)
                    procs.append((li, subprocess.Popen(["bash", "-c", script], stdout=subprocess.PIPE, text=True,
                                                       env=env, cwd=binary.parent)))
                vals = []
                for li, p in procs:
                    try:
                        text, _ = p.communicate(timeout=a.timeout * a.repeats)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        text = ""
                    for i, m in enumerate(REGION_RE.findall(text)):
                        rows.append({"benchmark": name, "binary": label, "condition": f"{a.lanes}_lanes", "lane": li,
                                     "run": i + 1, "rc": 0, "wall_s": None, "region_s": float(m), "load": _load()})
                        vals.append(float(m))
                conds[f"{a.lanes}_lanes"] = vals
                summary[name][label] = {c: _stats(v) for c, v in conds.items()}
                for c, st in summary[name][label].items():
                    print(f"   {label:15s} {c:10s} n={st.get('n', 0):2d} median {st.get('median_s', 0):.4f}s "
                          f"cv {st.get('cv', 0):.3f} max/min {st.get('max_over_min') or 0:.3f} "
                          f"→ resolvable ≥ {st.get('resolvable_speedup', 0):.3f}×", flush=True)
                print(json.dumps({name: {label: summary[name][label]}}), file=log, flush=True)
            with open(out / "runs.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["benchmark", "binary", "condition", "lane", "run", "rc", "wall_s",
                                                  "region_s", "load"])
                w.writeheader()
                w.writerows(rows)
            (out / "summary.json").write_text(json.dumps({
                "study": "T0.4 timing noise and lane interference on the shared host", "host": platform.node(),
                "started": started, "finished": time.strftime("%Y-%m-%dT%H:%M:%S"), "load_start": load0,
                "load_end": _load(), "repeats": a.repeats, "lanes": [c for c, _ in lanes], "threads": a.threads,
                "cc": cc, "cxx": cxx, "benchmarks": summary}, indent=2) + "\n")
    print(f"wrote {out / 'runs.csv'} and summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
