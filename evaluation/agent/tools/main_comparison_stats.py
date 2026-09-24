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


SLOWER = 1 / figures.WIN_RATIO            # a correct parallel program below this ships a slowdown


RACE_STAGES = ("tsan", "schedules")        # what makes a program racy; any other failed stage = not judgeable


def _best_speedup(t: dict) -> Optional[float]:
    """The trial's best kernel speedup over the sequential original (trial.json keeps it per
    thread count under verify.par; trials.csv's best_speedup is derived the same way)."""
    if t.get("best_speedup"):
        return float(t["best_speedup"])
    par = (t.get("verify") or {}).get("par") or {}
    sp = [float(v.get("speedup") or v.get("kernel_speedup") or 0) for v in par.values() if isinstance(v, dict)]
    sp = [x for x in sp if x > 0]
    return max(sp) if sp else None


def _run_of(t: dict) -> str:
    return str(t.get("run_id") or "")


def load_races(paths: Sequence[Path]) -> Dict[Tuple[str, str, str, int], str]:
    """race_check.py results: (run, benchmark, arm, repeat) -> 'clean' or the stage that failed."""
    out: Dict[Tuple[str, str, str, int], str] = {}
    for p in paths:
        for line in Path(p).read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            parts = str(r.get("trial", "")).split("/")
            # <group>/<section>/<run>/benchmarks/...: the run is the directory before `benchmarks`
            # (keyed on `runs/` until 24 Sep, which matched nothing archived under preflight/ or checks/)
            run = parts[parts.index("benchmarks") - 1] if "benchmarks" in parts[1:] else ""
            out[(run, str(r.get("benchmark")), str(r.get("arm")), int(r.get("repeat") or 0))] = str(r.get("verdict"))
    return out


def _wilcoxon(diffs: Sequence[float]) -> Dict[str, Any]:
    """Two-sided and one-sided (agent ahead) Wilcoxon signed-rank on per-benchmark differences."""
    nz = [d for d in diffs if abs(d) > 1e-12]
    out: Dict[str, Any] = {"n_pairs": len(diffs), "n_nonzero": len(nz),
                           "agent_ahead": sum(1 for d in nz if d > 0), "model_alone_ahead": sum(1 for d in nz if d < 0)}
    if len(nz) < 6:
        out["note"] = "fewer than 6 non-zero pairs: no test"
        return out
    try:
        from scipy import stats                      # type: ignore[import-untyped]
        out["p_two_sided"] = float(stats.wilcoxon(nz, alternative="two-sided", zero_method="wilcox").pvalue)
        out["p_agent_ahead"] = float(stats.wilcoxon(nz, alternative="greater", zero_method="wilcox").pvalue)
    except Exception as e:                           # noqa: BLE001 - reported, never hidden
        out["note"] = f"test not run: {e}"
    return out


def _did_not_compile(t: dict) -> bool:
    """The program the arm SHIPPED does not build: the harness's verification built the original
    and failed only on the final program.  A model-only arm can end this way (E1-bare `s244`
    rep 2); it is a delivered, unusable program — a verdict (H13), not a missing trial."""
    v = t.get("verify") or {}
    errs = v.get("build_errors") or {}
    return (v.get("status") == "verify_build_failed" and any(k.startswith("final") for k in errs)
            and not any(k.startswith("orig") for k in errs))


def _tampered(t: dict) -> bool:
    """The program changed the code that measures it (timer, perturbed input, digest), which
    every arm is told to leave alone: its speed and output verdicts measure nothing (H13)."""
    return t.get("outcome") == "SCAFFOLD_MODIFIED"


