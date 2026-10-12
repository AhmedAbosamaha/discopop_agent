#!/usr/bin/env python3
"""E4 step 2, the what-if on the saved replies (`e4_report_a_placement`, no model) — read-out.

The replies recorded by `e4_report_a` placed again: once as the agent places them (a control) and once with every
claimed dependence left out whose two lines lie inside a loop the same reply declares independent (a what-if, not
the agent as built). Decisions as in the main read-out: F after the fast refresh, X with the report, P after the
full re-profile; the names inside a clause in one order.

    venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/e4_report_placement_readout.py

Writes `e4_report_placement_readout.md` beside itself.
"""
import collections
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE.parent / "runs" / "e4_report_a"
CHECK = HERE.parent / "checks" / "e4_report_a_placement"
STEP1 = HERE.parent / "runs" / "e4_replay"
SEL = {(e["trial"], e["n"]): e for e in json.loads((HERE / "e4_report_selection.json").read_text())}
CLAUSE = re.compile(r"(\w+)\(([^)]*)\)")
SAME = ("reverted after both", "kept after both, the same directives")


def _clause(m):
    head, body = "", m.group(2)
    if ":" in body:
        head, body = body.split(":", 1)
        head = head.strip() + ":"
    return f"{m.group(1)}({head}{','.join(sorted(x.strip() for x in body.split(',')))})"


def kept(arm):
    if not arm or arm.get("status") != "exposed" or arm.get("judged") != "safe_deferred":
        return None
    singles = [c for c in arm.get("checks", []) if c["lines"] is not None and c["passed"]]
    together = [c for c in arm.get("checks", []) if c["lines"] is None]
    if together and not together[-1]["passed"]:
        singles = singles[:1]
    return sorted((tuple(c["lines"]), tuple(sorted(CLAUSE.sub(_clause, x) for x in c["pragmas"]))) for c in singles)


def against(x, p):
    kx, kp = kept(x), kept(p)
    if kx is None and kp is None:
        return "reverted after both"
    if kx is not None and kp is not None:
        return "kept after both, the same directives" if kx == kp else "kept after both, other directives"
    return "kept only after the full re-profile" if kp is not None else "kept only with the report"


def load(root):
    rows = {}
    for f in sorted(root.glob("*/results.jsonl")) + sorted(root.glob("*/*/results.jsonl")):
        for ln in f.read_text().splitlines():
            if ln.strip():
                r = json.loads(ln)
                rows[(r["trial"], r["n"])] = r
    return rows


