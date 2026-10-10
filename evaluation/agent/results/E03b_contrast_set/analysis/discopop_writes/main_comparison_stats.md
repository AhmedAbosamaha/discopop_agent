# The main comparison in numbers

Runs: e3b_1, e3b_2, e3b_3, e3b_4, e3b_bare_haiku. Agent arm: `default_v5`; baseline: `discopop_gate_v5` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 6 benchmarks, 30 agent trials. Verdicts: **gained** 24, **gained-not-faster** 1, **neither** 5.
- Trials reaching a verified parallel program — agent: 25 of 30 (83 %, 95 % CI 66–93 %); DiscoPoP alone: 0 of 30 (0 %, 95 % CI 0–11 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 24 of 30 (80 %, 95 % CI 63–90 %); DiscoPoP alone: 0 of 30 (0 %, 95 % CI 0–11 %).
- Benchmarks with at least one gain: 6 of 6 (tsvc_c4/s3113, tsvc_c4/s314, tsvc_c4/s315, tsvc_c4/s316, tsvc_c4/s318, tsvc_c4/s319).
- Speed, paired by benchmark (6 timeable benchmarks): median agent ÷ DiscoPoP alone = **2.32×** (bootstrap 95 % CI 1.10–3.78×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.83.
- **Unsafe acceptances: 0**.

## Class A — parallel as written (no-harm control)

- 1 benchmarks, 5 agent trials. Verdicts: **equal** 5.
- Trials reaching a verified parallel program — agent: 5 of 5 (100 %, 95 % CI 57–100 %); DiscoPoP alone: 5 of 5 (100 %, 95 % CI 57–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 5 of 5 (100 %, 95 % CI 57–100 %); DiscoPoP alone: 5 of 5 (100 %, 95 % CI 57–100 %).
- Benchmarks with at least one gain: 0 of 1.
- Speed, paired by benchmark (1 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×**; fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = -1.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 35 agent trials, 179 model calls (0 failed).
- Profile refreshes after a kept rewrite: 144 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 144 time(s).
- Explorer stalls (killed at the limit, draw repeated): 0 inside agents, 0 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–18.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `default_v5`, model alone `bare_llm_v4`, DiscoPoP alone `discopop_gate_v5`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

### Class R — 6 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 30 (0 %, 95 % CI 0–11 %) | 25 of 30 (83 %, 95 % CI 66–93 %) | 28 of 30 (93 %, 95 % CI 79–98 %) |
| FASTER (≥ 1.1×) | 0 of 30 (0 %, 95 % CI 0–11 %) | 24 of 30 (80 %, 95 % CI 63–90 %) | 28 of 30 (93 %, 95 % CI 79–98 %) |
| FASTER and race-free | 0 of 30 (0 %, 95 % CI 0–11 %) | 24 of 30 (80 %, 95 % CI 63–90 %) | 27 of 30 (90 %, 95 % CI 74–97 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **2** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 0 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 1 |
| shipped a program that does not compile | 0 | 0 | 0 |
| **unusable programs** (any of the four above) | **0** | **0** | **3** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | — | 3.27× | 8.67× |

- Unusable programs shipped by model alone (3): tsvc_c4/s315 rep2: racy; tsvc_c4/s316 rep5: BROKEN; tsvc_c4/s318 rep3: BROKEN.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 3, the model-only arm fewer on 0, tied on 3; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 2, tied on 4; fewer than 6 non-zero pairs: no test.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 2, tied on 4; fewer than 6 non-zero pairs: no test.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc_c4/s3113` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c4/s314` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |
| `tsvc_c4/s315` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 5 | 5 / 4 / 0 / 1 of 5 |
| `tsvc_c4/s316` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 5 | 4 / 4 / 1 / 1 of 5 |
| `tsvc_c4/s318` | 0 / 0 / 0 / 0 of 5 | 4 / 4 / 0 / 0 of 5 | 4 / 4 / 1 / 1 of 5 |
| `tsvc_c4/s319` | 0 / 0 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |

### Class A (no-harm control) — 1 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 5 of 5 (100 %, 95 % CI 57–100 %) | 5 of 5 (100 %, 95 % CI 57–100 %) | 5 of 5 (100 %, 95 % CI 57–100 %) |
| FASTER (≥ 1.1×) | 5 of 5 (100 %, 95 % CI 57–100 %) | 5 of 5 (100 %, 95 % CI 57–100 %) | 5 of 5 (100 %, 95 % CI 57–100 %) |
| FASTER and race-free | 5 of 5 (100 %, 95 % CI 57–100 %) | 5 of 5 (100 %, 95 % CI 57–100 %) | 5 of 5 (100 %, 95 % CI 57–100 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **0** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 0 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 |
| shipped a program that does not compile | 0 | 0 | 0 |
| **unusable programs** (any of the four above) | **0** | **0** | **0** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | 8.54× | 8.52× | 8.48× |

- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 0, the model-only arm fewer on 0, tied on 1; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 0, tied on 1; fewer than 6 non-zero pairs: no test.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 0, tied on 1; fewer than 6 non-zero pairs: no test.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc_c4/s311` | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 | 5 / 5 / 0 / 0 of 5 |

