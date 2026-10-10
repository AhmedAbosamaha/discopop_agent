#!/usr/bin/env python3
"""E3, the descriptive read-outs fixed in the pre-registration (THESIS_EXPERIMENTS §6, 9 Oct 2026): per loop and
per class — outcomes, speed-ups, model calls and cost per trial and per FASTER trial, who wrote each kept pragma,
and the gate's refusals by stage — for the two setups, from the archived trials. No test is run here.

    ../venv/bin/python agent/results/E03_who_writes_the_pragmas/analysis/e3_descriptive.py     (from evaluation/)
"""
import collections
import csv
import glob
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"
R = "s112 s121 s1213 s127 s211 s212 s241 s243 s244 s252 s254 s255 s281 s291 s292 s293 s331 s341".split()
D = "s321 s322 s323 s3112".split()
A = "s000 vpvtv s313".split()
CLS = {**{n: "R" for n in R}, **{n: "D" for n in D}, **{n: "A" for n in A}}
SETUPS = [("default_v5", "DiscoPoP writes"), ("llm_pragmas_v5", "the model writes")]


def num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


rows = []
for f in sorted(glob.glob(str(RUNS / "e3_*" / "figures" / "trials.csv"))):
    rows += list(csv.DictReader(open(f)))
assert all(int(num(r["llm_call_failures"])) == 0 for r in rows), "a trial with a failed model call is in the archive"
by = collections.defaultdict(list)
for r in rows:
    by[(r["arm"], r["benchmark"].split("/")[1])].append(r)

out = ["# E3 — descriptive read-outs (fixed in the pre-registration of 9 Oct 2026)", "",
       f"{len(rows)} trials in nine runs; no trial with a failed model call. Outcomes are the harness's; every changed "
       "program of the two setups is race-clean (`checks/e3_race_check`), so FASTER here is race-free FASTER.", ""]


def cell(arm, k):
    t = by[(arm, k)]
    c = collections.Counter(r["outcome"] for r in t)
    sp = [num(r["best_speedup"]) for r in t if r["outcome"] == "FASTER" and r["best_speedup"] not in ("", None)]
    return {"n": len(t), "F": c["FASTER"], "pnf": c["parallel-not-faster"], "nc": c["no-change"],
            "other": len(t) - c["FASTER"] - c["parallel-not-faster"] - c["no-change"],
            "sp": statistics.median(sp) if sp else None,
            "calls": sum(int(num(r["llm_calls"])) for r in t), "cost": sum(num(r["cost_usd_equivalent"]) for r in t),
            "dp": sum(int(num(r["pragmas_discopop"])) for r in t), "llm": sum(int(num(r["pragmas_llm"])) for r in t),
            "kept": sum(int(num(r["rewrites_kept"])) for r in t)}


out += ["## Per loop", "",
        "FASTER · parallel but not faster · no change; the median speed-up of the FASTER trials (best of 6 and 12 threads, "
        "against the original); model calls and cost per trial; kept pragmas by author (DiscoPoP + the model).", "",
        "| class | loop | DiscoPoP writes: outcomes | speed-up | calls | $ | pragmas | the model writes: outcomes | speed-up | calls | $ | pragmas |",
        "|---|---|---|---:|---:|---:|---|---|---:|---:|---:|---|"]
for k in R + D + A:
    line = f"| {CLS[k]} | `{k}` |"
    for arm, _ in SETUPS:
        c = cell(arm, k)
        sp = f"{c['sp']:.2f}×" if c["sp"] else "—"
        o = f"{c['F']} · {c['pnf']} · {c['nc']}" + (f" · other {c['other']}" if c["other"] else "")
        line += f" {o} | {sp} | {c['calls'] / c['n']:.1f} | {c['cost'] / c['n']:.2f} | {c['dp']} + {c['llm']} |"
    out.append(line)

