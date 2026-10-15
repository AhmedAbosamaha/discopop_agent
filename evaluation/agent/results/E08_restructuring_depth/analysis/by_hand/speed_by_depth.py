#!/usr/bin/env python3
"""E8, the 18 loops: what depth added to the programs that ended FASTER — the median speed-up at 6 and 12 threads of the
FASTER programs per loop at depth 0 (E3's cells, as e8_readout.py takes them) and at depth 1 and 2 (E8's runs).
No model; reads the archive. Run from the repository root."""
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, "evaluation/agent/tools")
import campaign  # noqa: E402

E3 = ("e3_r_1", "e3_r_2", "e3_r_3", "e3_r_4")
LOOP_RUNS = ("e8v5_r_1", "e8v5_r_2", "e8v5_r_3")


def speeds(runs, arm, name):
    out = {"6": [], "12": []}
    for run in runs:
        root = campaign.find_run(run)
        for f in sorted(root.glob(f"benchmarks/*/{name}/{arm}/*/rep*/trial.json")):
            t = json.loads(f.read_text())
            if t.get("outcome") == "FASTER":
                for k in out:
                    out[k].append(t["verify"]["par"][k]["speedup"])
    return out


def med(xs):
    return statistics.median(xs) if xs else None


names = sorted({p.name for r in LOOP_RUNS for p in campaign.find_run(r).glob("benchmarks/*/*")})
tot = {0: {"6": [], "12": []}, 1: {"6": [], "12": []}, 2: {"6": [], "12": []}}
above = []
for name in names:
    cells = [speeds(("e3c_v8_s341",) if name == "s341" else E3, "default_v5", name),
             speeds(LOOP_RUNS, "depth1_v5", name), speeds(LOOP_RUNS, "depth2_v5", name)]
    for k, c in enumerate(cells):
        for th in ("6", "12"):
            tot[k][th] += c[th]
    m6 = [med(c["6"]) for c in cells]
    if any(m6[k] is not None and m6[0] is not None and m6[k] > 1.1 * m6[0] for k in (1, 2)):
        above.append(name)
    print(f"{name:6s} FASTER {len(cells[0]['6'])}/{len(cells[1]['6'])}/{len(cells[2]['6'])} — median at 6 threads "
          + " / ".join(f"{x:.2f}" if x is not None else "—" for x in m6)
          + " — at 12 threads " + " / ".join(f"{med(c['12']):.2f}" if c["12"] else "—" for c in cells))
for k in (0, 1, 2):
    print(f"depth {k}: {len(tot[k]['6'])} FASTER programs, median {med(tot[k]['6']):.2f} at 6 threads, {med(tot[k]['12']):.2f} at 12")
print("loops where depth 1 or 2's median at 6 threads is more than 10 % above depth 0's:", above or "none")
