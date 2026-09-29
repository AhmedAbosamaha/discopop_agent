# The main comparison in numbers

Runs: e2b1_a_1, e2b1_a_2, e2b1_a_3, e2b1_b_1, e2b1_bare_m3_a, e2b1_bare_m3_b, e2b1_bare_m3_bfs, t0_11_b1_a, t0_11_b1_b, t0_11_b1_bfs15_a, t0_11_b1_bfs15_b, t0_11_b1_bfs15_c, t0_11_b1_c. Agent arm: `['bare_llm_nospeed', 'full_b1_nospeed', 'no_evidence_b1_nospeed', 'twin_full_nospeed', 'twin_no_evidence_nospeed']`; baseline: `discopop_capability` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Unclassified

- 10 benchmarks, 375 agent trials. Verdicts: **gained** 70, **gained-not-faster** 12, **better** 12, **equal** 37, **worse** 114, **lost** 2, **neither** 43, **unsafe** 70, **invalid** 15.
- Trials reaching a verified parallel program — agent: 245 of 360 (68 %, 95 % CI 63–73 %); DiscoPoP alone: 15 of 33 (45 %, 95 % CI 30–62 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 146 of 360 (41 %, 95 % CI 36–46 %); DiscoPoP alone: 15 of 33 (45 %, 95 % CI 30–62 %).
- Benchmarks with at least one gain: 4 of 10 (rodinia_b1/bfs, tsvc_b1/s131, tsvc_b1/s151, tsvc_b1/s161).
- Speed, paired by benchmark (10 timeable benchmarks): median agent ÷ DiscoPoP alone = **0.95×** (bootstrap 95 % CI 0.72–1.04×); Wilcoxon signed-rank, one-sided: W = 14, p = 0.8496, 9 non-zero pairs; Cliff's δ = -0.15.
- **Unsafe acceptances: 70** — tsvc_b1/s151 rep5, tsvc_b1/s151 rep7, tsvc_b1/s151 rep8, tsvc_b1/s151 rep7, tsvc_b1/s161 rep1, tsvc_b1/s161 rep4, tsvc_b1/s161 rep5, tsvc_b1/s161 rep6, tsvc_b1/s161 rep7, tsvc_b1/s161 rep8, tsvc_b1/s161 rep9, tsvc_b1/s161 rep1, tsvc_b1/s161 rep2, tsvc_b1/s161 rep5, rodinia_b1/bfs rep8, rodinia_b1/bfs rep1, rodinia_b1/bfs rep10, rodinia_b1/bfs rep2, rodinia_b1/bfs rep3, rodinia_b1/bfs rep4, rodinia_b1/bfs rep5, rodinia_b1/bfs rep6, rodinia_b1/bfs rep7, rodinia_b1/bfs rep8, rodinia_b1/bfs rep9, rodinia_b1/bfs rep1, rodinia_b1/bfs rep10, rodinia_b1/bfs rep3, rodinia_b1/bfs rep5, rodinia_b1/bfs rep6, rodinia_b1/bfs rep7, rodinia_b1/bfs rep8, tsvc_b1/s424 rep3, tsvc_b1/s424 rep5, tsvc_b1/s424 rep1, tsvc_b1/s424 rep10, tsvc_b1/s424 rep3, tsvc_b1/s424 rep4, tsvc_b1/s424 rep5, tsvc_b1/s424 rep2, tsvc_b1/s424 rep3, tsvc_b1/s424 rep9, tsvc_b1/s152 rep5, tsvc_b1/s171 rep5, tsvc_b1/s171 rep2, tsvc_b1/s171 rep3, tsvc_b1/s171 rep5, tsvc_b1/s481 rep2, tsvc_b1/s481 rep5, tsvc_b1/s481 rep1, tsvc_b1/s481 rep2, tsvc_b1/s481 rep5, tsvc_b1/s131 rep10, tsvc_b1/s131 rep3, tsvc_b1/s131 rep7, tsvc_b1/s131 rep8, tsvc_b1/s151 rep1, tsvc_b1/s161 rep10, tsvc_b1/s161 rep3, tsvc_b1/s161 rep8, tsvc_b1/s161 rep9, tsvc_b1/s424 rep1, tsvc_b1/s424 rep10, tsvc_b1/s424 rep2, tsvc_b1/s424 rep3, tsvc_b1/s424 rep4, tsvc_b1/s424 rep5, tsvc_b1/s424 rep6, tsvc_b1/s424 rep8, tsvc_b1/s424 rep9.
- Lost (DiscoPoP alone reaches a parallel program, the agent's trial does not): tsvc_b1/s152 rep1, tsvc_b1/s152 rep3.
- Missing or withheld (15): tsvc_b1/s151 rep3: invalid (SCAFFOLD_MODIFIED); tsvc_b1/s161 rep10: invalid (VERIFY_FAILED); tsvc_b1/s161 rep3: invalid (VERIFY_FAILED); rodinia_b1/bfs rep4: invalid (VERIFY_FAILED); tsvc_b1/s171 rep1: invalid (SCAFFOLD_MODIFIED); tsvc_b1/s277 rep2: invalid (VERIFY_FAILED); tsvc_b1/s481 rep1: invalid (VERIFY_FAILED); tsvc_b1/s481 rep4: invalid (VERIFY_FAILED); tsvc_b1/s481 rep4: invalid (VERIFY_FAILED); tsvc_b1/vas rep1: invalid (SCAFFOLD_MODIFIED); tsvc_b1/vas rep3: invalid (SCAFFOLD_MODIFIED); tsvc_b1/s171 rep2: invalid (VERIFY_FAILED); tsvc_b1/s171 rep3: invalid (VERIFY_FAILED); tsvc_b1/s171 rep4: invalid (VERIFY_FAILED); tsvc_b1/s277 rep5: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 375 agent trials, 523 model calls (0 failed).
- Profile refreshes after a kept rewrite: 211 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 211 time(s).
- Explorer stalls (killed at the limit, draw repeated): 11 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 375.
- Host load (1-min) at trial start: 2–40.

