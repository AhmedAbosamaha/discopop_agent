# The main comparison in numbers

Runs: e1c_r_2. Agent arm: `['bare_llm', 'default']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 5 benchmarks, 50 agent trials. Verdicts: **gained** 25, **gained-not-faster** 4, **worse** 5, **neither** 12, **unsafe** 3, **invalid** 1.
- Trials reaching a verified parallel program — agent: 34 of 49 (69 %, 95 % CI 55–80 %); DiscoPoP alone: 0 of 25 (0 %, 95 % CI 0–13 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 25 of 49 (51 %, 95 % CI 37–64 %); DiscoPoP alone: 0 of 25 (0 %, 95 % CI 0–13 %).
- Benchmarks with at least one gain: 5 of 5 (tsvc/s212, tsvc/s241, tsvc/s243, tsvc/s244, tsvc/s252).
- Speed, paired by benchmark (5 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.14×** (bootstrap 95 % CI 1.00–2.06×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.60.
- **Unsafe acceptances: 3** — tsvc/s241 rep2, tsvc/s241 rep4, tsvc/s244 rep2.
- Missing or withheld (1): tsvc/s252 rep2: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 50 agent trials, 55 model calls (0 failed).
- Profile refreshes after a kept rewrite: 26 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 26 time(s).
- Explorer stalls (killed at the limit, draw repeated): 6 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–16.

