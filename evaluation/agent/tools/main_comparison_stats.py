#!/usr/bin/env python3
"""The main comparison in numbers — DiscoPoP alone vs DiscoPoP + agent, per measured class.

The statistics are the ones the plan pre-registered (EXPERIMENT_PLAN.html §2, "Statistics"),
nothing chosen after seeing data:

  * rates with **Wilson 95 % intervals** — how many trials reach a verified parallel program,
    how many are FASTER, for the agent arm and for DiscoPoP alone;
  * **paired by benchmark: Wilcoxon signed-rank on per-benchmark medians**, one-sided (the
    agent's program is faster than the one DiscoPoP alone leaves), with **Cliff's delta** as
    the effect size;
  * a **bootstrap 95 % interval on the median** of agent ÷ DiscoPoP alone over benchmarks;
  * **unsafe acceptances as a count with every case named** — never a p-value;
  * everything that is MISSING (no verdict, no baseline, withheld ratios) listed, because a
    trial that is silently absent biases whatever is left.

Speeds enter only where they were measured: a kernel no size of which can be timed (the
harness switched the agent's speed check off, `speed_check_off`) counts for coverage and is
left out of every speed statistic, as pre-registered.

    agent/tools/main_comparison_stats.py e1_r_a e1_r_b [--arm default] [--out DIR]

`agent/benchmark plots` writes the same file next to the figures.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import figures  # noqa: E402

PARALLEL_VERDICTS = {"gained", "gained-not-faster", "better", "equal", "worse"}
NO_DATA = {"invalid", "no-baseline"}


def wilson(k: int, n: int, z: float = 1.959964) -> Tuple[float, float]:
    """Wilson score interval for k successes in n trials."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cliffs_delta(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    """P(a > b) - P(a < b) over all pairs; +1 = every a above every b."""
    if not a or not b:
        return None
    gt = sum(1 for x in a for y in b if x > y)
    lt = sum(1 for x in a for y in b if x < y)
    return (gt - lt) / (len(a) * len(b))


def bootstrap_median(vals: Sequence[float], n_boot: int = 10000, seed: int = 20260921) -> Optional[Tuple[float, float]]:
    if len(vals) < 3:
        return None
    rng = random.Random(seed)                       # fixed: the interval must be reproducible
    meds = sorted(statistics.median(rng.choices(list(vals), k=len(vals))) for _ in range(n_boot))
    return (meds[int(0.025 * n_boot)], meds[int(0.975 * n_boot) - 1])


def wilcoxon_greater(diffs: Sequence[float]) -> Dict[str, Any]:
    """One-sided Wilcoxon signed-rank on paired differences (H1: median difference > 0)."""
    nz = [d for d in diffs if abs(d) > 1e-12]
    out: Dict[str, Any] = {"n_pairs": len(diffs), "n_nonzero": len(nz)}
    if len(nz) < 6:
        out["note"] = "fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable)"
        return out
    try:
        from scipy import stats                      # type: ignore[import-untyped]
        r = stats.wilcoxon(nz, alternative="greater", zero_method="wilcox")
        out.update(statistic=float(r.statistic), p_value=float(r.pvalue))
    except Exception as e:                           # noqa: BLE001 - reported, never hidden
        out["note"] = f"test not run: {e}"
    return out


def _speed_check_off(t: dict) -> bool:
    """The agent's own speed check was off in this trial — by the per-trial record where it
    exists (since 2026-09-21), otherwise by the command line the trial really ran."""
    if t.get("speed_check_off") is not None:
        return bool(t["speed_check_off"])
    cmd = [str(x) for x in (t.get("agent_cmd") or [])]
    on = [i for i, x in enumerate(cmd) if x == "--require-speedup"]
    off = [i for i, x in enumerate(cmd) if x == "--no-require-speedup"]
    return bool(off) and (not on or max(off) > max(on))


def _untimeable(t: dict) -> bool:
    """No size of this kernel can be timed: the harness's own verification says so."""
    return (t.get("verify") or {}).get("speed_measurable") is False


