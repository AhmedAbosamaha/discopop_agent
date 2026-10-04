#!/usr/bin/env python3
"""The individual run times behind speed_probe.py's medians: raw_times.py RESULT.json [loop ...]"""
import json
import sys

r = json.load(open(sys.argv[1]))
want = set(sys.argv[2:])
for n, e in r["loops"].items():
    if want and n not in want:
        continue
    for v, d in e["variants"].items():
        raw = d["raw"]
        print(f"{n:6} {v:8} " + "  ".join(f"{k} {[round(x, 2) for x in raw[k]]}" for k in raw))
