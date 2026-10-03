# The main comparison in numbers

Runs: e2o3_agent, t0_11_o3_a, t0_11_o3_b, t0_11_o3_c. Agent arm: `full_b1_nospeed_v3`; baseline: `discopop_capability` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Unclassified

- 3 benchmarks, 30 agent trials. Verdicts: **gained** 29, **neither** 1.
- Trials reaching a verified parallel program — agent: 29 of 30 (97 %, 95 % CI 83–99 %); DiscoPoP alone: 0 of 9 (0 %, 95 % CI 0–30 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 29 of 30 (97 %, 95 % CI 83–99 %); DiscoPoP alone: 0 of 9 (0 %, 95 % CI 0–30 %).
- Benchmarks with at least one gain: 3 of 3 (tsvc_b1/k23, tsvc_b1/k31, tsvc_b1/k36).
- Speed, paired by benchmark (3 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.28×** (bootstrap 95 % CI 1.25–1.46×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +1.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 30 agent trials, 52 model calls (0 failed).
- Profile refreshes after a kept rewrite: 30 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 30 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 30.
- Host load (1-min) at trial start: 3–17.

