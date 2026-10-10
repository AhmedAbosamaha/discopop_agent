#!/usr/bin/env python3
"""E3b's one pre-registered test (THESIS_EXPERIMENTS §6, 10 Oct 2026), from the two per-setup read-outs.

E3b is E3's question — who writes the pragma, DiscoPoP from its analysis of the rewritten code (`default_v5`) or
the model in the same edit (`llm_pragmas_v5`) — on the contrast set: loops DiscoPoP alone leaves unchanged and
whose reference is one or a few directives away (suite `tsvc_c4`; the rule, its exclusions and the measured
classes are in the record). `main_comparison_stats.py` is run once per setup into `analysis/discopop_writes/`
and `analysis/model_writes/`, exactly as for E3; this reads the two `main_comparison_stats.json`:

  E3b-1  on the loops under test (class R of the read-outs), more race-free FASTER trials where the model writes
         the pragma than where DiscoPoP writes it — Cochran-Mantel-Haenszel stratified by loop, one-sided, the
         Mantel-Haenszel odds ratio with its 95 % interval and the exact conditional test beside it.  Refuted if
         the setup in which the model writes ships more unusable programs than the other over all its trials.

A new member of the campaign's family: the bound is p × M with M = 53.  The statistics are e3_tests.py's and
e2b1_stats.py's (checked there by `--self-test`); nothing is computed here that E3's script does not compute.

    venv/bin/python evaluation/agent/tools/e3b_tests.py --analysis evaluation/agent/results/E03b_contrast_set/analysis
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e3_tests import AGENT, SETUPS, _p, analyse  # noqa: E402

FAMILY = 53


def to_markdown(res: Dict[str, Any], reads: Dict[str, Dict[str, Any]], family: int) -> str:
    h6, un = res["h6"], res["unusable"]
    p1 = h6["cmh"].get("p_one_sided")                 # with the continuity correction, as E3's test
    p1 = 1.0 if p1 is None else float(p1)
    orr = h6["or"]
    or_txt = (f"Mantel-Haenszel odds ratio {orr['or']:.3g} (95 % {orr['ci95'][0]:.3g}–{orr['ci95'][1]:.3g})"
              if orr.get("ci95") else "Mantel-Haenszel odds ratio infinite (no loop with a trial against the model's setup)"
              if orr.get("or_infinite") else f"odds ratio: {orr.get('note', 'not estimable')}")
    mf = h6["cmh"].get("mantel_fleiss")
    cmh_txt = (h6["cmh"]["note"] if "note" in h6["cmh"] else
               f"{h6['cmh']['informative_strata']} informative loop(s); the normal approximation "
               + ("holds" if mf and mf["met"] else "does not hold (Mantel-Fleiss) — read the exact p"))
    exact = h6["exact"].get("p_greater")
    verdict = ("refuted (more unusable programs)" if h6["refuted_by_unusable"]
               else "supported" if p1 < 0.05 else "not established")
    d1 = (f"the model writes {h6['model'][0]} of {h6['model'][1]}, DiscoPoP writes {h6['discopop'][0]} of {h6['discopop'][1]}; "
          f"{len(h6['loops_that_differ'])} loop(s) differ ({', '.join(h6['loops_that_differ']) or 'none'}); {cmh_txt}; "
          f"{or_txt}; exact conditional p {_p(exact)}; unusable programs over all trials: "
          f"{un['model_writes']['unusable']} of {un['model_writes']['n']} where the model writes, "
          f"{un['discopop_writes']['unusable']} of {un['discopop_writes']['n']} where DiscoPoP writes")
    out = ["# E3b — the pre-registered test (the loops under test of the contrast set)", "",
           "Registered in THESIS_EXPERIMENTS §6 on 10 Oct 2026, before any of E3b's trials. One-sided as registered; one "
           f"test, a new member of the campaign's family: the bound is p × {family}.", "",
           "| test | hypothesis | p (one-sided) | family bound | verdict | detail |", "|---|---|---:|---:|---|---|",
           f"| E3b-1 | more race-free FASTER trials where the model writes the pragma than where DiscoPoP writes it "
           f"(CMH stratified by loop) | {_p(p1)} | {_p(min(1.0, p1 * family))} | {verdict} | {d1} |",
           "", "## Per loop under test: race-free FASTER trials", "",
           "| loop | DiscoPoP writes | the model writes | Haiku alone |", "|---|---:|---:|---:|"]
    for r in res["rows"]:
        a = r["alone"]
        out.append(f"| `{r['loop']}` | {r['discopop']['faster_race_free']} of {r['discopop']['n']} | "
                   f"{r['model']['faster_race_free']} of {r['model']['n']} | "
                   + (f"{a['faster_race_free']} of {a['n']}" if a.get("n") else "—") + " |")
    out += ["", "## The three-way table per setup", "",
            "| loops | setup | race-free FASTER | verified parallel | unusable (BROKEN · slower · racy · not compiling) |",
            "|---|---|---:|---:|---|"]
    names = {"R": "under test", "A": "control", "D": "recurrence"}
    for cls in ("R", "A", "D"):
        shown = False
        for s, name in SETUPS:
            block = reads[s]["three_way"]["classes"].get(cls)
            if not block:
                continue
            for label in (("DiscoPoP alone",) if not shown else ()) + (AGENT,) + (("model alone",) if s == "model_writes" else ()):
                v = block["arms"].get(label)
                if not v:
                    continue
                who = ("the agent, " + name) if label == AGENT else "Haiku alone" if label == "model alone" else label
                out.append(f"| {names[cls]} | {who} | {v['faster_race_free']['k']} of {v['with_verdict']} | {v['parallel']['k']} | "
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
    ap.add_argument("--out-name", default="e3b_tests.md")
    ap.add_argument("--no-write", action="store_true", help="print only (used to check the script on E3's read-outs)")
    a = ap.parse_args()
    reads: Dict[str, Dict[str, Any]] = {s: json.loads((a.analysis / s / "main_comparison_stats.json").read_text())
                                        for s, _ in SETUPS}
    res = analyse(reads)
    text = to_markdown(res, reads, a.family)
    if not a.no_write:
        (a.analysis / a.out_name).write_text(text)
        (a.analysis / "e3b_tests.json").write_text(json.dumps(
            {"e3b_1": res["h6"], "unusable": res["unusable"]}, indent=1, default=str) + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