def three_way(trials: List[dict], agent_arm: str, bare_arm: str = "bare_llm",
              races: Optional[Dict[Tuple[str, str, str, int], str]] = None) -> Dict[str, Any]:
    """D35: DiscoPoP alone · DiscoPoP + agent · the model alone, each against the sequential
    reference, then the agent against the model alone paired by benchmark.  A program the gate
    kept passed its race stages already; the model alone's are race-free only where
    race_check.py says 'clean' (without a race file its FASTER count is output-checked only)."""
    races = races or {}
    classes = figures._classes()
    arms = {"DiscoPoP alone": figures.BASELINE_ARM, "DiscoPoP + agent": agent_arm, "model alone": bare_arm}
    res: Dict[str, Any] = {"agent_arm": agent_arm, "bare_arm": bare_arm, "race_file": bool(races), "classes": {}}
    for cls in ("R", "A", "D"):
        ts = [t for t in trials if classes.get(str(t.get("benchmark")), "") == cls]
        if not any(t.get("arm") == bare_arm for t in ts):
            continue
        benches = sorted({str(t.get("benchmark")) for t in ts if t.get("arm") == bare_arm})
        block: Dict[str, Any] = {"benchmarks": len(benches), "arms": {}, "per_benchmark": {}}
        per: Dict[str, Dict[str, Dict[str, int]]] = {b: {} for b in benches}
        for label, arm in arms.items():
            at = [t for t in ts if t.get("arm") == arm and str(t.get("benchmark")) in benches]
            # With a verdict: every outcome that judges the delivered program — including a program
            # that does not build or that rewrote its own measurement (H13, the author 24 Sep:
            # "record that as a result"). Until then those two fell under "no verdict" and left the
            # denominator (E1-bare's "of 88" = 90 minus exactly these two).
            valid = [t for t in at if t.get("outcome") in figures.PARALLEL_OK + ("no-change", "BROKEN")
                     or _did_not_compile(t) or _tampered(t)]
            par = [t for t in valid if t.get("outcome") in figures.PARALLEL_OK]
            fast = [t for t in valid if t.get("outcome") == "FASTER"]

            def race(t: dict) -> str:
                if arm != bare_arm and not _model_only(arm):
                    return "clean"                    # kept by the gate: TSan and the schedule matrix passed
                return races.get((_run_of(t), str(t.get("benchmark")), str(arm), int(t.get("repeat") or 0)), "unchecked")
            clean_fast = [t for t in fast if race(t) == "clean"]
            racy = [t for t in par if race(t) in RACE_STAGES]
            unjudged = [t for t in par if race(t) not in RACE_STAGES + ("clean", "unchecked")]
            slower = [t for t in par if (_best_speedup(t) or 1.0) < SLOWER]
            broken = [t for t in valid if t.get("outcome") == "BROKEN"]
            no_build = [t for t in valid if _did_not_compile(t)]
            tampered = [t for t in valid if _tampered(t)]
            sp = [x for x in (_best_speedup(t) for t in fast) if x]
            block["arms"][label] = {
                "arm": arm, "trials": len(at), "with_verdict": len(valid),
                "invalid": sorted({str(t.get("outcome")) for t in at if t not in valid}),
                "invalid_n": len(at) - len(valid),
                "parallel": {"k": len(par), "n": len(valid), "wilson95": wilson(len(par), len(valid))},
                "faster": {"k": len(fast), "n": len(valid), "wilson95": wilson(len(fast), len(valid))},
                "faster_race_free": {"k": len(clean_fast), "n": len(valid), "wilson95": wilson(len(clean_fast), len(valid))},
                "faster_race_unchecked": sum(1 for t in fast if race(t) == "unchecked"),
                "broken": len(broken), "slower_shipped": len(slower), "racy": len(racy),
                "race_not_judgeable": len(unjudged),
                "did_not_compile": len(no_build), "tampered": len(tampered),
                "unusable": len({id(t) for t in broken + slower + racy + no_build + tampered}),
                "unusable_cases": [f"{t.get('benchmark')} rep{t.get('repeat')}: "
                                   + ("BROKEN" if t in broken else "did not compile" if t in no_build
                                      else "changed its measuring code" if t in tampered
                                      else "racy" if t in racy else "slower")
                                   for t in valid if t in broken + slower + racy + no_build + tampered],
                "broken_cases": [f"{t.get('benchmark')} rep{t.get('repeat')}" for t in broken],
                "median_speedup_of_faster": statistics.median(sp) if sp else None,
            }
            for b in benches:
                bt = [t for t in valid if str(t.get("benchmark")) == b]
                bad = {id(t) for t in bt if t.get("outcome") == "BROKEN" or _did_not_compile(t) or _tampered(t)
                       or (t.get("outcome") in figures.PARALLEL_OK
                           and ((_best_speedup(t) or 1.0) < SLOWER or race(t) in RACE_STAGES))}
                per[b][label] = {"faster": sum(1 for t in bt if t.get("outcome") == "FASTER"),
                                 "faster_race_free": sum(1 for t in bt if t.get("outcome") == "FASTER" and race(t) == "clean"),
                                 "broken": sum(1 for t in bt if t.get("outcome") == "BROKEN"),
                                 "unusable": len(bad), "n": len(bt)}
        block["per_benchmark"] = per
        for key in ("faster", "faster_race_free"):
            diffs = [per[b]["DiscoPoP + agent"][key] / max(1, per[b]["DiscoPoP + agent"]["n"])
                     - per[b]["model alone"][key] / max(1, per[b]["model alone"]["n"])
                     for b in benches if per[b].get("DiscoPoP + agent", {}).get("n") and per[b].get("model alone", {}).get("n")]
            block[f"agent_vs_model_alone_{key}"] = _wilcoxon(diffs)
        # H13 (the author, 24 Sep): an unusable program the model-only arm ships — wrong, racy or
        # slower than the original — is a RESULT, the pipeline's trust advantage, not a lost trial.
        # Paired per benchmark: the model-only arm's unusable rate minus the agent's ("agent ahead"
        # = the agent ships fewer).
        block["agent_vs_model_alone_unusable"] = _wilcoxon(
            [per[b]["model alone"]["unusable"] / max(1, per[b]["model alone"]["n"])
             - per[b]["DiscoPoP + agent"]["unusable"] / max(1, per[b]["DiscoPoP + agent"]["n"])
             for b in benches if per[b].get("DiscoPoP + agent", {}).get("n") and per[b].get("model alone", {}).get("n")])
        res["classes"][cls] = block
    return res


