#!/usr/bin/env python3
"""E11 part 2 read-out — RepoOMP's release, the agent, Sonnet 4.5 alone and DiscoPoP alone on E2-v6b's seven hidden-
order kernels (record §6, 6 Nov, "E11 part 2 pre-registered"; population `config/e11b_population.json`).

Every trial is judged as E2-v6b judged its trials (`e2b1_stats.judge`: exactly one bucket; a SUCCESS is a race-free
verified parallel program whose construct covers the hot loop; UNSAFE is racy, BROKEN, not compiling, or editing
the measurement; a failed model call or a harness edit is out of every denominator) with ONE change written in the
pre-registration: the race verdict of EVERY setup comes from `race_check.py` (E2 took the gate's verdict for the
agent's programs; RepoOMP's release has no gate of its own, and part 2 checks all four setups the same way). A
setup's parallel program with no race verdict is `race-unchecked`, never a success.

What is read out, in this order:
  1. per unit and setup: the buckets (and FASTER among the successes);
  2. direction (a) pooled per setup: successes and unsafe programs with Wilson 95 % intervals;
  3. RepoOMP's release at its three levels per unit: what its rules and its model PROPOSED, what its own check
     ACCEPTED (`opt_method`), what the harness and the race check JUDGED;
  4. the two pre-registered tests on direction (a), stratified by unit, one-sided, the exact conditional test
     (Birch 1964; Fisher's per stratum) as the p value, the Mantel-Haenszel odds ratio beside it, Holm over the two:
       E11b-i   successes, the agent (`llm_pragmas_v5`) against RepoOMP's release (more);
       E11b-ii  unsafe programs, RepoOMP's release against the agent (more);
  5. descriptive only: the same two counts against Sonnet alone and DiscoPoP alone; k48 and k53 apart;
  6. the by-hand class of the hot loop (classes fixed in the population file) where `--by-hand` is given;
  7. model calls and cost per setup.

    venv/bin/python evaluation/agent/results/E11_repoomp/analysis/part2_readout.py \
        e11b_r_repoomp e11b_r_agent_1 e11b_r_agent_2 e11b_bare \
        --races .../e11b_race_check/results.jsonl --by-hand .../by_hand.json --out .../analysis/part2
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
import e2b1_stats  # noqa: E402
import figures  # noqa: E402
from main_comparison_stats import load_races, wilson  # noqa: E402

POPULATION = HERE.parents[2] / "config" / "e11b_population.json"
SETUPS = ["repoomp_release", "llm_pragmas_v5", "bare_llm_v4", "discopop_gate_v5"]
NAMES = {"repoomp_release": "RepoOMP's release", "llm_pragmas_v5": "the agent", "bare_llm_v4": "Sonnet 4.5 alone",
         "discopop_gate_v5": "DiscoPoP alone"}
TESTS = [("E11b-i", "successes: the agent against RepoOMP's release", "llm_pragmas_v5", "repoomp_release", "success"),
         ("E11b-ii", "unsafe programs: RepoOMP's release against the agent", "repoomp_release", "llm_pragmas_v5", "unsafe")]

# The pre-registered change to E2's judge: every setup's race verdict from the race check (see the docstring).
e2b1_stats._model_only = lambda arm: True  # type: ignore[assignment]


def runner_label(t: dict) -> dict:
    """RepoOMP's release judged with the label the runner gives the agent's own trials.

    `verify-source` records `kind: baseline`, and the runner's `classify` never gives a baseline `no-change` or
    `changed-not-parallel` ("a parallelization by construction": an expert's directives, a compiler flag) — so an
    unchanged program is `parallel-not-faster`. RepoOMP's release is not one by construction: with no rule and no
    model program accepted (`opt_method: none`) it ships the original unchanged (the probe's k19, 6 Nov). Its trials
    therefore take `classify`'s rule for the agent's trials, in `classify`'s order (after BROKEN, before speed): the
    source unchanged → `no-change`; changed without an added directive → `changed-not-parallel`. The label the
    judge printed is kept as `outcome_verify_source`."""
    if t.get("arm") != "repoomp_release" or t.get("outcome") not in figures.PARALLEL_OK:
        return t
    if not t.get("source_changed"):
        return dict(t, outcome="no-change", outcome_verify_source=t.get("outcome"))
    if int(t.get("pragmas_in_final") or 0) == 0:
        return dict(t, outcome="changed-not-parallel", outcome_verify_source=t.get("outcome"))
    return t


def load_population(path: Path) -> Tuple[Dict[str, str], str]:
    spec = json.loads(path.read_text())
    role: Dict[str, str] = {}
    for d, block in spec["directions"].items():
        for u in block["units"]:
            role[u["benchmark"]] = d
    for u in spec.get("decline_units", []):
        role[u["benchmark"]] = "decline"
    return role, str(spec["model"])


def _model_ok(t: dict, model: Optional[str]) -> bool:
    if model is None or t.get("arm") == "discopop_gate_v5":
        return True
    if t.get("arm") == "repoomp_release":
        return t.get("repoomp_model") == model
    return t.get("model") == model


def levels(t: dict) -> Dict[str, Any]:
    """RepoOMP's release on one trial, step by step (repoomp_result.json): what its rules proposed and whether that passed
    its check; for its model (step 3, the original): whether the model answered, whether primitive_adder's own
    validation kept a candidate (`model_attempts`, recorded from 6 Nov), whether a CHANGED file reached the release's
    check — a file byte-equal to its input is no proposal (primitive_adder writes its input back when it keeps no
    candidate; the release may then accept that copy on timing noise) — and whether it passed; what the release
    accepted (`opt_method`)."""
    r = t.get("repoomp") or {}
    rules, model, on_rules = r.get("rules") or {}, r.get("model") or {}, r.get("model_on_rules") or {}
    att = r.get("model_attempts") or []
    reasons = [str(b.get("reason")) for a in att for b in ((a.get("status") or {}).get("batches") or [])
               if not b.get("accepted")]
    file_proposed = bool(model) and "skipped" not in model and not model.get("candidate_equals_source")
    return {"rules_proposed": int(r.get("rules_changes") or 0) > 0,
            "rules_passed_own_check": rules.get("verified") if "skipped" not in rules else None,
            "model_answered": int(t.get("llm_calls") or 0) - int(t.get("llm_call_failures") or 0) > 0,
            "model_kept_by_its_validation": (any(int(a.get("accepted_batches") or 0) > 0 for a in att)
                                             if att else None),
            "model_rejection_reasons": reasons,
            "model_proposed": file_proposed,
            "model_passed_own_check": model.get("verified") if file_proposed else None,
            "model_on_rules_run": bool(on_rules),
            "model_on_rules_proposed": bool(on_rules) and not on_rules.get("candidate_equals_source"),
            "accepted": str(r.get("opt_method") or "none"),
            "accepted_a_copy": str(r.get("opt_method")) in ("model", "rules+model") and not r.get("final_changed"),
            "own_speedup": r.get("speedup_own_check")}


def analyse(trials: List[dict], role: Dict[str, str], model: Optional[str],
            races: Dict[Tuple[str, str, str, int], str], by_hand: Dict[str, str]) -> Dict[str, Any]:
    js: List[Dict[str, Any]] = []
    for t in trials:
        if t.get("benchmark") not in role or t.get("arm") not in SETUPS or not _model_ok(t, model):
            continue
        t = runner_label(t)
        j = e2b1_stats.judge(t, races)
        j["role"] = role[str(t["benchmark"])]
        j["calls"] = int(t.get("llm_calls") or 0)
        j["cost"] = float((t.get("llm_usage") or {}).get("cost_usd") or 0.0)
        j["by_hand"] = by_hand.get(f"{j['arm']}/{j['benchmark']}/rep{j['repeat']}")
        if j["arm"] == "repoomp_release":
            j["levels"] = levels(t)
        js.append(j)
    units = sorted(role, key=lambda b: ({"a": 0, "b": 1, "decline": 2}[role[b]], b))
    per_unit: Dict[str, Dict[str, Any]] = {}
    for b in units:
        for s in SETUPS:
            cell = [j for j in js if j["benchmark"] == b and j["arm"] == s]
            if not cell:
                continue
            per_unit.setdefault(b, {})[s] = {
                "trials": len(cell), "with_verdict": sum(j["with_verdict"] for j in cell),
                "buckets": dict(Counter(j["bucket"] for j in cell)),
                "success": sum(j["success"] for j in cell), "unsafe": sum(j["unsafe"] for j in cell),
                "faster_successes": sum(j["success"] and j["faster"] for j in cell)}
    pooled: Dict[str, Dict[str, Any]] = {}
    for s in SETUPS:
        cell = [j for j in js if j["arm"] == s and j["role"] == "a" and j["with_verdict"]]
        if cell:
            n, k_s, k_u = len(cell), sum(j["success"] for j in cell), sum(j["unsafe"] for j in cell)
            pooled[s] = {"n": n, "success": k_s, "success_ci95": wilson(k_s, n), "unsafe": k_u,
                         "unsafe_ci95": wilson(k_u, n)}
    tests: Dict[str, Dict[str, Any]] = {}
    a_js = [j for j in js if j["role"] == "a"]
    for name, what, x, y, outcome in TESTS:
        strata = e2b1_stats.strata_for(a_js, x, y, outcome, key=lambda j: str(j["benchmark"]))
        tabs = [t for _, t in strata]
        missing = [s for s in (x, y) if not any(j["arm"] == s and j["with_verdict"] for j in a_js)]
        if missing:
            tests[name] = {"what": what, "note": "no trials of " + ", ".join(NAMES[s] for s in missing)}
            continue
        ex = e2b1_stats.exact_conditional(tabs)
        tests[name] = {"what": what, "x": x, "y": y, "outcome": outcome, "strata": {k: list(v) for k, v in strata},
                       "p_exact_one_sided": ex["p_greater"], "mh": e2b1_stats.mh_odds_ratio(tabs)}
    holm = e2b1_stats.holm({k: v.get("p_exact_one_sided") for k, v in tests.items()})
    for k in tests:
        tests[k]["p_holm"] = holm.get(k)
    rel: Dict[str, Dict[str, Any]] = {}
    for b in units:
        cell = [j for j in js if j["benchmark"] == b and j["arm"] == "repoomp_release"]
        if cell:
            L = [j["levels"] for j in cell]
            rel[b] = {"trials": len(cell), "rules_proposed": sum(x["rules_proposed"] for x in L),
                      "rules_passed_own_check": sum(x["rules_passed_own_check"] is True for x in L),
                      "model_answered": sum(x["model_answered"] for x in L),
                      "model_kept_by_its_validation": sum(x["model_kept_by_its_validation"] is True for x in L),
                      "model_rejection_reasons": dict(Counter(y for x in L for y in x["model_rejection_reasons"])),
                      "model_proposed": sum(x["model_proposed"] for x in L),
                      "model_passed_own_check": sum(x["model_passed_own_check"] is True for x in L),
                      "accepted_a_copy": sum(x["accepted_a_copy"] for x in L),
                      "accepted": dict(Counter(x["accepted"] for x in L)),
                      "judged": dict(Counter(j["bucket"] for j in cell))}
    hand: Dict[str, Dict[str, int]] = {}
    need: List[str] = []
    for j in js:
        if j["arm"] in ("repoomp_release", "llm_pragmas_v5", "bare_llm_v4") and \
                (j["outcome"] in ("FASTER", "parallel-not-faster", "parallel-speed-not-measurable", "BROKEN")):
            if j["by_hand"]:
                hand.setdefault(j["arm"], Counter())[j["by_hand"]] += 1  # type: ignore[index]
            else:
                need.append(f"{j['arm']}/{j['benchmark']}/rep{j['repeat']}")
    cost = {s: {"trials": sum(1 for j in js if j["arm"] == s), "calls": sum(j["calls"] for j in js if j["arm"] == s),
                "cost_usd": round(sum(j["cost"] for j in js if j["arm"] == s), 2)} for s in SETUPS}
    return {"units": units, "role": role, "per_unit": per_unit, "pooled_a": pooled, "tests": tests,
            "repoomp_levels": rel, "by_hand": {k: dict(v) for k, v in hand.items()}, "by_hand_missing": sorted(need),
            "cost": cost, "trials": js}


def _p(x: Optional[float]) -> str:
    return "—" if x is None else (f"{x:.2g}" if x < 0.001 else f"{x:.3f}")


def _ci(c: Optional[Tuple[float, float]]) -> str:
    return "" if not c else f" [{100 * c[0]:.0f}–{100 * c[1]:.0f} %]"


def to_markdown(r: Dict[str, Any]) -> str:
    L = ["# E11 part 2 — the hidden-order kernels", "",
         "Judged as E2-v6b judged its trials, every setup's race verdict from the race check (record §6, 6 Nov).", "",
         "## Per unit", "", "| unit | direction | setup | trials | success (FASTER) | unsafe | buckets |",
         "|---|---|---|---|---|---|---|"]
    for b in r["units"]:
        for s, c in r["per_unit"].get(b, {}).items():
            bk = ", ".join(f"{k} {v}" for k, v in sorted(c["buckets"].items()))
            L.append(f"| {b} | {r['role'][b]} | {NAMES[s]} | {c['trials']} | {c['success']} ({c['faster_successes']}) "
                     f"| {c['unsafe']} | {bk} |")
    L += ["", "## Direction (a), pooled", "", "| setup | with a verdict | success | unsafe |", "|---|---|---|---|"]
    for s, c in r["pooled_a"].items():
        L.append(f"| {NAMES[s]} | {c['n']} | {c['success']}{_ci(c['success_ci95'])} | {c['unsafe']}{_ci(c['unsafe_ci95'])} |")
    L += ["", "## The two tests (direction a, stratified by unit, one-sided, exact conditional p, Holm over the two)", "",
          "| test | what | p exact | p Holm | MH odds ratio [95 %] |", "|---|---|---|---|---|"]
    for k, t in r["tests"].items():
        mh = t.get("mh") or {}
        o = "∞" if mh.get("or_infinite") else ("—" if mh.get("or") is None else f"{mh['or']:.2f}")
        ci = f" [{mh['ci95'][0]:.2f}, {mh['ci95'][1]:.2f}]" if mh.get("ci95") else ""
        L.append(f"| {k} | {t['what']} | {_p(t.get('p_exact_one_sided'))} | {_p(t.get('p_holm'))} | {o}{ci} |")
    L += ["", "## RepoOMP's release at its three levels", "",
          "Model: answered = at least one call answered; kept = primitive_adder's own validation kept a candidate; "
          "file = a CHANGED file reached the release's check; passed = that file passed it. An accepted copy is the "
          "release accepting a model file byte-equal to its input (timing noise).", "",
          "| unit | trials | rules proposed | rules passed its check | model answered | kept by its validation | model file | passed its check | accepted (opt_method) | of which a copy | judged | its validation's reasons |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b, c in r["repoomp_levels"].items():
        acc = ", ".join(f"{k} {v}" for k, v in sorted(c["accepted"].items()))
        jd = ", ".join(f"{k} {v}" for k, v in sorted(c["judged"].items()))
        rs = ", ".join(f"{k} {v}" for k, v in sorted(c["model_rejection_reasons"].items())) or "—"
        L.append(f"| {b} | {c['trials']} | {c['rules_proposed']} | {c['rules_passed_own_check']} | {c['model_answered']} "
                 f"| {c['model_kept_by_its_validation']} | {c['model_proposed']} | {c['model_passed_own_check']} | {acc} "
                 f"| {c['accepted_a_copy']} | {jd} | {rs} |")
    L += ["", "## The hot loop by hand", ""]
    for s, c in r["by_hand"].items():
        L.append(f"- {NAMES[s]}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
    if r["by_hand_missing"]:
        L.append(f"- not yet classed: {len(r['by_hand_missing'])} program(s): " + ", ".join(r["by_hand_missing"]))
    L += ["", "## Model calls and cost", "", "| setup | trials | calls | cost (USD) |", "|---|---|---|---|"]
    for s, c in r["cost"].items():
        if c["trials"]:
            L.append(f"| {NAMES[s]} | {c['trials']} | {c['calls']} | {c['cost_usd']:.2f} |")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", help="run ids (RUN:ARM+ARM keeps only those arms)")
    ap.add_argument("--races", type=Path, action="append", default=[])
    ap.add_argument("--by-hand", type=Path, default=None, help='{"<setup>/<benchmark>/rep<N>": "<class>"}')
    ap.add_argument("--population", type=Path, default=POPULATION)
    ap.add_argument("--rename", action="append", default=[], metavar="OLD=NEW",
                    help="read an arm under a setup's name (testing this tool on an archived experiment)")
    ap.add_argument("--any-model", action="store_true", help="do not filter on the population's model (testing)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    role, model = load_population(a.population)
    trials = e2b1_stats.load_trials(a.runs)
    ren = dict(x.split("=", 1) for x in a.rename)
    for t in trials:
        if t.get("arm") in ren:
            t["arm"] = ren[t["arm"]]
    races = load_races(a.races)
    if ren:   # the race results name the old arm
        races = {(r, b, ren.get(arm, arm), n): v for (r, b, arm, n), v in races.items()}
    by_hand = json.loads(a.by_hand.read_text()) if a.by_hand else {}
    res = analyse(trials, role, None if a.any_model else model, races, by_hand)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "readout.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    (a.out / "readout.md").write_text(to_markdown(res))
    print(to_markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
