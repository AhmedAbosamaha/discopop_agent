#!/usr/bin/env python3
"""Where the agent's trials stop: the stage-by-stage funnel of every agent trial, and for the
ones that do not end FASTER, the step that stopped them.  No model, no build — it reads the
archived trial records and agent logs.

Written for the author's question of 25 Sep ("why did the evidence not help, why is the rest
not reached?"): E2's arms differ in what the model is TOLD, so the question is at which stage,
if any, the arms part.  Stages, in the order a trial passes them:

  1  the model was asked about a region
  2  one of its rewrites passed the gate (compile, sequential output on every input)
  3  DiscoPoP found parallelism in the rewritten lines, so the rewrite was kept
  4  a SAFE pragma for it existed in Phase B (it passed the gate's safety stages; Phase B's
     speed check comes after that) — the last stage before any speed judgment
  5  the finished program is still parallel after the speed checks (Phase B, D33, Settle)
  6  the harness's verdict: FASTER

Agent v3 (D40, 26 Sep) judges a kept rewrite the way it will ship before Phase B; a rewrite
it reverts passed the gate and DiscoPoP found parallelism in it, so it gets its own stop
(`D40: ...`) instead of "DiscoPoP found nothing", and the D40 verdicts get their own table.

Run: `agent/tools/failure_funnel.py RUN... [--arms a,b] [--cls R] [--loops s112,s121] [--out FILE]`.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Counter, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import campaign  # noqa: E402

AGENT_ARMS = "default,full_b1,no_evidence,no_evidence_b1"
STAGES = ["1 the model was asked", "2 a rewrite passed the gate (correct)",
          "3 DiscoPoP found parallelism in it (kept)", "4 a safe pragma existed (before any speed check)",
          "5 still parallel after the speed checks", "6 FASTER (harness)"]
STOPS = ["no model call", "every rewrite rejected by the gate", "rewrite correct, DiscoPoP found nothing in it",
         "D40: its pragmas failed the safety gate", "D40: the program with them was not faster",
         "rewrite kept, no pragma survived Phase B", "Settle: finished program slower than the original",
         "shipped parallel, harness below 1.1x", "harness edit", "other"]


def _classes() -> Dict[str, str]:
    doc = json.loads((HERE.parent / "config" / "benchmark_classes.json").read_text())
    return {b: c for c, bs in doc["classes"].items() for b in bs}


def _trials(runs: List[str]) -> List[Tuple[dict, str]]:
    out: List[Tuple[dict, str]] = []
    for run in runs:
        root = next((d for d in (HERE.parent / "runs" / run, campaign.find_run(run)) if d and d.exists()), None)
        if root is None:
            sys.exit(f"run {run} not found under runs/ or results/")
        for p in sorted(root.glob("benchmarks/**/trial.json")):
            log = p.parent / "agent.log"
            out.append((json.loads(p.read_text()), log.read_text(errors="replace") if log.exists() else ""))
    return out


def _stop(t: dict) -> str:
    """The step that stopped a trial that did not end FASTER."""
    rv = t.get("region_verdicts") or {}
    if t.get("outcome") == "SCAFFOLD_MODIFIED":
        return "harness edit"
    if not t.get("llm_calls"):
        return "no model call"
    if not rv.get("ACCEPTED"):
        d40 = t.get("d40_verdicts") or {}
        if d40.get("not_faster"):
            return "D40: the program with them was not faster"
        if d40.get("pattern_broken"):
            return "D40: its pragmas failed the safety gate"
        return ("every rewrite rejected by the gate" if not t.get("gate_passes_phase_a")
                else "rewrite correct, DiscoPoP found nothing in it")
    if not rv.get("APPLIED"):
        return "rewrite kept, no pragma survived Phase B"
    if not t.get("pragmas_in_final") and t.get("settle_dropped"):
        return "Settle: finished program slower than the original"
    if t.get("pragmas_in_final"):
        return "shipped parallel, harness below 1.1x"
    return "other"


def analyse(runs: List[str], arms: List[str], cls: str, loops: Sequence[str] = ()) -> str:
    classes = _classes()
    funnel: Dict[str, Counter[str]] = {a: collections.Counter() for a in arms}
    stops: Dict[str, Counter[str]] = {a: collections.Counter() for a in arms}
    calls: Dict[str, Counter[int]] = {a: collections.Counter() for a in arms}
    per_loop: Dict[str, Dict[str, Counter[str]]] = collections.defaultdict(
        lambda: {a: collections.Counter() for a in arms})
    settle: List[float] = []
    n: Counter[str] = collections.Counter()
    d40: Dict[str, Counter[str]] = {a: collections.Counter() for a in arms}
    all_calls: Dict[str, List[int]] = {a: [] for a in arms}
    for t, log in _trials(runs):
        a = str(t.get("arm"))
        if a not in arms or (cls and classes.get(str(t.get("benchmark"))) != cls):
            continue
        if loops and str(t.get("benchmark")).split("/")[-1] not in loops:
            continue
        n[a] += 1
        all_calls[a].append(int(t.get("llm_calls") or 0))
        if "d40_verdicts" in t:
            d40[a]["trials run under v3"] += 1
            for verdict, k in (t.get("d40_verdicts") or {}).items():
                d40[a][verdict] += k
            d40[a]["trials with a verdict"] += bool(t.get("d40_verdicts"))
        rv = t.get("region_verdicts") or {}
        phase_b = log.split("PHASE B", 1)[1] if "PHASE B" in log else ""
        safe_b = len(re.findall(r"marginal [0-9.]+", phase_b)) + len(re.findall(r"deferred", phase_b, re.I))
        reached = [bool(t.get("llm_calls")), bool(t.get("gate_passes_phase_a")), bool(rv.get("ACCEPTED")),
                   bool(rv.get("ACCEPTED")) and safe_b > 0, bool(t.get("pragmas_in_final")),
                   t.get("outcome") == "FASTER"]
        for s, ok in zip(STAGES, reached):
            funnel[a][s] += ok
        b = str(t.get("benchmark"))
        if t.get("outcome") == "FASTER":
            per_loop[b][a]["FASTER"] += 1
            continue
        why = _stop(t)
        stops[a][why] += 1
        per_loop[b][a][why] += 1
        calls[a][int(t.get("llm_calls") or 0)] += 1
        if why.startswith("Settle"):
            r = [float(x) for x in re.findall(r"slower than the original: ([0-9.]+)x", log)]
            if r:
                settle.append(max(r))
    head = "| | " + " | ".join(f"`{a}`" for a in arms) + " |"
    rule = "|---|" + "---:|" * len(arms)
    out = [f"# Where the agent's trials stop — {', '.join(runs)}", "",
           f"Class {cls or 'all'}{'; loops ' + ', '.join(loops) if loops else ''}; arms {', '.join(arms)}. Generated by `agent/tools/failure_funnel.py` from the archived "
           "trial records and agent logs (no model, no build).", "",
           "## The funnel: how many trials reach each stage", "", head, rule]
    out += [f"| {s} | " + " | ".join(str(funnel[a][s]) for a in arms) + " |" for s in STAGES]
    out += [f"| trials | " + " | ".join(str(n[a]) for a in arms) + " |", "",
            "## The trials that did not end FASTER: what stopped them", "", head, rule]
    out += [f"| {s} | " + " | ".join(str(stops[a][s]) for a in arms) + " |"
            for s in STOPS if any(stops[a][s] for a in arms)]
    if settle:
        settle.sort()
        out += ["", f"Settle's paired ratio (finished program ÷ original, best measured) in the {len(settle)} trials it "
                f"reverted: median {statistics.median(settle):.2f}×, lowest {settle[0]:.2f}×, highest {settle[-1]:.2f}×; "
                f"{sum(x >= 0.9 for x in settle)} at 0.9× or more."]
    out += ["", "Model calls per trial, every trial: " + "; ".join(
        f"`{a}` mean {statistics.mean(all_calls[a]):.2f}" for a in arms if all_calls[a]) + "."]
    if any(d40[a] for a in arms):
        rows = ["trials run under v3", "trials with a verdict", "ok", "not_faster", "pattern_broken", "exposed",
                "safe_deferred"]
        out += ["", "## D40 (agent v3): the verdicts on kept rewrites, judged as shipped", "",
                "A trial can hold several verdicts (one per rewrite judged); `exposed` = the timing could not be "
                "measured, so the rewrite went on to Phase B unjudged; `safe_deferred` (v3.1, D40.1) = its "
                "pragmas passed the safety half at a depth a deeper level follows, speed judged at the last.",
                "", head, rule]
        out += [f"| {r} | " + " | ".join(str(d40[a][r]) for a in arms) + " |" for r in rows]
    out += ["", "Model calls made by the trials that did not end FASTER: " + "; ".join(
        f"`{a}` " + ", ".join(f"{k} call(s): {v}" for k, v in sorted(calls[a].items())) for a in arms) + ".",
            "", "## Per loop: FASTER · no pragma survived Phase B · Settle reverted · shipped below 1.1× · "
            "gate or DiscoPoP stopped the rewrite · D40 reverted it (of the trials run)", "",
            "| loop | " + " | ".join(f"`{a}`" for a in arms) + " |", rule]
    for b in sorted(per_loop):
        cells = []
        for a in arms:
            k = per_loop[b][a]
            cells.append(f"{k['FASTER']} · {k[STOPS[5]]} · {k[STOPS[6]]} · {k[STOPS[7]]} · {k[STOPS[1]] + k[STOPS[2]]}"
                         f" · {k[STOPS[3]] + k[STOPS[4]]}")
        out.append(f"| `{b}` | " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--arms", default=AGENT_ARMS)
    ap.add_argument("--cls", default="R", help="benchmark class (benchmark_classes.json); '' for all")
    ap.add_argument("--loops", default="", help="only these loops, e.g. s112,s121 (the V3 pilot's ten)")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    md = analyse(a.runs, [x for x in a.arms.split(",") if x], a.cls, [x for x in a.loops.split(",") if x])
    print(md)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
