#!/usr/bin/env python3
"""Global performance analysis via uftrace.

Locates hot functions in a benchmark binary by recording an uftrace trace
and parsing the report table. Output is a JSON file consumed by the
primitive addition stage.

Usage:
    python hotspot_analyzer.py --bin <path-to-pg-binary> --out <out.json>
    python hotspot_analyzer.py --bin bin/cg.W.pg --out hot.json --threads 4
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

UFTRACE = shutil.which("uftrace")


def _run(cmd, env=None):
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout, proc.stderr


def record_trace(binary, trace_dir, threads=4, extra_opts=None):
    """Run uftrace record on a -pg compiled binary."""
    if not os.path.exists(binary):
        raise FileNotFoundError(f"binary not found: {binary}")
    if os.path.exists(trace_dir):
        shutil.rmtree(trace_dir)
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = str(threads)
    env["PATH"] = os.path.dirname(UFTRACE) + ":" + env.get("PATH", "")
    cmd = [UFTRACE, "record", "-d", trace_dir, "--no-libcall"]
    if extra_opts:
        cmd += extra_opts
    cmd += [binary]
    rc, out, err = _run(cmd, env=env)
    if not os.path.isdir(trace_dir):
        raise RuntimeError(
            f"uftrace produced no data dir. rc={rc} stderr={err.strip()}"
        )
    return trace_dir


_REPORT_ROW = re.compile(
    r"^\s*([\d.]+)\s+([a-z]+)\s+([\d.]+)\s+([a-z]+)\s+(\d+)\s+(.+)$"
)


def parse_report(trace_dir):
    """Parse `uftrace report` text table into a list of dicts."""
    env = dict(os.environ)
    env["PATH"] = os.path.dirname(UFTRACE) + ":" + env.get("PATH", "")
    rc, out, err = _run([UFTRACE, "report", "-d", trace_dir], env=env)
    if rc != 0:
        raise RuntimeError(f"uftrace report failed: {err.strip()}")
    funcs = []
    # uftrace report row example:
    #   "  753.160 ms  753.160 ms          16  conj_grad"
    row_re = re.compile(
        r"^\s*([\d.]+)\s*\w+\s+([\d.]+)\s*\w+\s+(\d+)\s+(.+?)\s*$"
    )
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("=") or line.startswith("Total") \
                or line.startswith("Function"):
            continue
        m = row_re.match(line)
        if not m:
            continue
        try:
            total = float(m.group(1))
            self_t = float(m.group(2))
            calls = int(m.group(3))
            name = m.group(4).strip()
        except (ValueError, IndexError):
            continue
        if not name:
            continue
        funcs.append({
            "name": name,
            "total_time_ms": total,
            "self_time_ms": self_t,
            "calls": calls,
        })
    return funcs


def identify_hotspots(funcs, top_n=5, min_self_ms=1.0):
    """Rank functions by self time. Return those above an absolute
    self-time threshold (milliseconds).

    A function is a hotspot worth optimizing if its total self time
    exceeds min_self_ms. This is an absolute wall-clock budget, not a
    percentage, so it stays meaningful across machines with different
    load. Default 1.0 ms: below that, even fully removing the function
    saves negligible time, and parallelizing it usually costs more in
    fork/join overhead than it gains.
    """
    if not funcs:
        return []
    total_self = sum(f["self_time_ms"] for f in funcs) or 1.0
    ranked = sorted(funcs, key=lambda f: f["self_time_ms"], reverse=True)
    hot = []
    for f in ranked:
        pct = f["self_time_ms"] / total_self * 100.0
        f["self_pct"] = round(pct, 2)
        if f["self_time_ms"] >= min_self_ms:
            hot.append(f)
        if len(hot) >= top_n:
            break
    return hot


def analyze(binary, trace_dir, threads=4, top_n=5, min_self_ms=1.0):
    """Full pipeline: record -> report -> rank. Returns dict."""
    record_trace(binary, trace_dir, threads=threads)
    funcs = parse_report(trace_dir)
    hot = identify_hotspots(funcs, top_n=top_n, min_self_ms=min_self_ms)
    return {
        "binary": os.path.abspath(binary),
        "threads": threads,
        "trace_dir": os.path.abspath(trace_dir),
        "self_time_threshold_ms": min_self_ms,
        "all_functions": funcs,
        "hotspots": hot,
        "hottest": hot[0]["name"] if hot else None,
    }


def main():
    ap = argparse.ArgumentParser(description="uftrace hotspot analyzer")
    ap.add_argument("--bin", required=True, help="path to -pg compiled binary")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--trace-dir", default=None,
                    help="uftrace data dir (default: <out>.uftrace)")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--min-self-ms", type=float, default=1.0,
                    help="absolute self-time threshold in ms; "
                         "functions at or above this are sent to the "
                         "primitive-addition stage (default 1.0)")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    trace_dir = args.trace_dir or (args.out + ".uftrace")
    res = analyze(args.bin, trace_dir, threads=args.threads,
                  top_n=args.top, min_self_ms=args.min_self_ms)
    with open(args.out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"[hotspot] wrote {args.out}")
    print(f"[hotspot] threshold: self_time >= {args.min_self_ms} ms "
          f"({len(res['hotspots'])} functions above threshold)")
    print(f"[hotspot] hottest: {res['hottest']} "
          f"({res['hotspots'][0]['self_time_ms']} ms self, "
          f"{res['hotspots'][0]['self_pct']}%)")
    for h in res["hotspots"]:
        print(f"  {h['name']:20s} self={h['self_time_ms']:10.3f} ms "
              f"({h['self_pct']:5.2f}%) calls={h['calls']}")
    below = [f for f in res["all_functions"]
             if f["self_time_ms"] < args.min_self_ms]
    if below:
        print(f"[hotspot] below threshold (skipped, not optimized):")
        for f in below[:8]:
            print(f"  {f['name']:20s} self={f['self_time_ms']:10.3f} ms "
                  f"calls={f['calls']}")


if __name__ == "__main__":
    main()