def analyse(trials: List[dict], arm: Optional[str] = None) -> Dict[str, Any]:
    rows = figures.vs_discopop_alone(trials)
    if arm:
        rows = [r for r in rows if r["arm"] == arm]
    by_trial = {(str(t.get("benchmark")), t.get("arm"), t.get("repeat")): t for t in trials}
    base = [t for t in trials if t.get("arm") == figures.BASELINE_ARM]
    classes = figures._classes()
    result: Dict[str, Any] = {"arm": arm or sorted({str(r["arm"]) for r in rows}),
                              "runs": sorted({str(t.get("run_id")) for t in trials}), "classes": {}}
    for cls in ("R", "A", "D", ""):
        rs = [r for r in rows if (r.get("class") or "") == cls]
        if not rs:
            continue
        benches = sorted({str(r["benchmark"]) for r in rs})
        n = len(rs)
        counts = {v: sum(1 for r in rs if r["verdict"] == v) for v, _ in figures.VS_ORDER}
        valid = [r for r in rs if r["verdict"] not in NO_DATA]
        k_par = sum(1 for r in valid if r["verdict"] in PARALLEL_VERDICTS)
        k_fast = sum(1 for r in valid if r.get("agent_outcome") == "FASTER")
        bs = [t for t in base if classes.get(str(t.get("benchmark")), "") == cls]
        kb_par = sum(1 for t in bs if t.get("outcome") in figures.PARALLEL_OK)
        kb_fast = sum(1 for t in bs if t.get("outcome") == "FASTER")
        # speed, paired by benchmark, only where the kernel can be timed
        pairs: List[Tuple[str, float, float]] = []
        untimeable: List[str] = []
        for b in benches:
            br = [r for r in rs if r["benchmark"] == b and r["verdict"] not in NO_DATA]
            if any(_untimeable(by_trial.get((b, r["arm"], r.get("repeat"))) or {}) for r in br) or \
               any(r.get("agent_outcome") == "parallel-speed-not-measurable" for r in br):
                untimeable.append(b)
                continue
            a = [r["agent_speedup_vs_seq"] for r in br if r["agent_speedup_vs_seq"] and r["timing_comparable"]]
            d = next((r["dp_alone_speedup_vs_seq"] for r in br if r["dp_alone_speedup_vs_seq"]), None)
            if a and d:
                pairs.append((b, statistics.median(a), float(d)))
        ratios = [a / d for _, a, d in pairs]
        result["classes"][cls or "unclassified"] = {
            "benchmarks": len(benches), "trials": n, "verdicts": counts,
            "agent_parallel_rate": {"k": k_par, "n": len(valid), "wilson95": wilson(k_par, len(valid))},
            "agent_faster_rate": {"k": k_fast, "n": len(valid), "wilson95": wilson(k_fast, len(valid))},
            "dp_alone_parallel_rate": {"k": kb_par, "n": len(bs), "wilson95": wilson(kb_par, len(bs))},
            "dp_alone_faster_rate": {"k": kb_fast, "n": len(bs), "wilson95": wilson(kb_fast, len(bs))},
            "benchmarks_with_a_gain": sorted({str(r["benchmark"]) for r in rs if r["verdict"] in ("gained", "gained-not-faster")}),
            "speed_pairs": len(pairs), "untimeable_benchmarks": untimeable,
            "median_ratio_agent_over_dp_alone": statistics.median(ratios) if ratios else None,
            "median_ratio_bootstrap95": bootstrap_median(ratios),
            "wilcoxon_agent_faster": wilcoxon_greater([math.log(a / d) for _, a, d in pairs]),
            "cliffs_delta": cliffs_delta([a for _, a, _ in pairs], [d for _, _, d in pairs]),
            "unsafe_cases": [f"{r['benchmark']} rep{r.get('repeat')}" for r in rs if r["verdict"] == "unsafe"],
            "lost_cases": [f"{r['benchmark']} rep{r.get('repeat')}" for r in rs if r["verdict"] == "lost"],
            "missing": [f"{r['benchmark']} rep{r.get('repeat')}: {r['verdict']} ({r.get('agent_outcome')})"
                        for r in rs if r["verdict"] in NO_DATA or r["verdict"] == "not-comparable"],
        }
    agent_trials = [t for t in trials if t.get("arm") != figures.BASELINE_ARM and (not arm or t.get("arm") == arm)]
    result["process"] = {
        "agent_trials": len(agent_trials),
        "llm_calls": sum(int(t.get("llm_calls") or 0) for t in agent_trials),
        "llm_call_failures": sum(int(t.get("llm_call_failures") or 0) for t in agent_trials),
        "refresh_full": sum(int(t.get("refresh_full") or 0) for t in agent_trials),
        "refresh_fast": sum(int(t.get("refresh_fast") or 0) for t in agent_trials),
        "refresh_fallback": sum(int(t.get("refresh_fallback") or 0) for t in agent_trials),
        "runtime_remeasurements": sum(int(t.get("runtime_remeasurements") or 0) for t in agent_trials),
        "explorer_stalls": sum(int(t.get("explorer_stalls") or 0) for t in trials),
        "profile_explorer_stalls": sum(int((t.get("profile") or {}).get("explore_stalls") or 0) for t in trials),
        "trials_with_speed_check_off": sum(1 for t in agent_trials if _speed_check_off(t)),
        "host_load_range": [min((t.get("host_load_start") or [0])[0] or 0 for t in trials) if trials else None,
                            max((t.get("host_load_start") or [0])[0] or 0 for t in trials) if trials else None],
    }
    return result