def table(head, body):
    return ["| " + " | ".join(head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"] \
        + ["| " + " | ".join(str(c) for c in r) + " |" for r in body]


loop = lambda k: k[0].split("/benchmarks/")[1].split("/")[1]
short = lambda k: f"`{k[0].split('/')[0]}` `{loop(k)}` repeat {k[0].rsplit('rep', 1)[1]}, rewrite {k[1]}"
runs = {"as recorded (`e4_report_a`, the model's calls)": load(MAIN),
        "placed again as built (the control)": load(CHECK / "as-built"),
        "placed again with the rule (the what-if)": load(CHECK / "respect-none")}
step1 = load(STEP1)
n_same = collections.Counter(loop(k) for k, r in step1.items() if against(r["fast"], r["full"]) in SAME)
manifests = [json.loads(f.read_text()) for f in sorted(CHECK.glob("*/*/manifest.json"))]


def summary(rows):
    rep = {k: r for k, r in rows.items() if k in SEL and (r.get("report") or {}).get("asked")}
    dif = {k: r for k, r in rep.items() if SEL[k]["stratum"] == "differs"}
    sam = {k: r for k, r in rep.items() if SEL[k]["stratum"] == "same" and against(r["fast"], r["full"]) in SAME}
    lost = [k for k in dif if against(dif[k]["fast"], dif[k]["full"]) == "kept only after the full re-profile"]
    back = [k for k in lost if against(dif[k]["report"], dif[k]["full"]) == "kept after both, the same directives"]
    fonly = [k for k in dif if kept(dif[k]["full"]) is None and kept(dif[k]["fast"]) is not None]
    broken = [k for k in sam if against(sam[k]["report"], sam[k]["full"]) not in SAME]
    wins = [k for k in broken if against(sam[k]["report"], sam[k]["full"]) == "kept only after the full re-profile"]
    m_loop = collections.Counter(loop(k) for k in sam)
    est = lambda ks: sum(n_same[lp] * sum(1 for k in ks if loop(k) == lp) / m for lp, m in m_loop.items())
    newly = [k for k in dif if against(dif[k]["fast"], dif[k]["full"]) == "kept after both, other directives"
             and against(dif[k]["report"], dif[k]["full"]) == "kept only after the full re-profile"]
    produced = [k for k in rep if kept(rep[k]["full"]) is None and kept(rep[k]["report"]) is not None and kept(rep[k]["fast"]) is None]
    return {"rep": rep, "n": len(rep), "dif": len(dif), "sam": len(sam),
            "repaired": sum(1 for k in dif if against(dif[k]["report"], dif[k]["full"]) in SAME),
            "lost": len(lost), "back": len(back), "fonly": len(fonly),
            "fonly_left": sum(1 for k in fonly if kept(dif[k]["report"]) is not None),
            "newly": newly, "broken": broken, "wins": wins, "est": est(broken), "est_wins": est(wins), "produced": produced,
            "left_out": sum(len(r["report"].get("claims_left_out") or []) for r in rep.values()),
            "left_out_replies": sum(1 for r in rep.values() if r["report"].get("claims_left_out")),
            "rows": sum(len(r["report"].get("rows") or []) for r in rep.values())}


S = {name: summary(rows) for name, rows in runs.items()}
names = list(runs)
md = ["# E4 step 2 — the saved replies placed again (`e4_report_a_placement`), no model", "",
      "Built by `e4_report_placement_readout.py`. The replies recorded by `e4_report_a` are placed again without a model: "
      "as the agent places them (a control, which should give `e4_report_a`'s decisions again) and with one rule changed — "
      "a claimed dependence is left out where both of its lines lie inside a loop the same reply declares independent. "
      "**The rule is a what-if chosen after the result was seen; it is not the agent as built.**", "",
      f"Commit `{', '.join(sorted({m['commit'][:9] for m in manifests}))}`, the DiscoPoP pass "
      f"`{', '.join(sorted({str(m['discopop_pass_sha256'])[:12] for m in manifests}))}`; "
      f"{min((m['started'] for m in manifests), default='?')} to {max((m['finished'] for m in manifests), default='?')}; "
      f"model calls: {sum(m.get('report_calls', 0) + m.get('deletion_calls', 0) for m in manifests)}.", ""]
row = lambda label, f: [label] + [f(S[n]) for n in names]
md += table([""] + names, [
    row("rewrites read out", lambda s: s["n"]),
    row("rows placed in the dependence file", lambda s: s["rows"]),
    row("claims left out by the rule (in how many replies)", lambda s: f"{s['left_out']} ({s['left_out_replies']})"),
    row("of the rewrites that differ after the fast refresh: repaired", lambda s: f"{s['repaired']} of {s['dif']}"),
    row("— of the wins the fast refresh loses: kept again with the full profile's directives", lambda s: f"{s['back']} of {s['lost']}"),
    row("— of the keeps the full profile does not make: still kept", lambda s: f"{s['fonly_left']} of {s['fonly']}"),
    row("— kept after both before, a win lost with the report", lambda s: len(s["newly"])),
    row("of the rewrites that agree after the fast refresh: broken", lambda s: f"{len(s['broken'])} of {s['sam']}"),
    row("— a win lost", lambda s: len(s["wins"])),
    row("— kept with other directives", lambda s: len(s["broken"]) - len(s["wins"])),
    row("broken among the 541, each loop's share times its number", lambda s: f"{s['est']:.1f}"),
    row("— wins lost among the 541, the same way", lambda s: f"{s['est_wins']:.1f}"),
    row("keeps the full profile does not make, produced by the report", lambda s: len(s["produced"])),
]) + [""]

a, c, w = (runs[n] for n in names)
keys = [k for k in SEL if k in a and k in c and k in w and all((r[k].get("report") or {}).get("asked") for r in (a, c, w))]
ctl = [k for k in keys if kept(c[k]["report"]) != kept(a[k]["report"])]
md += ["## The control", "",
       f"{len(keys)} rewrites in all three. Placed again as built, the decision with the report is `e4_report_a`'s in "
       f"{len(keys) - len(ctl)}; the decision after the fast refresh in "
       f"{sum(1 for k in keys if kept(c[k]['fast']) == kept(a[k]['fast']))}, after the full re-profile in "
       f"{sum(1 for k in keys if kept(c[k]['full']) == kept(a[k]['full']))}.", ""]
for k in ctl:
    md.append(f"- differs: {short(k)} — recorded {kept(a[k]['report'])}; placed again {kept(c[k]['report'])}")
chg = [k for k in keys if kept(w[k]["report"]) != kept(c[k]["report"])]
md += ["", "## What the rule changes, rewrite by rewrite", "",
       f"The decision with the rule differs from the decision placed again as built in {len(chg)} of {len(keys)} rewrites.", ""]
body = collections.Counter()
for k in chg:
    body[(SEL[k]["stratum"], against(c[k]["report"], c[k]["full"]), against(w[k]["report"], w[k]["full"]))] += 1
md += table(["drawn as", "as built, against the full re-profile", "with the rule, against the full re-profile", "rewrites"],
            [[s, x, y, v] for (s, x, y), v in sorted(body.items(), key=lambda kv: -kv[1])]) + [""]
for k in chg:
    md.append(f"- {short(k)} ({SEL[k]['stratum']}): the full re-profile {kept(w[k]['full'])}; as built {kept(c[k]['report'])}; with the rule "
              f"{kept(w[k]['report'])}; left out {w[k]['report'].get('claims_left_out')}")
still = [k for k in S[names[2]]["broken"]]
md += ["", "## Still broken with the rule", ""]
for k in still:
    rp = w[k]["report"]
    md.append(f"- {short(k)}: the full re-profile {kept(w[k]['full'])}; with the rule {kept(rp)}; left out {rp.get('claims_left_out')}; "
              f"claims placed {[cl for cl in rp.get('claims') or []]}; loops the reply declared independent {rp.get('loops_declared_independent')}")
md.append("")
(HERE / "e4_report_placement_readout.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
