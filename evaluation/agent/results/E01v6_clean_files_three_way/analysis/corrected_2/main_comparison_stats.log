# The main comparison in numbers

Runs: e1v6_a, e1v6_d, e1v6_r_1, e1v6_r_2, e1v6_r_3, e1v6_r_4, e1v6c_s241, e1v6c_s281, e1v6c_v7_agent, e1v6c_v7_control. Agent arm: `default_v4`; baseline: `discopop_gate_v4` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 90 agent trials. Verdicts: **gained** 79, **gained-not-faster** 6, **neither** 5.
- Trials reaching a verified parallel program — agent: 85 of 90 (94 %, 95 % CI 88–98 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 79 of 90 (88 %, 95 % CI 79–93 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 18 of 18 (tsvc_c2/s112, tsvc_c2/s121, tsvc_c2/s1213, tsvc_c2/s127, tsvc_c2/s211, tsvc_c2/s212, tsvc_c2/s243, tsvc_c2/s244, tsvc_c2/s252, tsvc_c2/s254, tsvc_c2/s255, tsvc_c2/s281, tsvc_c2/s291, tsvc_c2/s292, tsvc_c2/s293, tsvc_c2/s341, tsvc_c3/s241, tsvc_c3/s331).
- Speed, paired by benchmark (18 timeable benchmarks): median agent ÷ DiscoPoP alone = **2.24×** (bootstrap 95 % CI 1.38–3.11×); Wilcoxon signed-rank, one-sided: W = 153, p = 7.629e-06, 17 non-zero pairs; Cliff's δ = +0.94.
- **Unsafe acceptances: 0**.

## Class A — parallel as written (no-harm control)

- 3 benchmarks, 3 agent trials. Verdicts: **better** 1, **equal** 1, **worse** 1.
- Trials reaching a verified parallel program — agent: 3 of 3 (100 %, 95 % CI 44–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 3 of 3 (100 %, 95 % CI 44–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Benchmarks with at least one gain: 0 of 3.
- Speed, paired by benchmark (3 timeable benchmarks): median agent ÷ DiscoPoP alone = **0.98×** (bootstrap 95 % CI 0.78–1.16×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = -0.11.
- **Unsafe acceptances: 0**.

## Class D — true recurrences (must-decline control)

- 4 benchmarks, 12 agent trials. Verdicts: **neither** 12.
- Trials reaching a verified parallel program — agent: 0 of 12 (0 %, 95 % CI 0–24 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 0 of 12 (0 %, 95 % CI 0–24 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 0 of 4.
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×** (bootstrap 95 % CI 1.00–1.00×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 105 agent trials, 418 model calls (0 failed).
- Profile refreshes after a kept rewrite: 242 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 242 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–16.

