# E2-B1 in numbers — the evidence experiment on hidden facts

Runs: e2v6b_agent_1, e2v6b_agent_2, e2v6b_agent_3, e2v6b_fb_1, e2v6b_fb_2, e2v6b_fb_3. Model: claude-haiku-4-5-20251001. Race files for: no_evidence_b1_nospeed_v4, no_evidence_nospeed_v4. Continuity correction on; α = 0.05; the campaign's family M = 52.

> **The confirmatory tests are NOT ESTABLISHED.** E2B1-ii-twins: `twin_full_nospeed_v4`: no trial with a verdict; `twin_no_evidence_nospeed_v4`: no trial with a verdict. E2B1-ii-interaction: `twin_full_nospeed_v4`: no trial with a verdict; `twin_no_evidence_nospeed_v4`: no trial with a verdict. E2B1-iii: `bare_llm_nospeed_v4`: no trial with a verdict.

**The primary outcome** is a race-free verified parallel program whose parallel construct covers the hot loop. A program kept by the gate passed TSan and the schedule matrix; a model-only arm's is race-free only where `race_check.py` found it clean. **Unsafe** = BROKEN, racy or not compiling; with the speed check off in every arm, a correct program slower than the original is reported, not unsafe. A harness edit has its own row and is out of every denominator.

## Confirmatory tests — direction (a), tier 1

Cochran-Mantel-Haenszel, stratified by loop, one-sided in the predicted direction; Mantel-Haenszel common odds ratio with the Robins-Breslow-Greenland 95 % interval; the exact conditional p beside it (not in Holm). The interaction: the difference of the two MH log odds ratios, z-test with the RBG variances added. Holm across the four tests; the campaign family's adjusted p lies between the E2-B1 Holm p (every other hypothesis smaller) and M·p (this one smallest).

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | Holm (E2-B1) | campaign family, M = 52 | established |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E2B1-i: the evidence effect inside the agent | `no_evidence_nospeed_v4` vs `no_evidence_b1_nospeed_v4` | success, OR > 1 | 5 (4) | 3.58 (1.08–11.88) | 3.67 | **0.0278** | 0.026 | 0.111 | 0.111–1: not rejected whatever the other tests | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v4` vs `twin_no_evidence_nospeed_v4` | success, OR > 1 | 0 (0) | not estimable | — | **—** | — | 1 | 1–1: no test | **NO** |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | no informative stratum in the second set: no test | z = — | **—** | — | 1 | 1–1: no test | **NO** |
| E2B1-iii: unsafe programs: the agent against the model alone | `no_evidence_nospeed_v4` vs `bare_llm_nospeed_v4` | unsafe, OR < 1 | 5 (0) | not estimable | — | **—** | — | 1 | 1–1: no test | **NO** |

- E2B1-i: p one-sided without / with the continuity correction 0.0143 / 0.0278; two-sided 0.0556. Per loop (X with / X without / Y with / Y without): `tsvc_c2/k19` 5/5/0/10; `tsvc_c2/k23` 4/6/4/6; `tsvc_c2/k27` 0/10/0/10; `tsvc_c2/k31` 3/7/1/9; `tsvc_c2/s161` 10/0/9/1.
- E2B1-ii-twins: no informative stratum: no test (strata: none).
- E2B1-iii: no informative stratum: no test (strata: `tsvc_c2/k19` 0/10/0/0; `tsvc_c2/k23` 0/10/0/0; `tsvc_c2/k27` 0/10/0/0; `tsvc_c2/k31` 0/10/0/0; `tsvc_c2/s161` 0/10/0/0).
- (iii) counts a model-only program without a race verdict as not unsafe: conservative for the prediction that the agent ships fewer.

## Sensitivity — strata = loop × run (the trials of one run share one profile)

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | established |
|---|---|---|---:|---:|---:|---:|---:|---|
| E2B1-i: the evidence effect inside the agent | `no_evidence_nospeed_v4` vs `no_evidence_b1_nospeed_v4` | success, OR > 1 | 10 (0) | not estimable | — | **—** | — | **NO** |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v4` vs `twin_no_evidence_nospeed_v4` | success, OR > 1 | 0 (0) | not estimable | — | **—** | — | **NO** |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | no informative stratum in the first and the second set: no test | z = — | **—** | — | **NO** |
| E2B1-iii: unsafe programs: the agent against the model alone | `no_evidence_nospeed_v4` vs `bare_llm_nospeed_v4` | unsafe, OR < 1 | 5 (0) | not estimable | — | **—** | — | **NO** |

