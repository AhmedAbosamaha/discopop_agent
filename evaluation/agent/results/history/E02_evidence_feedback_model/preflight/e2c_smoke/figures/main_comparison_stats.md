# The main comparison in numbers

Runs: e2c_smoke. Agent arm: `['bare_llm', 'compiler_remarks_b1', 'default', 'full_b1', 'hotspot_only_b1', 'no_evidence', 'no_evidence_b1']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 2 benchmarks, 14 agent trials. Verdicts: **gained** 5, **neither** 7, **unsafe** 2.
- Trials reaching a verified parallel program — agent: 5 of 14 (36 %, 95 % CI 16–61 %); DiscoPoP alone: 0 of 2 (0 %, 95 % CI 0–66 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 5 of 14 (36 %, 95 % CI 16–61 %); DiscoPoP alone: 0 of 2 (0 %, 95 % CI 0–66 %).
- Benchmarks with at least one gain: 2 of 2 (tsvc/s121, tsvc/s281).
- Speed, paired by benchmark (2 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.13×**; fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.50.
- **Unsafe acceptances: 2** — tsvc/s121 rep1, tsvc/s281 rep1.

## What actually happened inside the trials

- 14 agent trials, 19 model calls (0 failed).
- Profile refreshes after a kept rewrite: 12 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 12 time(s).
- Explorer stalls (killed at the limit, draw repeated): 2 inside agents, 16 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3886–5958.

