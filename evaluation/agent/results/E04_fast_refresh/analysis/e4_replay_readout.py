#!/usr/bin/env python3
"""E4, step 1 — the read-out of the replay (`tools/refresh_replay.py`), fixed in the pre-registration of 12 Oct 2026.
No model. Reads every `results.jsonl` and `manifest.json` under the run's folder and counts, for the rewrites of
the model that passed the checks in the archived trials:

  the verdict   what DiscoPoP says about the rewritten lines after the fast refresh against after the full
                re-profile (`class`): the same, parallel only after one of them, or parallel after both with other
                loops or other directives
  the decision  whether the rewrite would be kept, speed aside, after each (`decision`): the safety half of the
                agent's own judgement of DiscoPoP's directives
  the control   the same two counts for a SECOND full re-profile of the same program against the first
  the test      E4-1 (H6's second half): per loop, the share of rewrites whose decision differs after the fast
                refresh against the share that differs in the control — one-sided Wilcoxon signed-rank over the loops
  the check     the full re-profile's verdict of the replay against the verdict the trial itself logged
  the time      seconds of one full re-profile and of one fast refresh

The order of the names inside a clause is not compared: `shared(a,b)` and `shared(b,a)` are one directive, and
two profiles of one program write them in either order. The tool's own `class` and `decision` fields compared the
text as written, so they are computed again here from the recorded directives and checks (the tool's fields are
kept in the records and counted in section 6).

    venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/e4_replay_readout.py [RUN_DIR]
"""
import collections
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAMILY = 54     # the campaign's family with this test in it: the bound is p × 54
sys.path.insert(0, str(HERE.parents[2] / "tools"))
sys.path.insert(0, str(HERE.parents[3] / "shared"))
from main_comparison_stats import wilcoxon_greater  # noqa: E402
RUN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / "runs" / "e4_replay"
PARTS = [("e3_r", "the pragma experiment, the 18 loops"), ("e3_d", "the pragma experiment, the recurrence loops"),
         ("e3b", "the contrast set"), ("e1v6", "the main comparison, the 18 loops")]
rows, manifests = [], {}
for part, _ in PARTS:
    for f in sorted((RUN / part).glob("**/results.jsonl")):
        for ln in f.read_text().splitlines():
            if ln.strip():
                r = json.loads(ln)
                r["part"] = part
                rows.append(r)
    for f in sorted((RUN / part).glob("**/manifest.json")):
        manifests.setdefault(part, []).append(json.loads(f.read_text()))


CLAUSE = re.compile(r"(\w+)\(([^)]*)\)")


def _clause(m):
    head, body = "", m.group(2)
    if ":" in body:                       # reduction(+:a,b): the operator stays in front
        head, body = body.split(":", 1)
        head = head.strip() + ":"
    return f"{m.group(1)}({head}{','.join(sorted(x.strip() for x in body.split(',')))})"


def norm(pragma):
    """A directive with the names inside each clause in one order."""
    return CLAUSE.sub(_clause, pragma)


def no_shared(pragma):
    """A directive without its `shared(...)` clauses: a variable declared outside the loop is shared by default, so
    the clause changes nothing in the program — used for the sensitivity count only."""
    return re.sub(r"\s+", " ", re.sub(r"\bshared\([^)]*\)", "", pragma)).strip()


def exposed_set(arm):
    return sorted(json.dumps([e[0], e[1], e[2], sorted(norm(x) for x in e[3])]) for e in arm.get("exposed", []))


def kept_directives(arm, drop_shared=False):
    """As `refresh_replay.kept_directives`, with the clauses' names in one order."""
    if arm.get("status") != "exposed" or arm.get("judged") != "safe_deferred":
        return None
    singles = [c for c in arm.get("checks", []) if c["lines"] is not None and c["passed"]]
    together = [c for c in arm.get("checks", []) if c["lines"] is None]
    if together and not together[-1]["passed"]:
        singles = singles[:1]
    f = (lambda x: no_shared(norm(x))) if drop_shared else norm
    return sorted((tuple(c["lines"]), tuple(sorted(f(x) for x in c["pragmas"]))) for c in singles)


