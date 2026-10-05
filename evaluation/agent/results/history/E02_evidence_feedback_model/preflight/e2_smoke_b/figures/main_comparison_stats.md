# The main comparison in numbers

Runs: e2_smoke_b. Agent arm: `['compiler_remarks_b1', 'default', 'full_b1', 'hotspot_only_b1', 'no_evidence', 'no_evidence_b1']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 1 benchmarks, 6 agent trials. Verdicts: **gained** 3, **neither** 3.
- Trials reaching a verified parallel program — agent: 3 of 6 (50 %, 95 % CI 19–81 %); DiscoPoP alone: 0 of 1 (0 %, 95 % CI 0–79 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 3 of 6 (50 %, 95 % CI 19–81 %); DiscoPoP alone: 0 of 1 (0 %, 95 % CI 0–79 %).
- Benchmarks with at least one gain: 1 of 1 (tsvc/s281).
- Speed, paired by benchmark (1 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.94×**; fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +1.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 6 agent trials, 8 model calls (0 failed).
- Profile refreshes after a kept rewrite: 6 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 6 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 7 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3953–6266.

