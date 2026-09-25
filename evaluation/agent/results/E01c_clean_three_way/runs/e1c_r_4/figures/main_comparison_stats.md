# The main comparison in numbers

Runs: e1c_r_4. Agent arm: `['bare_llm', 'default']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 4 benchmarks, 40 agent trials. Verdicts: **gained** 22, **worse** 6, **neither** 10, **unsafe** 1, **invalid** 1.
- Trials reaching a verified parallel program — agent: 28 of 39 (72 %, 95 % CI 56–83 %); DiscoPoP alone: 0 of 20 (0 %, 95 % CI 0–16 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 22 of 39 (56 %, 95 % CI 41–71 %); DiscoPoP alone: 0 of 20 (0 %, 95 % CI 0–16 %).
- Benchmarks with at least one gain: 3 of 4 (tsvc/s292, tsvc/s293, tsvc/s331).
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.80×** (bootstrap 95 % CI 1.00–2.87×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.50.
- **Unsafe acceptances: 1** — tsvc/s341 rep5.
- Missing or withheld (1): tsvc/s331 rep5: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 40 agent trials, 41 model calls (0 failed).
- Profile refreshes after a kept rewrite: 20 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 20 time(s).
- Explorer stalls (killed at the limit, draw repeated): 9 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 5–17.