def _pct(d: Dict[str, Any]) -> str:
    lo, hi = d["wilson95"]
    return f"{d['k']} of {d['n']} ({100 * d['k'] / d['n']:.0f} %, 95 % CI {100 * lo:.0f}–{100 * hi:.0f} %)" if d["n"] else "—"


def to_markdown(res: Dict[str, Any]) -> str:
    suite_note = (f" **Restricted to the `{res['suite']}` suite** — the primary set of D30; the registered set's "
                  f"numbers stand beside it, never behind it." if res.get("suite") else "")
    out = ["# The main comparison in numbers", "",
           f"Runs: {', '.join(res['runs'])}. Agent arm: `{res['arm']}`; baseline: `{figures.BASELINE_ARM}` "
           "(DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson "
           "intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, "
           "bootstrap interval on the median ratio; unsafe acceptances are named, not tested." + suite_note, ""]
    names = {"R": "Class R — DiscoPoP alone reaches nothing (THE CLAIM)",
             "A": "Class A — parallel as written (no-harm control)",
             "D": "Class D — true recurrences (must-decline control)", "unclassified": "Unclassified"}
    for cls, c in res["classes"].items():
        v = c["verdicts"]
        out += [f"## {names.get(cls, cls)}", "",
                f"- {c['benchmarks']} benchmarks, {c['trials']} agent trials. Verdicts: "
                + ", ".join(f"**{k}** {n}" for k, n in v.items() if n) + ".",
                f"- Trials reaching a verified parallel program — agent: {_pct(c['agent_parallel_rate'])}; "
                f"DiscoPoP alone: {_pct(c['dp_alone_parallel_rate'])}.",
                f"- Trials FASTER (≥ 1.1× over the sequential original) — agent: {_pct(c['agent_faster_rate'])}; "
                f"DiscoPoP alone: {_pct(c['dp_alone_faster_rate'])}.",
                f"- Benchmarks with at least one gain: {len(c['benchmarks_with_a_gain'])} of {c['benchmarks']}"
                + (f" ({', '.join(c['benchmarks_with_a_gain'])})" if c["benchmarks_with_a_gain"] else "") + "."]
        if c["speed_pairs"]:
            w = c["wilcoxon_agent_faster"]
            ci = c["median_ratio_bootstrap95"]
            out.append(f"- Speed, paired by benchmark ({c['speed_pairs']} timeable benchmarks): median agent ÷ DiscoPoP "
                       f"alone = **{c['median_ratio_agent_over_dp_alone']:.2f}×**"
                       + (f" (bootstrap 95 % CI {ci[0]:.2f}–{ci[1]:.2f}×)" if ci else "")
                       + (f"; Wilcoxon signed-rank, one-sided: W = {w['statistic']:.0f}, p = {w['p_value']:.4g}, "
                          f"{w['n_nonzero']} non-zero pairs" if "p_value" in w else f"; {w.get('note', '')}")
                       + (f"; Cliff's δ = {c['cliffs_delta']:+.2f}" if c["cliffs_delta"] is not None else "") + ".")
        if c["untimeable_benchmarks"]:
            out.append(f"- Left out of every speed statistic (no size can be timed): {', '.join(c['untimeable_benchmarks'])}.")
        out.append(f"- **Unsafe acceptances: {len(c['unsafe_cases'])}**" + (f" — {', '.join(c['unsafe_cases'])}" if c["unsafe_cases"] else "") + ".")
        if c["lost_cases"]:
            out.append(f"- Lost (DiscoPoP alone reaches a parallel program, the agent's trial does not): {', '.join(c['lost_cases'])}.")
        if c["missing"]:
            out.append(f"- Missing or withheld ({len(c['missing'])}): " + "; ".join(c["missing"]) + ".")
        out.append("")
    pr = res["process"]
    out += ["## What actually happened inside the trials", "",
            f"- {pr['agent_trials']} agent trials, {pr['llm_calls']} model calls ({pr['llm_call_failures']} failed).",
            f"- Profile refreshes after a kept rewrite: {pr['refresh_full']} full, {pr['refresh_fast']} fast, "
            f"**{pr['refresh_fallback']} fast→full fallback(s)**; runtimes re-measured {pr['runtime_remeasurements']} time(s).",
            f"- Explorer stalls (killed at the limit, draw repeated): {pr['explorer_stalls']} inside agents, "
            f"{pr['profile_explorer_stalls']} in the harness's profile step.",
            f"- Agent trials with the speed check off (untimeable kernel): {pr['trials_with_speed_check_off']}.",
            f"- Host load (1-min) at trial start: {pr['host_load_range'][0]:.0f}–{pr['host_load_range'][1]:.0f}." if pr["host_load_range"][0] is not None else "", ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--arm", default=None, help="agent arm to analyse (default: every non-baseline arm pooled)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--suite", default=None,
                    help="only benchmarks of this suite (`tsvc`): the PRIMARY set of D30, computed with the "
                         "same statistics as the registered set, never instead of it")
    a = ap.parse_args()
    trials: List[dict] = []
    for run in a.runs:
        # The working copy of a run if it is here, its tracked archive otherwise.
        root = next((d for d in (HERE.parent / "runs" / run, HERE.parent / "results" / run) if d.exists()), None)
        if root is None:
            sys.exit(f"run {run} not found under runs/ or results/")
        for p in sorted(root.glob("benchmarks/**/trial.json")):
            t = json.loads(p.read_text())
            t.setdefault("run_id", run)                 # a raw trial record does not name its run
            if a.suite and not str(t.get("benchmark", "")).startswith(a.suite + "/"):
                continue
            trials.append(t)
    res = analyse(trials, a.arm)
    if a.suite:
        res["suite"] = a.suite
    md = to_markdown(res)
    print(md)
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "main_comparison_stats.md").write_text(md + "\n")
        (a.out / "main_comparison_stats.json").write_text(json.dumps(res, indent=2, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
