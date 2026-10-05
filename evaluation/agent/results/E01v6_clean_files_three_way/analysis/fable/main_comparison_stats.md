# The main comparison in numbers

Runs: e1v6_a, e1v6_bare_fable, e1v6_d, e1v6_r_1, e1v6_r_2, e1v6_r_3, e1v6_r_4. Agent arm: `default_v4`; baseline: `discopop_gate_v4` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 18 benchmarks, 90 agent trials. Verdicts: **gained** 73, **gained-not-faster** 9, **neither** 8.
- Trials reaching a verified parallel program — agent: 82 of 90 (91 %, 95 % CI 83–95 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 73 of 90 (81 %, 95 % CI 72–88 %); DiscoPoP alone: 0 of 90 (0 %, 95 % CI 0–4 %).
- Benchmarks with at least one gain: 18 of 18 (tsvc_c2/s112, tsvc_c2/s121, tsvc_c2/s1213, tsvc_c2/s127, tsvc_c2/s211, tsvc_c2/s212, tsvc_c2/s241, tsvc_c2/s243, tsvc_c2/s244, tsvc_c2/s252, tsvc_c2/s254, tsvc_c2/s255, tsvc_c2/s281, tsvc_c2/s291, tsvc_c2/s292, tsvc_c2/s293, tsvc_c2/s331, tsvc_c2/s341).
- Speed, paired by benchmark (18 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.70×** (bootstrap 95 % CI 1.18–2.93×); Wilcoxon signed-rank, one-sided: W = 136, p = 1.526e-05, 16 non-zero pairs; Cliff's δ = +0.89.
- **Unsafe acceptances: 0**.

## Class A — parallel as written (no-harm control)

- 3 benchmarks, 3 agent trials. Verdicts: **better** 2, **worse** 1.
- Trials reaching a verified parallel program — agent: 3 of 3 (100 %, 95 % CI 44–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 3 of 3 (100 %, 95 % CI 44–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Benchmarks with at least one gain: 0 of 3.
- Speed, paired by benchmark (3 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.16×** (bootstrap 95 % CI 0.78–35.18×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.11.
- **Unsafe acceptances: 0**.

## Class D — true recurrences (must-decline control)

- 4 benchmarks, 12 agent trials. Verdicts: **neither** 12.
- Trials reaching a verified parallel program — agent: 0 of 12 (0 %, 95 % CI 0–24 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 0 of 12 (0 %, 95 % CI 0–24 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 0 of 4.
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×** (bootstrap 95 % CI 1.00–1.00×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 105 agent trials, 389 model calls (54 failed).
- Profile refreshes after a kept rewrite: 203 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 203 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–14.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `default_v4`, model alone `bare_llm_v4`, DiscoPoP alone `discopop_gate_v4`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

### Class R — 18 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 90 (0 %, 95 % CI 0–4 %) | 82 of 90 (91 %, 95 % CI 83–95 %) | 90 of 90 (100 %, 95 % CI 96–100 %) |
| FASTER (≥ 1.1×) | 0 of 90 (0 %, 95 % CI 0–4 %) | 73 of 90 (81 %, 95 % CI 72–88 %) | 89 of 90 (99 %, 95 % CI 94–100 %) |
| FASTER and race-free | 0 of 90 (0 %, 95 % CI 0–4 %) | 73 of 90 (81 %, 95 % CI 72–88 %) | 89 of 90 (99 %, 95 % CI 94–100 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **0** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 1 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 |
| shipped a program that does not compile | 0 | 0 | 0 |
| **unusable programs** (any of the four above) | **0** | **0** | **1** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | — | 2.47× | 3.08× |

- Unusable programs shipped by model alone (1): tsvc_c2/s121 rep4: slower.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 1, the model-only arm fewer on 0, tied on 17; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 6, tied on 12; p (two-sided) = 0.0312, p (agent ahead) = 1.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 6, tied on 12; p (two-sided) = 0.0312, p (agent ahead) = 1.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc_c2/s112` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s121` | 0 / 0 / 0 / 0 of 5 | 4 / 4 / 0 / 0 of 5 | 4 / 4 / 0 / 1 of 5 |
| `tsvc_c2/s1213` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s127` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s211` | 0 / 0 / 0 / 0 of 5 | 4 / 4 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s212` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s241` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s243` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s244` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s252` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s254` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s255` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s281` | 0 / 0 / 0 / 0 of 5 | 1 / 1 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s291` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s292` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s293` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s331` | 0 / 0 / 0 / 0 of 5 | 1 / 1 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c2/s341` | 0 / 0 / 0 / 0 of 5 | 4 / 4 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |

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
| median speedup of the FASTER trials | 3.67× | 3.96× | 3.59× |

- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 0, the model-only arm fewer on 0, tied on 3; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 0, tied on 3; fewer than 6 non-zero pairs: no test.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 0, tied on 3; fewer than 6 non-zero pairs: no test.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc_c2/s000` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 |
| `tsvc_c2/s313` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 |
| `tsvc_c2/vpvtv` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 |

### Class D (must-decline control) — 4 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 12 (0 %, 95 % CI 0–24 %) | 10 of 12 (83 %, 95 % CI 55–95 %) |
| FASTER (≥ 1.1×) | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 12 (0 %, 95 % CI 0–24 %) | 6 of 12 (50 %, 95 % CI 25–75 %) |
| FASTER and race-free | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 12 (0 %, 95 % CI 0–24 %) | 3 of 12 (25 %, 95 % CI 9–53 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **0** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 3 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 (+3 not judgeable) |
| shipped a program that does not compile | 0 | 0 | 0 |
| **unusable programs** (any of the four above) | **0** | **0** | **3** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | — | — | 4.04× |

- Unusable programs shipped by model alone (3): tsvc_c2/s323 rep1: slower; tsvc_c2/s323 rep2: slower; tsvc_c2/s323 rep3: slower.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 1, the model-only arm fewer on 0, tied on 3; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 2, tied on 2; fewer than 6 non-zero pairs: no test.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 1, tied on 3; fewer than 6 non-zero pairs: no test.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc_c2/s3112` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 3 / 0 / 0 / 0 of 3 |
| `tsvc_c2/s321` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 3 / 3 / 0 / 0 of 3 |
| `tsvc_c2/s322` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 |
| `tsvc_c2/s323` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 3 of 3 |

