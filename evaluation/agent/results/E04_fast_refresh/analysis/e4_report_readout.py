#!/usr/bin/env python3
"""E4 step 2 (`e4_report_a`) — read-out: the model's account of the dependences of its rewrite (the report), asked on
the selected rewrites, and the deletion review on the rewrites where it has something to ask.

Every decision is the agent's own, speed aside (the gate's safety checks applied), as in step 1. Per rewrite:
F after the fast refresh, X after the fast refresh with the report or the deletion, P after the full re-profile
of this pass. The names inside a clause are put in one order before directives are compared.

    venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/e4_report_readout.py [RUN_DIR]

Writes `e4_report_readout.md` beside itself.
"""
import collections
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / "runs" / "e4_report_a"
STEP1 = HERE.parent / "runs" / "e4_replay"
SEL = {(e["trial"], e["n"]): e for e in json.loads((HERE / "e4_report_selection.json").read_text())}
DEL = {(e["trial"], e["n"]): e for e in json.loads((HERE / "e4_deletion_selection.json").read_text())}
CLAUSE = re.compile(r"(\w+)\(([^)]*)\)")
SAME = ("reverted after both", "kept after both, the same directives")


def _clause(m):
    head, body = "", m.group(2)
    if ":" in body:
        head, body = body.split(":", 1)
        head = head.strip() + ":"
    return f"{m.group(1)}({head}{','.join(sorted(x.strip() for x in body.split(',')))})"


def norm(pragma, drop_shared=False):
    p = CLAUSE.sub(_clause, pragma)
    return re.sub(r"\s+", " ", re.sub(r"\bshared\([^)]*\)", "", p)).strip() if drop_shared else p


def kept(arm, drop_shared=False):
    """The directives a rewrite would be kept with, or None where it would be reverted."""
    if not arm or arm.get("status") != "exposed" or arm.get("judged") != "safe_deferred":
        return None
    singles = [c for c in arm.get("checks", []) if c["lines"] is not None and c["passed"]]
    together = [c for c in arm.get("checks", []) if c["lines"] is None]
    if together and not together[-1]["passed"]:
        singles = singles[:1]
    return sorted((tuple(c["lines"]), tuple(sorted(norm(x, drop_shared) for x in c["pragmas"]))) for c in singles)


def against(x, p, drop_shared=False, x_name="with the model's answer"):
    """The decision after `x` against the decision after the full re-profile `p`."""
    kx, kp = kept(x, drop_shared), kept(p, drop_shared)
    if kx is None and kp is None:
        return "reverted after both"
    if kx is not None and kp is not None:
        return "kept after both, the same directives" if kx == kp else "kept after both, other directives"
    return "kept only after the full re-profile" if kp is not None else f"kept only {x_name}"


def offered(arm):
    return {(e[0], e[1]): sorted(norm(x) for x in e[3]) for e in (arm or {}).get("exposed", [])}