def classify(full, other, second=False):
    if not full.get("usable"):
        return "full re-profile failed"
    if not other.get("usable"):
        return "second full re-profile failed" if second else "fast refresh unusable: the agent falls back to the full re-profile"
    fe, ue = full["status"] == "exposed", other["status"] == "exposed"
    if fe and ue:
        return "same: parallel in both, the same directives" if exposed_set(full) == exposed_set(other) \
            else "parallel in both, other loops or other directives"
    if ue and not fe:
        return "parallel only after the fast refresh"
    if fe and not ue:
        return "parallel only after the full re-profile"
    return "same: not parallel in either"


def decide(full, other, second=False, drop_shared=False):
    if not full.get("usable"):
        return "full re-profile failed"
    if not other.get("usable"):
        return "second full re-profile failed" if second else "fast refresh unusable: the agent falls back to the full re-profile"
    if "exposed" in (full.get("judged"), other.get("judged")):
        return "judgement left to the final annotation after one of the two"
    kf, ku = kept_directives(full, drop_shared), kept_directives(other, drop_shared)
    if kf is None and ku is None:
        return "reverted after both"
    if kf is not None and ku is not None:
        return "kept after both, the same directives" if kf == ku else "kept after both, other directives"
    return "kept only after the full re-profile" if kf is not None else "kept only after the fast refresh"


as_recorded = collections.Counter()
for r in rows:
    if "full" not in r:
        continue
    as_recorded["decision differs"] += r.get("decision") in ("kept after both, other directives", "kept only after the full re-profile", "kept only after the fast refresh")
    as_recorded["control differs"] += r.get("control_decision") in ("kept after both, other directives", "kept only after the full re-profile", "kept only after the fast refresh")
    as_recorded["verdict differs"] += not str(r.get("class")).startswith("same")
    as_recorded["control verdict differs"] += not str(r.get("control_class")).startswith("same")
    r["class"] = classify(r["full"], r["fast"])
    r["control_class"] = classify(r["full"], r["full2"], second=True)
    if "decision" in r:
        r["decision"] = decide(r["full"], r["fast"])
        r["control_decision"] = decide(r["full"], r["full2"], second=True)
        r["decision_no_shared"] = decide(r["full"], r["fast"], drop_shared=True)
        r["control_decision_no_shared"] = decide(r["full"], r["full2"], second=True, drop_shared=True)


