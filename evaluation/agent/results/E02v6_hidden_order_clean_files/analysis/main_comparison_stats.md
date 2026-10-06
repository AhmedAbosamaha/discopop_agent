# The main comparison in numbers

Runs: e2v6_agent_1, e2v6_agent_2, e2v6_agent_3, t0_11_c2_a, t0_11_c2_b, t0_11_c2_c. Agent arm: `full_b1_nospeed_v4`; baseline: `discopop_capability` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 6 benchmarks, 60 agent trials. Verdicts: **gained** 55, **neither** 5.
- Trials reaching a verified parallel program — agent: 55 of 60 (92 %, 95 % CI 82–96 %); DiscoPoP alone: 0 of 18 (0 %, 95 % CI 0–18 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 55 of 60 (92 %, 95 % CI 82–96 %); DiscoPoP alone: 0 of 18 (0 %, 95 % CI 0–18 %).
- Benchmarks with at least one gain: 6 of 6 (tsvc_c2/k19, tsvc_c2/k23, tsvc_c2/k27, tsvc_c2/k31, tsvc_c2/k48, tsvc_c2/s161).
- Speed, paired by benchmark (6 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.61×** (bootstrap 95 % CI 1.38–2.97×); Wilcoxon signed-rank, one-sided: W = 21, p = 0.01562, 6 non-zero pairs; Cliff's δ = +1.00.
- **Unsafe acceptances: 0**.

## Class D — true recurrences (must-decline control)

- 1 benchmarks, 10 agent trials. Verdicts: **neither** 10.
- Trials reaching a verified parallel program — agent: 0 of 10 (0 %, 95 % CI 0–28 %); DiscoPoP alone: 0 of 3 (0 %, 95 % CI 0–56 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 0 of 10 (0 %, 95 % CI 0–28 %); DiscoPoP alone: 0 of 3 (0 %, 95 % CI 0–56 %).
- Benchmarks with at least one gain: 0 of 1.
- Speed, paired by benchmark (1 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×**; fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 70 agent trials, 124 model calls (0 failed).
- Profile refreshes after a kept rewrite: 57 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 57 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 70.
- Host load (1-min) at trial start: 4–3470.

