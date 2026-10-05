# E1-bare in numbers — the model alone (`bare_llm`) and the agent (`default`), each against DiscoPoP alone

Two runs of `agent/tools/main_comparison_stats.py` on the same four runs, one per arm (the tool pools every non-baseline arm unless `--arm` is given, and a pooled figure would mean nothing here). The `default` half is byte-for-byte E1's own primary-set read-out (`E01_main_comparison/analysis/tsvc/`). Every BROKEN of the bare arm is named by cause in `README.md`.

---

# `bare_llm` — the same model, alone

Runs: e1_bare_a, e1_bare_b, e1_r_a, e1_r_b. Agent arm: `bare_llm`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested. **Restricted to the `tsvc` suite** — the primary set of D30; the registered set's numbers stand beside it, never behind it.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 90 agent trials. Verdicts: **gained** 58, **gained-not-faster** 1, **worse** 12, **unsafe** 17, **invalid** 2.
- Trials reaching a verified parallel program — agent: 71 of 88 (81 %, 95 % CI 71–88 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 58 of 88 (66 %, 95 % CI 56–75 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 16 of 18 (tsvc/s121, tsvc/s1213, tsvc/s127, tsvc/s212, tsvc/s241, tsvc/s243, tsvc/s244, tsvc/s252, tsvc/s254, tsvc/s255, tsvc/s281, tsvc/s291, tsvc/s292, tsvc/s293, tsvc/s331, tsvc/s341).
- Speed, paired by benchmark (17 timeable benchmarks): median agent ÷ DiscoPoP alone = **2.41×** (bootstrap 95 % CI 1.39–3.84×); Wilcoxon signed-rank, one-sided: W = 145, p = 0.0001907, 17 non-zero pairs; Cliff's δ = +0.65.
- **Unsafe acceptances: 17** — tsvc/s112 rep1, tsvc/s112 rep3, tsvc/s1213 rep2, tsvc/s1213 rep4, tsvc/s211 rep1, tsvc/s211 rep2, tsvc/s211 rep3, tsvc/s211 rep4, tsvc/s211 rep5, tsvc/s212 rep5, tsvc/s241 rep1, tsvc/s241 rep2, tsvc/s241 rep3, tsvc/s243 rep3, tsvc/s244 rep4, tsvc/s252 rep3, tsvc/s341 rep2.
- Missing or withheld (2): tsvc/s243 rep4: invalid (SCAFFOLD_MODIFIED); tsvc/s244 rep2: invalid (VERIFY_FAILED).

## What actually happened inside the trials

- 90 agent trials, 90 model calls (0 failed).
- Profile refreshes after a kept rewrite: 0 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 0 time(s).
- Explorer stalls (killed at the limit, draw repeated): 26 inside agents, 55 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 2464–7580.


---

# `default` — DiscoPoP + agent (E1)

Runs: e1_bare_a, e1_bare_b, e1_r_a, e1_r_b. Agent arm: `default`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested. **Restricted to the `tsvc` suite** — the primary set of D30; the registered set's numbers stand beside it, never behind it.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 90 agent trials. Verdicts: **gained** 44, **gained-not-faster** 2, **neither** 44.
- Trials reaching a verified parallel program — agent: 46 of 90 (51 %, 95 % CI 41–61 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 44 of 90 (49 %, 95 % CI 39–59 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 14 of 18 (tsvc/s112, tsvc/s1213, tsvc/s127, tsvc/s211, tsvc/s212, tsvc/s241, tsvc/s243, tsvc/s244, tsvc/s252, tsvc/s254, tsvc/s255, tsvc/s291, tsvc/s292, tsvc/s293).
- Speed, paired by benchmark (18 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.08×** (bootstrap 95 % CI 1.00–2.35×); Wilcoxon signed-rank, one-sided: W = 45, p = 0.001953, 9 non-zero pairs; Cliff's δ = +0.50.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 90 agent trials, 125 model calls (0 failed).
- Profile refreshes after a kept rewrite: 102 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 102 time(s).
- Explorer stalls (killed at the limit, draw repeated): 26 inside agents, 55 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 2464–7580.