def table(head, body):
    return ["| " + " | ".join(head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"] \
        + ["| " + " | ".join(str(c) for c in r) + " |" for r in body]


CLASSES = ["same: not parallel in either", "same: parallel in both, the same directives",
           "parallel in both, other loops or other directives", "parallel only after the fast refresh",
           "parallel only after the full re-profile", "fast refresh unusable: the agent falls back to the full re-profile",
           "full re-profile failed", "profile before the rewrite failed"]
DECISIONS = ["reverted after both", "kept after both, the same directives", "kept after both, other directives",
             "kept only after the full re-profile", "kept only after the fast refresh",
             "fast refresh unusable: the agent falls back to the full re-profile", "full re-profile failed",
             "second full re-profile failed", "judgement left to the final annotation after one of the two"]
md = ["# E4, step 1 — the fast refresh on the model's own rewrites, replayed without a model", "",
      "Generated by `analysis/e4_replay_readout.py` from `runs/e4_replay/`. No model in anything here."]
tot = collections.Counter()
for part, name in PARTS:
    for m in manifests.get(part, []):
        for k in ("trials", "passed", "replayable", "base_unknown", "kept_chain_broken", "before_profile_failed", "rewrites_written"):
            tot[k] += int(m.get(k) or 0)
passes = sorted({m.get("discopop_pass_sha256") for ms in manifests.values() for m in ms})
commits = sorted({m.get("commit") for ms in manifests.values() for m in ms})
md += ["", f"**The population:** {tot['trials']} trials, {tot['passed']} rewrites that passed the checks, {tot['replayable']} "
       f"with the program before them rebuilt ({tot['base_unknown']} whose diff applies to no state of its trial), "
       f"{len(rows)} replayed. Commit `{', '.join(str(c)[:9] for c in commits)}`; the DiscoPoP pass "
       f"`{', '.join(str(p)[:12] for p in passes)}`.", ""]

# ---- the verdict ---------------------------------------------------------------------------------------------------
md += ["## 1 What DiscoPoP says about the rewritten lines", ""]
c_all = collections.Counter(r["class"] for r in rows)
body = []
for part, name in PARTS:
    c = collections.Counter(r["class"] for r in rows if r["part"] == part)
    body.append([name, sum(c.values())] + [c[k] for k in CLASSES[:5]] + [sum(c[k] for k in CLASSES[5:])])
body.append(["**all**", len(rows)] + [c_all[k] for k in CLASSES[:5]] + [sum(c_all[k] for k in CLASSES[5:])])
md += table(["rewrites of", "replayed", "not parallel in either", "parallel in both, same directives",
             "parallel in both, other loops or directives", "parallel only after the fast refresh",
             "parallel only after the full re-profile", "no comparison"], body)
unknown = sorted(set(c_all) - set(CLASSES))
if unknown:
    md += ["", f"Classes not in the list: {unknown}."]
ok = [r for r in rows if "full" in r and r["full"].get("usable") and r["fast"].get("usable")]
differ = [r for r in ok if not r["class"].startswith("same")]
ctl = [r for r in rows if "full2" in r and r["full"].get("usable") and r["full2"].get("usable")]
ctl_differ = [r for r in ctl if not r["control_class"].startswith("same")]
md += ["", f"**The fast refresh's verdict differs from the full re-profile's in {len(differ)} of {len(ok)} rewrites compared. "
       f"The control — a second full re-profile of the same program against the first — differs in {len(ctl_differ)} of {len(ctl)}.**", ""]
st = collections.Counter((r["full"]["status"], r["fast"]["status"]) for r in ok)
md += table(["full re-profile says", "fast refresh says", "rewrites"], [[a, b, n] for (a, b), n in sorted(st.items(), key=lambda kv: -kv[1])])

# what the fast refresh adds: directives per rewrite, and on which kind of loop
extra = collections.Counter()
for r in ok:
    f = {json.dumps(e) for e in r["full"].get("exposed", [])}
    u = {json.dumps(e) for e in r["fast"].get("exposed", [])}
    extra["only after the fast refresh"] += len(u - f)
    extra["only after the full re-profile"] += len(f - u)
    extra["after both"] += len(u & f)
md += ["", f"Loops with a directive, summed over the rewrites: {extra['after both']} the same after both, "
       f"{extra['only after the fast refresh']} only after the fast refresh, {extra['only after the full re-profile']} only "
       "after the full re-profile.", ""]

# ---- the decision --------------------------------------------------------------------------------------------------
if any("decision" in r for r in rows):
    md += ["## 2 Whether the rewrite would be kept, speed aside", "",
           "The safety half of the agent's own judgement (`judge_as_shipped`, `measure=None`): DiscoPoP's directives for "
           "the exposed loops through the gate's safety checks, outermost first, one per nest, then together.", ""]
    d_all = collections.Counter(r.get("decision") for r in rows if "decision" in r)
    body = []
    for part, name in PARTS:
        c = collections.Counter(r.get("decision") for r in rows if r["part"] == part and "decision" in r)
        body.append([name, sum(c.values())] + [c[k] for k in DECISIONS[:5]] + [sum(c[k] for k in DECISIONS[5:])])
    body.append(["**all**", sum(d_all.values())] + [d_all[k] for k in DECISIONS[:5]] + [sum(d_all[k] for k in DECISIONS[5:])])
    md += table(["rewrites of", "judged", "reverted after both", "kept after both, same directives",
                 "kept after both, other directives", "kept only after the full re-profile",
                 "kept only after the fast refresh", "no comparison"], body)
    n_cmp = sum(d_all[k] for k in DECISIONS[:5])
    n_diff = sum(d_all[k] for k in DECISIONS[2:5])
    c_all2 = collections.Counter(r.get("control_decision") for r in rows if "control_decision" in r)
    c_cmp = sum(c_all2[k] for k in DECISIONS[:5])
    c_diff = sum(c_all2[k] for k in DECISIONS[2:5])
    md += ["", f"**The decision differs in {n_diff} of {n_cmp} rewrites compared** — {d_all[DECISIONS[3]]} kept only after the full "
           f"re-profile, {d_all[DECISIONS[4]]} only after the fast refresh, {d_all[DECISIONS[2]]} kept after both with other directives. "
           f"**The control (the second full re-profile against the first): {c_diff} of {c_cmp}**"
           + (" — " + ", ".join(f"{k}: {c_all2[k]}" for k in DECISIONS[2:5] if c_all2[k]) if c_diff else "") + ".", ""]
    # the gate on the fast refresh's own directives
    g = collections.Counter()
    for r in rows:
        for c in r.get("fast", {}).get("checks", []):
            if c["lines"] is not None:
                g["passed" if c["passed"] else f"refused: {c['stage']}"] += 1
    gf = collections.Counter()
    for r in rows:
        for c in r.get("full", {}).get("checks", []):
            if c["lines"] is not None:
                gf["passed" if c["passed"] else f"refused: {c['stage']}"] += 1
    md += ["Directives judged by the gate's safety checks (one check per loop): after the fast refresh "
           + (", ".join(f"{k} {v}" for k, v in sorted(g.items(), key=lambda kv: -kv[1])) or "none")
           + "; after the full re-profile " + (", ".join(f"{k} {v}" for k, v in sorted(gf.items(), key=lambda kv: -kv[1])) or "none") + ".", ""]
    # per loop: where the decision differs
    by = collections.defaultdict(collections.Counter)
    for r in rows:
        if "decision" in r:
            by[(r["part"], r["benchmark"])][r["decision"]] += 1
    md += ["### Per loop", ""]
    md += table(["rewrites of", "loop", "judged", "reverted after both", "kept after both, same", "kept after both, other",
                 "kept only after full", "kept only after fast"],
                [[p, f"`{b}`", sum(c.values())] + [c[k] for k in DECISIONS[:5]] for (p, b), c in sorted(by.items())])
    md.append("")
    # the rewrites the trial itself kept
    kept = [r for r in rows if r.get("kept_in_trial") and "decision" in r]
    kd = collections.Counter(r["decision"] for r in kept)
    md += [f"**The {len(kept)} rewrites the trials themselves kept** (after the full re-profile, with the speed check): "
           + ", ".join(f"{k}: {v}" for k, v in sorted(kd.items(), key=lambda kv: -kv[1])) + ".", ""]

    def kind(pragmas):
        text = " ".join(pragmas)
        m = re.search(r"reduction\(([^:]+):", text)
        return f"reduction({m.group(1)})" if m else "lastprivate" if "lastprivate" in text else "parallel for" if "parallel for" in text else "another construct"

    lost = [r for r in rows if r.get("decision") == "kept only after the full re-profile"]
    lk = collections.Counter(" + ".join(sorted(kind(p) for _, p in kept_directives(r["full"]))) for r in lost)
    lf = collections.Counter(("a pattern, every directive refused by the checks" if r["fast"].get("judged") == "pattern_broken"
                              else "a pattern, no usable directive" if r["fast"]["status"] == "no_usable_pragma" else "no pattern") for r in lost)
    md += [f"**The {len(lost)} rewrites kept only after the full re-profile** — the full profile's directives: "
           + ", ".join(f"{k} {v}" for k, v in sorted(lk.items(), key=lambda kv: -kv[1])) + "; after the fast refresh: "
           + ", ".join(f"{k} {v}" for k, v in sorted(lf.items(), key=lambda kv: -kv[1])) + f"; {sum(1 for r in lost if r.get('kept_in_trial'))} "
           "of them are rewrites their trial kept; by loop: "
           + ", ".join(f"`{k}` {v}" for k, v in sorted(collections.Counter(r["benchmark"].split("/")[1] for r in lost).items())) + ".", ""]
    # what the fast refresh offers on the very loop the full profile's kept directive stands on
    shape = lambda ps: re.sub(r"\s+", " ", CLAUSE.sub(
        lambda m: f"{m.group(1)}({m.group(2).split(':')[0] + ':' if ':' in m.group(2) else ''}…)", " ".join(ps).replace("#pragma omp ", "")))
    same_loop = collections.Counter()
    for r in lost:
        offered = {(e[0], e[1]): e[3] for e in r["fast"].get("exposed", [])}
        sent = {tuple(c["lines"]): c for c in r["fast"].get("checks", []) if c["lines"] is not None}
        for lines, pragmas in kept_directives(r["full"]):
            o, c = offered.get(tuple(lines)), sent.get(tuple(lines))
            same_loop[(shape(pragmas), shape(o) if o else "no directive",
                       "not sent to the gate" if c is None else "passed" if c["passed"] else f"refused: {c['stage']}")] += 1
    md += ["On the loop of each directive the full profile keeps there, the fast refresh offers (a directive the "
           "agent's clause check or the OpenMP build refuses is not sent to the gate):", ""]
    md += table(["the full profile's directive", "the fast refresh, the same loop", "the gate", "rewrites"],
                [[f"`{k[0]}`", f"`{k[1]}`" if k[1] != "no directive" else k[1], k[2], v]
                 for k, v in sorted(same_loop.items(), key=lambda kv: -kv[1])]) + [""]
    only_fast = [r for r in rows if r.get("decision") == "kept only after the fast refresh"]
    for r in only_fast:
        md.append(f"- kept only after the fast refresh: `{r['trial']}` #{r['n']} — the full re-profile: {r['full']['status']}"
                  + (f", {r['full'].get('judged')}" if r['full'].get('judged') else "") + "; the fast refresh keeps "
                  + "; ".join(f"lines {a[0]}–{a[1]} `{' '.join(p)}`" for a, p in kept_directives(r["fast"])) + ".")
    if only_fast:
        md.append("")
    oth = [r for r in rows if r.get("decision") == "kept after both, other directives"]
    sp = collections.Counter()
    for r in oth:
        a, b = kept_directives(r["full"]), kept_directives(r["fast"])
        la, lb = {x[0] for x in a}, {x[0] for x in b}
        sp["the same loops with other clauses" if la == lb else "the full profile's loops and more" if la < lb
           else "fewer loops than the full profile" if lb < la else "other loops"] += 1
    md += [f"**The {len(oth)} rewrites kept after both with other directives:** "
           + ", ".join(f"{k} {v}" for k, v in sorted(sp.items(), key=lambda kv: -kv[1])) + ".", ""]

# ---- the registered test -------------------------------------------------------------------------------------------
if any("decision" in r for r in rows):
    SAME = ("reverted after both", "kept after both, the same directives")
    loops = collections.defaultdict(lambda: [0, 0, 0])     # loop -> rewrites compared, differing after fast, differing in the control
    for r in rows:
        if "decision" not in r or "control_decision" not in r:
            continue
        if r["decision"] not in DECISIONS[:5] or r["control_decision"] not in DECISIONS[:5]:
            continue                                         # no comparison in one of the two
        name = r["benchmark"].split("/")[1]
        loops[name][0] += 1
        loops[name][1] += r["decision"] not in SAME
        loops[name][2] += r["control_decision"] not in SAME
    diffs = [v[1] / v[0] - v[2] / v[0] for v in loops.values() if v[0]]
    w = wilcoxon_greater(diffs)
    p = w.get("p_value")
    md += ["## 3 The registered test, E4-1", "",
           "H6's second half: the fast refresh changes no decision. Per loop (the rewrites of every experiment pooled), the "
           "share of rewrites whose decision differs after the fast refresh against the share that differs in the control; "
           f"one-sided Wilcoxon signed-rank over the loops; a new member of the campaign's family, the bound is p × {FAMILY}.", "",
           f"{len(loops)} loops; the decision differs after the fast refresh on {sum(1 for v in loops.values() if v[1])} of them "
           f"and in the control on {sum(1 for v in loops.values() if v[2])}; non-zero pairs {w.get('n_nonzero')}. "
           + (f"**p = {p:.3g}; family bound {min(1.0, p * FAMILY):.3g} — H6's second half is "
              f"{'refuted' if p < 0.05 else 'not refuted'} as a single test"
              f"{' and within the family' if p * FAMILY < 0.05 else ', not within the family' if p < 0.05 else ''}.**"
              if p is not None else f"**No test: {w.get('note')}.**"), ""]
    md += table(["loop", "rewrites compared", "decision differs after the fast refresh", "in the control"],
                [[f"`{k}`", v[0], v[1], v[2]] for k, v in sorted(loops.items())])
    md.append("")
    # the sensitivity: a directive that differs only in a `shared` clause counted as the same (not registered)
    loops2 = collections.defaultdict(lambda: [0, 0, 0])
    for r in rows:
        if r.get("decision_no_shared") not in DECISIONS[:5] or r.get("control_decision_no_shared") not in DECISIONS[:5]:
            continue
        name = r["benchmark"].split("/")[1]
        loops2[name][0] += 1
        loops2[name][1] += r["decision_no_shared"] not in SAME
        loops2[name][2] += r["control_decision_no_shared"] not in SAME
    w2 = wilcoxon_greater([v[1] / v[0] - v[2] / v[0] for v in loops2.values() if v[0]])
    p2 = w2.get("p_value")
    n2 = sum(v[1] for v in loops2.values())
    d2 = collections.Counter(r.get("decision_no_shared") for r in rows if "decision_no_shared" in r)
    md += ["**Sensitivity, not registered:** a variable declared outside a loop is shared by default, so a directive that differs "
           "from another only in a `shared(...)` clause is the same program. Counted that way the decision differs in "
           f"{n2} rewrites ({d2[DECISIONS[3]]} kept only after the full re-profile, {d2[DECISIONS[4]]} only after the fast refresh, "
           f"{d2[DECISIONS[2]]} kept after both on other loops) on {sum(1 for v in loops2.values() if v[1])} loops, in the control in "
           f"{sum(v[2] for v in loops2.values())}; non-zero pairs {w2.get('n_nonzero')}; "
           + (f"p = {p2:.3g}, family bound {min(1.0, p2 * FAMILY):.3g}." if p2 is not None else f"no test: {w2.get('note')}."), ""]

# ---- the check against the trials ----------------------------------------------------------------------------------
md += ["## 4 The replay's full re-profile against what the trial logged", ""]
have = [r for r in ok if r.get("trial_verdict")]
agree = [r for r in have if r["trial_verdict"] == r["full"]["status"]]
dis = collections.Counter((r["part"], r["benchmark"], r["trial_verdict"], r["full"]["status"]) for r in have if r not in agree)
md += [f"{len(agree)} of {len(have)} rewrites get from the replay's full re-profile the verdict their trial logged."
       + (" The others: " + "; ".join(f"`{b}` ({p}) trial {t} → replay {f}: {n}" for (p, b, t, f), n in sorted(dis.items())) + "."
          if dis else ""), ""]

# ---- the time ------------------------------------------------------------------------------------------------------
md += ["## 5 Seconds", ""]
fs = [r["full"]["seconds"] for r in ok]
us = [r["fast"]["seconds"] for r in ok]
if fs and us:
    md += table(["one refresh", "rewrites", "median s", "mean s", "sum s"],
                [["full re-profile (instrument, run, explore)", len(fs), f"{statistics.median(fs):.2f}", f"{statistics.mean(fs):.2f}", f"{sum(fs):.0f}"],
                 ["fast refresh (compile, carry over, explore)", len(us), f"{statistics.median(us):.2f}", f"{statistics.mean(us):.2f}", f"{sum(us):.0f}"]])
    js = [r["fast"].get("judge_seconds") or 0 for r in ok], [r["full"].get("judge_seconds") or 0 for r in ok]
    md += ["", f"The gate's safety checks on the directives: {sum(js[0]):.0f} s after the fast refresh, {sum(js[1]):.0f} s after the "
           f"full re-profile, summed. Refresh and checks together: {sum(us) + sum(js[0]):.0f} s after the fast refresh, "
           f"{sum(fs) + sum(js[1]):.0f} s after the full re-profile.", ""]
md += ["## 6 The tool's own fields, as recorded", "",
       "`refresh_replay.py` compared the directives as text. Counted on its `class` and `decision` fields: the verdict differs in "
       f"{as_recorded['verdict differs']} rewrites after the fast refresh and in {as_recorded['control verdict differs']} in the control; "
       f"the decision in {as_recorded['decision differs']} and {as_recorded['control differs']}. Every difference between that and the "
       "counts above is a clause whose names stand in another order.", ""]
(HERE / "e4_replay_readout.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
