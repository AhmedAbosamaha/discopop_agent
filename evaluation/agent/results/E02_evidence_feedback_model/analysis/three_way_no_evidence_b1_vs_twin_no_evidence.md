# The main comparison in numbers

Runs: e1c_r_1, e1c_r_2, e1c_r_3, e1c_r_4, e2c_ab_1, e2c_ab_2, e2c_ab_3, e2c_ab_4. Agent arm: `no_evidence_b1`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 90 agent trials. Verdicts: **gained** 51, **gained-not-faster** 7, **neither** 32.
- Trials reaching a verified parallel program — agent: 58 of 90 (64 %, 95 % CI 54–74 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 51 of 90 (57 %, 95 % CI 46–66 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 15 of 18 (tsvc/s112, tsvc/s121, tsvc/s1213, tsvc/s127, tsvc/s211, tsvc/s212, tsvc/s243, tsvc/s244, tsvc/s252, tsvc/s254, tsvc/s255, tsvc/s281, tsvc/s291, tsvc/s292, tsvc/s293).
- Speed, paired by benchmark (18 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.11×** (bootstrap 95 % CI 1.00–2.77×); Wilcoxon signed-rank, one-sided: W = 78, p = 0.0002441, 12 non-zero pairs; Cliff's δ = +0.67.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 90 agent trials, 111 model calls (0 failed).
- Profile refreshes after a kept rewrite: 86 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 86 time(s).
- Explorer stalls (killed at the limit, draw repeated): 134 inside agents, 180 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 2–19.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `no_evidence_b1`, model alone `twin_no_evidence`, DiscoPoP alone `discopop_gate`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

### Class R — 18 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 90 (0 %, 95 % CI 0–4 %) | 58 of 90 (64 %, 95 % CI 54–74 %) | 24 of 90 (27 %, 95 % CI 19–37 %) |
| FASTER (≥ 1.1×) | 0 of 90 (0 %, 95 % CI 0–4 %) | 51 of 90 (57 %, 95 % CI 46–66 %) | 17 of 90 (19 %, 95 % CI 12–28 %) |
| FASTER and race-free | 0 of 90 (0 %, 95 % CI 0–4 %) | 51 of 90 (57 %, 95 % CI 46–66 %) | 17 of 90 (19 %, 95 % CI 12–28 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **64** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 6 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 |
| shipped a program that does not compile | 0 | 0 | 1 |
| **unusable programs** (any of the four above) | **0** | **0** | **71** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | — | 2.76× | 1.84× |

- Unusable programs shipped by model alone (71): tsvc/s112 rep1: did not compile; tsvc/s112 rep2: BROKEN; tsvc/s112 rep5: BROKEN; tsvc/s121 rep1: BROKEN; tsvc/s121 rep2: BROKEN; tsvc/s121 rep4: BROKEN; tsvc/s1213 rep5: BROKEN; tsvc/s127 rep1: BROKEN; tsvc/s127 rep2: BROKEN; tsvc/s127 rep3: BROKEN; tsvc/s127 rep4: BROKEN; tsvc/s127 rep5: BROKEN; tsvc/s211 rep1: BROKEN; tsvc/s211 rep2: BROKEN; tsvc/s211 rep3: BROKEN; tsvc/s211 rep4: BROKEN; tsvc/s211 rep5: BROKEN; tsvc/s212 rep1: slower; tsvc/s212 rep2: slower; tsvc/s212 rep5: BROKEN; tsvc/s241 rep1: slower; tsvc/s241 rep4: BROKEN; tsvc/s241 rep5: slower; tsvc/s243 rep1: BROKEN; tsvc/s243 rep2: slower; tsvc/s243 rep4: BROKEN; tsvc/s244 rep2: BROKEN; tsvc/s244 rep5: BROKEN; tsvc/s252 rep1: BROKEN; tsvc/s252 rep2: BROKEN; tsvc/s252 rep3: BROKEN; tsvc/s252 rep4: BROKEN; tsvc/s252 rep5: BROKEN; tsvc/s254 rep1: BROKEN; tsvc/s254 rep2: BROKEN; tsvc/s254 rep3: BROKEN; tsvc/s254 rep4: BROKEN; tsvc/s254 rep5: BROKEN; tsvc/s255 rep1: BROKEN; tsvc/s255 rep2: BROKEN; tsvc/s255 rep3: BROKEN; tsvc/s255 rep4: BROKEN; tsvc/s255 rep5: BROKEN; tsvc/s281 rep1: BROKEN; tsvc/s281 rep3: BROKEN; tsvc/s281 rep4: BROKEN; tsvc/s291 rep1: BROKEN; tsvc/s291 rep2: BROKEN; tsvc/s291 rep3: BROKEN; tsvc/s291 rep4: BROKEN; tsvc/s291 rep5: BROKEN; tsvc/s292 rep1: BROKEN; tsvc/s292 rep2: BROKEN; tsvc/s292 rep3: BROKEN; tsvc/s292 rep4: BROKEN; tsvc/s292 rep5: BROKEN; tsvc/s293 rep1: BROKEN; tsvc/s293 rep2: BROKEN; tsvc/s293 rep3: BROKEN; tsvc/s293 rep4: BROKEN; tsvc/s293 rep5: BROKEN; tsvc/s331 rep1: BROKEN; tsvc/s331 rep2: slower; tsvc/s331 rep3: BROKEN; tsvc/s331 rep4: BROKEN; tsvc/s331 rep5: BROKEN; tsvc/s341 rep1: BROKEN; tsvc/s341 rep2: BROKEN; tsvc/s341 rep3: BROKEN; tsvc/s341 rep4: BROKEN; tsvc/s341 rep5: BROKEN.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 18, the model-only arm fewer on 0, tied on 0; p (two-sided) = 0.000136, p (agent fewer) = 6.81e-05. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 10, model alone ahead on 3, tied on 5; p (two-sided) = 0.00659, p (agent ahead) = 0.0033.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 10, model alone ahead on 3, tied on 5; p (two-sided) = 0.00659, p (agent ahead) = 0.0033.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc/s112` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 2 / 2 / 2 / 3 of 5 |
| `tsvc/s121` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 2 / 2 / 3 / 3 of 5 |
| `tsvc/s1213` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 5 | 4 / 4 / 1 / 1 of 5 |
| `tsvc/s127` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |
| `tsvc/s211` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |
| `tsvc/s212` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 2 / 2 / 1 / 3 of 5 |
| `tsvc/s241` | 0 / 0 / 0 / 0 of 5 | 0 / 0 / 0 / 0 of 5 | 1 / 1 / 1 / 3 of 5 |
| `tsvc/s243` | 0 / 0 / 0 / 0 of 5 | 1 / 1 / 0 / 0 of 5 | 2 / 2 / 2 / 3 of 5 |
| `tsvc/s244` | 0 / 0 / 0 / 0 of 5 | 4 / 4 / 0 / 0 of 5 | 3 / 3 / 2 / 2 of 5 |
| `tsvc/s252` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |
| `tsvc/s254` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |
| `tsvc/s255` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |
| `tsvc/s281` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 1 / 1 / 3 / 3 of 5 |
| `tsvc/s291` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |
| `tsvc/s292` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |
| `tsvc/s293` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |
| `tsvc/s331` | 0 / 0 / 0 / 0 of 5 | 0 / 0 / 0 / 0 of 5 | 0 / 0 / 4 / 5 of 5 |
| `tsvc/s341` | 0 / 0 / 0 / 0 of 5 | 0 / 0 / 0 / 0 of 5 | 0 / 0 / 5 / 5 of 5 |

