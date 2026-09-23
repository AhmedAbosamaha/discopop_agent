# The main comparison in numbers

Runs: e1_a, e1_d, e1_r_a, e1_r_b. Agent arm: `['default']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested. **Restricted to the `tsvc` suite** — the primary set of D30; the registered set's numbers stand beside it, never behind it.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 90 agent trials. Verdicts: **gained** 44, **gained-not-faster** 2, **neither** 44.
- Trials reaching a verified parallel program — agent: 46 of 90 (51 %, 95 % CI 41–61 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 44 of 90 (49 %, 95 % CI 39–59 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 14 of 18 (tsvc/s112, tsvc/s1213, tsvc/s127, tsvc/s211, tsvc/s212, tsvc/s241, tsvc/s243, tsvc/s244, tsvc/s252, tsvc/s254, tsvc/s255, tsvc/s291, tsvc/s292, tsvc/s293).
- Speed, paired by benchmark (18 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.08×** (bootstrap 95 % CI 1.00–2.35×); Wilcoxon signed-rank, one-sided: W = 45, p = 0.001953, 9 non-zero pairs; Cliff's δ = +0.50.
- **Unsafe acceptances: 0**.

## Class A — parallel as written (no-harm control)

- 3 benchmarks, 3 agent trials. Verdicts: **better** 1, **worse** 1, **lost** 1.
- Trials reaching a verified parallel program — agent: 2 of 3 (67 %, 95 % CI 21–94 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 2 of 3 (67 %, 95 % CI 21–94 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Benchmarks with at least one gain: 0 of 3.
- Speed, paired by benchmark (3 timeable benchmarks): median agent ÷ DiscoPoP alone = **0.58×** (bootstrap 95 % CI 0.25–1.15×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = -0.33.
- **Unsafe acceptances: 0**.
- Lost (DiscoPoP alone reaches a parallel program, the agent's trial does not): tsvc/s000 rep1.

## Class D — true recurrences (must-decline control)

- 4 benchmarks, 12 agent trials. Verdicts: **neither** 12.
- Trials reaching a verified parallel program — agent: 0 of 12 (0 %, 95 % CI 0–24 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 0 of 12 (0 %, 95 % CI 0–24 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 0 of 4.
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×** (bootstrap 95 % CI 1.00–1.00×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 105 agent trials, 196 model calls (0 failed).
- Profile refreshes after a kept rewrite: 117 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 117 time(s).
- Explorer stalls (killed at the limit, draw repeated): 30 inside agents, 26 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 2464–7580.