def three_way_markdown(tw: Dict[str, Any]) -> str:
    out = ["## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone", "",
           f"Agent arm `{tw['agent_arm']}`, model alone `{tw['bare_arm']}`, DiscoPoP alone `{figures.BASELINE_ARM}`; "
           "the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept "
           "passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` "
           "found them clean" + ("" if tw["race_file"] else " — **no race file given: its race-free count is not established**") + ".", ""]
    names = {"R": "Class R", "A": "Class A (no-harm control)", "D": "Class D (must-decline control)"}
    for cls, b in tw["classes"].items():
        out += [f"### {names.get(cls, cls)} — {b['benchmarks']} benchmarks", "",
                "| vs the sequential original | " + " | ".join(b["arms"]) + " |",
                "|---|" + "---:|" * len(b["arms"])]
        rows = [("verified parallel program", lambda a: _pct(a["parallel"])),
                ("FASTER (≥ 1.1×)", lambda a: _pct(a["faster"])),
                ("FASTER and race-free", lambda a: _pct(a["faster_race_free"]) + (f" (+{a['faster_race_unchecked']} unchecked)" if a["faster_race_unchecked"] else "")),
                ("**BROKEN** (wrong output shipped)", lambda a: f"**{a['broken']}**"),
                ("correct but slower, shipped (< 0.91×)", lambda a: str(a["slower_shipped"])),
                ("racy (race check: TSan or the schedule matrix)", lambda a: str(a["racy"]) + (f" (+{a['race_not_judgeable']} not judgeable)" if a["race_not_judgeable"] else "")),
                ("shipped a program that does not compile", lambda a: str(a["did_not_compile"])),
                ("changed the code that measures it (told not to)", lambda a: str(a["tampered"])),
                ("**unusable programs** (any of the five above)", lambda a: f"**{a['unusable']}**"),
                ("no verdict", lambda a: f"{a['invalid_n']}" + (f" ({', '.join(a['invalid'])})" if a["invalid"] else "")),
                ("median speedup of the FASTER trials", lambda a: f"{a['median_speedup_of_faster']:.2f}×" if a["median_speedup_of_faster"] else "—")]
        for name, f in rows:
            out.append(f"| {name} | " + " | ".join(f(a) for a in b["arms"].values()) + " |")
        out.append("")
        for label, a in b["arms"].items():
            if a["unusable_cases"]:
                out.append(f"- Unusable programs shipped by {label} ({a['unusable']}): " + "; ".join(a["unusable_cases"]) + ".")
        w = b["agent_vs_model_alone_unusable"]
        out.append(f"- **H13 — unusable programs shipped (wrong, racy, slower, not compiling, or measurement changed), rate per benchmark, paired:** the agent ships "
                   f"fewer on {w['agent_ahead']}, the model-only arm fewer on {w['model_alone_ahead']}, tied on "
                   f"{w['n_pairs'] - w['n_nonzero']}"
                   + (f"; p (two-sided) = {w['p_two_sided']:.3g}, p (agent fewer) = {w['p_agent_ahead']:.3g}" if "p_two_sided" in w else f"; {w.get('note', '')}")
                   + ". Each is a result, not a discarded trial.")
        for key, label in (("faster", "FASTER"), ("faster_race_free", "race-free FASTER")):
            w = b[f"agent_vs_model_alone_{key}"]
            out.append(f"- Agent vs model alone, {label} rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on "
                       f"{w['agent_ahead']}, model alone ahead on {w['model_alone_ahead']}, tied on {w['n_pairs'] - w['n_nonzero']}"
                       + (f"; p (two-sided) = {w['p_two_sided']:.3g}, p (agent ahead) = {w['p_agent_ahead']:.3g}" if "p_two_sided" in w else f"; {w.get('note', '')}") + ".")
        out.append("")
        out += ["| benchmark | " + " | ".join(f"{k} FASTER / race-free / BROKEN / unusable" for k in b["arms"]) + " |",
                "|---|" + "---:|" * len(b["arms"])]
        for bench, d in b["per_benchmark"].items():
            out.append(f"| `{bench}` | " + " | ".join(
                f"{v['faster']} / {v['faster_race_free']} / {v['broken']} / {v['unusable']} of {v['n']}" if v else "—"
                for v in (d.get(k) for k in b["arms"])) + " |")
        out.append("")
    return "\n".join(out)


