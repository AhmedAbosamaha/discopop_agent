#!/usr/bin/env python3
"""Read speed_probe.py results: per loop and variant the sequential time, the reference's best time and its
speedup; then the medians and the per-loop ratios against the first variant.

    python3 probe_table.py RESULT.json [RESULT.json ...] [--variants=v4,c1,c2] [--stat=min|median]

`--stat=min` (default) takes the FASTEST of the repetitions of each configuration: on a shared machine a run
is now and then slowed by another user's process on one of the lane's cores (a 12-thread run of a loop bound
by arithmetic then takes up to twice as long), and the fastest run is the one that was not. `--stat=median`
is what the harness's verification uses.
"""
import json
import statistics
import sys

files = [a for a in sys.argv[1:] if not a.startswith("--")]
want = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--variants=")), None)
stat = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--stat=")), "min")
agg = min if stat == "min" else statistics.median
loops = {}
for f in files:
    loops.update(json.load(open(f))["loops"])
variants = want or sorted({v for r in loops.values() for v in r["variants"]})
order = sorted(loops, key=lambda n: (n[0] != "s", n))


def times(d):
    raw = d["raw"]
    seq = agg(raw["seq"]) if raw.get("seq") else None
    par = [agg(raw[k]) for k in raw if k != "seq" and raw[k]]
    return seq, (min(par) if par else None)


print(f"statistic over the repetitions: {stat}")
print(f"{'loop':6} {'size':10} " + " ".join(f"| {v + ' seq':>10} {'ref':>7} {'x':>5}" for v in variants))
rows = {v: [] for v in variants}
for n in order:
    r = loops[n]
    cells = []
    for v in variants:
        d = r["variants"].get(v)
        if not d:
            cells.append(f"| {'':>10} {'':>7} {'':>6}")
            continue
        s, b = times(d)
        x = (s / b) if s and b else None
        flag = " " if d.get("ref_max_rel_err", 0) <= 1e-9 else "!"
        cells.append(f"| {s if s is not None else float('nan'):10.3f} {b if b else float('nan'):7.3f} {x if x else float('nan'):5.2f}{flag}")
        rows[v].append((n, s, b, x))
    print(f"{n:6} {r['size']:10} " + " ".join(cells) + (f"   {r['notes']}" if r.get("notes") else ""))
print()
base = variants[0]
bmap = {n: (s, b, x) for n, s, b, x in rows[base]}
for v in variants:
    xs = [x for _n, _s, _b, x in rows[v] if x]
    line = (f"{v:8} loops {len(rows[v]):2}  speedup of the reference: median {statistics.median(xs):.2f}  "
            f"min {min(xs):.2f}  max {max(xs):.2f}") if xs else f"{v:8} loops {len(rows[v]):2}  no reference"
    if v != base:
        rs = [s / bmap[n][0] for n, s, _b, _x in rows[v] if n in bmap and s and bmap[n][0]]
        rb = [b / bmap[n][1] for n, _s, b, _x in rows[v] if n in bmap and b and bmap[n][1]]
        rx = [x / bmap[n][2] for n, _s, _b, x in rows[v] if n in bmap and x and bmap[n][2]]
        if rs:
            line += f" | sequential / {base}: median {statistics.median(rs):.3f} [{min(rs):.3f}–{max(rs):.3f}]"
        if rb:
            line += f" | reference time / {base}: median {statistics.median(rb):.3f} [{min(rb):.3f}–{max(rb):.3f}]"
        if rx:
            line += f" | speedup / {base}: median {statistics.median(rx):.3f} [{min(rx):.3f}–{max(rx):.3f}]"
    print(line)
