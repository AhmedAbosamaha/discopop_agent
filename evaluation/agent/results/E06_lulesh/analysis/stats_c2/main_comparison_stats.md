# The main comparison in numbers

Runs: e6c_bare, e6x_1, e6x_2, e6x_3. Agent arm: `llm_pragmas_v5_exact`; baseline: `discopop_gate_v5` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Unclassified

- 1 benchmarks, 5 agent trials. Verdicts: **better** 5.
- Trials reaching a verified parallel program — agent: 5 of 5 (100 %, 95 % CI 57–100 %); DiscoPoP alone: 5 of 5 (100 %, 95 % CI 57–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 5 of 5 (100 %, 95 % CI 57–100 %); DiscoPoP alone: 5 of 5 (100 %, 95 % CI 57–100 %).
- Benchmarks with at least one gain: 0 of 1.
- Speed, paired by benchmark (1 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.33×**; fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +1.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 5 agent trials, 199 model calls (0 failed).
- Profile refreshes after a kept rewrite: 90 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 90 time(s).
- Explorer stalls (killed at the limit, draw repeated): 49 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–19.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `llm_pragmas_v5_exact`, model alone `bare_llm_v4`, DiscoPoP alone `discopop_gate_v5`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

