#!/usr/bin/env python3
"""E2-B1 in numbers — the evidence experiment on hidden facts (record §6, 26 and 27 Sep; docs/e2b1/PREPARATION.md).

E2-B1 asks whether DiscoPoP's evidence lets the model find CORRECT parallelism when the fact that
decides it — may the hot loop run in parallel? — is not in the loop's own statements. The
statistics are the ones the author decided on 27 Sep ("The author's decisions on E2-B1's design"),
written before any E2-B1 measurement:

  * **the primary outcome, per trial:** a verified parallel program (correct on the shipped and
    the perturbed input), race-free, whose parallel construct COVERS THE HOT LOOP (decision 3:
    "parallel" alone means any pragma anywhere in the program). Race-free: a program the gate kept
    passed TSan and the schedule matrix already; a model-only arm's (the twins, the model alone)
    only where `race_check.py` found it clean. Coverage is the per-trial field `hot_loop_covered`
    written by a separate mechanical check; a trial without it is "coverage unknown" and is NOT
    counted as a success — the output says so in its headline;
  * **unsafe programs, per trial:** BROKEN, racy, or a program that does not compile. The speed
    check is off in every E2-B1 arm, so "correct but slower" is reported apart and is not unsafe
    (decision 4); a harness edit (SCAFFOLD_MODIFIED) has its own row and is never counted (the
    author, 24 Sep);
  * **the confirmatory tests, direction (a) tier 1 only** (decision 4: named on their own and added
    to the campaign's Holm family), each a Cochran-Mantel-Haenszel test stratified by loop,
    one-sided in the predicted direction, with the Mantel-Haenszel common odds ratio and its
    Robins-Breslow-Greenland 95 % interval:
      (i)   `full_b1_nospeed` vs `no_evidence_b1_nospeed` on the primary outcome (evidence helps);
      (ii)  `twin_full_nospeed` vs `twin_no_evidence_nospeed` on the primary outcome, and the
            INTERACTION — the evidence effect inside the agent against its effect on the matched
            twins (H12's registered one-sided form: larger inside the agent);
      (iii) unsafe programs, `full_b1_nospeed` vs `bare_llm_nospeed` (the agent ships fewer);
    Holm across these four, and where each sits in the campaign's whole family (`--family-size`);
  * **sensitivity:** the same tests stratified by loop × run (the trials of one run share one
    DiscoPoP profile);
  * **descriptive only:** direction (b) (decision 1) and direction (a) tier 2 (reported apart) —
    rates with Wilson 95 % intervals per arm, and the model alone against DiscoPoP alone per loop;
  * **DiscoPoP alone** from a selectable arm (default `discopop_capability`: the three v4 T0.11
    draws), labelled "selected on" and never tested against: a unit is admitted BECAUSE of what
    DiscoPoP alone does on it (class R for (a), class A for (b); ruling 5).

The interaction: statsmodels is not in the harness's venv, so no stratified logistic model; the
fallback the design allows is a Breslow-Day-style homogeneity test, here the z-test of the
difference between the two Mantel-Haenszel log odds ratios (agent, twins) with their
Robins-Breslow-Greenland variances added — the two are independent samples of trials (a
Woolf-type homogeneity test of two pooled estimates; Altman & Bland, BMJ 326:219, 2003).
`--self-test` checks the CMH statistic, the MH odds ratio and its RBG interval on Agresti's
textbook example (An Introduction to Categorical Data Analysis, Wiley 1996, Table 3.3 — Liu 1992's
eight Chinese case-control studies), the exact conditional test against Fisher's, and Holm.

    agent/tools/e2b1_stats.py e2b1_a_1 e2b1_a_2 t0_11_v4_a:discopop_capability ... \\
        --races analysis/e2b1_race_check/twins/results.jsonl --races .../bare/results.jsonl \\
        --model claude-haiku-4-5-20251001 [--out DIR]
    agent/tools/e2b1_stats.py --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import figures  # noqa: E402
from main_comparison_stats import (  # noqa: E402
    RACE_STAGES, _did_not_compile, _model_only, _pct, _run_of, _ships_slowdown, _tampered, _with_verdict,
    load_races, wilson)

POPULATION_FILE = HERE.parent / "config" / "e2b1_population.json"
Z95 = 1.959964

# The registered arms (arms.json, ids E2-B1); each can be renamed on the command line.
ARM_ROLES: List[Tuple[str, str, str]] = [
    ("agent_full", "full_b1_nospeed", "agent, full evidence"),
    ("agent_none", "no_evidence_b1_nospeed", "agent, no evidence"),
    ("twin_full", "twin_full_nospeed", "twin, full evidence"),
    ("twin_none", "twin_no_evidence_nospeed", "twin, no evidence"),
    ("bare", "bare_llm_nospeed", "model alone"),
    ("dp_alone", "discopop_capability", "DiscoPoP alone (selected on)"),
]

# What each trial ends as, in the order the tables show it. Exactly one per trial.
BUCKETS: List[Tuple[str, str]] = [
    ("success", "race-free verified parallel program covering the hot loop (PRIMARY)"),
    ("coverage-unknown", "race-free verified parallel program, coverage not recorded — not a success"),
    ("not-covering", "race-free verified parallel program, the hot loop not covered"),
    ("race-unchecked", "verified parallel program, no race verdict (model-only arm) — not a success"),
    ("race-not-judgeable", "verified parallel program the race check could not judge"),
    ("racy", "racy (TSan or the schedule matrix) — unsafe"),
    ("BROKEN", "BROKEN (wrong output shipped, or a crash at the verification size) — unsafe"),
    ("timed-out-correct", "correct, but a verification run did not finish at one thread count (verified exact at another) — "
                          "correct but slower: reported, not unsafe"),
    ("did-not-compile", "shipped a program that does not compile — unsafe"),
    ("changed-not-parallel", "changed, not parallel"),
    ("no-change", "left unchanged"),
]
UNSAFE = ("racy", "BROKEN", "did-not-compile")
OUT_OF_DENOMINATOR = ("harness-edit", "no-verdict")

# The four named tests of decision 4 (27 Sep). (name, what, arm role X, arm role Y, outcome, predicted)
# `predicted` is the one-sided alternative on the odds ratio of X against Y.
CMH_TESTS: List[Tuple[str, str, str, str, str, str]] = [
    ("E2B1-i", "the evidence effect inside the agent", "agent_full", "agent_none", "success", "greater"),
    ("E2B1-ii-twins", "the evidence effect on the matched twins", "twin_full", "twin_none", "success", "greater"),
    ("E2B1-iii", "unsafe programs: the agent against the model alone", "agent_full", "bare", "unsafe", "less"),
]
INTERACTION = ("E2B1-ii-interaction", "the evidence effect inside the agent against on the twins (H12's form)")
TEST_ORDER = ["E2B1-i", "E2B1-ii-twins", INTERACTION[0], "E2B1-iii"]

# The campaign's family: the 19 hypothesis rows of EXPERIMENT_PLAN.html §2 (H1-H13 with H5b, H5c,
# H5d, H6b, H7b, H10b) plus E2-B1's four named tests (27 Sep decision 4). An upper count — some rows
# are counts, not tests — and a larger family only widens the bound below; the author sets it when
# the family is fixed.
FAMILY_SIZE = 23

Table = Tuple[float, float, float, float]   # a, b, c, d — row 1 = arm X, column 1 = the outcome present


# ---- the statistics, as pure functions ----------------------------------------------------

def _phi(z: float) -> float:
    """Standard normal CDF."""
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def _chi2_1_sf(x: float) -> float:
    """P(chi-square with 1 df > x)."""
    return math.erfc(math.sqrt(max(0.0, x) / 2.0))


def mh_odds_ratio(strata: Sequence[Table], z: float = Z95) -> Dict[str, Any]:
    """The Mantel-Haenszel common odds ratio and its 95 % interval from the Robins-Breslow-Greenland
    variance of its logarithm (Robins, Breslow & Greenland, Biometrics 42:311-323, 1986).

    A stratum with an empty row (one arm has no trial there) or a single outcome contributes 0 to
    both sums, so it needs no special case. When no stratum has a pair against X (S = 0) the
    estimate is infinite, when none has one for X (R = 0) it is 0 — reported, with no interval."""
    R = S = 0.0
    parts: List[Tuple[float, float, float, float]] = []
    for a, b, c, d in strata:
        n = a + b + c + d
        if n <= 0:
            continue
        r, s = a * d / n, b * c / n
        parts.append(((a + d) / n, (b + c) / n, r, s))
        R += r
        S += s
    out: Dict[str, Any] = {"R": R, "S": S, "or": None, "or_infinite": False, "log_or": None,
                           "var_log_or": None, "ci95": None}
    if R == 0 and S == 0:
        out["note"] = "not estimable: no stratum has both outcomes in both arms"
        return out
    if S == 0:
        out.update(or_infinite=True, note="infinite: no stratum holds a pair against the first arm")
        return out
    if R == 0:
        out.update({"or": 0.0, "note": "zero: no stratum holds a pair for the first arm"})
        return out
    var = (sum(p * r for p, _, r, _ in parts) / (2 * R * R)
           + sum(p * s + q * r for p, q, r, s in parts) / (2 * R * S)
           + sum(q * s for _, q, _, s in parts) / (2 * S * S))
    lo = math.log(R / S)
    out.update({"or": R / S, "log_or": lo, "var_log_or": var,
                "ci95": [math.exp(lo - z * math.sqrt(var)), math.exp(lo + z * math.sqrt(var))]})
    return out


def _hypergeometric(n1: int, n2: int, m1: int) -> Tuple[int, List[float]]:
    """The central hypergeometric distribution of a stratum's `a` given its margins: (lowest a, pmf)."""
    lo, hi = max(0, m1 - n2), min(n1, m1)
    total = math.comb(n1 + n2, m1)
    return lo, [math.comb(n1, x) * math.comb(n2, m1 - x) / total for x in range(lo, hi + 1)]