def table(head, body):
    return ["| " + " | ".join(head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"] \
        + ["| " + " | ".join(str(c) for c in r) + " |" for r in body]


def upper95(k, n):
    """The exact one-sided 95 % upper bound of a share with k of n observed."""
    if n == 0:
        return float("nan")
    if k == 0:
        return 1 - 0.05 ** (1 / n)
    from scipy import stats                              # type: ignore[import-untyped]
    return float(stats.beta.ppf(0.95, k + 1, n - k)) if k < n else 1.0


def load(root):
    rows = {}
    for f in sorted(root.glob("*/results.jsonl")) + sorted(root.glob("*/*/results.jsonl")):
        for ln in f.read_text().splitlines():
            if ln.strip():
                r = json.loads(ln)
                rows[(r["trial"], r["n"])] = r
    return rows


rows, step1 = load(RUN), load(STEP1)
manifests = [json.loads(f.read_text()) for f in sorted(RUN.glob("*/manifest.json"))]
failed = [json.loads(ln) for f in sorted(RUN.glob("*/call_failed.jsonl")) for ln in f.read_text().splitlines() if ln.strip()]
rep = {k: r for k, r in rows.items() if k in SEL and (r.get("report") or {}).get("asked")}
dele = {k: r for k, r in rows.items() if k in DEL and "deletion" in r}
loop = lambda k: k[0].split("/benchmarks/")[1].split("/")[1]
short = lambda k: f"`{k[0].split('/')[0]}` `{loop(k)}` repeat {k[0].rsplit('rep', 1)[1]}, rewrite {k[1]}"

md = ["# E4 step 2 — the model's report and the deletion review on the saved rewrites (`e4_report_a`)", "",
      "Built by `e4_report_readout.py` from the run's records. F: the decision after the fast refresh; X: after the "
      "fast refresh with the model's report (or with the deletion); P: after the full re-profile of this pass. "
      "Decisions are the agent's own, speed aside, as in step 1.", ""]
calls = [r["report"]["request"] for r in rep.values() if r["report"].get("request")] + \
        [r["deletion"]["request"] for r in dele.values() if r["deletion"].get("asked") and r["deletion"].get("request")]
cost = [c.get("cost_usd") or 0 for c in calls]
secs = [c.get("seconds") or 0 for c in calls]
md += [f"**{len(rep)} of the {len(SEL)} rewrites selected for the report and {len(dele)} of the {len(DEL)} selected for the "
       f"deletion are read out.** Model calls counted: {len(calls)} "
       f"({sum(1 for r in rep.values() if r['report'].get('request'))} for the report, "
       f"{sum(1 for r in dele.values() if r['deletion'].get('asked'))} for the deletion); calls that failed and were asked "
       f"again or are still open: {len(failed)}. Commit `{', '.join(sorted({m['commit'][:9] for m in manifests}))}`, the "
       f"DiscoPoP pass `{', '.join(sorted({str(m['discopop_pass_sha256'])[:12] for m in manifests}))}`; "
       f"{min((m['started'] for m in manifests), default='?')} to {max((m['finished'] for m in manifests), default='?')}.", ""]
if cost:
    md += [f"Cost of the counted calls: ${sum(cost):.2f} in all; per call ${min(cost):.3f} to ${max(cost):.3f}, median "
           f"${statistics.median(cost):.3f}. Seconds per call: {min(secs):.1f} to {max(secs):.1f}, median {statistics.median(secs):.1f}.", ""]
missing = sorted(set(SEL) - set(rep)), sorted(set(DEL) - set(dele))
if missing[0] or missing[1]:
    md += [f"Not read out: {len(missing[0])} of the report's rewrites, {len(missing[1])} of the deletion's — "
           + "; ".join(short(k) for k in (missing[0] + missing[1])[:8]) + ".", ""]

# ---- 0 this pass against step 1 ------------------------------------------------------------------------------------
both = [k for k in rows if k in step1 and "fast" in rows[k]]
same_f = sum(1 for k in both if kept(rows[k]["fast"]) == kept(step1[k]["fast"]))
same_p = sum(1 for k in both if "full" in rows[k] and kept(rows[k]["full"]) == kept(step1[k]["full"]))
md += ["## 0 This pass against step 1's record of the same rewrites", "",
       f"{len(both)} rewrites: the decision after the fast refresh is step 1's in {same_f}, the decision after the full "
       f"re-profile in {same_p}.", ""]
for k in both:
    if kept(rows[k]["fast"]) != kept(step1[k]["fast"]) or ("full" in rows[k] and kept(rows[k]["full"]) != kept(step1[k]["full"])):
        md.append(f"- {short(k)}: fast {kept(step1[k]['fast'])} → {kept(rows[k]['fast'])}; full {kept(step1[k]['full'])} → {kept(rows[k].get('full'))}")

# where the model's answer left the profile as the fast refresh made it, X and F are two judgements of one profile
unch = [(k, r["report"]) for k, r in rep.items() if r["report"].get("status") and not r["report"].get("profile_changed")] + \
       [(k, r["deletion"]) for k, r in dele.items() if r["deletion"].get("status") and not r["deletion"].get("profile_changed")]
unch_diff = [k for k, x in unch if kept(x) != kept(rows[k]["fast"])]
md += ["", f"Answers that left the profile as the fast refresh made it (no row placed, nothing removed): {len(unch)}; the decision "
       f"judged again on that same profile differs from the first judgement in {len(unch_diff)} — the checks' own variation, not "
       "the model's doing" + (": " + "; ".join(short(k) for k in unch_diff) if unch_diff else "") + "."]

# ---- 1 the report on the rewrites whose decision differs -----------------------------------------------------------
md += ["", "## 1 The report on the rewrites whose decision differs after the fast refresh", ""]
dif = {k: r for k, r in rep.items() if SEL[k]["stratum"] == "differs"}
body, tot = [], collections.Counter()
for cls in ("kept only after the full re-profile", "kept only after the fast refresh", "kept after both, other directives"):
    ks = [k for k in dif if against(dif[k]["fast"], dif[k]["full"], x_name="after the fast refresh") == cls]
    c = collections.Counter()
    for k in ks:
        x = against(dif[k]["report"], dif[k]["full"], x_name="with the report")
        c["repaired" if x in SAME else x] += 1
        c["changed by the report"] += kept(dif[k]["report"]) != kept(dif[k]["fast"])
        c["repaired, `shared` clauses aside"] += against(dif[k]["report"], dif[k]["full"], True) in SAME
    body.append([cls, len(ks), c["repaired"], c["kept only after the full re-profile"], c["kept only with the report"],
                 c["kept after both, other directives"], c["changed by the report"], c["repaired, `shared` clauses aside"]])
    tot.update(c)
    tot["n"] += len(ks)
body.append(["**all**", tot["n"], tot["repaired"], tot["kept only after the full re-profile"], tot["kept only with the report"],
             tot["kept after both, other directives"], tot["changed by the report"], tot["repaired, `shared` clauses aside"]])
md += table(["after the fast refresh alone (F against P)", "rewrites", "repaired: X equals P", "still kept only after the full re-profile",
             "kept only with the report", "kept after both, other directives", "X differs from F", "X equals P, `shared` clauses aside"], body) + [""]
lost = [k for k in dif if against(dif[k]["fast"], dif[k]["full"]) == "kept only after the full re-profile"]
back = [k for k in lost if against(dif[k]["report"], dif[k]["full"]) == "kept after both, the same directives"]
md += [f"**Of the {len(lost)} wins the fast refresh loses, {len(back)} are kept again with the full profile's directives.** By loop "
       "(kept again of lost): " + ", ".join(
           f"`{lp}` {sum(1 for k in back if loop(k) == lp)} of {sum(1 for k in lost if loop(k) == lp)}"
           for lp in sorted({loop(k) for k in lost})) + ".", ""]
for k in lost:
    if k not in back:
        rp = dif[k]["report"]
        md.append(f"- not kept again: {short(k)} — the reply: {rp.get('summary', 'nothing the agent could read')}; "
                  f"claims {rp.get('claims')}; after it: {rp.get('status')}/{rp.get('judged')}")
md.append("")

# ---- 2 the report on the rewrites whose decision is the same -------------------------------------------------------
md += ["## 2 The report on the rewrites whose decision is the same after the fast refresh", ""]
sam = {k: r for k, r in rep.items() if SEL[k]["stratum"] == "same"}
body, tot = [], collections.Counter()
for cls in SAME:
    ks = [k for k in sam if against(sam[k]["fast"], sam[k]["full"]) == cls]
    c = collections.Counter(against(sam[k]["report"], sam[k]["full"], x_name="with the report") for k in ks)
    c["shared"] = sum(1 for k in ks if against(sam[k]["report"], sam[k]["full"], True) not in SAME)
    body.append([cls, len(ks), sum(c[s] for s in SAME), c["kept only after the full re-profile"], c["kept only with the report"],
                 c["kept after both, other directives"], c["shared"]])
    tot.update(c)
    tot["n"] += len(ks)
body.append(["**all**", tot["n"], sum(tot[s] for s in SAME), tot["kept only after the full re-profile"], tot["kept only with the report"],
             tot["kept after both, other directives"], tot["shared"]])
md += table(["after the fast refresh alone (F equals P)", "rewrites", "intact: X equals P", "broken: a win lost",
             "broken: kept only with the report", "broken: other directives", "broken, `shared` clauses aside"], body) + [""]
odd = [k for k in sam if against(sam[k]["fast"], sam[k]["full"]) not in SAME]
if odd:
    md += [f"{len(odd)} rewrite(s) drawn as 'the same' differ after the fast refresh in this pass and are in no row above: "
           + "; ".join(short(k) for k in odd) + ".", ""]
broken = [k for k in sam if k not in odd and against(sam[k]["report"], sam[k]["full"]) not in SAME]
n_same = collections.Counter(loop(k) for k, r in step1.items() if against(r["fast"], r["full"]) in SAME)
m_loop = collections.Counter(loop(k) for k in sam if k not in odd)
b_loop = collections.Counter(loop(k) for k in broken)
est = sum(n_same[lp] * b_loop.get(lp, 0) / m for lp, m in m_loop.items())
n_ok = len(sam) - len(odd)
ub = upper95(len(broken), n_ok)
md += [f"**Broken: {len(broken)} of {n_ok}.** For the {sum(n_same.values())} such rewrites of step 1: each loop's broken share times "
       f"its number of them gives {est:.1f}; the exact one-sided 95 % bound on the broken share is {100 * ub:.1f} %, that is "
       f"{ub * sum(n_same.values()):.0f} rewrites (the draw is by loop, the bound is not: an indication).", ""]
for k in broken:
    rp = sam[k]["report"]
    md.append(f"- broken: {short(k)} — F and P: {kept(sam[k]['full'])}; with the report: {rp.get('status')}/{rp.get('judged')} "
              f"{kept(rp)}; claims {rp.get('claims')}")
md.append("")

# ---- 3 keeps the full profile does not make ------------------------------------------------------------------------
md += ["## 3 Keeps the full re-profile does not make", ""]
f_only = [k for k in rep if kept(rep[k]["full"]) is None and kept(rep[k]["fast"]) is not None]
x_only = [k for k in rep if kept(rep[k]["full"]) is None and kept(rep[k]["report"]) is not None]
new = [k for k in x_only if k not in f_only]
md += [f"On the {len(rep)} rewrites the report was asked on: after the fast refresh alone {len(f_only)}; with the report "
       f"{len(x_only)}, of which {len(new)} the report produced (reverted after the fast refresh alone) and "
       f"{len(x_only) - len(new)} were already so; {sum(1 for k in f_only if k not in x_only)} of the fast refresh's own are gone "
       "with the report.", ""]
for k in sorted(set(f_only) | set(x_only)):
    md.append(f"- {short(k)}: after the fast refresh {kept(rep[k]['fast'])}; with the report {kept(rep[k]['report'])}; "
              f"claims {rep[k]['report'].get('claims')}")
md.append("")

# ---- 4 what the replies held ---------------------------------------------------------------------------------------
md += ["## 4 What the replies held", ""]
c = collections.Counter()
why = collections.Counter()
for r in rep.values():
    rp = r["report"]
    c["replies"] += 1
    c["empty"] += bool(rp.get("reply_empty"))
    c["nothing read"] += (not rp.get("reply_empty")) and not rp.get("claims") and not rp.get("loops_declared_independent")
    c["claims"] += len(rp.get("claims") or [])
    c["rows"] += len(rp.get("rows") or [])
    c["with a row"] += bool(rp.get("rows"))
    c["independent"] += len(rp.get("loops_declared_independent") or [])
    c["contradicting"] += len({x[0] for x in rp.get("contradicting_static") or []})
    c["explorer failed"] += rp.get("explorer_rc") not in (None, 0)
    for u in rp.get("unresolved") or []:
        key = "on lines the rewrite did not touch (left out by design)" if "not this arm's gap" in u[5] else re.sub(r"'[^']*'", "‹name›", u[5])
        why[key] += 1
md += [f"{c['replies']} replies: {c['empty']} empty, {c['nothing read']} from which the agent's parser read nothing; "
       f"{c['claims']} dependences claimed, {c['rows']} placed as rows of the dependence file (in {c['with a row']} replies); "
       f"{c['independent']} loops declared independent, {c['contradicting']} of them loops on which static "
       f"analysis records a dependence; the explorer failed after a merge in {c['explorer failed']}.", "",
       "Claims not placed: " + ("; ".join(f"{k} {v}" for k, v in sorted(why.items(), key=lambda kv: -kv[1])) or "none") + ".", ""]

# ---- 5 the deletion ------------------------------------------------------------------------------------------------
md += ["## 5 The deletion review on the rewrites where it has something to ask", ""]
c = collections.Counter()
notes = collections.Counter()
for k, r in dele.items():
    d = r["deletion"]
    c["rewrites"] += 1
    c["asked"] += bool(d.get("asked"))
    for v in d.get("reviewed") or []:
        c[v["verdict"]] += 1
    m = re.search(r"reports (\d+) static dependence", (d.get("request") or {}).get("prompt", ""))
    c["blockers"] += int(m.group(1)) if m else 0
    notes[re.sub(r"\d+", "N", d.get("note", ""))] += 1
md += [f"{c['rewrites']} rewrites, a request on {c['asked']}; {c['blockers']} blockers asked about: {c['REAL']} called real, "
       f"{c['SPURIOUS']} called spurious, {c['blockers'] - c['REAL'] - c['SPURIOUS']} not answered (kept as real).", "",
       "What the review then did: " + "; ".join(f"'{k}' {v}" for k, v in sorted(notes.items(), key=lambda kv: -kv[1])) + ".", ""]
body = collections.Counter()
for k, r in dele.items():
    d = r["deletion"]
    x = d if d.get("status") else r["fast"]                     # nothing asked or nothing judged: the fast refresh stands
    body[(against(r["fast"], r["full"], x_name="after the fast refresh"), against(x, r["full"], x_name="with the deletion"),
          kept(x) != kept(r["fast"]))] += 1
md += table(["after the fast refresh alone (F against P)", "with the deletion (X against P)", "X differs from F", "rewrites"],
            [[a, b, "yes" if ch else "no", v] for (a, b, ch), v in sorted(body.items(), key=lambda kv: -kv[1])]) + [""]
d_only = [k for k, r in dele.items() if kept(r["full"]) is None and kept(r["deletion"] if r["deletion"].get("status") else r["fast"]) is not None
          and kept(r["fast"]) is None]
extra, stopped = 0, collections.Counter()
for k, r in dele.items():
    d = r["deletion"]
    if not d.get("status"):
        continue
    of, ox = offered(r["fast"]), offered(d)
    for lines in ox:
        if lines not in of or ox[lines] != of[lines]:
            extra += 1
            chk = next((ch for ch in d.get("checks", []) if ch["lines"] is not None and tuple(ch["lines"]) == lines), None)
            stopped["not sent to the gate (the clause check or the build refused it, or a loop around it was kept)" if chk is None
                    else "passed" if chk["passed"] else f"refused: {chk['stage']}"] += 1
md += [f"**Keeps the full re-profile does not make, produced by the deletion: {len(d_only)} of {len(dele)}.** Directives DiscoPoP "
       f"offers after a deletion that it did not offer after the fast refresh alone: {extra}"
       + (" — " + ", ".join(f"{k} {v}" for k, v in sorted(stopped.items(), key=lambda kv: -kv[1])) if extra else "") + ".", ""]
for k in d_only:
    md.append(f"- {short(k)}: with the deletion {kept(dele[k]['deletion'])}; reviewed {[(v['var'], v['loop'], v['verdict']) for v in dele[k]['deletion'].get('reviewed') or []]}")
for k, r in dele.items():
    d = r["deletion"]
    sp = [(v["dep_type"], v["var"], v["loop"]) for v in d.get("reviewed") or [] if v["verdict"] == "SPURIOUS"]
    if sp:
        md.append(f"- called spurious: {short(k)} — {sp}; then: {d.get('note')}; decision with the deletion "
                  f"{kept(d if d.get('status') else r['fast'])}, after the full re-profile {kept(r['full'])}")
md.append("")

# ---- 6 the two hypotheses as registered ----------------------------------------------------------------------------
repaired = sum(1 for k in dif if against(dif[k]["report"], dif[k]["full"]) in SAME)
md += ["## 6 The two hypotheses, read as registered", "",
       f"**H7** (the report reduces the decisions that differ; refuted by no reduction or by an increase in keeps the full "
       f"profile does not make): repaired {repaired} of {len(dif)} that differ ({len(back)} of the {len(lost)} lost wins kept again); "
       f"broken {len(broken)} of {n_ok} that agree (estimate for the {sum(n_same.values())}: {est:.1f}; 95 % bound "
       f"{ub * sum(n_same.values()):.0f}); keeps the full profile does not make: {len(f_only)} after the fast refresh alone, "
       f"{len(x_only)} with the report ({len(new)} produced by it).", "",
       f"**H7b** (deleting produces keeps the full profile does not make, adding does not; refuted if deletion produces no more "
       f"than addition): the deletion produced {len(d_only)} on {len(dele)} rewrites; the report produced {len(new)} on {len(rep)}.", ""]

(HERE / "e4_report_readout.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
