#!/usr/bin/env python3
"""E4 step 3 (`e4_refresh_time`, no model) — read-out: what one fast refresh saves where the profiling run is long.

    venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/e4_refresh_time_readout.py [RUN_DIR]

Writes `e4_refresh_time_readout.md` beside itself.
"""
import glob
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / "runs" / "e4_refresh_time"
RESULTS = HERE.parents[1]
# the agent trials of September on these programs (arm `default`): for the share of a whole trial
EARLIER = {"burkardt/md": "e1_r_a", "npb/is": "e1_r_a", "rodinia-3.1/hotspot": "e1_r_b"}


def table(head, body):
    return ["| " + " | ".join(head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"] \
        + ["| " + " | ".join(str(c) for c in r) + " |" for r in body]


def med(xs):
    return statistics.median(xs) if xs else float("nan")


def span(xs):
    return f"{med(xs):.1f} ({min(xs):.1f}–{max(xs):.1f})" if xs else "—"


rows = []
for f in sorted(RUN.glob("*/results.jsonl")):
    rows += [json.loads(ln) for ln in f.read_text().splitlines() if ln.strip()]
manifests = [json.loads(f.read_text()) for f in sorted(RUN.glob("*/manifest.json"))]
rows.sort(key=lambda r: -med([x["full"]["seconds"] for x in r["repeats"]] or [0]))

md = ["# E4 step 3 — what one fast refresh saves where the profiling run is long (`e4_refresh_time`), no model", "",
      "Built by `e4_refresh_time_readout.py` from the run's records. Per program: the unchanged program profiled in "
      "full; one comment line put in front of the file; then, five times in turn, the fast refresh (from the profile "
      "before) and the full re-profile.", "",
      f"Commit `{', '.join(sorted({m['commit'][:9] for m in manifests}))}`, the DiscoPoP pass "
      f"`{', '.join(sorted({str(m['discopop_pass_sha256'])[:12] for m in manifests}))}`; "
      f"{min(m['started'] for m in manifests)} to {max(m['finished'] for m in manifests)}.", "",
      "## 1 Seconds of one refresh", "", "Median of the five, with the smallest and the largest.", ""]
body = []
for r in rows:
    fu = [x["full"]["seconds"] for x in r["repeats"] if x["full"]["ok"]]
    fa = [x["fast"]["seconds"] for x in r["repeats"] if x["fast"]["ok"]]
    pairs = [(x["full"]["seconds"], x["fast"]["seconds"]) for x in r["repeats"] if x["full"]["ok"] and x["fast"]["ok"]]
    saved = [a - b for a, b in pairs]
    body.append([f"`{r['benchmark']}`", r["lines"], span(fu), span(fa), span(saved),
                 f"{100 * med(saved) / med(fu):.0f} %" if pairs else "—",
                 f"{sum(1 for a, b in pairs if b < a)} of {len(pairs)}",
                 f"{sum(1 for x in r['repeats'] if x['fast']['ok'])} of {len(r['repeats'])}"])
md += table(["program", "lines of the file", "full re-profile, s", "fast refresh, s", "saved, s", "share of a full re-profile",
             "pairs in which the fast refresh is shorter", "fast refresh usable"], body) + [""]

md += ["## 2 The parts", "", "Medians of the five, seconds. The carrying over is what remains of a fast refresh beside its "
       "compile and its explorer run.", ""]
body = []
for r in rows:
    fu = [x["full"] for x in r["repeats"] if x["full"]["ok"]]
    fa = [x["fast"] for x in r["repeats"] if x["fast"]["ok"]]
    if not fu or not fa:
        continue
    body.append([f"`{r['benchmark']}`", f"{med([x.get('compile_s', 0) for x in fu]):.2f}", f"{med([x.get('run_s', 0) for x in fu]):.2f}",
                 f"{med([x.get('explore_s', 0) for x in fu]):.2f}", f"{med([x.get('compile_s', 0) for x in fa]):.2f}",
                 f"{med([x.get('explore_s', 0) for x in fa]):.2f}",
                 f"{med([x['seconds'] - x.get('compile_s', 0) - x.get('explore_s', 0) for x in fa]):.2f}"])
md += table(["program", "full: compile", "full: instrumented run", "full: explorer", "fast: compile", "fast: explorer",
             "fast: carrying over"], body) + [""]
notes = {r["benchmark"]: sorted({x["fast"].get("note", "") for x in r["repeats"]}) for r in rows}
md += ["What the fast refresh carried over: " + "; ".join(f"`{b}` — {' / '.join(n)}" for b, n in notes.items()) + ".", ""]

md += ["## 3 DiscoPoP's patterns after each", "",
       "An unchanged program: the fast refresh should give the Do-All and reduction loops of the full profile, with "
       "the same clauses. Where the five full profiles differ among themselves, a difference from the fast refresh "
       "says nothing. Task patterns are counted apart: their number changes from one profile to the next and no "
       "directive of the agent comes from them.", ""]
body = []
for r in rows:
    loops = lambda p: json.dumps([q for q in p if q[0] != "task"])
    tasks = lambda p: next((q[1] for q in p if q[0] == "task"), 0)
    fulls = [x["full"]["patterns"] for x in r["repeats"] if x["full"]["ok"]]
    fasts = [x["fast"]["patterns"] for x in r["repeats"] if x["fast"]["ok"]]
    same_pair = sum(1 for x in r["repeats"] if x["full"]["ok"] and x["fast"]["ok"]
                    and loops(x["fast"]["patterns"]) == loops(x["full"]["patterns"]))
    one = fulls[0] if fulls else []
    full_set = {loops(p) for p in fulls}
    body.append([f"`{r['benchmark']}`", sum(1 for q in one if q[0] == "do_all"), sum(1 for q in one if q[0] == "reduction"),
                 len(full_set), len({loops(p) for p in fasts}), f"{same_pair} of {len(r['repeats'])}",
                 f"{sum(1 for p in fasts if loops(p) in full_set)} of {len(fasts)}",
                 f"{min(map(tasks, fulls))}–{max(map(tasks, fulls))}", f"{min(map(tasks, fasts))}–{max(map(tasks, fasts))}"])
md += table(["program", "Do-All loops (first full profile)", "reductions", "different answers among the five full profiles",
             "among the five fast refreshes", "pairs with the same loops and clauses", "fast refreshes equal to some full profile",
             "task patterns, full", "task patterns, fast"], body) + [""]
ex = {r["benchmark"]: ([x["full"].get("explore_s") for x in r["repeats"]] + [x["fast"].get("explore_s") for x in r["repeats"]]
                       + [r["before"].get("explore_s")]) for r in rows}
md += ["The explorer's own seconds over the eleven profiles of each program (five full, five fast, the one before): "
       + "; ".join(f"`{b}` {min(v):.1f} to {max(v):.1f}" for b, v in ex.items()) + ".", ""]

md += ["## 4 As a share of an agent trial", "",
       "The agent's trials of September on these programs (`history/E01_main_comparison`, arm `default`, the agent of "
       "that time): each trial's number of full re-profiles times the seconds saved by one fast refresh here, over the "
       "trial's duration.", ""]
body = []
for r in rows:
    run = EARLIER.get(r["benchmark"])
    pairs = [x["full"]["seconds"] - x["fast"]["seconds"] for x in r["repeats"] if x["full"]["ok"] and x["fast"]["ok"]]
    if not run or not pairs:
        continue
    trials = [json.loads(Path(f).read_text()) for f in sorted(glob.glob(
        str(RESULTS / "history" / "E01_main_comparison" / "runs" / run / "benchmarks" / r["benchmark"] / "default" / "*" / "rep*" / "trial.json")))]
    shares = sorted(100 * t["refresh_full"] * med(pairs) / t["agent_s"] for t in trials if t.get("agent_s"))
    if not shares:
        continue
    body.append([f"`{r['benchmark']}`", len(trials), f"{min(t['agent_s'] for t in trials):.0f}–{max(t['agent_s'] for t in trials):.0f}",
                 f"{min(t['refresh_full'] for t in trials)}–{max(t['refresh_full'] for t in trials)}", f"{med(pairs):.1f}",
                 f"{shares[0]:.1f}–{shares[-1]:.1f} %", f"{med(shares):.1f} %"])
md += table(["program", "trials", "trial duration, s", "full re-profiles per trial", "saved by one fast refresh, s",
             "share of the trial", "median"], body) + [""]

(HERE / "e4_refresh_time_readout.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
