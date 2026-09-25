# The main comparison in numbers

Runs: e1c_d. Agent arm: `['bare_llm', 'default']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class D — true recurrences (must-decline control)

- 4 benchmarks, 24 agent trials. Verdicts: **gained-not-faster** 2, **worse** 1, **neither** 13, **unsafe** 6, **invalid** 2.
- Trials reaching a verified parallel program — agent: 3 of 22 (14 %, 95 % CI 5–33 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 0 of 22 (0 %, 95 % CI 0–15 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 2 of 4 (tsvc/s321, tsvc/s323).
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×** (bootstrap 95 % CI 1.00–1.00×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.00.
- **Unsafe acceptances: 6** — tsvc/s321 rep1, tsvc/s321 rep2, tsvc/s322 rep1, tsvc/s322 rep2, tsvc/s322 rep3, tsvc/s323 rep1.
- Missing or withheld (2): tsvc/s3112 rep2: invalid (VERIFY_FAILED); tsvc/s323 rep2: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 24 agent trials, 70 model calls (0 failed).
- Profile refreshes after a kept rewrite: 12 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 12 time(s).
- Explorer stalls (killed at the limit, draw repeated): 2 inside agents, 36 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–22.

