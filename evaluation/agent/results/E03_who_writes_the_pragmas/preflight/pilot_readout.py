#!/usr/bin/env python3
"""E3's pilot read out against what its row said it has to show (THESIS_EXPERIMENTS §6, 9 Oct, "Plan, E3 pilot").

    venv/bin/python evaluation/agent/results/E03_who_writes_the_pragmas/preflight/pilot_readout.py   (from the repository root)

Reads the four archived runs beside this file — nothing is run.  (i) every trial has an outcome and no failed model
call; (ii) in the setup in which the model writes the pragma its rewrites arrive with pragmas and go through the gate,
and the trial record says who wrote each kept pragma; (iii) the instructions and requests the model was sent are prompt
version 5's; (iv) what a trial cost."""
import collections
import csv
import glob
import json
from pathlib import Path

H = Path(__file__).resolve().parent
RUNS = ["e3_pilot_s331", "e3_pilot_s341", "e3_pilot_pair", "e3_pilot_s321"]
GONE = ["Nothing downstream adds", "Nothing here re-profiles", "Nothing re-profiles your rewrite", "nothing adds a pragma for you",
        "still a sequential program", "than both", "whole judgement", "not observed on the profiling input", "usually a reused",
        "it could not rule out"]
LEGEND = "static = not marked, which for a scalar does not mean it did not occur"
MODEL_WRITES = ["DiscoPoP profiles the program again", "it adds its own pragma", "judged differently: it is kept only if DiscoPoP",
                "be at least 1.1× faster", "which it must not be slower than"]
TASK = "no slower than the program as it stood before your rewrite"

rows = []
for r in RUNS:
    rows += list(csv.DictReader(open(H / r / "figures" / "trials.csv")))
agent = [r for r in rows if r["arm"] != "discopop_gate_v5"]
print(f"{len(rows)} trials archived: {len(agent)} with a model (Haiku), {len(rows) - len(agent)} of DiscoPoP alone (no model)\n")

print("(i) outcomes and failed model calls")
print(f"    trials with a failed model call: {sum(int(r['llm_call_failures'] or 0) > 0 for r in rows)} of {len(rows)};"
      f"  scaffold intact: {sum(r['scaffold_ok'] == 'True' for r in rows)} of {len(rows)}")
print(f"    DiscoPoP alone: {dict(collections.Counter(r['outcome'] for r in rows if r['arm'] == 'discopop_gate_v5'))}\n")

print("(ii) and (iv) per trial: outcome, best speed-up, kept pragmas by DiscoPoP + by the model, model calls, cost")
for r in sorted(agent, key=lambda r: (r["arm"], r["benchmark"], r["repeat"])):
    print(f"    {r['arm']:15s} {r['benchmark'].split('/')[-1]:6s} rep{r['repeat']}  {r['outcome']:10s} {float(r['best_speedup']):5.2f}x  "
          f"pragmas {r['pragmas_discopop']}+{r['pragmas_llm']}  calls {int(r['llm_calls']):2d}  ${float(r['cost_usd_equivalent']):.2f}")
for arm in ("llm_pragmas_v5", "default_v5"):
    a = [r for r in agent if r["arm"] == arm]
    print(f"    {arm}: {len(a)} trials, FASTER {sum(r['outcome'] == 'FASTER' for r in a)}, "
          f"${sum(float(r['cost_usd_equivalent']) for r in a):.2f}")
print(f"    pilot in all: ${sum(float(r['cost_usd_equivalent'] or 0) for r in rows):.2f}\n")

