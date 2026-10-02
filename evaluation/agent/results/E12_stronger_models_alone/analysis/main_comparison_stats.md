# The main comparison in numbers

Runs: e12_agent_v3, e12_opus_b1, e12_opus_v3, e2v3_k19, e2v3_k48, t0_11_b1_a, t0_11_b1_b, t0_11_b1_c, t0_11_v3b_a, t0_11_v3b_b, t0_11_v3b_c. Agent arm: `full_b1_nospeed_v3`; baseline: `discopop_capability` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Unclassified

- 4 benchmarks, 40 agent trials. Verdicts: **gained** 30, **gained-not-faster** 1, **worse** 1, **neither** 8.
- Trials reaching a verified parallel program — agent: 32 of 40 (80 %, 95 % CI 65–90 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 30 of 40 (75 %, 95 % CI 60–86 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 4 of 4 (tsvc_b1/k19, tsvc_b1/k48, tsvc_b1/s161, tsvc_b1/s424).
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.79×** (bootstrap 95 % CI 1.00–4.02×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.75.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 40 agent trials, 62 model calls (0 failed).
- Profile refreshes after a kept rewrite: 35 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 35 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 40.
- Host load (1-min) at trial start: 3–20.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `full_b1_nospeed_v3`, model alone `bare_llm_nospeed_v3`, DiscoPoP alone `discopop_capability`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

