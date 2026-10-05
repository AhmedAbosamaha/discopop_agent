# The main comparison in numbers

Runs: e2b1_a_1, e2b1_a_2, e2b1_a_3, e2b1_b_1, e2b1_bare_m3_a, e2b1_bare_m3_b, e2b1_bare_m3_bfs, t0_11_b1_a, t0_11_b1_b, t0_11_b1_bfs15_a, t0_11_b1_bfs15_b, t0_11_b1_bfs15_c, t0_11_b1_c. Agent arm: `full_b1_nospeed`; baseline: `discopop_capability` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Unclassified

- 10 benchmarks, 75 agent trials. Verdicts: **gained** 13, **gained-not-faster** 4, **equal** 5, **worse** 40, **lost** 2, **neither** 8, **unsafe** 3.
- Trials reaching a verified parallel program — agent: 62 of 75 (83 %, 95 % CI 73–90 %); DiscoPoP alone: 15 of 33 (45 %, 95 % CI 30–62 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 25 of 75 (33 %, 95 % CI 24–45 %); DiscoPoP alone: 15 of 33 (45 %, 95 % CI 30–62 %).
- Benchmarks with at least one gain: 4 of 10 (rodinia_b1/bfs, tsvc_b1/s131, tsvc_b1/s151, tsvc_b1/s161).
- Speed, paired by benchmark (10 timeable benchmarks): median agent ÷ DiscoPoP alone = **0.57×** (bootstrap 95 % CI 0.34–0.90×); Wilcoxon signed-rank, one-sided: W = 7, p = 0.9863, 10 non-zero pairs; Cliff's δ = -0.47.
- **Unsafe acceptances: 3** — tsvc_b1/s424 rep3, tsvc_b1/s424 rep5, tsvc_b1/s171 rep5.
- Lost (DiscoPoP alone reaches a parallel program, the agent's trial does not): tsvc_b1/s152 rep1, tsvc_b1/s152 rep3.

## What actually happened inside the trials

- 75 agent trials, 146 model calls (0 failed).
- Profile refreshes after a kept rewrite: 104 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 104 time(s).
- Explorer stalls (killed at the limit, draw repeated): 3 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 75.
- Host load (1-min) at trial start: 2–40.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `full_b1_nospeed`, model alone `bare_llm_nospeed`, DiscoPoP alone `discopop_capability`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

