# V3 pilot in numbers — agent v3 (`default`, `no_evidence`) against DiscoPoP alone and the model alone

Two runs of `agent/tools/main_comparison_stats.py`, one per agent arm (a pooled file would mean nothing). The pilot's own trials are the v3 agent arms; DiscoPoP alone (`discopop_gate`) and the model alone (`bare_llm`, race-checked by `e1c_race_check`) are E1c's trials on the same ten loops — neither arm runs the agent, so the agent version does not change them (record §6, 26 Sep). The pilot's question, v3 against its v2 baseline, is answered in the record (§7) and in `why_trials_fail_v3.md` beside `why_trials_fail_v2_baseline.md`.

---

# The main comparison in numbers

Runs: e1c_r_1, e1c_r_2, e1c_r_3, v3_pilot_1, v3_pilot_2, v3_pilot_3, v3_pilot_4. Agent arm: `default`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 10 benchmarks, 30 agent trials. Verdicts: **gained** 22, **gained-not-faster** 5, **neither** 3.
- Trials reaching a verified parallel program — agent: 27 of 30 (90 %, 95 % CI 74–97 %); DiscoPoP alone: 0 of 50 (0 %, 95 % CI 0–7 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 22 of 30 (73 %, 95 % CI 56–86 %); DiscoPoP alone: 0 of 50 (0 %, 95 % CI 0–7 %).
- Benchmarks with at least one gain: 10 of 10 (tsvc/s112, tsvc/s121, tsvc/s1213, tsvc/s211, tsvc/s212, tsvc/s241, tsvc/s243, tsvc/s244, tsvc/s252, tsvc/s281).
- Speed, paired by benchmark (10 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.39×** (bootstrap 95 % CI 1.17–2.03×); Wilcoxon signed-rank, one-sided: W = 36, p = 0.003906, 8 non-zero pairs; Cliff's δ = +0.80.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 30 agent trials, 82 model calls (0 failed).
- Profile refreshes after a kept rewrite: 56 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 56 time(s).
- Explorer stalls (killed at the limit, draw repeated): 32 inside agents, 32 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 2–16.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `default`, model alone `bare_llm`, DiscoPoP alone `discopop_gate`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

### Class R — 10 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 50 (0 %, 95 % CI 0–7 %) | 27 of 30 (90 %, 95 % CI 74–97 %) | 29 of 50 (58 %, 95 % CI 44–71 %) |
| FASTER (≥ 1.1×) | 0 of 50 (0 %, 95 % CI 0–7 %) | 22 of 30 (73 %, 95 % CI 56–86 %) | 15 of 50 (30 %, 95 % CI 19–44 %) |
| FASTER and race-free | 0 of 50 (0 %, 95 % CI 0–7 %) | 22 of 30 (73 %, 95 % CI 56–86 %) | 15 of 50 (30 %, 95 % CI 19–44 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **15** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 11 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 |
| shipped a program that does not compile | 0 | 0 | 5 |
| **unusable programs** (any of the four above) | **0** | **0** | **31** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | — | 1.51× | 2.19× |

- Unusable programs shipped by model alone (31): tsvc/s112 rep1: slower; tsvc/s112 rep2: slower; tsvc/s112 rep3: slower; tsvc/s112 rep4: BROKEN; tsvc/s112 rep5: slower; tsvc/s121 rep1: slower; tsvc/s121 rep2: BROKEN; tsvc/s121 rep3: BROKEN; tsvc/s121 rep4: slower; tsvc/s121 rep5: BROKEN; tsvc/s1213 rep1: did not compile; tsvc/s1213 rep2: BROKEN; tsvc/s1213 rep3: BROKEN; tsvc/s1213 rep4: BROKEN; tsvc/s1213 rep5: did not compile; tsvc/s211 rep1: BROKEN; tsvc/s211 rep2: BROKEN; tsvc/s211 rep3: BROKEN; tsvc/s211 rep4: did not compile; tsvc/s241 rep2: BROKEN; tsvc/s241 rep3: slower; tsvc/s241 rep4: BROKEN; tsvc/s243 rep1: slower; tsvc/s243 rep2: slower; tsvc/s243 rep4: slower; tsvc/s243 rep5: slower; tsvc/s244 rep2: BROKEN; tsvc/s252 rep2: did not compile; tsvc/s281 rep2: BROKEN; tsvc/s281 rep3: BROKEN; tsvc/s281 rep4: did not compile.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 9, the model-only arm fewer on 0, tied on 1; p (two-sided) = 0.00391, p (agent fewer) = 0.00195. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 7, model alone ahead on 1, tied on 2; p (two-sided) = 0.0547, p (agent ahead) = 0.0273.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 7, model alone ahead on 1, tied on 2; p (two-sided) = 0.0547, p (agent ahead) = 0.0273.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc/s112` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 1 / 5 of 5 |
| `tsvc/s121` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 3 / 5 of 5 |
| `tsvc/s1213` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 3 / 5 of 5 |
| `tsvc/s211` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 3 | 1 / 1 / 3 / 4 of 5 |
| `tsvc/s212` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 5 / 5 / 0 / 0 of 5 |
| `tsvc/s241` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 2 / 3 of 5 |
| `tsvc/s243` | 0 / 0 / 0 / 0 of 5 | 0 / 0 / 0 / 0 of 3 | 0 / 0 / 0 / 4 of 5 |
| `tsvc/s244` | 0 / 0 / 0 / 0 of 5 | 1 / 1 / 0 / 0 of 3 | 4 / 4 / 1 / 1 of 5 |
| `tsvc/s252` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 3 | 3 / 3 / 0 / 1 of 5 |
| `tsvc/s281` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 3 | 2 / 2 / 2 / 3 of 5 |


---

# The main comparison in numbers

Runs: e1c_r_1, e1c_r_2, e1c_r_3, v3_pilot_1, v3_pilot_2, v3_pilot_3, v3_pilot_4. Agent arm: `no_evidence`; baseline: `discopop_gate` (DiscoPoP's own pragmas through the same gate, no model). Statistics as pre-registered: Wilson intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided), Cliff's delta, bootstrap interval on the median ratio; unsafe acceptances are named, not tested.

## Class R — DiscoPoP alone reaches nothing (THE CLAIM)

- 10 benchmarks, 30 agent trials. Verdicts: **gained** 26, **gained-not-faster** 3, **neither** 1.
- Trials reaching a verified parallel program — agent: 29 of 30 (97 %, 95 % CI 83–99 %); DiscoPoP alone: 0 of 50 (0 %, 95 % CI 0–7 %).
- Trials FASTER (≥ 1.1× over the sequential original) — agent: 26 of 30 (87 %, 95 % CI 70–95 %); DiscoPoP alone: 0 of 50 (0 %, 95 % CI 0–7 %).
- Benchmarks with at least one gain: 10 of 10 (tsvc/s112, tsvc/s121, tsvc/s1213, tsvc/s211, tsvc/s212, tsvc/s241, tsvc/s243, tsvc/s244, tsvc/s252, tsvc/s281).
- Speed, paired by benchmark (10 timeable benchmarks): median agent ÷ DiscoPoP alone = **1.40×** (bootstrap 95 % CI 1.24–2.31×); Wilcoxon signed-rank, one-sided: W = 55, p = 0.0009766, 10 non-zero pairs; Cliff's δ = +1.00.
- **Unsafe acceptances: 0**.

## What actually happened inside the trials

- 30 agent trials, 66 model calls (0 failed).
- Profile refreshes after a kept rewrite: 51 full, 0 fast, **0 fast→full fallback(s)**; runtimes re-measured 51 time(s).
- Explorer stalls (killed at the limit, draw repeated): 32 inside agents, 32 in the harness's profile step.
- Agent trials with the speed check off (untimeable kernel): 0.
- Host load (1-min) at trial start: 2–16.

## The three-way comparison (D35): DiscoPoP alone · DiscoPoP + agent · the model alone

Agent arm `no_evidence`, model alone `bare_llm`, DiscoPoP alone `discopop_gate`; the sequential original is the reference (1×). Rates over trials with a verdict. A program the gate kept passed its race stages; the model alone's FASTER programs count as race-free only where `race_check.py` found them clean.

### Class R — 10 benchmarks

| vs the sequential original | DiscoPoP alone | DiscoPoP + agent | model alone |
|---|---:|---:|---:|
| verified parallel program | 0 of 50 (0 %, 95 % CI 0–7 %) | 29 of 30 (97 %, 95 % CI 83–99 %) | 29 of 50 (58 %, 95 % CI 44–71 %) |
| FASTER (≥ 1.1×) | 0 of 50 (0 %, 95 % CI 0–7 %) | 26 of 30 (87 %, 95 % CI 70–95 %) | 15 of 50 (30 %, 95 % CI 19–44 %) |
| FASTER and race-free | 0 of 50 (0 %, 95 % CI 0–7 %) | 26 of 30 (87 %, 95 % CI 70–95 %) | 15 of 50 (30 %, 95 % CI 19–44 %) |
| **BROKEN** (wrong output shipped) | **0** | **0** | **15** |
| correct but slower, shipped (< 0.91×, parallel or not) | 0 | 0 | 11 |
| racy (race check: TSan or the schedule matrix) | 0 | 0 | 0 |
| shipped a program that does not compile | 0 | 0 | 5 |
| **unusable programs** (any of the four above) | **0** | **0** | **31** |
| touched the harness — no valid measurement, not counted above | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 |
| median speedup of the FASTER trials | — | 1.50× | 2.19× |

- Unusable programs shipped by model alone (31): tsvc/s112 rep1: slower; tsvc/s112 rep2: slower; tsvc/s112 rep3: slower; tsvc/s112 rep4: BROKEN; tsvc/s112 rep5: slower; tsvc/s121 rep1: slower; tsvc/s121 rep2: BROKEN; tsvc/s121 rep3: BROKEN; tsvc/s121 rep4: slower; tsvc/s121 rep5: BROKEN; tsvc/s1213 rep1: did not compile; tsvc/s1213 rep2: BROKEN; tsvc/s1213 rep3: BROKEN; tsvc/s1213 rep4: BROKEN; tsvc/s1213 rep5: did not compile; tsvc/s211 rep1: BROKEN; tsvc/s211 rep2: BROKEN; tsvc/s211 rep3: BROKEN; tsvc/s211 rep4: did not compile; tsvc/s241 rep2: BROKEN; tsvc/s241 rep3: slower; tsvc/s241 rep4: BROKEN; tsvc/s243 rep1: slower; tsvc/s243 rep2: slower; tsvc/s243 rep4: slower; tsvc/s243 rep5: slower; tsvc/s244 rep2: BROKEN; tsvc/s252 rep2: did not compile; tsvc/s281 rep2: BROKEN; tsvc/s281 rep3: BROKEN; tsvc/s281 rep4: did not compile.
- **H13 — unusable programs shipped (wrong, racy, slower or not compiling — failures of the code under test), rate per benchmark, paired:** the agent ships fewer on 9, the model-only arm fewer on 0, tied on 1; p (two-sided) = 0.00391, p (agent fewer) = 0.00195. Each is a result, not a discarded trial.
- Agent vs model alone, FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 8, model alone ahead on 1, tied on 1; p (two-sided) = 0.0195, p (agent ahead) = 0.00977.
- Agent vs model alone, race-free FASTER rate per benchmark (Wilcoxon signed-rank, paired): agent ahead on 8, model alone ahead on 1, tied on 1; p (two-sided) = 0.0195, p (agent ahead) = 0.00977.

| benchmark | DiscoPoP alone FASTER / race-free / BROKEN / unusable | DiscoPoP + agent FASTER / race-free / BROKEN / unusable | model alone FASTER / race-free / BROKEN / unusable |
|---|---:|---:|---:|
| `tsvc/s112` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 1 / 5 of 5 |
| `tsvc/s121` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 3 / 5 of 5 |
| `tsvc/s1213` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 3 / 5 of 5 |
| `tsvc/s211` | 0 / 0 / 0 / 0 of 5 | 1 / 1 / 0 / 0 of 3 | 1 / 1 / 3 / 4 of 5 |
| `tsvc/s212` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 5 / 5 / 0 / 0 of 5 |
| `tsvc/s241` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 2 / 3 of 5 |
| `tsvc/s243` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 0 / 0 / 0 / 4 of 5 |
| `tsvc/s244` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 3 | 4 / 4 / 1 / 1 of 5 |
| `tsvc/s252` | 0 / 0 / 0 / 0 of 5 | 2 / 2 / 0 / 0 of 3 | 3 / 3 / 0 / 1 of 5 |
| `tsvc/s281` | 0 / 0 / 0 / 0 of 5 | 3 / 3 / 0 / 0 of 3 | 2 / 2 / 2 / 3 of 5 |