def exact_conditional(strata: Sequence[Table]) -> Dict[str, Any]:
    """The exact conditional test of a common odds ratio of 1: the distribution of sum(a) given every
    stratum's margins is the convolution of the strata's hypergeometric distributions (Birch 1964;
    one stratum = Fisher's exact test). Reported beside the CMH p as a check on the normal
    approximation at E2-B1's small counts (10 trials per arm and loop); it does not enter Holm."""
    base, dist = 0, [1.0]
    for a, b, c, d in strata:
        lo, pmf = _hypergeometric(int(a + b), int(c + d), int(a + c))
        base += lo
        new = [0.0] * (len(dist) + len(pmf) - 1)
        for i, p in enumerate(dist):
            for j, q in enumerate(pmf):
                new[i + j] += p * q
        dist = new
    s = int(sum(t[0] for t in strata)) - base
    p_obs = dist[s]
    return {"p_greater": min(1.0, sum(dist[s:])), "p_less": min(1.0, sum(dist[:s + 1])),
            "p_two_sided": min(1.0, sum(p for p in dist if p <= p_obs * (1 + 1e-7)))}


def cmh(strata: Sequence[Table], alternative: str = "greater", continuity: bool = True) -> Dict[str, Any]:
    """The Cochran-Mantel-Haenszel test of a common odds ratio of 1 across 2x2 strata.

    `alternative` is the predicted direction of X against Y: "greater" (odds ratio > 1) or "less".
    `continuity`: subtract 1/2 from the deviation of sum(a) from its expectation, against the
    alternative (Mantel & Haenszel, JNCI 22:719-748, 1959, as published; the conservative form at
    small counts). Both the corrected and the uncorrected values are always returned.

    A stratum of fewer than two trials, or with one arm absent, or with one outcome only has no
    variance and adds nothing; `informative_strata` counts the rest. No informative stratum, no test.
    The Mantel-Fleiss criterion (Am J Epidemiol 112:129-134, 1980: min distance of the expected
    sum from its bounds >= 5) says whether the normal approximation is adequate; the exact
    conditional p is beside it either way."""
    if alternative not in ("greater", "less"):
        raise ValueError(f"alternative must be 'greater' or 'less', not {alternative!r}")
    delta = var = expected = lower = upper = 0.0
    informative = 0
    for a, b, c, d in strata:
        n1, n2, m1, m2 = a + b, c + d, a + c, b + d
        n = n1 + n2
        if n < 2:
            continue
        e = n1 * m1 / n
        v = n1 * n2 * m1 * m2 / (n * n * (n - 1))
        delta += a - e
        expected += e
        var += v
        lower += max(0.0, n1 - m2)
        upper += min(n1, m1)
        informative += v > 0
    out: Dict[str, Any] = {"strata": len(strata), "informative_strata": informative, "alternative": alternative,
                           "continuity": continuity, "sum_a": sum(t[0] for t in strata), "expected": expected,
                           "delta": delta, "variance": var}
    if var <= 0:
        out["note"] = "no informative stratum: no test"
        return out
    cc = 0.5
    sign = 1.0 if alternative == "greater" else -1.0

    def one_sided(corr: float) -> Tuple[float, float]:
        zz = (delta - sign * corr) / math.sqrt(var)
        return zz, (1 - _phi(zz)) if alternative == "greater" else _phi(zz)

    z_u, p_u = one_sided(0.0)
    z_c, p_c = one_sided(cc)
    chi2_u = delta * delta / var
    chi2_c = max(0.0, abs(delta) - cc) ** 2 / var
    mf = min(expected - lower, upper - expected)
    out.update({
        "chi2": chi2_u, "chi2_cc": chi2_c,
        "z_uncorrected": z_u, "p_one_sided_uncorrected": p_u, "z_corrected": z_c, "p_one_sided_corrected": p_c,
        "p_two_sided_uncorrected": _chi2_1_sf(chi2_u), "p_two_sided_corrected": _chi2_1_sf(chi2_c),
        "z": z_c if continuity else z_u, "p_one_sided": p_c if continuity else p_u,
        "p_two_sided": _chi2_1_sf(chi2_c if continuity else chi2_u),
        "mantel_fleiss": {"value": mf, "met": mf >= 5},
    })
    if all(float(x).is_integer() for t in strata for x in t):
        ex = exact_conditional(strata)
        out["exact"] = {"p_one_sided": ex["p_greater"] if alternative == "greater" else ex["p_less"],
                        "p_two_sided": ex["p_two_sided"]}
    return out


def _estimable(r: Dict[str, Any]) -> bool:
    return r.get("log_or") is not None and (r.get("var_log_or") or 0) > 0


def _haldane(t: Table) -> Table:
    """1/2 added to every cell of a stratum where both arms have trials — never where one arm has
    none, which would invent a comparison."""
    a, b, c, d = t
    if a + b > 0 and c + d > 0:
        return (a + 0.5, b + 0.5, c + 0.5, d + 0.5)
    return t


