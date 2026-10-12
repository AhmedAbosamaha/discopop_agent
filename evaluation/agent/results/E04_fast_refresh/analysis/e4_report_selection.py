#!/usr/bin/env python3
"""E4 step 2 — which rewrites the model is asked about. The rule is fixed in the record before this is run.

From step 1's records (`runs/e4_replay`), with the decision as its read-out counts it (the names inside a clause in
one order):

  * the report is asked on every rewrite whose decision differs after the fast refresh (58), and on as many of the
    541 whose decision is the same, drawn so that every loop with such a rewrite is in: one per loop first, the
    rest in proportion to the loop's number of same-decision rewrites (largest remainders; ties by the loop's
    name), and inside a loop the first ones of a shuffle with a fixed seed of the rewrites sorted by part, trial
    and number;
  * the deletion is asked on every rewrite on which the dry pass (`preflight/e4_report_dry`) found that the
    agent's review has something to ask.

    venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/e4_report_selection.py

Writes `e4_report_selection.json`, `e4_deletion_selection.json` (lists of {trial, n, ...} for
`report_replay.py --select / --select-deletion`) and `e4_report_selection.md` beside itself.
"""
import collections
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEP1 = HERE.parent / "runs" / "e4_replay"
DRY = HERE.parent / "preflight" / "e4_report_dry"
SEED = 20261012
PARTS = ["e3_r", "e3_d", "e3b", "e1v6"]
CLAUSE = re.compile(r"(\w+)\(([^)]*)\)")


def _clause(m):
    head, body = "", m.group(2)
    if ":" in body:
        head, body = body.split(":", 1)
        head = head.strip() + ":"
    return f"{m.group(1)}({head}{','.join(sorted(x.strip() for x in body.split(',')))})"


def kept(arm):
    if arm.get("status") != "exposed" or arm.get("judged") != "safe_deferred":
        return None
    singles = [c for c in arm.get("checks", []) if c["lines"] is not None and c["passed"]]
    together = [c for c in arm.get("checks", []) if c["lines"] is None]
    if together and not together[-1]["passed"]:
        singles = singles[:1]
    return sorted((tuple(c["lines"]), tuple(sorted(CLAUSE.sub(_clause, x) for x in c["pragmas"]))) for c in singles)


def decision(r):
    kf, ku = kept(r["full"]), kept(r["fast"])
    if kf is None and ku is None:
        return "reverted after both"
    if kf is not None and ku is not None:
        return "kept after both, the same directives" if kf == ku else "kept after both, other directives"
    return "kept only after the full re-profile" if kf is not None else "kept only after the fast refresh"


def load(root):
    rows = []
    for part in PARTS:
        for f in sorted((root / part).glob("**/results.jsonl")):
            for ln in f.read_text().splitlines():
                if ln.strip():
                    r = json.loads(ln)
                    r["part"] = part
                    rows.append(r)
    return rows


rows = load(STEP1)
for r in rows:
    r["loop"] = r["benchmark"].split("/")[1]
    r["step1_decision"] = decision(r)
SAME = ("reverted after both", "kept after both, the same directives")
differ = [r for r in rows if r["step1_decision"] not in SAME]
same = [r for r in rows if r["step1_decision"] in SAME]
want = len(differ)

by_loop = collections.defaultdict(list)
for r in sorted(same, key=lambda r: (r["part"], r["trial"], r["n"])):
    by_loop[r["loop"]].append(r)
loops = sorted(by_loop)
total = sum(len(v) for v in by_loop.values())
rest = want - len(loops)
assert rest >= 0, "more loops than rewrites to draw"
share = {lp: rest * len(by_loop[lp]) / total for lp in loops}
quota = {lp: 1 + int(share[lp]) for lp in loops}
for lp in sorted(loops, key=lambda lp: (-(share[lp] - int(share[lp])), lp)):
    if sum(quota.values()) >= want:
        break
    quota[lp] += 1
over = {lp: quota[lp] - len(by_loop[lp]) for lp in loops if quota[lp] > len(by_loop[lp])}
for lp, k in over.items():                      # a loop cannot give more than it has: the others take the rest
    quota[lp] -= k
    for other in sorted(loops, key=lambda x: (-(share[x] - int(share[x])), x)):
        while k and quota[other] < len(by_loop[other]) and other not in over:
            quota[other] += 1
            k -= 1
assert sum(quota.values()) == want, (sum(quota.values()), want)

rng = random.Random(SEED)
drawn = []
for lp in loops:
    pool = list(by_loop[lp])
    rng.shuffle(pool)
    drawn += pool[:quota[lp]]

dry = {(r["trial"], r["n"]): r for r in load(DRY)}
ask_deletion = [r for r in rows if (dry.get((r["trial"], r["n"]), {}).get("deletion") or {}).get("asked")]

entry = lambda r, stratum: {"trial": r["trial"], "n": r["n"], "part": r["part"], "loop": r["loop"], "stratum": stratum,
                            "step1_decision": r["step1_decision"], "kept_in_trial": r["kept_in_trial"]}
report = [entry(r, "differs") for r in differ] + [entry(r, "same") for r in drawn]
report.sort(key=lambda e: (e["part"], e["trial"], e["n"]))
deletion = sorted((entry(r, "deletion") for r in ask_deletion), key=lambda e: (e["part"], e["trial"], e["n"]))
(HERE / "e4_report_selection.json").write_text(json.dumps(report, indent=1) + "\n")
(HERE / "e4_deletion_selection.json").write_text(json.dumps(deletion, indent=1) + "\n")

n_d = collections.Counter(r["loop"] for r in differ)
n_del = collections.Counter(r["loop"] for r in ask_deletion)
in_both = sum(1 for e in deletion if any(x["trial"] == e["trial"] and x["n"] == e["n"] for x in report))
md = ["# E4 step 2 — the rewrites the model is asked about", "",
      f"Built by `e4_report_selection.py` from step 1's records and the dry pass; seed {SEED}.", "",
      f"**The report: {len(report)} rewrites** — the {len(differ)} whose decision differs after the fast refresh and "
      f"{len(drawn)} of the {len(same)} whose decision is the same. **The deletion: {len(deletion)} rewrites** "
      f"({in_both} of them also among those the report is asked on). Model calls: {len(report) + len(deletion)}.", "",
      "| loop | rewrites | decision differs: all asked | decision the same | of those, drawn | deletion asked |",
      "|---|---:|---:|---:|---:|---:|"]
allr = collections.Counter(r["loop"] for r in rows)
for lp in sorted(allr):
    md.append(f"| `{lp}` | {allr[lp]} | {n_d.get(lp, 0)} | {len(by_loop.get(lp, []))} | {quota.get(lp, 0)} | {n_del.get(lp, 0)} |")
md.append(f"| **all** | {len(rows)} | {len(differ)} | {len(same)} | {len(drawn)} | {len(deletion)} |")
dec = collections.Counter((e["stratum"], e["step1_decision"]) for e in report)
md += ["", "By step 1's decision: " + "; ".join(f"{s}: {d} {k}" for (s, d), k in sorted(dec.items())) + ".",
       "", "By part: " + ", ".join(f"{p} {sum(1 for e in report if e['part'] == p)} for the report and "
                                   f"{sum(1 for e in deletion if e['part'] == p)} for the deletion" for p in PARTS) + ".", ""]
(HERE / "e4_report_selection.md").write_text("\n".join(md))
print("\n".join(md))