## direction (a), tier 1 — CONFIRMATORY — 5 loops: `tsvc_c2/k19`, `tsvc_c2/k23`, `tsvc_c2/k27`, `tsvc_c2/k31`, `tsvc_c2/s161`

| per arm | agent, full evidence `no_evidence_nospeed_v4` | agent, no evidence `no_evidence_b1_nospeed_v4` | twin, full evidence `twin_full_nospeed_v4` | twin, no evidence `twin_no_evidence_nospeed_v4` | model alone `bare_llm_nospeed_v4` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 22 of 50 (44 %, 95 % CI 31–58 %) | 14 of 50 (28 %, 95 % CI 17–42 %) | — | — | — | — |
| race-free verified parallel program, any coverage | 24 of 50 (48 %, 95 % CI 35–61 %) | 14 of 50 (28 %, 95 % CI 17–42 %) | — | — | — | — |
| FASTER (≥ 1.1×, reported beside) | 20 of 50 (40 %, 95 % CI 28–54 %) | 12 of 50 (24 %, 95 % CI 14–37 %) | — | — | — | — |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 50 (0 %, 95 % CI 0–7 %) | 0 of 50 (0 %, 95 % CI 0–7 %) | — | — | — | — |
| race-free verified parallel program covering the hot loop (PRIMARY) | 22 | 14 | — | — | — | — |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | — | — | — | — |
| race-free verified parallel program, the hot loop not covered | 2 | 0 | — | — | — | — |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | — | — | — | — |
| verified parallel program the race check could not judge | 0 | 0 | — | — | — | — |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | — | — | — | — |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | — | — | — | — |
| correct, but a verification run did not finish in 30 minutes (output verified exact beforehand) — correct but slower: reported, not unsafe | 0 | 0 | — | — | — | — |
| shipped a program that does not compile — unsafe | 0 | 0 | — | — | — | — |
| still edits the measurement lines after every redo (3 Oct) — counted, unsafe | 0 | 0 | — | — | — | — |
| changed, not parallel | 0 | 0 | — | — | — | — |
| left unchanged | 26 | 36 | — | — | — | — |
| correct but slower (< 0.91×; not unsafe) | 3 | 2 | — | — | — | — |
| touched the harness — own row, no valid measurement | 0 | 0 | — | — | — | — |
| no verdict | 0 | 0 | — | — | — | — |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_c2/k19` | 5 / 0 / 10 | 0 / 0 / 10 | — | — | — | — |
| `tsvc_c2/k23` | 4 / 0 / 10 | 4 / 0 / 10 | — | — | — | — |
| `tsvc_c2/k27` | 0 / 0 / 10 | 0 / 0 / 10 | — | — | — | — |
| `tsvc_c2/k31` | 3 / 0 / 10 | 1 / 0 / 10 | — | — | — | — |
| `tsvc_c2/s161` | 10 / 0 / 10 | 9 / 0 / 10 | — | — | — | — |

The model alone (`bare_llm_nospeed_v4`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_c2/k19` | — | — | — | — | — |
| `tsvc_c2/k23` | — | — | — | — | — |
| `tsvc_c2/k27` | — | — | — | — | — |
| `tsvc_c2/k31` | — | — | — | — | — |
| `tsvc_c2/s161` | — | — | — | — | — |

## direction (b) — descriptive — 1 loops: `tsvc_c2/k48`