def or_difference(first: Sequence[Table], second: Sequence[Table], alternative: str = "greater",
                  z: float = Z95) -> Dict[str, Any]:
    """Is the common odds ratio of the first set of strata larger (or smaller) than the second's?
    z = (ln OR_MH,1 - ln OR_MH,2) / sqrt(Var_RBG,1 + Var_RBG,2): the two sets are independent samples
    of trials, so the variances add (Altman & Bland, BMJ 326:219, 2003); for two estimates it is the
    Woolf-type chi-square of homogeneity. Pre-specified rule for zero cells: when either log odds
    ratio is infinite or has no variance, 1/2 is added to every cell of every stratum of BOTH sets
    (`corrected`, flagged; the uncorrected estimates are kept beside)."""
    r1, r2 = mh_odds_ratio(first, z), mh_odds_ratio(second, z)
    out: Dict[str, Any] = {"alternative": alternative, "corrected": False,
                           "uncorrected": {"first": r1, "second": r2}}
    # A set without one stratum holding both arms and both outcomes says nothing about its effect;
    # the ½ rule would turn that silence into an odds ratio of 1 — so no test, not a test of nothing.
    empty = [n for n, s in (("first", first), ("second", second))
             if not any(a + b > 0 and c + d > 0 and a + c > 0 and b + d > 0 for a, b, c, d in s)]
    if empty:
        out["note"] = f"no informative stratum in the {' and the '.join(empty)} set: no test"
        return out
    if not (_estimable(r1) and _estimable(r2)):
        r1 = mh_odds_ratio([_haldane(t) for t in first], z)
        r2 = mh_odds_ratio([_haldane(t) for t in second], z)
        out["corrected"] = True
        if not (_estimable(r1) and _estimable(r2)):
            out["note"] = "not estimable even with 1/2 added to every cell: no test"
            return out
    d = float(r1["log_or"]) - float(r2["log_or"])
    se = math.sqrt(float(r1["var_log_or"]) + float(r2["var_log_or"]))
    zz = d / se
    out.update({"first": r1, "second": r2, "log_ratio": d, "se": se, "z": zz,
                "ratio_of_odds_ratios": math.exp(d), "ci95": [math.exp(d - z * se), math.exp(d + z * se)],
                "p_one_sided": (1 - _phi(zz)) if alternative == "greater" else _phi(zz),
                "p_two_sided": _chi2_1_sf(zz * zz)})
    return out


def holm(pvalues: Dict[str, Optional[float]]) -> Dict[str, float]:
    """Holm's step-down adjusted p-values (Holm, Scand J Statist 6:65-70, 1979). The family is the
    tests NAMED, fixed in advance: a test that could not be run enters with p = 1, so a missing test
    never relaxes the correction of the others."""
    m = len(pvalues)
    ps = {k: (1.0 if v is None else float(v)) for k, v in pvalues.items()}
    adjusted: Dict[str, float] = {}
    running = 0.0
    for i, name in enumerate(sorted(ps, key=lambda k: ps[k])):
        running = max(running, min(1.0, (m - i) * ps[name]))
        adjusted[name] = running
    return adjusted


def family_bounds(p: Optional[float], holm_within: float, family_size: int, alpha: float) -> Dict[str, Any]:
    """Where a test sits in the campaign's Holm family of `family_size` hypotheses when the other
    hypotheses' p-values are not in hand: its adjusted p is at least its Holm p within E2-B1's own
    tests (reached when every other hypothesis has a smaller p) and at most min(1, M·p) (reached
    when it has the smallest p of the family). So it is rejected at `alpha` whatever the others if
    M·p <= alpha, never if the within-E2-B1 Holm p > alpha, and otherwise the others decide."""
    if p is None:
        return {"lower": 1.0, "upper": 1.0, "verdict": "no test"}
    upper = min(1.0, family_size * p)
    verdict = ("rejected whatever the other tests" if upper <= alpha
               else "not rejected whatever the other tests" if holm_within > alpha
               else "depends on the other tests' p-values")
    return {"lower": holm_within, "upper": upper, "verdict": verdict}


# ---- trials ---------------------------------------------------------------------------------

def _covered(t: dict) -> Optional[bool]:
    """Does the program's parallel construct cover the hot loop? Written per trial by the coverage
    check (decision 3, 27 Sep) as `hot_loop_covered`; None when the trial has not been checked."""
    v = t.get("hot_loop_covered")
    return v if isinstance(v, bool) else None


def _timed_out_correct(t: dict) -> bool:
    """The author's ruling of 28 Sep (record §6, taken after the data, applying the pre-registered "correct but
    slower is reported, not unsafe"): the harness calls a program BROKEN when any verification run fails, and a run
    that exceeds its 30-minute limit fails like a crash. A program whose sequential dump is exact and which finished
    exact at some thread count before a run at another failed is correct and too slow — not unsafe. A program that
    failed at the first thread count it ran (a stack array sized by the problem: a crash at the verification size)
    stays BROKEN."""
    v = t.get("verify") or {}
    if t.get("outcome") != "BROKEN" or not str(v.get("status", "")).startswith("final_run_failed_T"):
        return False
    if v.get("dump_exact") is not True:
        return False
    par = v.get("par") or {}
    return any(isinstance(r, dict) and r.get("max_rel_err") == 0.0 for r in par.values())


def judge(t: dict, races: Dict[Tuple[str, str, str, int], str]) -> Dict[str, Any]:
    """One trial, as E2-B1 counts it: exactly one bucket, and whether it is a success (the primary
    outcome), unsafe, correct but slower, FASTER."""
    arm = str(t.get("arm"))
    outcome = t.get("outcome")
    race = "clean"                            # kept by the gate: TSan and the schedule matrix passed
    if _model_only(arm):
        race = races.get((_run_of(t), str(t.get("benchmark")), arm, int(t.get("repeat") or 0)), "unchecked")
    cov = _covered(t)
    if _tampered(t):
        bucket = "harness-edit"
    elif not _with_verdict(t):
        bucket = "no-verdict"
    elif _timed_out_correct(t):
        bucket = "timed-out-correct"
    elif outcome == "BROKEN":
        bucket = "BROKEN"
    elif _did_not_compile(t):
        bucket = "did-not-compile"
    elif outcome in figures.PARALLEL_OK:
        bucket = ("racy" if race in RACE_STAGES else "race-unchecked" if race == "unchecked"
                  else "race-not-judgeable" if race != "clean"
                  else "success" if cov is True else "not-covering" if cov is False else "coverage-unknown")
    else:
        bucket = str(outcome)                  # no-change, changed-not-parallel
    counted = bucket not in OUT_OF_DENOMINATOR
    return {"benchmark": str(t.get("benchmark")), "arm": arm, "run": _run_of(t), "repeat": int(t.get("repeat") or 0),
            "model": t.get("model"), "outcome": outcome, "bucket": bucket, "race": race, "covered": cov,
            "with_verdict": counted, "success": bucket == "success", "unsafe": bucket in UNSAFE,
            # speed off in every arm: a correct program slower than the original is reported, not unsafe
            "slower": counted and bucket not in UNSAFE and (_ships_slowdown(t) or bucket == "timed-out-correct"),
            "faster": counted and outcome == "FASTER" and bucket not in UNSAFE}


def load_population(path: Path) -> Tuple[Dict[str, Dict[str, Any]], int]:
    """(benchmark -> its direction, tier and planned N per cell; DiscoPoP alone's planned draws)."""
    spec = json.loads(path.read_text())
    units: Dict[str, Dict[str, Any]] = {}
    for direction, block in spec["directions"].items():
        for u in block["units"]:
            units[u["benchmark"]] = {"direction": direction, "tier": int(u.get("tier", 1)),
                                     "n_per_cell": int(block["n_per_cell"])}
    return units, int(spec.get("dp_alone_draws", 3))


def group_of(unit: Dict[str, Any]) -> str:
    return f"{unit['direction']}{unit['tier']}"


GROUP_NAMES = {"a1": "direction (a), tier 1 — CONFIRMATORY", "a2": "direction (a), tier 2 — descriptive (reported apart)",
               "b1": "direction (b) — descriptive"}


