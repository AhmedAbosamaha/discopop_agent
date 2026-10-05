# The main comparison in numbers

Runs: e1c_a. Agent arm: `['bare_llm', 'default']`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class A — parallel as written (no-harm control)

- 3 benchmarks, 6 agent trials. Verdicts: **equal** 4, **invalid** 2.
- Trials reaching a verified parallel program — agent: 4 of 4 (100 %, 95 % CI 51–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 4 of 4 (100 %, 95 % CI 51–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Benchmarks with at least one gain: 0 of 3.
- Speed, paired by benchmark (3 timeable benchmarks): median agent ÷ DiscoPoP alone = **0.99×** (bootstrap 95 % CI 0.99–1.06×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = -0.11.
- **Unsafe acceptances: 0**.
- Missing or withheld (2): tsvc/s313 rep1: invalid (SCAFFOLD_MODIFIED); tsvc/vpvtv rep1: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 6 agent trials, 6 model calls (0 failed).
- Profile refreshes after a kept rewrite: 3 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 3 time(s).
- Explorer stalls (killed at the limit, draw repeated): 2 inside agents, 6 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 5–10.

