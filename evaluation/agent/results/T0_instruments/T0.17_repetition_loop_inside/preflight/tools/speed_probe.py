#!/usr/bin/env python3
"""Time the package forms against each other — no model, no DiscoPoP, nothing of the repository written.

For every loop: the sequential ORIGINAL and the expert REFERENCE of each variant, built as the harness's own
verification builds them (`clang -O2 -D<SIZE>_DATASET`, the reference with `-fopenmp`), at the loop's
verification size, run on ONE lane (`numactl --physcpubind --membind`). The runs are interleaved: one
repetition of every variant, then the next repetition — so drift on the machine falls on all variants alike.
The time is the program's own timed region (`DP_TIMED_REGION_SECONDS`), the median over the repetitions.

    python3 speed_probe.py PROBE --cores 36-47 --node 1 --variants v4,c1,c2 --loops s000,s211 \
        --threads 6,12 --repeats 5 --out OUT.json

A variant name is a source tree of PROBE, optionally with `+lto` (built with -flto) — e.g. `c1+lto`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REGION_RE = re.compile(r"^DP_TIMED_REGION_SECONDS\s+([0-9.eE+-]+)", re.M)
TOL = 1e-9


def digest(out: str) -> Dict[str, float]:
    return {k: float(v) for k, v in (l.split() for l in out.splitlines() if l.startswith("pb_"))}


def rel(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or a.keys() != b.keys():
        return float("inf")
    return max((abs(a[k] - b[k]) / max(abs(a[k]), abs(b[k]), 1e-300)) for k in a)


def run(binary: Path, prefix: List[str], threads: Optional[int], timeout: float) -> Tuple[int, Optional[float], str]:
    env = dict(os.environ)
    if threads:
        env["OMP_NUM_THREADS"] = str(threads)
    try:
        p = subprocess.run([*prefix, str(binary)], capture_output=True, text=True, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return -9, None, ""
    m = REGION_RE.findall(p.stderr)
    return p.returncode, (sum(float(x) for x in m) if m else None), p.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("probe")
    ap.add_argument("--cores", required=True)
    ap.add_argument("--node", required=True)
    ap.add_argument("--variants", required=True)
    ap.add_argument("--loops", default="")
    ap.add_argument("--threads", default="6,12")
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cc", default="clang-20")
    ap.add_argument("--lto-flags", default="-flto")
    ap.add_argument("--size", default="", help="override every loop's size")
    a = ap.parse_args()
    probe = Path(a.probe).resolve()
    man = json.loads((probe / "manifest.json").read_text())
    threads = [int(x) for x in a.threads.split(",")]
    variants = a.variants.split(",")
    loops = a.loops.split(",") if a.loops else [n for n, r in man["loops"].items() if r["expert"]]
    # `--cores node` leaves the threads every core of the node (T0.10's set-up), anything else is a lane
    bind = f"--cpunodebind={a.node}" if a.cores == "node" else f"--physcpubind={a.cores}"
    prefix = ["numactl", bind, f"--membind={a.node}"] if shutil.which("numactl") else []
    work = Path(a.out).with_suffix(".build")
    work.mkdir(parents=True, exist_ok=True)
    result: Dict[str, object] = {"cores": a.cores, "node": a.node, "threads": threads, "repeats": a.repeats,
                                 "cc": a.cc, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "loops": {}}
    for n in loops:
        row = man["loops"][n]
        size = a.size or row["size"]
        if not size:
            print(f"{n}: no size — skipped", flush=True)
            continue
        bins: Dict[str, Dict[str, Path]] = {}
        notes: Dict[str, str] = {}
        for v in variants:
            tree, lto = (v[:-4], True) if v.endswith("+lto") else (v, False)
            if tree not in row["variants"]:
                continue
            units = [u.format(loop=n) for u in man["variants"][tree]["units"]]
            extra = (a.lto_flags.split() if lto else []) + (["-mcmodel=medium"] if tree == "c2arr" else [])
            bins[v] = {}
            for kind, omp in (("orig", False), ("ref", True)):
                src = probe / tree / n / kind
                if not src.is_dir():
                    continue
                out = work / f"{n}.{v}.{kind}"
                cmd = [a.cc, "-O2", f"-D{size}_DATASET", *extra, f"-I{src}", f"-I{probe / '_h'}",
                       *[str(src / u) for u in units], "-o", str(out), *(["-fopenmp"] if omp else []), "-lm"]
                p = subprocess.run(cmd, capture_output=True, text=True)
                if p.returncode != 0:
                    notes[f"{v}.{kind}"] = "build failed: " + p.stderr.strip()[-300:]
                    continue
                bins[v][kind] = out
        times: Dict[str, Dict[str, List[float]]] = {v: {"seq": [], **{f"T{t}": [] for t in threads}} for v in bins}
        seq_digest: Dict[str, Dict[str, float]] = {}
        worst: Dict[str, float] = {v: 0.0 for v in bins}
        for _rep in range(a.repeats):
            for v, b in bins.items():
                if "orig" in b:
                    rc, t, out = run(b["orig"], prefix, None, 1800)
                    if rc != 0 or t is None:
                        notes[f"{v}.orig"] = f"run failed rc={rc}"
                    else:
                        times[v]["seq"].append(t)
                        seq_digest[v] = digest(out)
                if "ref" in b:
                    for tc in threads:
                        rc, t, out = run(b["ref"], prefix, tc, 1800)
                        if rc != 0 or t is None:
                            notes[f"{v}.ref"] = f"run failed rc={rc} at {tc} threads"
                        else:
                            times[v][f"T{tc}"].append(t)
                            if v in seq_digest:
                                worst[v] = max(worst[v], rel(seq_digest[v], digest(out)))
        entry: Dict[str, object] = {"size": size, "variants": {}, "notes": notes}
        ref_digest = seq_digest.get(variants[0]) or next(iter(seq_digest.values()), {})
        line = [f"{n:6} {size:10}"]
        for v in bins:
            med = {k: (round(statistics.median(x), 4) if x else None) for k, x in times[v].items()}
            sp = {k: (round(med["seq"] / med[k], 3) if med.get("seq") and med.get(k) else None)
                  for k in med if k != "seq"}
            same = (rel(ref_digest, seq_digest[v]) == 0.0) if v in seq_digest else None
            entry["variants"][v] = {"median_s": med, "speedup": sp, "raw": times[v],          # type: ignore[index]
                                    "ref_max_rel_err": worst[v], "original_digest_as_first_variant": same}
            best = max([x for x in sp.values() if x] or [0.0])
            line.append(f"{v}: seq {med['seq']}  " + "  ".join(f"{k} {med[k]}" for k in med if k != 'seq')
                        + f"  best {best:.2f}x" + ("" if worst[v] <= TOL else f"  REF DIFFERS {worst[v]:.1e}")
                        + ("" if same in (True, None) else "  ORIGINAL DIFFERS"))
        result["loops"][n] = entry            # type: ignore[index]
        print(" | ".join(line) + (f"  notes: {notes}" if notes else ""), flush=True)
        Path(a.out).write_text(json.dumps(result, indent=1) + "\n")
    result["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    Path(a.out).write_text(json.dumps(result, indent=1) + "\n")
    shutil.rmtree(work, ignore_errors=True)
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
