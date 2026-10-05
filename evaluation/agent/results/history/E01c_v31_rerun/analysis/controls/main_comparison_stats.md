# The main comparison in numbers

Runs: e1c31_a, e1c31_d, e1c_a, e1c_d. Agent arm: `default`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class A — parallel as written (no-harm control)

- 3 benchmarks, 3 agent trials. Verdicts: **equal** 3.
- Trials reaching a verified parallel program — agent: 3 of 3 (100 %, 95 % CI 44–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 3 of 3 (100 %, 95 % CI 44–100 %); DiscoPoP alone: 3 of 3 (100 %, 95 % CI 44–100 %).
- Benchmarks with at least one gain: 0 of 3.
- Speed, paired by benchmark (3 timeable benchmarks): median agent ÷ DiscoPoP alone = **0.99×** (bootstrap 95 % CI 0.94–0.99×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = -0.33.
- **Unsafe acceptances: 0**.

## Class D — true recurrences (must-decline control)

- 4 benchmarks, 12 agent trials. Verdicts: **neither** 11, **invalid** 1.
- Trials reaching a verified parallel program — agent: 0 of 11 (0 %, 95 % CI 0–26 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 0 of 11 (0 %, 95 % CI 0–26 %); DiscoPoP alone: 0 of 12 (0 %, 95 % CI 0–24 %).
- Benchmarks with at least one gain: 0 of 4.
- Speed, paired by benchmark (4 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.00×** (bootstrap 95 % CI 1.00–1.00×); fewer than 6 non-zero pairs: no test (the smallest n at which p < 0.05 is reachable); Cliff's δ = +0.00.
- **Unsafe acceptances: 0**.
- Missing or withheld (1): tsvc/s3112 rep1: invalid (SCAFFOLD_MODIFIED).

## What actually happened inside the trials

- 15 agent trials, 114 model calls (0 failed).
- Profile refreshes after a kept rewrite: 47 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 47 time(s).
- Explorer stalls (killed at the limit, draw repeated): 13 inside agents, 29 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 3–22.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `default`, model alone `bare_llm`, DiscoPoP alone `discopop_gate`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

### Class A (no-harm control) — 3 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) | 2 of 3 (67 %, 95 % CI 21–94 %) |
| FASTER (≥ 1.1×) | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) | 2 of 3 (67 %, 95 % CI 21–94 %) |
| FASTER and race-free | 3 of 3 (100 %, 95 % CI 44–100 %) | 3 of 3 (100 %, 95 % CI 44–100 %) | 2 of 3 (67 %, 95 % CI 21–94 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **0** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 0 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 |
| shipped a program that does not compile | 0 | 0 | 1 |
| **unusable programs** (any of the four above) | **0** | **0** | **1** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | 3.67× | 3.64× | 4.24× |

- Unusable programs shipped by model alone (1): tsvc/vpvtv rep1: did not compile.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 1, the model-only arm fewer on 0, tied on 2; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 1, model alone ahead on 0, tied on 2; fewer than 6 non-zero pairs: no test.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 1, model alone ahead on 0, tied on 2; fewer than 6 non-zero pairs: no test.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc/s000` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 |
| `tsvc/s313` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 |
| `tsvc/vpvtv` | 1 / 1 / 0 / 0 of 1 | 1 / 1 / 0 / 0 of 1 | 0 / 0 / 0 / 1 of 1 |

### Class D (must-decline control) — 4 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 11 (0 %, 95 % CI 0–26 %) | 3 of 12 (25 %, 95 % CI 9–53 %) |
| FASTER (≥ 1.1×) | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 11 (0 %, 95 % CI 0–26 %) | 0 of 12 (0 %, 95 % CI 0–24 %) |
| FASTER and race-free | 0 of 12 (0 %, 95 % CI 0–24 %) | 0 of 11 (0 %, 95 % CI 0–26 %) | 0 of 12 (0 %, 95 % CI 0–24 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **6** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 1 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 (+2 not judgeable) |
| shipped a program that does not compile | 0 | 0 | 2 |
| **unusable programs** (any of the four above) | **0** | **0** | **9** |
| touched the harness — no valid measurement, not counted above | 0 | 1 | 0 |
| no verdict | 0 | 1 (SCAFFOLD_MODIFIED) | 0 |
| median speedup of the FASTER trials | — | — | — |

- Unusable programs shipped by model alone (9): tsvc/s3112 rep1: slower; tsvc/s3112 rep2: did not compile; tsvc/s321 rep1: BROKEN; tsvc/s321 rep2: BROKEN; tsvc/s322 rep1: BROKEN; tsvc/s322 rep2: BROKEN; tsvc/s322 rep3: BROKEN; tsvc/s323 rep1: BROKEN; tsvc/s323 rep2: did not compile.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 4, the model-only arm fewer on 0, tied on 0; fewer than 6 non-zero pairs: no test. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 0, tied on 4; fewer than 6 non-zero pairs: no test.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 0, model alone ahead on 0, tied on 4; fewer than 6 non-zero pairs: no test.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc/s3112` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 2 | 0 / 0 / 0 / 2 of 3 |
| `tsvc/s321` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 2 / 2 of 3 |
| `tsvc/s322` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 3 / 3 of 3 |
| `tsvc/s323` | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 1 / 2 of 3 |

