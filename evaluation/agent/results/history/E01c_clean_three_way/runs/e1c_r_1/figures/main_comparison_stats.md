# The main comparison in numbers

Runs: e1c_r_1. Agent arm: `['bare_llm', 'default']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 5 benchmarks, 50 agent trials. Verdicts: **gained** 17, **worse** 6, **neither** 14, **unsafe** 10, **invalid** 3.
- Trials reaching a verified parallel program — agent: 23 of 47 (49 %, 95 % CI 35–63 %); DiscoPoP alone: 0 of 25 (0 %, 95 % CI 0–13 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 17 of 47 (36 %, 95 % CI 24–50 %); DiscoPoP alone: 0 of 25 (0 %, 95 % CI 0–13 %).
- Benchmarks with at least one gain: 4 of 5 (tsvc/s121, tsvc/s1213, tsvc/s127, tsvc/s211).
- Speed, paired by benchmark (5 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×** (bootstrap 95 % CI 1.00–3.77×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.40.
- **Unsafe acceptances: 10** — tsvc/s112 rep4, tsvc/s121 rep2, tsvc/s121 rep3, tsvc/s121 rep5, tsvc/s1213 rep2, tsvc/s1213 rep3, tsvc/s1213 rep4, tsvc/s211 rep1, tsvc/s211 rep2, tsvc/s211 rep3.
- Missing or withheld (3): tsvc/s1213 rep1: invalid (VERIFY_FAILED); tsvc/s1213 rep5: invalid (VERIFY_FAILED); tsvc/s211 rep4: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 50 agent trials, 79 model calls (0 failed).
- Profile refreshes after a kept rewrite: 26 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 26 time(s).
- Explorer stalls (killed at the limit, draw repeated): 2 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 2–16.

