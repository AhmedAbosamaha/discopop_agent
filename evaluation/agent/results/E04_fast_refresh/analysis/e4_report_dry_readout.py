#!/usr/bin/env python3
"""E4 step 2, the dry pass (`e4_report_dry`, no model) — read-out.

How many requests a run of step 2 over the 599 rewrites would send, where the deletion review has anything to ask
about, and the fast refresh's own repeatability against step 1's record of the same rewrite.

    venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/e4_report_dry_readout.py [DRY_RUN_DIR]

Writes `e4_report_dry_readout.md` beside itself.
"""
import collections
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRY = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / "preflight" / "e4_report_dry"
STEP1 = HERE.parent / "runs" / "e4_replay"
PARTS = [("e3_r", "the pragma experiment, the 18 loops"), ("e3_d", "the pragma experiment, the recurrence loops"),
         ("e3b", "the contrast set"), ("e1v6", "the main comparison, the 18 loops")]
CLAUSE = re.compile(r"(\w+)\(([^)]*)\)")


def _clause(m):
    head, body = "", m.group(2)
    if ":" in body:
        head, body = body.split(":", 1)
        head = head.strip() + ":"
    return f"{m.group(1)}({head}{','.join(sorted(x.strip() for x in body.split(',')))})"


def norm(pragma):
    return CLAUSE.sub(_clause, pragma)


def load(root):
    rows = {}
    for part, _ in PARTS:
        for f in sorted((root / part).glob("**/results.jsonl")):
            for ln in f.read_text().splitlines():
                if ln.strip():
                    r = json.loads(ln)
                    r["part"] = part
                    rows[(r["trial"], r["n"])] = r
    return rows


def exposed_set(arm):
    return sorted(json.dumps([e[0], e[1], e[2], sorted(norm(x) for x in e[3])]) for e in arm.get("exposed", []))


def kept(arm):
    if arm.get("status") != "exposed" or arm.get("judged") != "safe_deferred":
        return None
    singles = [c for c in arm.get("checks", []) if c["lines"] is not None and c["passed"]]
    together = [c for c in arm.get("checks", []) if c["lines"] is None]
    if together and not together[-1]["passed"]:
        singles = singles[:1]
    return sorted((tuple(c["lines"]), tuple(sorted(norm(x) for x in c["pragmas"]))) for c in singles)