print("(ii) what the gate did with every candidate (phase A = the model's rewrites; A-D40 and B = DiscoPoP's pragmas)")
print("(iii) the texts the model was sent")
bad = 0
for d in sorted(glob.glob(str(H / "e3_pilot_*/benchmarks/*/*/*_v5/*/rep*"))):
    p = Path(d)
    if p.parts[-3] == "discopop_gate_v5":
        continue
    tag = f"{p.parts[-3]} {p.parts[-4]} {p.parts[-1]}"
    cands = [json.loads(l) for l in open(p / "agent_patches" / "candidates.jsonl")]
    reqs = [json.loads(l) for l in open(p / "agent_patches" / "requests" / "requests.jsonl")]
    systems = {r["system"] for r in reqs}
    system = "".join((p / "agent_patches" / "requests" / f"system_{s}.txt").read_text() for s in sorted(systems))
    sent = "\n".join(r["sent"] for r in reqs)
    writes = p.parts[-3] == "llm_pragmas_v5"
    old = [s for s in GONE if s in system + sent]
    lack = [s for s in ([LEGEND] + (MODEL_WRITES if writes else [])) if s not in system]
    if writes and TASK not in sent:
        lack.append("the task line's two timings")
    bad += bool(old or lack)
    own = sum(bool(c.get("self_annotated")) for c in cands if c.get("phase") == "A")
    print(f"    {tag}: {len(reqs)} request(s), {len(systems)} instruction text(s); removed sentences present: {old or 'none'}; "
          f"version-5 sentences missing: {lack or 'none'}")
    print(f"        corrected blocker note in a request: {'static: DiscoPoP did not mark it as observed' in sent};  "
          f"'already parallel' passage: {'Already parallel according to DiscoPoP' in sent};  "
          f"rewrites that carried a pragma of the model's: {own} of {sum(c.get('phase') == 'A' for c in cands)}")
    st = collections.Counter((c.get("phase"), "passed" if c.get("passed") else f"refused at {c.get('stage')}") for c in cands)
    print("        " + "; ".join(f"{k[0]} {k[1]}: {n}" for k, n in sorted(st.items())))
print(f"\n    trials whose texts are not version 5's: {bad}")

print("\nthe race check over the finished programs (e3_pilot_race_check: the gate's ThreadSanitizer build and schedule matrix, no model)")
for part in ("model_writes", "discopop_writes"):
    res = [json.loads(l) for l in open(H / "e3_pilot_race_check" / part / "results.jsonl")]
    c = collections.Counter(r.get("verdict") or r.get("result") or r.get("status") for r in res)
    print(f"    {part}: {len(res)} program(s): {dict(c)}")

print("\n(iv) what the 210 trials may cost — E1-v6's cost per class (analysis/corrected_2/trials.csv, the agent arm) and the pilot beside it")
E1 = H.parents[1] / "E01v6_clean_files_three_way" / "analysis" / "corrected_2" / "trials.csv"
old = [r for r in csv.DictReader(open(E1)) if r["arm"] == "default_v4"]
cost = collections.defaultdict(list)
for r in old:
    cost[r["benchmark"].split("/")[-1]].append(float(r["cost_usd_equivalent"] or 0))
D, A = ["s3112", "s321", "s322", "s323"], ["s000", "vpvtv", "s313"]
R = [b for b in cost if b not in D + A]
tot = lambda names: sum(sum(cost[b]) for b in names)
print(f"    E1-v6, one setup: class R {len(R)} loops ${tot(R):.2f}, class D ${tot(D):.2f}, class A ${tot(A):.2f} = ${tot(R) + tot(D) + tot(A):.2f}")
mean = lambda b: sum(cost[b]) / len(cost[b])
pil = collections.defaultdict(list)
for r in agent:
    pil[(r["arm"], r["benchmark"].split("/")[-1])].append(float(r["cost_usd_equivalent"]))
for (arm, b), v in sorted(pil.items()):
    print(f"    pilot {arm:15s} {b:6s}: mean ${sum(v) / len(v):.2f} over {len(v)}   (E1-v6, DiscoPoP writes: ${mean(b):.2f})")
ratio_d = pil[("llm_pragmas_v5", "s321")][0] / mean("s321")
rest = tot(R) - sum(cost["s331"]) - sum(cost["s341"])
mw_r = rest + 5 * pil[("llm_pragmas_v5", "s331")][0] + 5 * pil[("llm_pragmas_v5", "s341")][0]
mw = mw_r + tot(D) * ratio_d + tot(A)
dp = tot(R) + tot(D) + tot(A)
print(f"    the setup in which DiscoPoP writes the pragma, as E1-v6: ${dp:.0f}")
print(f"    the setup in which the model writes it: class R ${mw_r:.0f} (E1-v6's costs, s331 and s341 at the pilot's), class D ${tot(D) * ratio_d:.0f} "
      f"(E1-v6's x {ratio_d:.2f}, the one pilot trial on s321), class A ${tot(A):.0f} = ${mw:.0f}")
lo = 2 * (dp - sum(cost['s331']) + 5 * pil[('llm_pragmas_v5', 's331')][0])
hi = dp + tot(R) + tot(D) * ratio_d + tot(A)
print(f"    both: about ${dp + mw:.0f}; between ${lo:.0f} (both setups at E1-v6's costs with s331 solved at once) and ${hi:.0f} "
      f"(class R at E1-v6's cost in both, class D at the pilot's ratio where the model writes)")
