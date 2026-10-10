# The main comparison in numbers

Runs: e3_a, e3_d_1, e3_d_2, e3_d_3, e3_d_4, e3_r_1, e3_r_2, e3_r_3, e3_r_4, e3c_v8_s341. Agent arm: `['default_v5', 'llm_pragmas_v5']`; baseline: `discopop_gate_v5` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 180 agent trials. Verdicts: **gained** 155, **gained-not-faster** 7, **neither** 18.
- Trials reaching a verified parallel program — agent: 162 of 180 (90 %, 95 % CI 85–94 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 155 of 180 (86 %, 95 % CI 80–90 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 17 of 18 (tsvc_c2/s112, tsvc_c2/s121, tsvc_c2/s1213, tsvc_c2/s127, tsvc_c2/s211, tsvc_c2/s212, tsvc_c2/s243, tsvc_c2/s244, tsvc_c2/s252, tsvc_c2/s254, tsvc_c2/s255, tsvc_c2/s281, tsvc_c2/s291, tsvc_c2/s292, tsvc_c2/s293, tsvc_c3/s241, tsvc_c3/s331).
- Speed, paired by benchmark (18 timeable benchmarks): median agent ÷ DiscoPoP alone = **2.59×** (bootstrap 95 % CI 1.37–3.15×); Wilcoxon signed-rank, one-sided: W = 153, p = 7.629e-06, 17 non-zero pairs; Cliff's δ = +0.94.
- **Unsafe acceptances: 0**.

## Class A — parallel as written (no-harm control)

- 3 benchmarks, 6 agent trials. Verdicts: **better** 1, **equal** 5.
- Trials reaching a verified parallel program — agent: 6 of 6 (100 %, 95 % CI 61–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 6 of 6 (100 %, 95 % CI 61–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Benchmarks with at least one gain: 0 of 3.
- Speed, paired by benchmark (3 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.01×** (bootstrap 95 % CI 0.99–18.37×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.56.
- **Unsafe acceptances: 0**.

## Class D — true recurrences (must-decline control)

- 4 benchmarks, 24 agent trials. Verdicts: **neither** 24.
- Trials reaching a verified parallel program — agent: 0 of 24 (0 %, 95 % CI 0–14 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 0 of 24 (0 %, 95 % CI 0–14 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 0 of 4.
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×** (bootstrap 95 % CI 1.00–1.00×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 210 agent trials, 912 model calls (0 failed).
- Profile refreshes after a kept rewrite: 377 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 377 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–19.

