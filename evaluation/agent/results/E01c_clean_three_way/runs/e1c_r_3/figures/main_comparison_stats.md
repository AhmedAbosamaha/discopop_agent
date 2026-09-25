# The main comparison in numbers

Runs: e1c_r_3. Agent arm: `['bare_llm', 'default']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 4 benchmarks, 40 agent trials. Verdicts: **gained** 31, **gained-not-faster** 3, **neither** 1, **unsafe** 2, **invalid** 3.
- Trials reaching a verified parallel program — agent: 34 of 37 (92 %, 95 % CI 79–97 %); DiscoPoP alone: 0 of 20 (0 %, 95 % CI 0–16 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 31 of 37 (84 %, 95 % CI 69–92 %); DiscoPoP alone: 0 of 20 (0 %, 95 % CI 0–16 %).
- Benchmarks with at least one gain: 4 of 4 (tsvc/s254, tsvc/s255, tsvc/s281, tsvc/s291).
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **2.73×** (bootstrap 95 % CI 1.09–3.44×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +1.00.
- **Unsafe acceptances: 2** — tsvc/s281 rep2, tsvc/s281 rep3.
- Missing or withheld (3): tsvc/s254 rep5: invalid (VERIFY_FAILED); tsvc/s255 rep5: invalid (VERIFY_FAILED); tsvc/s281 rep4: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 40 agent trials, 41 model calls (0 failed).
- Profile refreshes after a kept rewrite: 20 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 20 time(s).
- Explorer stalls (killed at the limit, draw repeated): 5 inside agents, 30 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 4–14.

