# The main comparison in numbers

Runs: e1c_r_1, e1c_r_2, e1c_r_3, e1c_r_4, e2c_ab_1, e2c_ab_2, e2c_ab_3, e2c_ab_4. Agent arm: `full_b1`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 90 agent trials. Verdicts: **gained** 48, **gained-not-faster** 3, **neither** 39.
- Trials reaching a verified parallel program — agent: 51 of 90 (57 %, 95 % CI 46–66 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 48 of 90 (53 %, 95 % CI 43–63 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 15 of 18 (tsvc/s112, tsvc/s121, tsvc/s1213, tsvc/s127, tsvc/s211, tsvc/s212, tsvc/s241, tsvc/s243, tsvc/s252, tsvc/s254, tsvc/s255, tsvc/s281, tsvc/s291, tsvc/s292, tsvc/s293).
- Speed, paired by benchmark (18 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.08×** (bootstrap 95 % CI 1.00–2.85×); Wilcoxon signed-rank, one-sided: W = 45, p = 0.001953, 9 non-zero pairs; Cliff's δ = +0.50.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 90 agent trials, 114 model calls (0 failed).
- Profile refreshes after a kept rewrite: 89 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 89 time(s).
- Explorer stalls (killed at the limit, draw repeated): 134 inside agents, 180 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 2–19.

## H5b — do extra attempts help more without evidence?

Without evidence: `no_evidence` − `no_evidence_b1`; with evidence: `default` − `full_b1`. Per benchmark, the effect on the rate, then the difference of the two effects; Wilcoxon signed-rank over benchmarks, Cliff's δ between the two sets of effects. Rates over trials with a verdict (parallel, unchanged, changed but not parallel, wrong, not building; a harness edit is left out). Race-free counts a model-only program only where `race_check.py` found it clean.

### Class R — 18 benchmarks

- race-free FASTER (the pre-registered measure): mean effect without evidence +0.04, with evidence +0.03; larger without evidence on 5 benchmarks, with evidence on 5, tied on 8; p (two-sided) = 0.922, p (larger without evidence) = 0.578; Cliff's δ = +0.06.
- FASTER: mean effect without evidence +0.04, with evidence +0.03; larger without evidence on 5 benchmarks, with evidence on 5, tied on 8; p (two-sided) = 0.922, p (larger without evidence) = 0.578; Cliff's δ = +0.06.

| benchmark | `no_evidence` | `no_evidence_b1` | `default` | `full_b1` | effect without evidence | effect with evidence | difference |
|---|---:|---:|---:|---:|---:|---:|---:|
| `tsvc/s112` | 0.60 | 0.40 | 0.00 | 0.20 | +0.20 | -0.20 | +0.40 |
| `tsvc/s121` | 0.60 | 0.40 | 0.40 | 0.40 | +0.20 | +0.00 | +0.20 |
| `tsvc/s1213` | 0.60 | 0.60 | 0.40 | 0.80 | +0.00 | -0.40 | +0.40 |
| `tsvc/s127` | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 |
| `tsvc/s211` | 0.60 | 0.40 | 0.60 | 0.20 | +0.20 | +0.40 | -0.20 |
| `tsvc/s212` | 0.80 | 0.40 | 0.60 | 0.60 | +0.40 | +0.00 | +0.40 |
| `tsvc/s241` | 0.20 | 0.00 | 0.80 | 0.20 | +0.20 | +0.60 | -0.40 |
| `tsvc/s243` | 0.00 | 0.20 | 0.40 | 0.20 | -0.20 | +0.20 | -0.40 |
| `tsvc/s244` | 0.60 | 0.80 | 0.00 | 0.00 | -0.20 | +0.00 | -0.20 |
| `tsvc/s252` | 0.80 | 0.60 | 0.80 | 0.40 | +0.20 | +0.40 | -0.20 |
| `tsvc/s254` | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 |
| `tsvc/s255` | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 |
| `tsvc/s281` | 0.20 | 0.40 | 0.20 | 0.60 | -0.20 | -0.40 | +0.20 |
| `tsvc/s291` | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 |
| `tsvc/s292` | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 |
| `tsvc/s293` | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 |
| `tsvc/s331` | 0.00 | 0.00 | 0.00 | 0.00 | +0.00 | +0.00 | +0.00 |
| `tsvc/s341` | 0.00 | 0.00 | 0.00 | 0.00 | +0.00 | +0.00 | +0.00 |
