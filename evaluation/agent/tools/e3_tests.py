#!/usr/bin/env python3
"""E3's two pre-registered tests (THESIS_EXPERIMENTS §6, 9 Oct 2026), from the two per-setup read-outs.

E3 asks who writes the pragma — DiscoPoP from its analysis of the rewritten code (`default_v5`) or the model
in the same edit (`llm_pragmas_v5`) — on E1-v6's set. `main_comparison_stats.py` is run once per setup (that
setup's and DiscoPoP alone's trials plus Haiku alone's from E1-v6, `--three-way ARM --bare bare_llm_v4
--baseline-arm discopop_gate_v5 --races …`) into `analysis/discopop_writes/` and `analysis/model_writes/`;
this reads the two `main_comparison_stats.json` and writes the tests as registered, class R:

  E3-1 (H6, its half on the pragma's author; registered 14 Sep)  more race-free FASTER trials where the model
       writes the pragma than where DiscoPoP writes it — Cochran-Mantel-Haenszel stratified by loop, one-sided
       in the registered direction, the Mantel-Haenszel odds ratio with its 95 % interval and the exact
       conditional test beside it.  Refuted, as restated on 9 Oct, if the setup in which the model writes ships
       more unusable programs than the other over its 105 trials (all three classes);
  E3-2 (H6b, registered 23 Sep, restated 9 Oct)  with the model writing the pragma the agent reaches at least
       Haiku alone's race-free FASTER rate with no BROKEN trial — refuted if lower (Wilcoxon signed-rank on the
       per-loop rates, one-sided: Haiku alone ahead) or if any of its trials is BROKEN.

Both are members of the campaign's family already: Holm over the two inside E3, and the family's bound p × M
(M = 52).  A paired comparison with fewer than six non-zero pairs cannot reach significance and is reported
"no test" (p = 1), as in E1's tests.  The statistics are e2b1_stats.py's (checked there by `--self-test`).

    venv/bin/python evaluation/agent/tools/e3_tests.py --analysis evaluation/agent/results/E03_who_writes_the_pragmas/analysis
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e2b1_stats import Table, cmh, exact_conditional, mh_odds_ratio  # noqa: E402

FAMILY = 52
AGENT = "DiscoPoP + agent"
SETUPS = (("discopop_writes", "DiscoPoP writes the pragma"), ("model_writes", "the model writes the pragma"))


def holm(ps: List[float]) -> List[float]:
    """Holm's step-down adjusted p-values, in the input order."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj = [1.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


def wilcoxon_less(diffs: List[float]) -> Dict[str, Any]:
    """One-sided Wilcoxon signed-rank on per-loop differences, alternative: the differences are below zero.
    Fewer than six non-zero pairs: no test, as main_comparison_stats.py's paired tests."""
    nz = [d for d in diffs if abs(d) > 1e-12]
    out: Dict[str, Any] = {"n_pairs": len(diffs), "n_nonzero": len(nz), "above": sum(1 for d in nz if d > 0),
                           "below": sum(1 for d in nz if d < 0)}
    if len(nz) < 6:
        out["note"] = "fewer than 6 non-zero pairs: no test"
        return out
    from scipy import stats                          # type: ignore[import-untyped]
    out["p_less"] = float(stats.wilcoxon(nz, alternative="less", zero_method="wilcox").pvalue)
    return out


def _short(b: str) -> str:
    return b.split("/")[-1]