def table(head, body):
    return ["| " + " | ".join(head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"] \
        + ["| " + " | ".join(str(c) for c in r) + " |" for r in body]


dry, step1 = load(DRY), load(STEP1)
manifests = [json.loads(f.read_text()) for f in sorted(DRY.glob("*/*/manifest.json"))]
md = ["# E4 step 2 — the dry pass (`e4_report_dry`), no model", "",
      "Built by `e4_report_dry_readout.py` from the run's records. Every request was built as the agent builds it "
      "and recorded; none was sent.", "",
      f"**{len(dry)} rewrites** ({len(step1)} in step 1); commit "
      f"`{', '.join(sorted({m['commit'][:9] for m in manifests}))}`, the DiscoPoP pass "
      f"`{', '.join(sorted({str(m['discopop_pass_sha256'])[:12] for m in manifests}))}`; "
      f"{min(m['started'] for m in manifests)} to {max(m['finished'] for m in manifests)}; "
      f"profiles before a rewrite that failed: {sum(m['before_profile_failed'] for m in manifests)}; "
      f"fast refreshes that reported themselves unusable: {sum(1 for r in dry.values() if not r.get('fast', {}).get('usable'))}.", ""]

# ---- 1 the report requests -----------------------------------------------------------------------------------------
md += ["## 1 The report requests", ""]
body = []
tot = collections.Counter()
sizes, nloops = [], []
systems = set()
for part, label in PARTS:
    rs = [r for r in dry.values() if r["part"] == part]
    asked = [r for r in rs if (r.get("report") or {}).get("asked")]
    for r in asked:
        q = r["report"]["request"]
        sizes.append(len(q["prompt"]))
        nloops.append(len(r["report"]["loops"]))
        systems.add((q["system_sha256"], q["system_chars"]))
    body.append([label, len(rs), len(asked), len(rs) - len(asked)])
    tot.update(rewrites=len(rs), asked=len(asked))
body.append(["**all**", tot["rewrites"], tot["asked"], tot["rewrites"] - tot["asked"]])
md += table(["rewrites of", "rewrites", "a request would be sent", "none (the rewrite left no new line)"], body) + [""]
if sizes:
    md += [f"The request: {min(sizes)} to {max(sizes)} characters, median {int(statistics.median(sizes))}; the "
           f"instructions with it: {', '.join(f'{c} characters (`{h}`)' for h, c in sorted(systems))}. Loops named per "
           f"request: {min(nloops)} to {max(nloops)}, median {statistics.median(nloops):g}; requests that name no loop: "
           f"{sum(1 for x in nloops if x == 0)}.", ""]

# ---- 2 the deletion review -----------------------------------------------------------------------------------------
md += ["## 2 Where the deletion review has anything to ask", "",
       "The agent's review asks only about Do-All blockers that DiscoPoP recorded from STATIC analysis and whose loop "
       "holds a rewritten line.", ""]
body = []
tot = collections.Counter()
items_per = []
by_loop = collections.Counter()
for part, label in PARTS:
    rs = [r for r in dry.values() if r["part"] == part and "deletion" in r]
    any_rec = sum(1 for r in rs if r["deletion"]["blockers_recorded"])
    stat = sum(1 for r in rs if any("STATIC" in o.upper() for o in r["deletion"]["blockers_by_origin"]))
    asked = [r for r in rs if r["deletion"]["asked"]]
    for r in asked:
        m = re.search(r"reports (\d+) static dependence", r["deletion"]["request"]["prompt"])
        items_per.append(int(m.group(1)) if m else 0)
        by_loop[r["benchmark"].split("/")[1]] += 1
    body.append([label, len(rs), any_rec, stat, len(asked)])
    tot.update(rewrites=len(rs), any=any_rec, stat=stat, asked=len(asked))
body.append(["**all**", tot["rewrites"], tot["any"], tot["stat"], tot["asked"]])
md += table(["rewrites of", "rewrites", "with any Do-All blocker recorded", "with one of static origin",
             "a request would be sent"], body) + [""]
origins = collections.Counter()
for r in dry.values():
    for o, k in (r.get("deletion") or {}).get("blockers_by_origin", {}).items():
        origins[o] += k
md += ["Blockers recorded after the fast refresh, by origin, summed over the rewrites: "
       + (", ".join(f"{o} {k}" for o, k in sorted(origins.items(), key=lambda kv: -kv[1])) or "none") + ".", ""]
if items_per:
    md += [f"Blockers asked about per request: {min(items_per)} to {max(items_per)}, median "
           f"{statistics.median(items_per):g}, {sum(items_per)} in all; by loop: "
           + ", ".join(f"`{k}` {v}" for k, v in sorted(by_loop.items())) + ".", ""]
def step1_decision(r):
    kf, ku = kept(r["full"]), kept(r["fast"])
    if kf is None and ku is None:
        return "reverted after both"
    if kf is not None and ku is not None:
        return "kept after both, the same directives" if kf == ku else "kept after both, other directives"
    return "kept only after the full re-profile" if kf is not None else "kept only after the fast refresh"


asked_keys = [k for k, r in dry.items() if (r.get("deletion") or {}).get("asked") and k in step1]
if asked_keys:
    by_dec = collections.Counter(step1_decision(step1[k]) for k in asked_keys)
    md += ["Step 1's decision on the rewrites the review would ask about: "
           + ", ".join(f"{k} {v}" for k, v in sorted(by_dec.items(), key=lambda kv: -kv[1])) + ".", ""]
notes = collections.Counter(re.sub(r"\d+", "N", (r.get("deletion") or {}).get("note", "")) for r in dry.values() if "deletion" in r)
md += ["What the review said (no answer was given, so nothing is removed): "
       + "; ".join(f"'{k}' {v}" for k, v in sorted(notes.items(), key=lambda kv: -kv[1])) + ".", ""]

# ---- 3 the fast refresh against step 1's record --------------------------------------------------------------------
md += ["## 3 The fast refresh a second time", "",
       "The verdict and the decision after the fast refresh here against step 1's record of the same rewrite — the "
       "fast refresh's own repeatability (step 1's control compared two full re-profiles).", ""]
both = [(dry[k], step1[k]) for k in dry if k in step1 and "fast" in dry[k] and "fast" in step1[k]]
same_status = sum(1 for d, s in both if d["fast"].get("status") == s["fast"].get("status"))
same_verdict = sum(1 for d, s in both if d["fast"].get("status") == s["fast"].get("status")
                   and exposed_set(d["fast"]) == exposed_set(s["fast"]))
same_decision = sum(1 for d, s in both if kept(d["fast"]) == kept(s["fast"]))
md += [f"{len(both)} rewrites in both; the same status in {same_status}, the same status and directives in "
       f"{same_verdict}, the same decision (kept with the same directives, or reverted) in {same_decision}.", ""]
diff = [(d, s) for d, s in both if kept(d["fast"]) != kept(s["fast"])
        or d["fast"].get("status") != s["fast"].get("status") or exposed_set(d["fast"]) != exposed_set(s["fast"])]
for d, s in diff[:20]:
    md.append(f"- `{d['trial']}` #{d['n']}: step 1 {s['fast'].get('status')}/{s['fast'].get('judged')} "
              f"{kept(s['fast'])} → here {d['fast'].get('status')}/{d['fast'].get('judged')} {kept(d['fast'])}")
if diff:
    md.append("")
missing = sorted(k for k in step1 if k not in dry)
if missing:
    md += [f"Rewrites of step 1 not in the dry pass: {len(missing)} — {missing[:5]}", ""]

(HERE / "e4_report_dry_readout.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
