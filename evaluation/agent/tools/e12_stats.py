#!/usr/bin/env python3
"""E12's read-out (pre-registered, THESIS_EXPERIMENTS §6, 30 Sep 2026): a small model inside the pipeline against
stronger models alone.

Per loop, the Haiku agent with DiscoPoP's evidence against each model used alone (the mirror: no DiscoPoP, no
gate) — Opus 5.5, Fable 5.1, Sonnet 5 where it ran, and Haiku alone before and after the SDK upgrade (the CLI
control). Every trial is judged exactly as E2-B1 judges it (`e2b1_stats.judge`: the race check on every
model-only parallel program, the hot-loop coverage, a harness edit out of every denominator). Reported per loop
and arm: successes (a race-free verified parallel program covering the hot loop), FASTER beside them, and unsafe
programs; each model alone against the agent with Fisher's exact test, one-sided (the agent more successes, more
FASTER, fewer unsafe). Descriptive, outside the campaign family.

    venv/bin/python evaluation/agent/tools/e12_stats.py --races R.jsonl ... --out DIR
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from math import comb
from pathlib import Path
from typing import Any, Dict, List, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "shared"))
import campaign  # noqa: E402
import e2b1_stats as es  # noqa: E402

AGENT = "Haiku agent + evidence (v3)"
# (label, run, arm, loops); the agent rows are the comparison point
ROWS: List[Tuple[str, str, str, Tuple[str, ...]]] = [
    (AGENT, "e2v3_k19", "full_b1_nospeed_v3", ("tsvc_b1/k19",)),
    (AGENT, "e2v3_k48", "full_b1_nospeed_v3", ("tsvc_b1/k48",)),
    (AGENT, "e2v3_s1213", "full_b1_nospeed_v3", ("tsvc_b1/s1213",)),
    (AGENT, "e2v3_s211", "full_b1_nospeed_v3", ("tsvc_b1/s211",)),
    (AGENT, "e12_agent_v3", "full_b1_nospeed_v3", ("tsvc_b1/s424", "tsvc_b1/s161")),
    ("Opus 5.5 alone", "e12_opus_v3", "bare_llm_nospeed_v3", ("tsvc_b1/k19", "tsvc_b1/k48")),
    ("Opus 5.5 alone", "e12_opus_v3b", "bare_llm_nospeed_v3", ("tsvc_b1/s1213", "tsvc_b1/s211")),
    ("Opus 5.5 alone", "e12_opus_b1", "bare_llm_nospeed", ("tsvc_b1/s424", "tsvc_b1/s161")),
    ("Fable 5.1 alone", "e12_fable_v3", "bare_llm_nospeed_v3", ("tsvc_b1/k19", "tsvc_b1/k48")),
    ("Fable 5.1 alone", "e12_fable_redo", "bare_llm_nospeed_v3", ("tsvc_b1/k19", "tsvc_b1/k48")),
    ("Fable 5.1 alone", "e12_fable_v3b", "bare_llm_nospeed_v3", ("tsvc_b1/s1213", "tsvc_b1/s211")),
    ("Fable 5.1 alone", "e12_fable_b1", "bare_llm_nospeed", ("tsvc_b1/s424", "tsvc_b1/s161")),
    ("Sonnet 5 alone", "e2v3s_k19", "bare_llm_nospeed_v3", ("tsvc_b1/k19",)),
    ("Sonnet 5 alone", "e12_sonnet_v3", "bare_llm_nospeed_v3", ("tsvc_b1/k48", "tsvc_b1/s1213", "tsvc_b1/s211")),
    ("Sonnet 5 alone", "e12_sonnet_b1", "bare_llm_nospeed", ("tsvc_b1/s424", "tsvc_b1/s161")),
    ("Haiku alone (new CLI)", "e12_haiku_v3", "bare_llm_nospeed_v3", ("tsvc_b1/k19", "tsvc_b1/k48")),
    ("Haiku alone (new CLI)", "e12_haiku_b1", "bare_llm_nospeed", ("tsvc_b1/s424", "tsvc_b1/s161")),
    ("Haiku alone (old CLI)", "e2v3_k19", "bare_llm_nospeed_v3", ("tsvc_b1/k19",)),
    ("Haiku alone (old CLI)", "e2v3_k48", "bare_llm_nospeed_v3", ("tsvc_b1/k48",)),
    ("Haiku alone (old CLI)", "e2v3_s1213", "bare_llm_nospeed_v3", ("tsvc_b1/s1213",)),
    ("Haiku alone (old CLI)", "e2v3_s211", "bare_llm_nospeed_v3", ("tsvc_b1/s211",)),
    ("Haiku alone (old CLI)", "e2b1_bare_m3_a", "bare_llm_nospeed", ("tsvc_b1/s424", "tsvc_b1/s161")),
]
# The completion of 3 Oct (§6): every model alone on the agent's six loops; Fable's three harness-edit trials
# of `e12_fable_v3` redone in `e12_fable_redo` (Fix 103) — the edits stay listed, marked redone.
LOOPS = ("tsvc_b1/k19", "tsvc_b1/k48", "tsvc_b1/s1213", "tsvc_b1/s211", "tsvc_b1/s424", "tsvc_b1/s161")


def fisher_greater(a: int, n1: int, c: int, n2: int) -> float:
    """P(X >= a) for the first group's count under the hypergeometric (one-sided Fisher)."""
    k, n = a + c, n1 + n2
    tot = comb(n, k)
    return sum(comb(n1, x) * comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / tot if tot else 1.0


def load(run: str, arm: str, loop: str) -> List[dict]:
    root = campaign.find_run(run)
    if root is None:
        sys.exit(f"run {run} not archived")
    out = []
    for p in sorted(glob.glob(str(root / "benchmarks" / loop / arm / "*" / "rep*" / "trial.json"))):
        t = json.loads(Path(p).read_text())
        t.setdefault("run_id", run)
        out.append(t)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--races", type=Path, action="append", default=[])
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    races = es.load_races(a.races)
    cells: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for label, run, arm, loops in ROWS:
        for loop in loops:
            js = [es.judge(t, races) for t in load(run, arm, loop)]
            c = cells.setdefault((label, loop), {"n": 0, "success": 0, "faster": 0, "unsafe": 0, "harness": 0,
                                                 "unchecked": 0, "runs": []})
            c["runs"].append(run)
            for j in js:
                if j["bucket"] == "harness-edit":
                    c["harness"] += 1
                    continue
                if not j["with_verdict"]:
                    continue
                c["n"] += 1
                c["success"] += j["success"]
                c["faster"] += j["faster"] and j["bucket"] == "success"
                c["unsafe"] += j["unsafe"]
                c["unchecked"] += j["bucket"] == "race-unchecked"
    labels = list(dict.fromkeys(r[0] for r in ROWS))
    md = ["# E12 — the Haiku agent with evidence against stronger models alone", "",
          "Per loop: successes (race-free verified parallel program covering the hot loop) · of them FASTER · "
          "unsafe (BROKEN, racy, not compiling) · trials with a verdict; harness edits apart. p: Fisher's exact, "
          "one-sided, the agent against the row (more successes / more FASTER successes / fewer unsafe).", ""]
    md += ["| arm | " + " | ".join(f"`{l.split('/')[1]}`" for l in LOOPS) + " |", "|---|" + "---|" * len(LOOPS)]
    for lab in labels:
        row = [lab]
        for loop in LOOPS:
            cell = cells.get((lab, loop))
            if cell is None:
                row.append("—")
                continue
            c = cell
            txt = f"{c['success']}/{c['n']} ({c['faster']} faster) · {c['unsafe']} unsafe"
            if c["harness"]:
                redone = any(r.endswith("_redo") for r in c["runs"])
                txt += f" · {c['harness']} harness edit(s){', redone' if redone else ''}"
            if c["unchecked"]:
                txt += f" · {c['unchecked']} race-unchecked"
            if lab != AGENT and (AGENT, loop) in cells:
                g = cells[(AGENT, loop)]
                ps = fisher_greater(g["success"], g["n"], c["success"], c["n"])
                pf = fisher_greater(g["faster"], g["n"], c["faster"], c["n"])
                pu = fisher_greater(c["unsafe"], c["n"], g["unsafe"], g["n"])
                txt += f"<br>p: success {ps:.3g} · faster {pf:.3g} · unsafe {pu:.3g}"
            row.append(txt)
        md.append("| " + " | ".join(row) + " |")
    md += ["", "Runs: " + "; ".join(f"{lab} — " + ", ".join(sorted({r for (l, _), c in cells.items() if l == lab
                                                                        for r in c['runs']})) for lab in labels) + "."]
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "e12_stats.md").write_text("\n".join(md) + "\n")
    (a.out / "e12_stats.json").write_text(json.dumps({f"{k[0]} | {k[1]}": v for k, v in cells.items()}, indent=1) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
