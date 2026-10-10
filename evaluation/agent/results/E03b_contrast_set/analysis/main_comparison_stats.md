# The main comparison in numbers

Runs: e3b_1, e3b_2, e3b_3, e3b_4. Agent arm: `['default_v5', 'llm_pragmas_v5']`; baseline: `discopop_gate_v5` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 6 benchmarks, 60 agent trials. Verdicts: **gained** 54, **gained-not-faster** 1, **neither** 5.
- Trials reaching a verified parallel program — agent: 55 of 60 (92 %, 95 % CI 82–96 %); DiscoPoP alone: 0 of 30 (0 %, 95 % CI 0–11 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 54 of 60 (90 %, 95 % CI 80–95 %); DiscoPoP alone: 0 of 30 (0 %, 95 % CI 0–11 %).
- Benchmarks with at least one gain: 6 of 6 (tsvc_c4/s3113, tsvc_c4/s314, tsvc_c4/s315, tsvc_c4/s316, tsvc_c4/s318, tsvc_c4/s319).
- Speed, paired by benchmark (6 timeable benchmarks): median agent ÷ DiscoPoP alone = **6.61×** (bootstrap 95 % CI 4.23–8.07×); Wilcoxon signed-rank, one-sided: W = 21, p = 0.01562, 6 non-zero pairs; Cliff's δ = +1.00.
- **Unsafe acceptances: 0**.

## Class A — parallel as written (no-harm control)

- 1 benchmarks, 10 agent trials. Verdicts: **equal** 9, **worse** 1.
- Trials reaching a verified parallel program — agent: 10 of 10 (100 %, 95 % CI 72–100 %); DiscoPoP alone: 5 of 5 (100 %, 95 % CI 57–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 10 of 10 (100 %, 95 % CI 72–100 %); DiscoPoP alone: 5 of 5 (100 %, 95 % CI 57–100 %).
- Benchmarks with at least one gain: 0 of 1.
- Speed, paired by benchmark (1 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×**; fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = -1.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 70 agent trials, 231 model calls (0 failed).
- Profile refreshes after a kept rewrite: 177 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 177 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–18.