def _model_only(arm: str) -> bool:
    """An arm whose programs no gate saw — the model alone (`bare_llm`) or a twin (D38): its
    FASTER programs are race-free only where race_check.py found them clean."""
    try:
        spec = json.loads(figures.ARMS_FILE.read_text())["arms"].get(arm, {})
    except (OSError, ValueError, KeyError):
        return False
    return spec.get("runner") in ("bare_llm", "twin")


def interaction(trials: List[dict], agent_hi: str, agent_lo: str, twin_hi: str, twin_lo: str,
                races: Optional[Dict[Tuple[str, str, str, int], str]] = None) -> Dict[str, Any]:
    """H12 (D38, pre-registered 24 Sep): does a factor act THROUGH the pipeline?  Per benchmark,
    the factor's effect on the race-free FASTER rate inside the agent (agent_hi - agent_lo)
    minus its effect on the matched twins (twin_hi - twin_lo); Wilcoxon signed-rank over the
    benchmarks (two-sided, and one-sided 'larger inside the pipeline'), Cliff's delta between
    the two sets of per-benchmark effects.  A model-only arm's program counts as race-free only
    where race_check.py says 'clean': without its race file the test is refused, not run on
    output-checked counts."""
    races = races or {}
    arms = {"agent_hi": agent_hi, "agent_lo": agent_lo, "twin_hi": twin_hi, "twin_lo": twin_lo}
    unchecked = [a for a in (twin_hi, twin_lo, agent_hi, agent_lo)
                 if _model_only(a) and not any(k[2] == a for k in races)]
    res: Dict[str, Any] = {"arms": arms, "races_missing_for": unchecked, "classes": {}}
    classes = figures._classes()
    for cls in ("R", "A", "D", ""):
        ts = [t for t in trials if (classes.get(str(t.get("benchmark")), "") or "") == cls]
        benches = sorted({str(t.get("benchmark")) for t in ts
                          if all(any(u.get("arm") == a and str(u.get("benchmark")) == str(t.get("benchmark")) for u in ts)
                                 for a in arms.values())})
        if not benches:
            continue

        def rate(arm: str, bench: str, key: str) -> Optional[float]:
            at = [t for t in ts if t.get("arm") == arm and str(t.get("benchmark")) == bench
                  and t.get("outcome") in figures.PARALLEL_OK + ("no-change", "BROKEN")]
            if not at:
                return None
            def ok(t: dict) -> bool:
                if t.get("outcome") != "FASTER":
                    return False
                if key == "faster" or not _model_only(arm):
                    return True                      # kept by the gate: its race stages passed
                return races.get((_run_of(t), bench, arm, int(t.get("repeat") or 0))) == "clean"
            return sum(1 for t in at if ok(t)) / len(at)

        block: Dict[str, Any] = {"benchmarks": len(benches)}
        for key in ("faster_race_free", "faster"):
            per: Dict[str, Dict[str, float]] = {}
            for b in benches:
                r = {n: rate(a, b, key) for n, a in arms.items()}
                if any(v is None for v in r.values()):
                    continue
                ra = {n: float(v) for n, v in r.items() if v is not None}
                per[b] = {"agent_effect": ra["agent_hi"] - ra["agent_lo"],
                          "twin_effect": ra["twin_hi"] - ra["twin_lo"], **ra}
                per[b]["interaction"] = per[b]["agent_effect"] - per[b]["twin_effect"]
            w = _wilcoxon([v["interaction"] for v in per.values()])
            block[key] = {
                "per_benchmark": per, "wilcoxon": w,
                "cliffs_delta": cliffs_delta([v["agent_effect"] for v in per.values()],
                                             [v["twin_effect"] for v in per.values()]),
                "mean_agent_effect": statistics.mean(v["agent_effect"] for v in per.values()) if per else None,
                "mean_twin_effect": statistics.mean(v["twin_effect"] for v in per.values()) if per else None,
            }
        res["classes"][cls or "unclassified"] = block
    return res