| per arm | agent, full evidence `no_evidence_nospeed_v4` | agent, no evidence `no_evidence_b1_nospeed_v4` | twin, full evidence `twin_full_nospeed_v4` | twin, no evidence `twin_no_evidence_nospeed_v4` | model alone `bare_llm_nospeed_v4` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | — | — | — | — |
| race-free verified parallel program, any coverage | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | — | — | — | — |
| FASTER (≥ 1.1×, reported beside) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | — | — | — | — |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | — | — | — | — |
| race-free verified parallel program covering the hot loop (PRIMARY) | 10 | 10 | — | — | — | — |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | — | — | — | — |
| race-free verified parallel program, the hot loop not covered | 0 | 0 | — | — | — | — |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | — | — | — | — |
| verified parallel program the race check could not judge | 0 | 0 | — | — | — | — |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | — | — | — | — |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | — | — | — | — |
| correct, but a verification run did not finish in 30 minutes (output verified exact beforehand) — correct but slower: reported, not unsafe | 0 | 0 | — | — | — | — |
| shipped a program that does not compile — unsafe | 0 | 0 | — | — | — | — |
| still edits the measurement lines after every redo (3 Oct) — counted, unsafe | 0 | 0 | — | — | — | — |
| changed, not parallel | 0 | 0 | — | — | — | — |
| left unchanged | 0 | 0 | — | — | — | — |
| correct but slower (< 0.91×; not unsafe) | 0 | 0 | — | — | — | — |
| touched the harness — own row, no valid measurement | 0 | 0 | — | — | — | — |
| no verdict | 0 | 0 | — | — | — | — |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_c2/k48` | 10 / 0 / 10 | 10 / 0 / 10 | — | — | — | — |

The model alone (`bare_llm_nospeed_v4`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_c2/k48` | — | — | — | — | — |

## Completeness — trials with a verdict against the plan (a silently missing trial biases what is left)

- `tsvc_c2/k19` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k19` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k19` · `bare_llm_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k19` · `discopop_capability`: 0 of 3 planned (0 found)
- `tsvc_c2/k23` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k23` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k23` · `bare_llm_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k23` · `discopop_capability`: 0 of 3 planned (0 found)
- `tsvc_c2/k27` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k27` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k27` · `bare_llm_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k27` · `discopop_capability`: 0 of 3 planned (0 found)
- `tsvc_c2/k31` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k31` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k31` · `bare_llm_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k31` · `discopop_capability`: 0 of 3 planned (0 found)
- `tsvc_c2/k48` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k48` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k48` · `bare_llm_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k48` · `discopop_capability`: 0 of 3 planned (0 found)
- `tsvc_c2/s161` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/s161` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/s161` · `bare_llm_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/s161` · `discopop_capability`: 0 of 3 planned (0 found)

Trials outside the population or the named arms (not analysed): tsvc_c2/k19 · full_b1_nospeed_v4 ×10, tsvc_c2/k19 · full_nospeed_v4 ×10, tsvc_c2/k23 · full_b1_nospeed_v4 ×10, tsvc_c2/k23 · full_nospeed_v4 ×10, tsvc_c2/k27 · full_b1_nospeed_v4 ×10, tsvc_c2/k27 · full_nospeed_v4 ×10, tsvc_c2/k31 · full_b1_nospeed_v4 ×10, tsvc_c2/k31 · full_nospeed_v4 ×10, tsvc_c2/k48 · full_b1_nospeed_v4 ×10, tsvc_c2/k48 · full_nospeed_v4 ×10, tsvc_c2/k53 · full_b1_nospeed_v4 ×10, tsvc_c2/k53 · full_nospeed_v4 ×10, tsvc_c2/k53 · no_evidence_b1_nospeed_v4 ×10, tsvc_c2/k53 · no_evidence_nospeed_v4 ×10, tsvc_c2/s161 · full_b1_nospeed_v4 ×10, tsvc_c2/s161 · full_nospeed_v4 ×10.
