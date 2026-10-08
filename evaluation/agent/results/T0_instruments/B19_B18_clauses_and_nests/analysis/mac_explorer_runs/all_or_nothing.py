#!/usr/bin/env python3
"""The Mac's PolyBench runs (three runs of each explorer on one kept profile per package, `polybench_dumps/`): where
the three runs of one explorer do not agree on which loops are blocked, does a run block every loop in question, none
of them, or some? Writes the counts into summary.json (keys `states`, `all_or_nothing`) and prints the table.

    venv/bin/python evaluation/agent/results/T0_instruments/B19_B18_clauses_and_nests/analysis/mac_explorer_runs/all_or_nothing.py
"""
import collections
import glob
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
packs = sorted({os.path.basename(f)[len("polybench_"):].rsplit("_", 2)[0] for f in glob.glob(str(HERE / "polybench_dumps" / "*.json"))})
states, tally = {}, {"old": collections.Counter(), "new": collections.Counter()}
for k in packs:
    for ex in ("old", "new"):
        runs = [frozenset(b[0] for b in json.loads((HERE / "polybench_dumps" / f"polybench_{k}_{ex}_{n}.json").read_text())["blocked"])
                for n in (1, 2, 3)]
        vary = frozenset().union(*runs) - frozenset.intersection(*runs)
        if not vary:
            tally[ex]["the three runs agree"] += 1
            continue
        st = ["all" if r & vary == vary else ("none" if not r & vary else "part") for r in runs]
        states.setdefault(k, {})[ex] = {"loops": len(vary), "runs": st}
        tally[ex]["packages"] += 1
        for x in st:
            tally[ex][x] += 1
        print(f"{k:18s} {ex}  loops in question {len(vary):2d}   runs: {st}")
tot = {x: tally["old"][x] + tally["new"][x] for x in ("all", "none", "part")}
sentence = (f"Where the three runs of one explorer on one profile do not agree ({tally['old']['packages']} packages with the explorer "
            f"before the repairs, {tally['new']['packages']} with the one after), a run blocks either every loop in question or "
            f"none of them: {tot['all']} runs block all, {tot['none']} block none, {tot['part']} block some. "
            f"(`mac_explorer_runs/all_or_nothing.py`.)")
print(sentence)
p = HERE / "summary.json"
s = json.loads(p.read_text())
s["states"] = states
s["all_or_nothing"] = sentence
p.write_text(json.dumps(s, indent=1, ensure_ascii=False) + "\n")