def analyse(reads: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """The two tests and the tables they rest on, from the two per-setup read-outs."""
    per = {s: reads[s]["three_way"]["classes"]["R"]["per_benchmark"] for s, _ in SETUPS}
    loops = sorted(per["model_writes"], key=_short)
    if sorted(per["discopop_writes"], key=_short) != loops:
        raise SystemExit("the two read-outs do not hold the same class-R loops")
    strata: List[Table] = []
    rows: List[Dict[str, Any]] = []
    for b in loops:
        m, d = per["model_writes"][b][AGENT], per["discopop_writes"][b][AGENT]
        alone = per["model_writes"][b].get("model alone", {})
        strata.append((float(m["faster_race_free"]), float(m["n"] - m["faster_race_free"]),
                       float(d["faster_race_free"]), float(d["n"] - d["faster_race_free"])))
        rows.append({"loop": _short(b), "model": m, "discopop": d, "alone": alone})
    unusable: Dict[str, Dict[str, Any]] = {}
    for s, _ in SETUPS:
        arms = [reads[s]["three_way"]["classes"][c]["arms"][AGENT] for c in ("R", "D", "A")
                if c in reads[s]["three_way"]["classes"]]
        unusable[s] = {"n": sum(int(a["with_verdict"]) for a in arms), "unusable": sum(int(a["unusable"]) for a in arms),
                       "broken": sum(int(a["broken"]) for a in arms),
                       "cases": [c for a in arms for c in a.get("unusable_cases", [])]}
    differ = [r["loop"] for r in rows if r["model"]["faster_race_free"] * r["discopop"]["n"]
              != r["discopop"]["faster_race_free"] * r["model"]["n"]]
    h6 = {"cmh": cmh(strata, alternative="greater"), "or": mh_odds_ratio(strata), "exact": exact_conditional(strata),
          "model": [sum(int(t[0]) for t in strata), sum(int(t[0] + t[1]) for t in strata)],
          "discopop": [sum(int(t[2]) for t in strata), sum(int(t[2] + t[3]) for t in strata)], "loops_that_differ": differ,
          "refuted_by_unusable": unusable["model_writes"]["unusable"] > unusable["discopop_writes"]["unusable"]}
    paired = [r for r in rows if r["alone"].get("n") and r["model"]["n"]]       # a loop both have trials on
    h6b = wilcoxon_less([r["model"]["faster_race_free"] / max(1, r["model"]["n"])
                         - r["alone"]["faster_race_free"] / max(1, r["alone"]["n"]) for r in paired])
    h6b.update({"model": [sum(r["model"]["faster_race_free"] for r in paired), sum(r["model"]["n"] for r in paired)],
                "alone": [sum(r["alone"]["faster_race_free"] for r in paired), sum(r["alone"]["n"] for r in paired)],
                "broken_class_r": sum(int(r["model"]["broken"]) for r in rows)})
    return {"rows": rows, "h6": h6, "h6b": h6b, "unusable": unusable}


def _p(x: Optional[float]) -> str:
    return "—" if x is None else f"{x:.3g}"


def to_markdown(res: Dict[str, Any], reads: Dict[str, Dict[str, Any]], family: int) -> str:
    h6, h6b, un = res["h6"], res["h6b"], res["unusable"]
    p1 = h6["cmh"].get("p_one_sided")                 # with the continuity correction, as E2-B1's tests
    p1 = 1.0 if p1 is None else float(p1)
    p2 = float(h6b.get("p_less", 1.0))
    adj = holm([p1, p2])
    orr = h6["or"]
    or_txt = (f"Mantel-Haenszel odds ratio {orr['or']:.3g} (95 % {orr['ci95'][0]:.3g}–{orr['ci95'][1]:.3g})"
              if orr.get("ci95") else "Mantel-Haenszel odds ratio infinite (no loop with a trial against the model's setup)"
              if orr.get("or_infinite") else f"odds ratio: {orr.get('note', 'not estimable')}")
    mf = h6["cmh"].get("mantel_fleiss")
    cmh_txt = (h6["cmh"]["note"] if "note" in h6["cmh"] else
               f"{h6['cmh']['informative_strata']} informative loop(s); the normal approximation "
               + ("holds" if mf and mf["met"] else "does not hold (Mantel-Fleiss) — read the exact p"))
    d1 = (f"the model writes {h6['model'][0]} of {h6['model'][1]}, DiscoPoP writes {h6['discopop'][0]} of {h6['discopop'][1]}; "
          f"{len(h6['loops_that_differ'])} loop(s) differ ({', '.join(h6['loops_that_differ']) or 'none'}); {cmh_txt}; "
          f"{or_txt}; exact conditional p {_p(h6['exact'].get('p_greater'))}; unusable programs over all classes: "
          f"{un['model_writes']['unusable']} of {un['model_writes']['n']} where the model writes, "
          f"{un['discopop_writes']['unusable']} of {un['discopop_writes']['n']} where DiscoPoP writes"
          + (" — REFUTED by the unusable programs, as restated" if h6["refuted_by_unusable"] else ""))
    d2 = (f"the model writes {h6b['model'][0]} of {h6b['model'][1]}, Haiku alone {h6b['alone'][0]} of {h6b['alone'][1]}; "
          f"the agent ahead on {h6b['above']} loops, Haiku alone on {h6b['below']}"
          + (f"; {h6b['note']}" if "note" in h6b else "")
          + f"; BROKEN trials of the setup on class R: {h6b['broken_class_r']}, over all classes: {un['model_writes']['broken']}")
    refuted_b = p2 < 0.05 or un["model_writes"]["broken"] > 0
    out = ["# E3 — the two pre-registered tests (class R, 18 loops)", "",
           "Registered in THESIS_EXPERIMENTS §6 (H6: 14 Sep; H6b: 23 Sep; both restated on 9 Oct 2026, before any of E3's "
           f"trials). One-sided as registered; Holm over the two; the campaign family's bound is p × {family}.", "",
           "| test | hypothesis | p (one-sided) | Holm (E3) | family bound | verdict | detail |", "|---|---|---:|---:|---:|---|---|",
           f"| E3-1 | H6 — more race-free FASTER trials where the model writes the pragma than where DiscoPoP writes it "
           f"(CMH stratified by loop) | {_p(p1)} | {_p(adj[0])} | {_p(min(1.0, p1 * family))} | "
           f"{'refuted (more unusable programs)' if h6['refuted_by_unusable'] else 'supported' if adj[0] < 0.05 else 'not established'} | {d1} |",
           f"| E3-2 | H6b — with the model writing, at least Haiku alone's race-free FASTER rate and nothing BROKEN; p is "
           f"the refuting direction (Haiku alone ahead, Wilcoxon on the per-loop rates) | {_p(p2)} | {_p(adj[1])} | "
           f"{_p(min(1.0, p2 * family))} | {'REFUTED' if refuted_b else 'not refuted'} | {d2} |",
           "", "## Per loop (class R): race-free FASTER trials", "",
           "| loop | DiscoPoP writes | the model writes | Haiku alone (E1-v6) |", "|---|---:|---:|---:|"]
    for r in res["rows"]:
        a = r["alone"]
        out.append(f"| `{r['loop']}` | {r['discopop']['faster_race_free']} of {r['discopop']['n']} | "
                   f"{r['model']['faster_race_free']} of {r['model']['n']} | "
                   + (f"{a['faster_race_free']} of {a['n']}" if a.get("n") else "—") + " |")
    out += ["", "## The three-way table per setup, by class", "",
            "| class | setup | race-free FASTER | verified parallel | unusable (BROKEN · slower · racy · not compiling) |",
            "|---|---|---:|---:|---|"]
    for cls in ("R", "D", "A"):
        shown = False
        for s, name in SETUPS:
            block = reads[s]["three_way"]["classes"].get(cls)
            if not block:
                continue
            for label in (("DiscoPoP alone",) if not shown else ()) + (AGENT,) + (("model alone",) if s == "model_writes" else ()):
                v = block["arms"].get(label)
                if not v:
                    continue
                who = ("the agent, " + name) if label == AGENT else "Haiku alone (E1-v6)" if label == "model alone" else label
                out.append(f"| {cls} | {who} | {v['faster_race_free']['k']} of {v['with_verdict']} | {v['parallel']['k']} | "
                           f"**{v['unusable']}** ({v['broken']} · {v['slower_shipped']} · {v['racy']} · {v['did_not_compile']})"
                           + (f" — {'; '.join(v['unusable_cases'])}" if label == AGENT and v.get("unusable_cases") else "") + " |")
            shown = True
    for s, name in SETUPS:
        out += ["", f"**Unusable programs shipped by the agent where {name}: {un[s]['unusable']} of {un[s]['n']}** — "
                + ("; ".join(un[s]["cases"]) or "none") + "."]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--analysis", type=Path, required=True)
    ap.add_argument("--family", type=int, default=FAMILY, help="the campaign family's size M for the bound p × M")
    ap.add_argument("--out-name", default="e3_tests.md")
    a = ap.parse_args()
    reads: Dict[str, Dict[str, Any]] = {s: json.loads((a.analysis / s / "main_comparison_stats.json").read_text())
                                        for s, _ in SETUPS}
    res = analyse(reads)
    text = to_markdown(res, reads, a.family)
    (a.analysis / a.out_name).write_text(text)
    (a.analysis / "e3_tests.json").write_text(json.dumps(
        {"h6": res["h6"], "h6b": res["h6b"], "unusable": res["unusable"]}, indent=1, default=str) + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
