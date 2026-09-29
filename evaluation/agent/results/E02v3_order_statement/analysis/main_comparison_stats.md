# The main comparison in numbers

Runs: e2v3_k19, e2v3_k48, e2v3_s1213, e2v3_s211, t0_11_v3_a, t0_11_v3_b, t0_11_v3_c, t0_11_v3b_a, t0_11_v3b_b, t0_11_v3b_c. Agent arm: `['bare_llm_nospeed_v3', 'full_b1_nospeed_v3', 'no_evidence_b1_nospeed_v3', 'twin_full_nospeed_v3', 'twin_no_evidence_nospeed_v3']`; baseline: `discopop_capability` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Unclassified

- 4 benchmarks, 200 agent trials. Verdicts: **gained** 106, **gained-not-faster** 6, **worse** 10, **neither** 11, **unsafe** 60, **invalid** 7.
- Trials reaching a verified parallel program — agent: 122 of 193 (63 %, 95 % CI 56–70 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 106 of 193 (55 %, 95 % CI 48–62 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 4 of 4 (tsvc_b1/k19, tsvc_b1/k48, tsvc_b1/s1213, tsvc_b1/s211).
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.93×** (bootstrap 95 % CI 1.10–3.97×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +1.00.
- **Unsafe acceptances: 60** — tsvc_b1/k19 rep10, tsvc_b1/k19 rep2, tsvc_b1/k19 rep3, tsvc_b1/k19 rep4, tsvc_b1/k19 rep5, tsvc_b1/k19 rep6, tsvc_b1/k19 rep7, tsvc_b1/k19 rep8, tsvc_b1/k19 rep9, tsvc_b1/k19 rep1, tsvc_b1/k19 rep10, tsvc_b1/k19 rep2, tsvc_b1/k19 rep3, tsvc_b1/k19 rep4, tsvc_b1/k19 rep5, tsvc_b1/k19 rep6, tsvc_b1/k19 rep7, tsvc_b1/k19 rep8, tsvc_b1/k19 rep9, tsvc_b1/s1213 rep1, tsvc_b1/s1213 rep5, tsvc_b1/s1213 rep8, tsvc_b1/s1213 rep3, tsvc_b1/s1213 rep4, tsvc_b1/s1213 rep5, tsvc_b1/s1213 rep6, tsvc_b1/s1213 rep1, tsvc_b1/s1213 rep3, tsvc_b1/s1213 rep5, tsvc_b1/s1213 rep8, tsvc_b1/s1213 rep9, tsvc_b1/s211 rep1, tsvc_b1/s211 rep10, tsvc_b1/s211 rep2, tsvc_b1/s211 rep4, tsvc_b1/s211 rep6, tsvc_b1/s211 rep8, tsvc_b1/s211 rep1, tsvc_b1/s211 rep10, tsvc_b1/s211 rep2, tsvc_b1/s211 rep3, tsvc_b1/s211 rep4, tsvc_b1/s211 rep6, tsvc_b1/s211 rep8, tsvc_b1/s211 rep9, tsvc_b1/s211 rep1, tsvc_b1/s211 rep10, tsvc_b1/s211 rep3, tsvc_b1/s211 rep6, tsvc_b1/s211 rep7, tsvc_b1/s211 rep9, tsvc_b1/k48 rep1, tsvc_b1/k48 rep3, tsvc_b1/k48 rep4, tsvc_b1/k48 rep5, tsvc_b1/k48 rep6, tsvc_b1/k48 rep7, tsvc_b1/k48 rep9, tsvc_b1/k48 rep1, tsvc_b1/k48 rep8.
- Missing or withheld (7): tsvc_b1/k19 rep1: invalid (VERIFY_FAILED); tsvc_b1/s1213 rep10: invalid (VERIFY_FAILED); tsvc_b1/s1213 rep9: invalid (VERIFY_FAILED); tsvc_b1/s211 rep3: invalid (VERIFY_FAILED); tsvc_b1/s211 rep7: invalid (SCAFFOLD_MODIFIED); tsvc_b1/k48 rep10: invalid (VERIFY_FAILED); tsvc_b1/k48 rep8: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 200 agent trials, 243 model calls (0 failed).
- Profile refreshes after a kept rewrite: 69 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 69 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 200.
- Host load (1-min) at trial start: 2–25.

