#!/usr/bin/env python3
"""What the fast refresh could save, read from the archive (9 Oct 2026) — nothing run.

    venv/bin/python <this file>        (from the repository root)

Part 1: the 90 agent trials on the 18 class-R loops of E1-v6 (`analysis/corrected_2/trials.csv`): the agent's
time, the full re-profiles, and the time of one profile of such a program (the trial's first profile: the record
does not time each re-profile). The fast refresh skips the profiled run only; the compile and the explorer run.
Part 2: the profiled run's time on whole programs, from the three no-model draws of DiscoPoP alone of 8 Oct.
Goes into E3's pre-flight folder when the group is registered (THESIS_EXPERIMENTS §6, 9 Oct, "Finding + proposal,
E3 design")."""
import collections
import csv
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "evaluation/agent/tools"), str(ROOT / "evaluation/shared")]
import campaign  # noqa: E402

R = set("s112 s121 s1213 s127 s211 s212 s243 s244 s252 s254 s255 s291 s292 s293 s341 s281 s331 s241".split())
reg = json.loads((ROOT / "evaluation/agent/results/campaign.json").read_text())
table = ROOT / "evaluation/agent/results/E01v6_clean_files_three_way/analysis/corrected_2/trials.csv"
rows = list(csv.DictReader(table.open()))
keys = {(r["run_id"], r["benchmark"], r["repeat"]) for r in rows
        if r["arm"] == "default_v4" and r["benchmark"].split("/")[-1] in R}
got = []
for run in sorted({k[0] for k in keys}):
    for tj in campaign.find_run(run).glob("benchmarks/**/trial.json"):
        d = json.loads(tj.read_text())
        if d.get("arm") != "default_v4" or (run, d.get("benchmark"), str(d.get("repeat"))) not in keys:
            continue
        p = d.get("profile") or {}
        got.append((d["agent_s"], d.get("refresh_full") or 0, d.get("refresh_fast") or 0,
                    p.get("instrument_s") or 0, p.get("profiled_run_s") or 0, p.get("explore_s") or 0))
ag = [g[0] for g in got]
print(f"agent trials on the 18 loops: {len(got)} of {len(keys)}")
print(f"agent time: sum {sum(ag):.0f} s, mean {st.mean(ag):.0f} s, median {st.median(ag):.0f} s")
print(f"re-profiles: {sum(g[1] for g in got)} full, {sum(g[2] for g in got)} fast")
print(f"one profile: instrument mean {st.mean(g[3] for g in got):.2f} s, run mean {st.mean(g[4] for g in got):.2f} s "
      f"(max {max(g[4] for g in got):.2f}), explore mean {st.mean(g[5] for g in got):.2f} s (max {max(g[5] for g in got):.2f})")
saved = sum(g[1] * g[4] for g in got)
whole = sum(g[1] * (g[3] + g[4] + g[5]) for g in got)
print(f"re-profiles x the run (what skipping the run could save): {saved:.1f} s = {100 * saved / sum(ag):.3f} % of the agent's time")
print(f"re-profiles x the whole profile: {whole:.1f} s = {100 * whole / sum(ag):.2f} %")

runs = sorted(r for r, v in reg["runs"].items() if r.startswith("t0_11_b19r_apps") and v.get("status") == "valid")
per: dict = collections.defaultdict(list)
for run in runs:
    for tj in campaign.find_run(run).glob("benchmarks/**/trial.json"):
        d = json.loads(tj.read_text())
        p = d.get("profile") or {}
        if p.get("profiled_run_s") is not None:
            per[str(d.get("benchmark"))].append((p["profiled_run_s"], p.get("explore_s") or 0))
med = {b: (st.median(x[0] for x in v), st.median(x[1] for x in v)) for b, v in per.items()}
print(f"\nwhole programs ({', '.join(runs)}): {len(med)} with a profile record")
for b, (run_s, exp_s) in sorted(med.items(), key=lambda kv: -kv[1][0])[:8]:
    print(f"  {b}: profiled run {run_s:.1f} s, explore {exp_s:.1f} s")
print(f"profiled run over 5 s: {sum(1 for m in med.values() if m[0] > 5)}; over 1 s: {sum(1 for m in med.values() if m[0] > 1)}")