out += ["", "## Per class", "",
        "| class | setup | trials | FASTER | parallel, not faster | no change | model calls | cost | per trial | per FASTER trial | kept rewrites | kept pragmas: DiscoPoP's | the model's |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
tot = {}
for c in ("R", "D", "A", "all"):
    for arm, name in SETUPS:
        t = [r for r in rows if r["arm"] == arm and (c == "all" or CLS[r["benchmark"].split("/")[1]] == c)]
        o = collections.Counter(r["outcome"] for r in t)
        cost = sum(num(r["cost_usd_equivalent"]) for r in t)
        calls = sum(int(num(r["llm_calls"])) for r in t)
        tot[(c, arm)] = cost
        out.append(f"| {c} | {name} | {len(t)} | {o['FASTER']} | {o['parallel-not-faster']} | {o['no-change']} | {calls} | "
                   f"${cost:.2f} | ${cost / len(t):.2f} | " + (f"${cost / o['FASTER']:.2f}" if o["FASTER"] else "—") + " | "
                   f"{sum(int(num(r['rewrites_kept'])) for r in t)} | {sum(int(num(r['pragmas_discopop'])) for r in t)} | "
                   f"{sum(int(num(r['pragmas_llm'])) for r in t)} |")
out += ["", f"Both setups together: ${tot[('all', 'default_v5')] + tot[('all', 'llm_pragmas_v5')]:.2f}.", ""]

# ---- the gate's refusals by stage, from every recorded candidate ----
cand = collections.defaultdict(collections.Counter)
verd = collections.defaultdict(collections.Counter)
mixed, floor_a, b_gap = [], [], []
floor = collections.Counter()
for f in sorted(glob.glob(str(RUNS / "e3_*" / "benchmarks" / "*" / "*" / "*" / "*" / "rep*" / "trial.json"))):
    t = json.load(open(f))
    arm = t["arm"]
    if arm not in dict(SETUPS):
        continue
    k = t["benchmark"].split("/")[1]
    key = (CLS[k], arm)
    for name in ("exposure_verdicts", "d40_verdicts"):
        for v, n in (t.get(name) or {}).items():
            verd[key][f"{name.split('_')[0]}: {v}"] += n
    p = Path(f).parent / "agent_patches" / "candidates.jsonl"
    if p.exists():
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            c = json.loads(line)
            who = "with the model's pragma" if c.get("self_annotated") else "without a pragma"
            ph = str(c.get("phase"))
            cand[key][(ph, who, "passed" if c.get("passed") else f"refused: {c.get('stage')}")] += 1
    if arm == "llm_pragmas_v5" and int(t.get("pragmas_discopop") or 0) > 0:
        mixed.append((k, Path(f).parent.name, int(t.get("pragmas_discopop") or 0), int(t.get("pragmas_llm") or 0), t.get("outcome")))
    floor[(arm, str(t.get("dp_floor")))] += 1
    if CLS[k] == "A":
        floor_a.append((k, dict(SETUPS)[arm], str(t.get("dp_floor")), int(t.get("rewrites_kept") or 0),
                        int(t.get("pragmas_discopop") or 0), int(t.get("pragmas_llm") or 0)))
    if p.exists():
        b_pass = sum(1 for line in p.read_text().splitlines() if line.strip()
                     and str(json.loads(line).get("phase")) == "B" and json.loads(line).get("passed"))
        if arm == "llm_pragmas_v5" and b_pass > int(t.get("pragmas_discopop") or 0) and str(t.get("dp_floor")) == "original":
            b_gap.append((k, Path(f).parent.name, b_pass, int(t.get("pragmas_discopop") or 0)))

out += ["## The gate's verdicts on every candidate, by stage", "",
        "Phase A = a rewrite the model proposed; A-D40 = a rewrite without a pragma judged as it would ship (DiscoPoP's "
        "pragma added, then the same checks); A-tier1 = DiscoPoP's own pragma for a loop it already finds parallel, sent "
        "through the safety checks before the model is asked; B = DiscoPoP's own pragma for a loop that carries none.", ""]
for c in ("R", "D", "A"):
    for arm, name in SETUPS:
        key = (c, arm)
        n = sum(cand[key].values())
        out.append(f"**class {c}, {name}** — {n} candidates recorded")
        for (ph, who, res), v in sorted(cand[key].items()):
            out.append(f"- phase {ph}, {who}, {res}: {v}")
        if verd[key]:
            out.append("- after phase A (rewrites without a pragma): "
                       + ", ".join(f"{a} {b}" for a, b in sorted(verd[key].items())))
        out.append("")

out += ["## Where the model may write and DiscoPoP added a pragma of its own", "",
        "| loop | trial | DiscoPoP's | the model's | outcome |", "|---|---|---:|---:|---|"]
out += [f"| `{k}` | {rep} | {a} | {b} | {o} |" for k, rep, a, b, o in mixed] or ["| — | | | | |"]
out += ["", "A pragma of DiscoPoP's that passed the checks in phase B and is not in the final program (dropped after the "
        "checks — the agent's log gives the reason): "
        + (", ".join(f"`{k}` {rep} ({a} passed, {b} in the final program)" for k, rep, a, b in b_gap) or "none") + ".", "",
        "## The floor: which program was shipped", "",
        "The floor decides last (D32): the agent's program, or DiscoPoP's own — what the DiscoPoP-alone setup delivers — "
        "if that is faster. `original`: DiscoPoP alone keeps nothing on this loop, so there is nothing to fall back to.", "",
        "| setup | " + " | ".join(sorted({k[1] for k in floor})) + " |",
        "|---|" + "---:|" * len({k[1] for k in floor})]
for arm, name in SETUPS:
    out.append(f"| {name} | " + " | ".join(str(floor[(arm, v)]) for v in sorted({k[1] for k in floor})) + " |")
out += ["", "| class A loop | setup | shipped | kept rewrites | DiscoPoP's pragmas | the model's |", "|---|---|---|---:|---:|---:|"]
out += [f"| `{k}` | {name} | {v} | {kept} | {a} | {b} |" for k, name, v, kept, a, b in sorted(floor_a)]
text = "\n".join(out) + "\n"
(HERE / "e3_descriptive.md").write_text(text)
print(text)
