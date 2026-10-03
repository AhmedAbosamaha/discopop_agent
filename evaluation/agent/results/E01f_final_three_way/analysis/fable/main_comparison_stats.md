# The main comparison in numbers

Runs: e1f_a, e1f_bare_fable, e1f_d, e1f_fix103_redo2, e1f_r_1, e1f_r_2, e1f_r_3, e1f_r_4. Agent arm: `default_v3`; baseline: `discopop_gate_v3` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 90 agent trials. Verdicts: **gained** 65, **gained-not-faster** 17, **neither** 8.
- Trials reaching a verified parallel program — agent: 82 of 90 (91 %, 95 % CI 83–95 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 65 of 90 (72 %, 95 % CI 62–80 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 18 of 18 (tsvc_b1/s112, tsvc_b1/s121, tsvc_b1/s1213, tsvc_b1/s127, tsvc_b1/s211, tsvc_b1/s212, tsvc_b1/s241, tsvc_b1/s243, tsvc_b1/s244, tsvc_b1/s252, tsvc_b1/s254, tsvc_b1/s255, tsvc_b1/s281, tsvc_b1/s291, tsvc_b1/s292, tsvc_b1/s293, tsvc_b1/s331, tsvc_b1/s341).
- Speed, paired by benchmark (18 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.85×** (bootstrap 95 % CI 1.12–2.70×); Wilcoxon signed-rank, one-sided: W = 135, p = 3.052e-05, 16 non-zero pairs; Cliff's δ = +0.78.
- **Unsafe acceptances: 0**.

## Class A — parallel as written (no-harm control)

- 3 benchmarks, 3 agent trials. Verdicts: **equal** 3.
- Trials reaching a verified parallel program — agent: 3 of 3 (100 %, 95 % CI 44–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 3 of 3 (100 %, 95 % CI 44–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Benchmarks with at least one gain: 0 of 3.
- Speed, paired by benchmark (3 timeable benchmarks): median agent ÷ DiscoPoP alone = **0.97×** (bootstrap 95 % CI 0.92–1.00×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = -0.33.
- **Unsafe acceptances: 0**.

## Class D — true recurrences (must-decline control)

- 4 benchmarks, 12 agent trials. Verdicts: **neither** 12.
- Trials reaching a verified parallel program — agent: 0 of 12 (0 %, 95 % CI 0–24 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 0 of 12 (0 %, 95 % CI 0–24 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 0 of 4.
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×** (bootstrap 95 % CI 1.00–1.00×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 105 agent trials, 358 model calls (0 failed).
- Profile refreshes after a kept rewrite: 267 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 267 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–17.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `default_v3`, model alone `bare_llm_v3`, DiscoPoP alone `discopop_gate_v3`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

### Class R — 18 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 90 (0 %, 95 % CI 0–4 %) | 82 of 90 (91 %, 95 % CI 83–95 %) | 90 of 90 (100 %, 95 % CI 96–100 %) |
| FASTER (≥ 1.1×) | 0 of 90 (0 %, 95 % CI 0–4 %) | 65 of 90 (72 %, 95 % CI 62–80 %) | 90 of 90 (100 %, 95 % CI 96–100 %) |
| FASTER and race-free | 0 of 90 (0 %, 95 % CI 0–4 %) | 65 of 90 (72 %, 95 % CI 62–80 %) | 90 of 90 (100 %, 95 % CI 96–100 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **0** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 0 |
| racy (race check: TSan or the schedule matrix) | 0 | 1 | 0 |
| shipped a program that does not compile | 0 | 0 | 0 |
| **unusable programs** (any of the four above) | **0** | **1** | **0** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | — | 2.47× | 3.04× |

- Unusable programs shipped by DiscoPoP + agent (1): tsvc_b1/s341 rep1: racy.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 0, the model-only arm fewer on 1, tied on 17; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 8, tied on 10; p (two-sided) = 0.00781, p (agent ahead) = 1.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 8, tied on 10; p (two-sided) = 0.00781, p (agent ahead) = 1.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc_b1/s112` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s121` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s1213` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s127` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s211` | 0 / 0 / 0 / 0 of 5 | 4 / 4 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s212` | 0 / 0 / 0 / 0 of 5 | 1 / 1 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s241` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s243` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s244` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s252` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s254` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s255` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s281` | 0 / 0 / 0 / 0 of 5 | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s291` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s292` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s293` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s331` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_b1/s341` | 0 / 0 / 0 / 0 of 5 | 0 / 0 / 0 / 1 of 5 | 5 / 5 / 0 / 0 of 5 |

### Class A (no-harm control) — 3 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) |
| FASTER (≥ 1.1×) | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) |
| FASTER and race-free | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **0** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 0 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 |
| shipped a program that does not compile | 0 | 0 | 0 |
| **unusable programs** (any of the four above) | **0** | **0** | **0** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | 3.95× | 3.62× | 3.48× |

- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 0, the model-only arm fewer on 0, tied on 3; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 0, tied on 3; fewer than 6 non-zero pairs: no test.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 0, tied on 3; fewer than 6 non-zero pairs: no test.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc_b1/s000` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 |
| `tsvc_b1/s313` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 |
| `tsvc_b1/vpvtv` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 |

### Class D (must-decline control) — 4 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 12 (0 %, 95 % CI 0–24 %) | 12 of 12 (100 %, 95 % CI 76–100 %) |
| FASTER (≥ 1.1×) | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 12 (0 %, 95 % CI 0–24 %) | 10 of 12 (83 %, 95 % CI 55–95 %) |
| FASTER and race-free | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 12 (0 %, 95 % CI 0–24 %) | 6 of 12 (50 %, 95 % CI 25–75 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **0** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 2 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 (+4 not judgeable) |
| shipped a program that does not compile | 0 | 0 | 0 |
| **unusable programs** (any of the four above) | **0** | **0** | **2** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | — | — | 3.48× |

- Unusable programs shipped by model alone (2): tsvc_b1/s323 rep1: slower; tsvc_b1/s323 rep2: slower.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 1, the model-only arm fewer on 0, tied on 3; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 4, tied on 0; fewer than 6 non-zero pairs: no test.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 2, tied on 2; fewer than 6 non-zero pairs: no test.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc_b1/s3112` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 3 / 0 / 0 / 0 of 3 |
| `tsvc_b1/s321` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 3 / 3 / 0 / 0 of 3 |
| `tsvc_b1/s322` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 3 / 3 / 0 / 0 of 3 |
| `tsvc_b1/s323` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 1 / 0 / 0 / 2 of 3 |