def load_trials(specs: Sequence[str]) -> List[dict]:
    """RUN or RUN:ARM+ARM (only those arms of that run) — the working copy of a run under runs/ if it
    is here, its tracked archive otherwise; as main_comparison_stats.py loads them."""
    import campaign
    trials: List[dict] = []
    for spec in specs:
        run, _, arms = spec.partition(":")
        keep = set(arms.split("+")) if arms else None
        root = next((d for d in (HERE.parent / "runs" / run, campaign.find_run(run)) if d and d.exists()), None)
        if root is None:
            sys.exit(f"run {run} not found under runs/ or results/")
        for p in sorted(root.glob("benchmarks/**/trial.json")):
            t = json.loads(p.read_text())
            t.setdefault("run_id", run)             # a raw trial record does not name its run
            if keep is None or t.get("arm") in keep:
                trials.append(t)
    return trials


# ---- the analysis ---------------------------------------------------------------------------

def summarise(js: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Rates over the trials with a verdict (a harness edit and a trial that ended before any
    program was judged are out of every denominator, each listed)."""
    valid = [j for j in js if j["with_verdict"]]
    n = len(valid)

    def rate(key: str) -> Dict[str, Any]:
        k = sum(1 for j in valid if j[key])
        return {"k": k, "n": n, "wilson95": wilson(k, n)}

    verified = sum(1 for j in valid if j["bucket"] in ("success", "coverage-unknown", "not-covering"))
    case = lambda j: f"{j['benchmark']} {j['run']} rep{j['repeat']}"  # noqa: E731
    return {
        "trials": len(js), "with_verdict": n,
        "buckets": {b: sum(1 for j in valid if j["bucket"] == b) for b, _ in BUCKETS},
        "success": rate("success"), "unsafe": rate("unsafe"), "faster": rate("faster"),
        "verified_parallel_race_free": {"k": verified, "n": n, "wilson95": wilson(verified, n)},
        "correct_but_slower": sum(1 for j in valid if j["slower"]),
        "coverage_unknown": sum(1 for j in valid if j["bucket"] == "coverage-unknown"),
        "race_unchecked": sum(1 for j in valid if j["bucket"] == "race-unchecked"),
        "unsafe_cases": [f"{case(j)}: {j['bucket']}" for j in valid if j["unsafe"]],
        "harness_edits": [case(j) for j in js if j["bucket"] == "harness-edit"],
        "no_verdict": [f"{case(j)}: {j['outcome']}" for j in js if j["bucket"] == "no-verdict"],
    }


def strata_for(js: List[Dict[str, Any]], arm_x: str, arm_y: str, outcome: str,
               key: Callable[[Dict[str, Any]], str]) -> List[Tuple[str, Table]]:
    """One 2x2 table per stratum: (X with the outcome, X without, Y with, Y without), over trials
    with a verdict."""
    cells: Dict[str, List[float]] = {}
    for j in js:
        if not j["with_verdict"] or j["arm"] not in (arm_x, arm_y):
            continue
        c = cells.setdefault(key(j), [0.0, 0.0, 0.0, 0.0])
        c[(0 if j["arm"] == arm_x else 2) + (0 if j[outcome] else 1)] += 1
    return [(k, (v[0], v[1], v[2], v[3])) for k, v in sorted(cells.items())]


def _gaps(js: List[Dict[str, Any]], arms: Sequence[str], outcome: str) -> List[str]:
    """What keeps a test from being established: a race-free parallel program without its coverage
    verdict (the primary outcome), a model-only program without its race verdict (both outcomes)."""
    out = []
    for arm in arms:
        aj = [j for j in js if j["arm"] == arm and j["with_verdict"]]
        if not aj:
            out.append(f"`{arm}`: no trial with a verdict")
            continue
        unk = sum(1 for j in aj if j["bucket"] == "coverage-unknown")
        unr = sum(1 for j in aj if j["bucket"] == "race-unchecked")
        if outcome == "success" and unk:
            out.append(f"`{arm}`: {unk} race-free parallel program(s) without `hot_loop_covered`")
        if unr:
            out.append(f"`{arm}`: {unr} parallel program(s) without a race verdict — run race_check.py")
    return out


def run_tests(js: List[Dict[str, Any]], arms: Dict[str, str], key: Callable[[Dict[str, Any]], str],
              continuity: bool) -> Dict[str, Dict[str, Any]]:
    tests: Dict[str, Dict[str, Any]] = {}
    strata_of: Dict[str, List[Tuple[str, Table]]] = {}
    for name, what, rx, ry, outcome, alt in CMH_TESTS:
        st = strata_for(js, arms[rx], arms[ry], outcome, key)
        strata_of[name] = st
        tables = [t for _, t in st]
        c = cmh(tables, alt, continuity)
        tests[name] = {"what": what, "x": arms[rx], "y": arms[ry], "outcome": outcome, "predicted": alt,
                       "strata": {k: list(t) for k, t in st}, "cmh": c, "mh_or": mh_odds_ratio(tables),
                       "p": c.get("p_one_sided"), "gaps": _gaps(js, (arms[rx], arms[ry]), outcome)}
        tests[name]["established"] = not tests[name]["gaps"] and c.get("p_one_sided") is not None
    ix = or_difference([t for _, t in strata_of["E2B1-i"]], [t for _, t in strata_of["E2B1-ii-twins"]], "greater")
    gaps = tests["E2B1-i"]["gaps"] + tests["E2B1-ii-twins"]["gaps"]
    tests[INTERACTION[0]] = {"what": INTERACTION[1], "x": f"{arms['agent_full']} vs {arms['agent_none']}",
                             "y": f"{arms['twin_full']} vs {arms['twin_none']}", "outcome": "success",
                             "predicted": "greater", "test": ix, "p": ix.get("p_one_sided"), "gaps": gaps,
                             "established": not gaps and ix.get("p_one_sided") is not None}
    return {k: tests[k] for k in TEST_ORDER}


def analyse(trials: List[dict], units: Dict[str, Dict[str, Any]], arms: Dict[str, str],
            races: Dict[Tuple[str, str, str, int], str], continuity: bool = True, alpha: float = 0.05,
            family_size: int = FAMILY_SIZE, dp_draws: int = 3) -> Dict[str, Any]:
    if family_size < len(TEST_ORDER):
        raise ValueError(f"the campaign family cannot be smaller than E2-B1's own {len(TEST_ORDER)} tests")
    known_arms = set(arms.values())
    outside: Dict[str, int] = {}
    js: List[Dict[str, Any]] = []
    for t in sorted(trials, key=lambda t: (str(t.get("benchmark")), str(t.get("arm")), _run_of(t),
                                           int(t.get("repeat") or 0))):
        b = str(t.get("benchmark"))
        if b not in units or t.get("arm") not in known_arms:
            outside[f"{b} · {t.get('arm')}"] = outside.get(f"{b} · {t.get('arm')}", 0) + 1
            continue
        j = judge(t, races)
        j["group"] = group_of(units[b])
        js.append(j)
    res: Dict[str, Any] = {
        "arms": arms, "runs": sorted({j["run"] for j in js}),
        "models": sorted({str(j["model"]) for j in js if j["arm"] != arms["dp_alone"]}),
        "settings": {"continuity": continuity, "alpha": alpha, "family_size": family_size},
        "races_given_for": sorted({k[2] for k in races}), "outside_population": dict(sorted(outside.items())),
        "groups": {}, "completeness": {}, "trials": js,
    }
    by_unit_arm: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for j in js:
        by_unit_arm.setdefault((j["benchmark"], j["arm"]), []).append(j)
    for g in sorted({group_of(u) for u in units.values()}):
        loops = sorted(b for b, u in units.items() if group_of(u) == g)
        gj = [j for j in js if j["group"] == g]
        res["groups"][g] = {
            "loops": loops,
            "per_arm": {role: summarise([j for j in gj if j["arm"] == arm]) for role, arm in arms.items()},
            "per_loop": {b: {role: summarise(by_unit_arm.get((b, arm), [])) for role, arm in arms.items()}
                         for b in loops},
        }
    for b, u in sorted(units.items()):
        res["completeness"][b] = {
            role: {"found": len(by_unit_arm.get((b, arm), [])),
                   "with_verdict": sum(1 for j in by_unit_arm.get((b, arm), []) if j["with_verdict"]),
                   "planned": dp_draws if role == "dp_alone" else u["n_per_cell"]}
            for role, arm in arms.items()}
    # the confirmatory tests: direction (a) tier 1 only
    conf = [j for j in js if j["group"] == "a1"]
    tests = run_tests(conf, arms, lambda j: j["benchmark"], continuity)
    adj = holm({k: v["p"] for k, v in tests.items()})
    for k, v in tests.items():
        v["holm_e2b1"] = adj[k]
        v["campaign_family"] = family_bounds(v["p"], adj[k], family_size, alpha)
    res["tests"] = tests
    res["sensitivity_loop_x_run"] = run_tests(conf, arms, lambda j: f"{j['benchmark']} · {j['run']}", continuity)
    # A test is established when its inputs are complete (no gaps) AND it could be run; the headline
    # and the table's last column must agree.
    missing = [f"{k}: " + ("; ".join(v["gaps"]) if v["gaps"]
                           else (v.get("cmh") or v.get("test") or {}).get("note", "no test"))
               for k, v in tests.items() if not v["established"]]
    res["established"] = not missing
    res["not_established"] = missing
    res["coverage_unknown_total"] = sum(1 for j in js if j["bucket"] == "coverage-unknown")
    res["race_unchecked_total"] = sum(1 for j in js if j["bucket"] == "race-unchecked")
    return res


# ---- the report -----------------------------------------------------------------------------

def _f(x: Optional[float], nd: int = 3) -> str:
    return "—" if x is None else f"{x:.{nd}g}"


def _or_text(r: Dict[str, Any]) -> str:
    if r.get("or_infinite"):
        return "∞ (no interval)"
    if r.get("or") is None:
        return "not estimable"
    if r["or"] == 0:
        return "0 (no interval)"
    ci = r.get("ci95")
    return f"{r['or']:.2f}" + (f" ({ci[0]:.2f}–{ci[1]:.2f})" if ci else " (no interval)")


def _test_rows(tests: Dict[str, Dict[str, Any]], with_holm: bool, family_size: int) -> List[str]:
    head = ("| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | "
            "p one-sided | exact p | " + ("Holm (E2-B1) | campaign family, M = " + str(family_size) + " | " if with_holm else "")
            + "established |")
    out = [head, "|---|---|---|---:|---:|---:|---:|---:|" + ("---:|---|" if with_holm else "") + "---|"]
    for name, v in tests.items():
        hol = (f" {v['holm_e2b1']:.3g} | {v['campaign_family']['lower']:.3g}–{v['campaign_family']['upper']:.3g}: "
               f"{v['campaign_family']['verdict']} |") if with_holm else ""
        est = "yes" if v["established"] else "**NO**"
        pred = f"{v['outcome']}, OR {'>' if v['predicted'] == 'greater' else '<'} 1"
        if "cmh" in v:
            c = v["cmh"]
            chi = c.get("chi2_cc" if c["continuity"] else "chi2")
            ex = (c.get("exact") or {}).get("p_one_sided")
            out.append(f"| {name}: {v['what']} | `{v['x']}` vs `{v['y']}` | {pred} | {c['strata']} ({c['informative_strata']}) | "
                       f"{_or_text(v['mh_or'])} | {_f(chi)} | **{_f(v['p'])}** | {_f(ex)} |{hol} {est} |")
        else:
            t = v["test"]
            ratio = (f"ratio {t['ratio_of_odds_ratios']:.2f} ({t['ci95'][0]:.2f}–{t['ci95'][1]:.2f})"
                     + (", ½ added" if t["corrected"] else "")) if "z" in t else t.get("note", "—")
            out.append(f"| {name}: {v['what']} | agent vs twins | success, agent's OR > twins' | — | {ratio} | "
                       f"z = {_f(t.get('z'))} | **{_f(v['p'])}** | — |{hol} {est} |")
    return out


def _cell(s: Dict[str, Any]) -> str:
    return f"{s['success']['k']} / {s['unsafe']['k']} / {s['with_verdict']}" if s["trials"] else "—"


def to_markdown(res: Dict[str, Any]) -> str:
    arms, st = res["arms"], res["settings"]
    labels = {r: lab for r, _, lab in ARM_ROLES}
    out = ["# E2-B1 in numbers — the evidence experiment on hidden facts", "",
           f"Runs: {', '.join(res['runs']) or '—'}. Model: {', '.join(res['models']) or '—'}. "
           f"Race files for: {', '.join(res['races_given_for']) or 'none'}. Continuity correction "
           f"{'on' if st['continuity'] else 'off'}; α = {st['alpha']}; the campaign's family M = {st['family_size']}.", ""]
    # Anything that keeps a number from meaning what it says goes here, above every table.
    if not res["established"]:
        out += ["> **The confirmatory tests are NOT ESTABLISHED.** " + " ".join(f"{m}." for m in res["not_established"]), ""]
    if res["coverage_unknown_total"]:
        out += [f"> **{res['coverage_unknown_total']} race-free parallel program(s) carry no `hot_loop_covered` verdict** "
                "(all groups): each is counted as NOT reaching the primary outcome until the coverage check has run "
                "over it.", ""]
    if res["race_unchecked_total"]:
        out += [f"> **{res['race_unchecked_total']} parallel program(s) of a model-only arm have no race verdict** "
                "(all groups): none counts as a success, none as unsafe — run race_check.py over them.", ""]
    out += ["**The primary outcome** is a race-free verified parallel program whose parallel construct covers the hot "
            "loop. A program kept by the gate passed TSan and the schedule matrix; a model-only arm's is race-free only "
            "where `race_check.py` found it clean. **Unsafe** = BROKEN, racy or not compiling; with the speed check off "
            "in every arm, a correct program slower than the original is reported, not unsafe. A harness edit has its own "
            "row and is out of every denominator.", "",
            "## Confirmatory tests — direction (a), tier 1", "",
            "Cochran-Mantel-Haenszel, stratified by loop, one-sided in the predicted direction; Mantel-Haenszel common odds "
            "ratio with the Robins-Breslow-Greenland 95 % interval; the exact conditional p beside it (not in Holm). The "
            "interaction: the difference of the two MH log odds ratios, z-test with the RBG variances added. Holm across "
            "the four tests; the campaign family's adjusted p lies between the E2-B1 Holm p (every other hypothesis "
            "smaller) and M·p (this one smallest).", ""]
    out += _test_rows(res["tests"], True, st["family_size"])
    out.append("")
    for name, v in res["tests"].items():
        if "cmh" in v:
            c = v["cmh"]
            if c.get("note"):
                out.append(f"- {name}: {c['note']} (strata: " + ("; ".join(
                    f"`{k}` {'/'.join(str(int(x)) for x in t)}" for k, t in v["strata"].items()) or "none") + ").")
            if c.get("mantel_fleiss") and not c["mantel_fleiss"]["met"]:
                out.append(f"- {name}: the Mantel-Fleiss criterion is not met ({c['mantel_fleiss']['value']:.2f} < 5) — "
                           "the normal approximation is rough here; the exact conditional p stands beside it.")
            if c.get("p_one_sided_uncorrected") is not None:
                out.append(f"- {name}: p one-sided without / with the continuity correction "
                           f"{c['p_one_sided_uncorrected']:.3g} / {c['p_one_sided_corrected']:.3g}; two-sided "
                           f"{c['p_two_sided']:.3g}. Per loop (X with / X without / Y with / Y without): "
                           + "; ".join(f"`{k}` {'/'.join(str(int(x)) for x in t)}" for k, t in v["strata"].items()) + ".")
        else:
            t = v["test"]
            if "z" in t:
                out.append(f"- {name}: agent OR {_or_text(t['first'])}, twins OR {_or_text(t['second'])}"
                           + (" (½ added to every cell: an odds ratio was 0 or infinite)" if t["corrected"] else "")
                           + f"; p two-sided {t['p_two_sided']:.3g}. The one-sided direction is H12's registered form.")
    out.append("- (iii) counts a model-only program without a race verdict as not unsafe: conservative for the "
               "prediction that the agent ships fewer.")
    out += ["", "## Sensitivity — strata = loop × run (the trials of one run share one profile)", ""]
    out += _test_rows(res["sensitivity_loop_x_run"], False, st["family_size"])
    for g, block in res["groups"].items():
        out += ["", f"## {GROUP_NAMES.get(g, g)} — {len(block['loops'])} loops: "
                + ", ".join(f"`{b}`" for b in block["loops"]), "",
                "| per arm | " + " | ".join(f"{labels[r]} `{arms[r]}`" for r in arms) + " |",
                "|---|" + "---:|" * len(arms)]
        pa = block["per_arm"]
        rows: List[Tuple[str, Callable[[Dict[str, Any]], str]]] = [
            ("**primary outcome** (covers the hot loop)", lambda s: _pct(s["success"])),
            ("race-free verified parallel program, any coverage", lambda s: _pct(s["verified_parallel_race_free"])),
            ("FASTER (≥ 1.1×, reported beside)", lambda s: _pct(s["faster"])),
            ("**unsafe** (BROKEN, racy, not compiling)", lambda s: _pct(s["unsafe"])),
        ]
        rows += [(lab, (lambda key: lambda s: str(s["buckets"][key]))(b)) for b, lab in BUCKETS]
        rows += [("correct but slower (< 0.91×; not unsafe)", lambda s: str(s["correct_but_slower"])),
                 ("touched the harness — own row, no valid measurement", lambda s: str(len(s["harness_edits"]))),
                 ("no verdict", lambda s: str(len(s["no_verdict"])))]
        for name, fn in rows:
            out.append(f"| {name} | " + " | ".join(fn(pa[r]) if pa[r]["trials"] else "—" for r in arms) + " |")
        out += ["", "| loop: success / unsafe / with a verdict | " + " | ".join(labels[r] for r in arms) + " |",
                "|---|" + "---:|" * len(arms)]
        for b, per in block["per_loop"].items():
            out.append(f"| `{b}` | " + " | ".join(_cell(per[r]) for r in arms) + " |")
        out += ["", f"The model alone (`{arms['bare']}`) against DiscoPoP alone (`{arms['dp_alone']}`, **selected on** — "
                "the unit was admitted because of what DiscoPoP alone does on it; no test):", "",
                "| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | "
                "wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established "
                "(coverage or race unknown) |", "|---|---:|---:|---:|---:|---:|"]
        for b, per in block["per_loop"].items():
            d, m = per["dp_alone"], per["bare"]
            mb = m["buckets"]
            out.append(f"| `{b}` | " + (f"{d['success']['k']} / {d['verified_parallel_race_free']['k']} / {d['with_verdict']}"
                                         if d["trials"] else "—") + " | "
                       + (f"{m['success']['k']} of {m['with_verdict']} | {m['unsafe']['k']} | "
                          f"{mb['no-change'] + mb['changed-not-parallel'] + mb['not-covering']} | "
                          f"{mb['coverage-unknown'] + mb['race-unchecked'] + mb['race-not-judgeable']}"
                          if m["trials"] else "— | — | — | —") + " |")
        cases = [(labels[r], pa[r]) for r in arms]
        for lab, s in cases:
            if s["unsafe_cases"]:
                out.append(f"- Unsafe programs, {lab}: " + "; ".join(s["unsafe_cases"]) + ".")
            if s["harness_edits"]:
                out.append(f"- Harness edits, {lab} (not counted): " + "; ".join(s["harness_edits"]) + ".")
            if s["no_verdict"]:
                out.append(f"- No verdict, {lab}: " + "; ".join(s["no_verdict"]) + ".")
    short = [(b, r, c) for b, per in res["completeness"].items() for r, c in per.items() if c["with_verdict"] < c["planned"]]
    out += ["", "## Completeness — trials with a verdict against the plan (a silently missing trial biases what is left)", ""]
    out += ([f"- `{b}` · `{arms[r]}`: {c['with_verdict']} of {c['planned']} planned ({c['found']} found)" for b, r, c in short]
            or ["- Every cell holds its planned trials."])
    if res["outside_population"]:
        out += ["", "Trials outside the population or the named arms (not analysed): "
                + ", ".join(f"{k} ×{n}" for k, n in res["outside_population"].items()) + "."]
    return "\n".join(out) + "\n"


# ---- self-test --------------------------------------------------------------------------------

def self_test() -> int:
    fails = 0

    def expect(label: str, cond: bool, detail: str = "") -> None:
        nonlocal fails
        fails += not cond
        print(f"  [{'pass' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail and not cond else ''}")

    # 1. Agresti, An Introduction to Categorical Data Analysis (Wiley 1996), Table 3.3 p. 60: smoking
    #    and lung cancer in eight Chinese cities (Liu, Int J Epidemiol 21:197-201, 1992); rows smoker /
    #    non-smoker, columns case / control. Reference values: SAS PROC FREQ on the book's data (UCLA
    #    OARC's textbook examples for Agresti 1996, ch. 3, pp. 62-63): CMH 280.1375 (uncorrected), MH
    #    odds ratio 2.1745, 95 % limits 1.9840-2.3832 (SAS's MH limits use the RBG variance); the same
    #    three numbers in statsmodels' StratifiedTable documentation (280.138; 2.174, 1.984-2.383).
    china: List[Table] = [(126, 100, 35, 61), (908, 688, 497, 807), (913, 747, 336, 598), (235, 172, 58, 121),
                          (402, 308, 121, 215), (182, 156, 72, 98), (60, 99, 11, 43), (104, 89, 21, 36)]
    print("1. Agresti (1996) Table 3.3 — CMH, MH odds ratio, RBG interval")
    c = cmh(china, "greater", continuity=False)
    r = mh_odds_ratio(china)
    expect("CMH statistic 280.1375", abs(c["chi2"] - 280.1375) < 5e-4, f"{c['chi2']}")
    expect("MH odds ratio 2.1745", abs(r["or"] - 2.1745) < 5e-5, f"{r['or']}")
    expect("RBG 95 % interval 1.9840-2.3832", abs(r["ci95"][0] - 1.9840) < 5e-5 and abs(r["ci95"][1] - 2.3832) < 5e-5,
           f"{r['ci95']}")
    # by hand from the same sums: sum(a) = 2930, sum E = 2645.07..., the corrected chi2 is (|delta| - 1/2)^2 / V
    expect("continuity correction = (|Σa − ΣE| − ½)² / V",
           abs(c["chi2_cc"] - (abs(c["delta"]) - 0.5) ** 2 / c["variance"]) < 1e-9 and c["chi2_cc"] < c["chi2"])
    expect("one-sided p against the prediction is ~1", cmh(china, "less")["p_one_sided"] > 0.999)
    expect("Mantel-Fleiss criterion met on 8419 subjects", c["mantel_fleiss"]["met"])

    # 2. Agresti (1996) Table 3.2 pp. 58-59: two clinics, each odds ratio exactly 1, the pooled table's 2 —
    #    stratification must remove the association entirely (Simpson's paradox).
    print("2. Agresti (1996) Table 3.2 — conditional independence")
    clinic: List[Table] = [(18, 12, 12, 8), (2, 8, 8, 32)]
    c2, r2 = cmh(clinic, "greater", continuity=False), mh_odds_ratio(clinic)
    expect("MH odds ratio exactly 1", abs(r2["or"] - 1.0) < 1e-12, f"{r2['or']}")
    expect("CMH statistic 0, one-sided p 0.5", abs(c2["chi2"]) < 1e-12 and abs(c2["p_one_sided"] - 0.5) < 1e-12)
    expect("the collapsed table's odds ratio is 2", abs(mh_odds_ratio([(20, 20, 20, 40)])["or"] - 2.0) < 1e-12)

    # 3. Strata with zero margins add nothing and break nothing.
    print("3. zero margins")
    padded = china + [(0, 0, 3, 2), (5, 0, 5, 0), (1, 0, 0, 0), (0, 0, 0, 0)]
    cp, rp = cmh(padded, "greater", continuity=False), mh_odds_ratio(padded)
    expect("an empty arm, one outcome, one trial, no trial: CMH unchanged", abs(cp["chi2"] - c["chi2"]) < 1e-9
           and cp["informative_strata"] == 8, f"{cp['chi2']} {cp['informative_strata']}")
    expect("MH odds ratio and interval unchanged", abs(rp["or"] - r["or"]) < 1e-12 and abs(rp["ci95"][0] - r["ci95"][0]) < 1e-12)
    expect("no informative stratum: no test", "p_one_sided" not in cmh([(3, 0, 4, 0), (0, 0, 2, 3)]))
    inf = mh_odds_ratio([(3, 0, 0, 3), (2, 0, 1, 1)])
    expect("no pair against X: odds ratio infinite, no interval", inf["or_infinite"] and inf["ci95"] is None)
    expect("no pair for X: odds ratio 0, no interval", mh_odds_ratio([(0, 3, 3, 0)])["or"] == 0.0)

    # 4. The exact conditional test. One stratum (3,0 | 0,3): P(a >= 3) = C(3,3)C(3,0)/C(6,3) = 1/20 by hand.
    print("4. exact conditional test")
    expect("one stratum by hand: 1/20", abs(exact_conditional([(3, 0, 0, 3)])["p_greater"] - 0.05) < 1e-12)
    two = [(4, 1, 2, 3), (3, 2, 1, 4)]
    brute = 0.0
    lo1, pm1 = _hypergeometric(5, 5, 6)
    lo2, pm2 = _hypergeometric(5, 5, 4)
    for i, p in enumerate(pm1):
        for k, q in enumerate(pm2):
            if lo1 + i + lo2 + k >= 7:
                brute += p * q
    expect("two strata against enumeration", abs(exact_conditional(two)["p_greater"] - brute) < 1e-12)
    try:
        from scipy import stats  # type: ignore[import-untyped]
        for t in [(7, 3, 2, 8), (1, 9, 5, 5), (10, 0, 4, 6)]:
            ref = stats.fisher_exact([[t[0], t[1]], [t[2], t[3]]], alternative="greater").pvalue
            expect(f"one stratum {t} = Fisher's exact (scipy)", abs(exact_conditional([t])["p_greater"] - ref) < 1e-10)
    except ImportError:
        print("  (scipy not found: Fisher cross-check skipped)")

    # 5. The interaction: identical contrasts differ by nothing; a contrast against its mirror by 2 ln OR.
    print("5. the difference of two MH log odds ratios")
    same = or_difference(china, china)
    expect("identical sets: z = 0, one-sided p = 0.5", abs(same["z"]) < 1e-12 and abs(same["p_one_sided"] - 0.5) < 1e-12)
    mirror = [(b, a, d, c) for a, b, c, d in china]                   # outcome columns swapped: OR -> 1/OR
    m = or_difference(china, mirror)
    expect("mirror: ln-ratio 2 ln 2.1745, se sqrt(2 V)", abs(m["log_ratio"] - 2 * math.log(r["or"])) < 1e-9
           and abs(m["se"] - math.sqrt(2 * r["var_log_or"])) < 1e-12)
    z0 = or_difference([(3, 0, 0, 3)], [(1, 1, 1, 1)])
    expect("an infinite odds ratio: ½ added to every cell, flagged", z0["corrected"] and "z" in z0)
    z1 = or_difference([(0, 5, 0, 5), (0, 5, 0, 5)], [(1, 1, 1, 1)])
    expect("a set with no informative stratum: no test, not an odds ratio of 1 by the ½ rule",
           "z" not in z1 and "first set" in z1.get("note", ""))

    # 6. Holm (Scand J Statist 6:65-70, 1979), by hand: p = .01, .04, .03, .005 over m = 4 —
    #    .005·4 = .02; max(.02, .01·3) = .03; max(.03, .03·2) = .06; max(.06, .04·1) = .06.
    print("6. Holm and the campaign family")
    h = holm({"A": 0.01, "B": 0.04, "C": 0.03, "D": 0.005})
    want = {"A": 0.03, "B": 0.06, "C": 0.06, "D": 0.02}
    expect("adjusted .03 .06 .06 .02", all(abs(h[k] - v) < 1e-12 for k, v in want.items()), f"{h}")
    h2 = holm({"A": 0.01, "B": None, "C": 0.03, "D": 0.005})
    expect("a test not run counts in m (p = 1)", abs(h2["D"] - 0.02) < 1e-12 and h2["B"] == 1.0)
    fb = family_bounds(0.005, h["D"], 23, 0.05)
    expect("bounds .02–.115, depends on the others", abs(fb["lower"] - 0.02) < 1e-12 and abs(fb["upper"] - 0.115) < 1e-12
           and fb["verdict"].startswith("depends"))
    expect("M·p ≤ α: rejected whatever", family_bounds(0.001, 0.004, 23, 0.05)["verdict"].startswith("rejected"))
    expect("E2-B1 Holm > α: never", family_bounds(0.03, 0.06, 23, 0.05)["verdict"].startswith("not rejected"))

    # 7. Trials end to end: every bucket, the denominators, the headline when coverage is missing.
    print("7. trials → buckets → tests")
    ok_v = {"status": "ok", "par": {"12": {"speedup": 2.0}}}

    def trial(bench: str, arm: str, rep: int, outcome: str, **kw: Any) -> dict:
        t = {"benchmark": bench, "arm": arm, "repeat": rep, "run_id": "r1", "model": "m", "outcome": outcome,
             "verify": dict(ok_v), "best_speedup": 2.0}
        t.update(kw)
        return t
    arms = {role: arm for role, arm, _ in ARM_ROLES}
    pop = {"tsvc_b1/s151": {"direction": "a", "tier": 1, "n_per_cell": 2},
           "tsvc_b1/s161": {"direction": "a", "tier": 1, "n_per_cell": 2},
           "tsvc_b1/s152": {"direction": "b", "tier": 1, "n_per_cell": 2}}
    ts = [trial("tsvc_b1/s151", arms["agent_full"], 1, "FASTER", hot_loop_covered=True),
          trial("tsvc_b1/s151", arms["agent_full"], 2, "parallel-not-faster", hot_loop_covered=False),
          trial("tsvc_b1/s151", arms["agent_none"], 1, "no-change"),
          trial("tsvc_b1/s151", arms["agent_none"], 2, "SCAFFOLD_MODIFIED"),
          trial("tsvc_b1/s151", arms["bare"], 1, "FASTER", hot_loop_covered=True),
          trial("tsvc_b1/s151", arms["bare"], 2, "BROKEN"),
          trial("tsvc_b1/s151", arms["twin_full"], 1, "FASTER"),
          trial("tsvc_b1/s151", arms["twin_none"], 1, "VERIFY_FAILED", verify={"status": "verify_build_failed",
                "build_errors": {"final_seq": "error"}}),
          trial("tsvc_b1/s161", arms["agent_full"], 1, "FASTER"),
          trial("tsvc_b1/s161", arms["agent_none"], 1, "AGENT_ERROR"),
          trial("tsvc_b1/s152", arms["dp_alone"], 1, "FASTER", hot_loop_covered=True, model="other"),
          trial("tsvc/s000", arms["agent_full"], 1, "FASTER")]
    races = {("r1", "tsvc_b1/s151", arms["bare"], 1): "tsan"}
    res = analyse(ts, pop, arms, races)
    b = {(j["benchmark"], j["arm"], j["repeat"]): j["bucket"] for j in res["trials"]}
    expect("gate arm, covered: success", b[("tsvc_b1/s151", arms["agent_full"], 1)] == "success")
    expect("gate arm, not covering", b[("tsvc_b1/s151", arms["agent_full"], 2)] == "not-covering")
    expect("gate arm, no coverage field: coverage-unknown", b[("tsvc_b1/s161", arms["agent_full"], 1)] == "coverage-unknown")
    expect("model alone, TSan: racy", b[("tsvc_b1/s151", arms["bare"], 1)] == "racy")
    expect("twin without a race verdict: race-unchecked", b[("tsvc_b1/s151", arms["twin_full"], 1)] == "race-unchecked")
    expect("final program does not build: did-not-compile", b[("tsvc_b1/s151", arms["twin_none"], 1)] == "did-not-compile")
    expect("harness edit and agent error out of the denominator",
           res["groups"]["a1"]["per_arm"]["agent_none"]["with_verdict"] == 1)
    expect("DiscoPoP alone is exempt from the model list", res["models"] == ["m"])
    expect("outside the population listed", any(k.startswith("tsvc/s000") for k in res["outside_population"]))
    expect("coverage and race gaps: NOT established", not res["established"] and res["coverage_unknown_total"] == 1)
    quiet = analyse([trial("tsvc_b1/s151", arms[r], k, "no-change") for r in ("agent_full", "agent_none") for k in (1, 2)],
                    pop, arms, {})
    expect("a test with complete inputs that cannot run: not established, and why",
           not quiet["tests"]["E2B1-i"]["gaps"] and "E2B1-i: no informative stratum: no test" in quiet["not_established"],
           f"{quiet['not_established']}")
    # the 28 Sep ruling: a verification run that did not finish after the program verified exact elsewhere
    slow = {"benchmark": "tsvc_b1/s424", "arm": "full_b1_nospeed", "outcome": "BROKEN", "repeat": 3, "run": "x",
            "verify": {"status": "final_run_failed_T12", "dump_exact": True,
                       "par": {"6": {"max_rel_err": 0.0, "speedup": 0.011}}}}
    crash = {"benchmark": "tsvc_b1/s171", "arm": "full_b1_nospeed", "outcome": "BROKEN", "repeat": 5, "run": "x",
             "verify": {"status": "final_run_failed_T6", "dump_exact": True, "par": {}}}
    js, jc = judge(slow, {}), judge(crash, {})
    expect("a run that did not finish after an exact one elsewhere: correct but slower, not unsafe",
           js["bucket"] == "timed-out-correct" and not js["unsafe"] and js["slower"] and not js["success"], str(js))
    expect("a crash at the first thread count stays BROKEN and unsafe", jc["bucket"] == "BROKEN" and jc["unsafe"], str(jc))
    expect("E2B1-iii counts BROKEN and racy of the model alone",
           res["tests"]["E2B1-iii"]["strata"]["tsvc_b1/s151"] == [0.0, 2.0, 2.0, 0.0])
    md = to_markdown(res)
    head = md.split("## ")[0]
    expect("the report renders, NOT ESTABLISHED and the missing coverage in its headline",
           "NOT ESTABLISHED" in head and "carry no `hot_loop_covered`" in head and "have no race verdict" in head)
    try:
        json.dumps(res, default=str, allow_nan=False)
        strict = True
    except ValueError:
        strict = False
    expect("the JSON holds no NaN or Infinity", strict)

    # 8. The frozen population is the one decided on 27 Sep (a change is a substitution, logged).
    print("8. the population file")
    units, draws = load_population(POPULATION_FILE)
    by = lambda d, t: sorted(b for b, u in units.items() if u["direction"] == d and u["tier"] == t)  # noqa: E731
    expect("(a) tier 1: s151, s161, bfs", by("a", 1) == ["rodinia_b1/bfs", "tsvc_b1/s151", "tsvc_b1/s161"], f"{by('a', 1)}")
    expect("(a) tier 2: s131, s424", by("a", 2) == ["tsvc_b1/s131", "tsvc_b1/s424"], f"{by('a', 2)}")
    expect("(b): s152, s171, s277, s481, vas (s482 and s258 left by the substitution rule, 27 Sep)",
           by("b", 1) == [f"tsvc_b1/{k}" for k in ("s152", "s171", "s277", "s481", "vas")], f"{by('b', 1)}")
    expect("N = 10 for (a), 5 for (b); DiscoPoP alone 3 draws",
           {u["n_per_cell"] for u in units.values() if u["direction"] == "a"} == {10}
           and {u["n_per_cell"] for u in units.values() if u["direction"] == "b"} == {5} and draws == 3)
    print(f"\nself-test: {'ALL PASS' if not fails else f'{fails} FAILURE(S)'}")
    return 1 if fails else 0


# ---- command line -------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="*", help="run ids; RUN:ARM+ARM keeps only those arms of a run (DiscoPoP alone "
                    "from the T0.11 v4 draws, e.g. t0_11_v4_a:discopop_capability)")
    ap.add_argument("--population", type=Path, default=POPULATION_FILE,
                    help="the frozen population (default config/e2b1_population.json, the 27 Sep decisions)")
    ap.add_argument("--races", type=Path, action="append", default=[],
                    help="race_check.py results.jsonl for the model-only arms' programs (repeatable); without "
                         "them their parallel programs are not race-checked and the tests are NOT established")
    ap.add_argument("--model", default=None,
                    help="the model whose cells are analysed; required when the model-driven arms hold more than "
                         "one (Haiku and the pre-registered Qwen cells are never pooled). DiscoPoP alone is exempt")
    for role, arm, label in ARM_ROLES:
        ap.add_argument(f"--{role.replace('_', '-')}", default=arm, help=f"{label} (default {arm}, arms.json E2-B1)")
    ap.add_argument("--no-continuity", action="store_true",
                    help="CMH without the 1/2 continuity correction (default: with it — Mantel & Haenszel 1959 as "
                         "published, conservative at 10 trials per arm and loop; both values are always reported)")
    ap.add_argument("--alpha", type=float, default=0.05, help="the campaign's error budget (EXPERIMENT_PLAN.html §2)")
    ap.add_argument("--family-size", type=int, default=FAMILY_SIZE,
                    help=f"hypotheses in the campaign's Holm family (default {FAMILY_SIZE}: the plan's 19 rows H1–H13 "
                         "with their lettered forms, plus E2-B1's four named tests of 27 Sep)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true", help="check the statistics on textbook examples and exit")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.runs:
        ap.error("give at least one run (or --self-test)")
    arms = {role: str(getattr(a, role)) for role, _, _ in ARM_ROLES}
    trials = load_trials(a.runs)
    models = sorted({str(t.get("model")) for t in trials if t.get("arm") in set(arms.values()) - {arms["dp_alone"]}})
    if a.model:
        trials = [t for t in trials if t.get("arm") == arms["dp_alone"] or str(t.get("model")) == a.model]
    elif len(models) > 1:
        sys.exit(f"the model-driven arms hold {len(models)} models ({', '.join(models)}): pass --model — they are never pooled")
    units, dp_draws = load_population(a.population)
    res = analyse(trials, units, arms, load_races(a.races), continuity=not a.no_continuity, alpha=a.alpha,
                  family_size=a.family_size, dp_draws=dp_draws)
    res["population_file"] = str(a.population)
    md = to_markdown(res)
    print(md)
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "e2b1_stats.md").write_text(md)
        (a.out / "e2b1_stats.json").write_text(json.dumps(res, indent=2, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