def interaction_markdown(ix: Dict[str, Any]) -> str:
    a = ix["arms"]
    out = [f"## H12 — does the factor act through the pipeline? (D38)", "",
           f"Inside the agent: `{a['agent_hi']}` − `{a['agent_lo']}`; on the matched twins (no gate): "
           f"`{a['twin_hi']}` − `{a['twin_lo']}`. Per benchmark, the effect on the rate, then the difference of "
           "the two effects; Wilcoxon signed-rank over benchmarks, Cliff's δ between the two sets of effects. "
           "Race-free counts a model-only program only where `race_check.py` found it clean."]
    if ix["races_missing_for"]:
        out += ["", f"**No race file for {', '.join(ix['races_missing_for'])}: the race-free rows are NOT established "
                "— run race_check.py over those arms first.**"]
    for cls, b in ix["classes"].items():
        out += ["", f"### Class {cls} — {b['benchmarks']} benchmarks", ""]
        for key, label in (("faster_race_free", "race-free FASTER (the pre-registered measure)"), ("faster", "FASTER")):
            d = b[key]
            w = d["wilcoxon"]
            me, mt = d["mean_agent_effect"], d["mean_twin_effect"]
            out.append(f"- {label}: mean effect inside the agent {me:+.2f}, on the twins {mt:+.2f}; larger inside the "
                       f"pipeline on {w['agent_ahead']} benchmarks, on the twins on {w['model_alone_ahead']}, tied on "
                       f"{w['n_pairs'] - w['n_nonzero']}"
                       + (f"; p (two-sided) = {w['p_two_sided']:.3g}, p (larger inside) = {w['p_agent_ahead']:.3g}"
                          if "p_two_sided" in w else f"; {w.get('note', '')}")
                       + (f"; Cliff's δ = {d['cliffs_delta']:+.2f}" if d["cliffs_delta"] is not None else "") + "."
                       if me is not None and mt is not None else f"- {label}: no benchmark has all four arms.")
        per = b["faster_race_free"]["per_benchmark"]
        out += ["", "| benchmark | agent hi | agent lo | twin hi | twin lo | agent effect | twin effect | interaction |",
                "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for bench, v in per.items():
            out.append(f"| `{bench}` | {v['agent_hi']:.2f} | {v['agent_lo']:.2f} | {v['twin_hi']:.2f} | {v['twin_lo']:.2f} | "
                       f"{v['agent_effect']:+.2f} | {v['twin_effect']:+.2f} | {v['interaction']:+.2f} |")
    return "\n".join(out)


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
    ap.add_argument("--three-way", default=None, metavar="AGENT_ARM",
                    help="D35: add DiscoPoP alone · this agent arm · the model alone (--bare) against sequential")
    ap.add_argument("--bare", default="bare_llm", help="the model-alone arm for --three-way")
    ap.add_argument("--races", type=Path, action="append", default=[],
                    help="race_check.py results.jsonl for the model alone's programs (repeatable)")
    ap.add_argument("--interaction", default=None, metavar="AGENT_HI,AGENT_LO,TWIN_HI,TWIN_LO",
                    help="H12 (D38): the factor's effect inside the agent against its effect on the twins, "
                         "e.g. full_b1,no_evidence_b1,twin_full,twin_no_evidence (--races for the twins)")
    ap.add_argument("--suite", default=None,
                    help="only benchmarks of this suite (`tsvc`): the PRIMARY set of D30, computed with the "
                         "same statistics as the registered set, never instead of it")
    a = ap.parse_args()
    trials: List[dict] = []
    for run in a.runs:
        # The working copy of a run if it is here, its tracked archive otherwise.
        import campaign
        root = next((d for d in (HERE.parent / "runs" / run, campaign.find_run(run)) if d and d.exists()), None)
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
    if a.three_way:
        res["three_way"] = three_way(trials, a.three_way, a.bare, load_races(a.races))
        md += "\n" + three_way_markdown(res["three_way"])
    if a.interaction:
        hi_lo = a.interaction.split(",")
        if len(hi_lo) != 4:
            sys.exit("--interaction takes four arms: AGENT_HI,AGENT_LO,TWIN_HI,TWIN_LO")
        res["interaction"] = interaction(trials, hi_lo[0], hi_lo[1], hi_lo[2], hi_lo[3], load_races(a.races))
        md += "\n" + interaction_markdown(res["interaction"])
    print(md)
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "main_comparison_stats.md").write_text(md + "\n")
        (a.out / "main_comparison_stats.json").write_text(json.dumps(res, indent=2, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
