#!/usr/bin/env python3
"""E1-final's nine pre-registered tests (THESIS_EXPERIMENTS §6, 2 Oct 2026), from the four per-model read-outs.

`main_comparison_stats.py` is run once per model alone (the agent's and DiscoPoP alone's runs plus that model's
run, `--three-way default_v3 --bare bare_llm_v3 --baseline-arm discopop_gate_v3 --races …`) into
`analysis/<model>/`; this reads the four `main_comparison_stats.json` and writes the tests as registered, class R,
paired by loop:

  T1 (H1)      the agent against DiscoPoP alone — Wilcoxon signed-rank on per-loop medians, one-sided;
  T2–T5 (H13)  the agent against each model alone — per-loop unusable rate, one-sided (the agent fewer);
  T6–T9        the agent against each model alone — per-loop race-free FASTER rate, one-sided (the agent more);

Holm over the nine inside E1-final, and the campaign family's bound (M = 40). A comparison with fewer than six
non-zero pairs cannot reach significance and is reported "no test" (p = 1). H2 is a count with every case named.
The opposite direction of T6–T9 (a model alone ahead) is reported beside them, two-sided, as description.

    venv/bin/python evaluation/agent/tools/e1f_tests.py --analysis evaluation/agent/results/E01f_final_three_way/analysis
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

MODELS = (("haiku", "Haiku 4.5"), ("sonnet", "Sonnet 5"), ("opus", "Opus 5.5"), ("fable", "Fable 5.1"))
FAMILY = 40


def holm(ps: List[float]) -> List[float]:
    """Holm's step-down adjusted p-values, in the input order."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj = [1.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--analysis", type=Path, required=True)
    a = ap.parse_args()
    reads: Dict[str, Dict[str, Any]] = {m: json.loads((a.analysis / m / "main_comparison_stats.json").read_text())
                                        for m, _ in MODELS}
    first = reads["haiku"]
    h1 = first["classes"]["R"]["wilcoxon_agent_faster"]
    tests: List[Tuple[str, str, float, str]] = [
        ("T1", "H1 — the agent faster than DiscoPoP alone (per-loop medians)", float(h1["p_value"]),
         f"{h1['n_nonzero']} non-zero pairs of {h1['n_pairs']}, median agent ÷ DiscoPoP alone "
         f"{first['classes']['R']['median_ratio_agent_over_dp_alone']}×")]
    rows: List[str] = []
    for key, label, test in (("agent_vs_model_alone_unusable", "H13 — fewer unusable programs than {m}", "T{n}"),
                             ("agent_vs_model_alone_faster_race_free", "reach — more race-free FASTER than {m}", "T{n}")):
        for j, (m, name) in enumerate(MODELS):
            w = reads[m]["three_way"]["classes"]["R"][key]
            p = float(w.get("p_agent_ahead", 1.0)) if "p_agent_ahead" in w else 1.0
            n = 2 + j if key.endswith("unusable") else 6 + j
            detail = (f"the agent ahead on {w['agent_ahead']} loops, {name} alone on {w['model_alone_ahead']}"
                      + (f"; two-sided p {w['p_two_sided']:.3g}" if "p_two_sided" in w else f"; {w.get('note', '')}"))
            tests.append((test.format(n=n), label.format(m=name + " alone"), p, detail))
    adj = holm([t[2] for t in tests])
    out = ["# E1-final — the nine pre-registered tests (class R, 18 loops, paired by loop)", "",
           "Registered in THESIS_EXPERIMENTS §6, 2 Oct 2026, before any main trial. One-sided as registered; Holm "
           f"over the nine; the campaign family's bound is p × {FAMILY}. \"no test\": fewer than six loops differ.", "",
           "| test | hypothesis | p (one-sided) | Holm (E1-final) | family bound | rejected (Holm, 0.05) | detail |",
           "|---|---|---:|---:|---:|---|---|"]
    for (t, label, p, detail), q in zip(tests, adj):
        out.append(f"| {t} | {label} | {p:.3g} | {q:.3g} | {min(1.0, p * FAMILY):.3g} | {'yes' if q < 0.05 else 'no'} | {detail} |")
    out += ["", "## The three-way table per model (class R, 90 trials per setup)", "",
            "| setup | race-free FASTER | verified parallel | unusable (BROKEN · slower · racy · not compiling) |",
            "|---|---:|---:|---|"]
    shown = False
    for m, name in MODELS:
        arms = reads[m]["three_way"]["classes"]["R"]["arms"]
        for label in (("DiscoPoP alone", "DiscoPoP + agent") if not shown else ()) + ("model alone",):
            v = arms[label]
            who = name + " alone" if label == "model alone" else label
            out.append(f"| {who} | {v['faster_race_free']['k']} of {v['with_verdict']} | {v['parallel']['k']} | "
                       f"**{v['unusable']}** ({v['broken']} · {v['slower_shipped']} · {v['racy']} · {v['did_not_compile']})"
                       + (f" — {'; '.join(v['unusable_cases'])}" if label == "DiscoPoP + agent" and v["unusable_cases"] else "")
                       + " |")
        shown = True
    agent = reads["haiku"]["three_way"]["classes"]["R"]["arms"]["DiscoPoP + agent"]
    out += ["", f"**H2 (the agent ships no unusable program): {agent['unusable']} case(s)** — "
            + ("; ".join(agent["unusable_cases"]) or "none") + "."]
    (a.analysis / "e1f_tests.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
