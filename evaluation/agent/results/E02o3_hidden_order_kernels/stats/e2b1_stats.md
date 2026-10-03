# E2-B1 in numbers — the evidence experiment on hidden facts

Runs: e2o3_agent, e2o3_bare_haiku, e2v3_k48, t0_11_o3_a, t0_11_o3_b, t0_11_o3_c, t0_11_v3b_a, t0_11_v3b_b, t0_11_v3b_c. Model: claude-haiku-4-5-20251001. Race files for: bare_llm_nospeed_v3, full_b1_nospeed_v3, no_evidence_b1_nospeed_v3, twin_full_nospeed_v3, twin_no_evidence_nospeed_v3. Continuity correction on; α = 0.05; the campaign's family M = 41.

> **The confirmatory tests are NOT ESTABLISHED.** E2B1-ii-twins: `twin_full_nospeed_v3`: no trial with a verdict; `twin_no_evidence_nospeed_v3`: no trial with a verdict. E2B1-ii-interaction: `twin_full_nospeed_v3`: no trial with a verdict; `twin_no_evidence_nospeed_v3`: no trial with a verdict.

**The primary outcome** is a race-free verified parallel program whose parallel construct covers the hot loop. A program kept by the gate passed TSan and the schedule matrix; a model-only arm's is race-free only where `race_check.py` found it clean. **Unsafe** = BROKEN, racy or not compiling; with the speed check off in every arm, a correct program slower than the original is reported, not unsafe. A harness edit has its own row and is out of every denominator.

## Confirmatory tests — direction (a), tier 1

Cochran-Mantel-Haenszel, stratified by loop, one-sided in the predicted direction; Mantel-Haenszel common odds ratio with the Robins-Breslow-Greenland 95 % interval; the exact conditional p beside it (not in Holm). The interaction: the difference of the two MH log odds ratios, z-test with the RBG variances added. Holm across the four tests; the campaign family's adjusted p lies between the E2-B1 Holm p (every other hypothesis smaller) and M·p (this one smallest).

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | Holm (E2-B1) | campaign family, M = 41 | established |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed_v3` vs `no_evidence_b1_nospeed_v3` | success, OR > 1 | 3 (3) | ∞ (no interval) | 49.8 | **8.43e-13** | 1.74e-15 | 2.53e-12 | 2.53e-12–3.46e-11: rejected whatever the other tests | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v3` vs `twin_no_evidence_nospeed_v3` | success, OR > 1 | 0 (0) | not estimable | — | **—** | — | 1 | 1–1: no test | **NO** |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | no informative stratum in the second set: no test | z = — | **—** | — | 1 | 1–1: no test | **NO** |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed_v3` vs `bare_llm_nospeed_v3` | unsafe, OR < 1 | 3 (3) | 0 (no interval) | 53.3 | **1.46e-13** | 1.59e-16 | 5.83e-13 | 5.83e-13–5.98e-12: rejected whatever the other tests | yes |

- E2B1-i: p one-sided without / with the continuity correction 1.33e-13 / 8.43e-13; two-sided 1.69e-12. Per loop (X with / X without / Y with / Y without): `tsvc_b1/k23` 9/1/0/10; `tsvc_b1/k31` 10/0/0/10; `tsvc_b1/k36` 10/0/0/10.
- E2B1-ii-twins: no informative stratum: no test (strata: none).
- E2B1-iii: p one-sided without / with the continuity correction 2.18e-14 / 1.46e-13; two-sided 2.92e-13. Per loop (X with / X without / Y with / Y without): `tsvc_b1/k23` 0/10/10/0; `tsvc_b1/k31` 0/10/10/0; `tsvc_b1/k36` 0/10/10/0.
- (iii) counts a model-only program without a race verdict as not unsafe: conservative for the prediction that the agent ships fewer.

## Sensitivity — strata = loop × run (the trials of one run share one profile)

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | established |
|---|---|---|---:|---:|---:|---:|---:|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed_v3` vs `no_evidence_b1_nospeed_v3` | success, OR > 1 | 3 (3) | ∞ (no interval) | 49.8 | **8.43e-13** | 1.74e-15 | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v3` vs `twin_no_evidence_nospeed_v3` | success, OR > 1 | 0 (0) | not estimable | — | **—** | — | **NO** |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | no informative stratum in the second set: no test | z = — | **—** | — | **NO** |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed_v3` vs `bare_llm_nospeed_v3` | unsafe, OR < 1 | 6 (0) | not estimable | — | **—** | — | **NO** |

## direction (a), tier 1 — CONFIRMATORY — 3 loops: `tsvc_b1/k23`, `tsvc_b1/k31`, `tsvc_b1/k36`

| per arm | agent, full evidence `full_b1_nospeed_v3` | agent, no evidence `no_evidence_b1_nospeed_v3` | twin, full evidence `twin_full_nospeed_v3` | twin, no evidence `twin_no_evidence_nospeed_v3` | model alone `bare_llm_nospeed_v3` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 29 of 30 (97 %, 95 % CI 83–99 %) | 0 of 30 (0 %, 95 % CI 0–11 %) | — | — | 0 of 30 (0 %, 95 % CI 0–11 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| race-free verified parallel program, any coverage | 29 of 30 (97 %, 95 % CI 83–99 %) | 2 of 30 (7 %, 95 % CI 2–21 %) | — | — | 0 of 30 (0 %, 95 % CI 0–11 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| FASTER (≥ 1.1×, reported beside) | 29 of 30 (97 %, 95 % CI 83–99 %) | 0 of 30 (0 %, 95 % CI 0–11 %) | — | — | 0 of 30 (0 %, 95 % CI 0–11 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 30 (0 %, 95 % CI 0–11 %) | 0 of 30 (0 %, 95 % CI 0–11 %) | — | — | 30 of 30 (100 %, 95 % CI 89–100 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 29 | 0 | — | — | 0 | 0 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | — | — | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 0 | 2 | — | — | 0 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | — | — | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | — | — | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | — | — | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | — | — | 28 | 0 |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | 0 | 0 | — | — | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | — | — | 2 | 0 |
| still edits the measurement lines after every redo (3 Oct) — counted, unsafe | 0 | 0 | — | — | 0 | 0 |
| changed, not parallel | 0 | 0 | — | — | 0 | 0 |
| left unchanged | 1 | 28 | — | — | 0 | 9 |
| correct but slower (< 0.91×; not unsafe) | 0 | 2 | — | — | 0 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | — | — | 0 | 0 |
| no verdict | 0 | 0 | — | — | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_b1/k23` | 9 / 0 / 10 | 0 / 0 / 10 | — | — | 0 / 10 / 10 | 0 / 0 / 3 |
| `tsvc_b1/k31` | 10 / 0 / 10 | 0 / 0 / 10 | — | — | 0 / 10 / 10 | 0 / 0 / 3 |
| `tsvc_b1/k36` | 10 / 0 / 10 | 0 / 0 / 10 | — | — | 0 / 10 / 10 | 0 / 0 / 3 |

The model alone (`bare_llm_nospeed_v3`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_b1/k23` | 0 / 0 / 3 | 0 of 10 | 10 | 0 | 0 |
| `tsvc_b1/k31` | 0 / 0 / 3 | 0 of 10 | 10 | 0 | 0 |
| `tsvc_b1/k36` | 0 / 0 / 3 | 0 of 10 | 10 | 0 | 0 |
- Unsafe programs, model alone: tsvc_b1/k23 e2o3_bare_haiku rep1: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep2: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep3: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep4: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep5: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep6: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep7: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep8: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep9: BROKEN; tsvc_b1/k23 e2o3_bare_haiku rep10: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep1: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep2: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep3: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep4: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep5: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep6: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep7: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep8: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep9: BROKEN; tsvc_b1/k31 e2o3_bare_haiku rep10: did-not-compile; tsvc_b1/k36 e2o3_bare_haiku rep1: BROKEN; tsvc_b1/k36 e2o3_bare_haiku rep2: BROKEN; tsvc_b1/k36 e2o3_bare_haiku rep3: did-not-compile; tsvc_b1/k36 e2o3_bare_haiku rep4: BROKEN; tsvc_b1/k36 e2o3_bare_haiku rep5: BROKEN; tsvc_b1/k36 e2o3_bare_haiku rep6: BROKEN; tsvc_b1/k36 e2o3_bare_haiku rep7: BROKEN; tsvc_b1/k36 e2o3_bare_haiku rep8: BROKEN; tsvc_b1/k36 e2o3_bare_haiku rep9: BROKEN; tsvc_b1/k36 e2o3_bare_haiku rep10: BROKEN.

## direction (b) — descriptive — 1 loops: `tsvc_b1/k48`

| per arm | agent, full evidence `full_b1_nospeed_v3` | agent, no evidence `no_evidence_b1_nospeed_v3` | twin, full evidence `twin_full_nospeed_v3` | twin, no evidence `twin_no_evidence_nospeed_v3` | model alone `bare_llm_nospeed_v3` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 8 of 10 (80 %, 95 % CI 49–94 %) | 1 of 10 (10 %, 95 % CI 2–40 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| race-free verified parallel program, any coverage | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 8 of 10 (80 %, 95 % CI 49–94 %) | 1 of 10 (10 %, 95 % CI 2–40 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| FASTER (≥ 1.1×, reported beside) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 8 of 10 (80 %, 95 % CI 49–94 %) | 1 of 10 (10 %, 95 % CI 2–40 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 2 of 10 (20 %, 95 % CI 6–51 %) | 9 of 10 (90 %, 95 % CI 60–98 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 10 | 10 | 10 | 8 | 1 | 0 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | 0 | 0 | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | 0 | 2 | 7 | 0 |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | 0 | 0 | 2 | 0 |
| still edits the measurement lines after every redo (3 Oct) — counted, unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| changed, not parallel | 0 | 0 | 0 | 0 | 0 | 0 |
| left unchanged | 0 | 0 | 0 | 0 | 0 | 3 |
| correct but slower (< 0.91×; not unsafe) | 0 | 0 | 0 | 0 | 0 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | 0 | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 | 0 | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_b1/k48` | 10 / 0 / 10 | 10 / 0 / 10 | 10 / 0 / 10 | 8 / 2 / 10 | 1 / 9 / 10 | 0 / 0 / 3 |

The model alone (`bare_llm_nospeed_v3`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_b1/k48` | 0 / 0 / 3 | 1 of 10 | 9 | 0 | 0 |
- Unsafe programs, twin, no evidence: tsvc_b1/k48 e2v3_k48 rep1: BROKEN; tsvc_b1/k48 e2v3_k48 rep8: BROKEN.
- Unsafe programs, model alone: tsvc_b1/k48 e2v3_k48 rep1: BROKEN; tsvc_b1/k48 e2v3_k48 rep3: BROKEN; tsvc_b1/k48 e2v3_k48 rep4: BROKEN; tsvc_b1/k48 e2v3_k48 rep5: BROKEN; tsvc_b1/k48 e2v3_k48 rep6: BROKEN; tsvc_b1/k48 e2v3_k48 rep7: BROKEN; tsvc_b1/k48 e2v3_k48 rep8: did-not-compile; tsvc_b1/k48 e2v3_k48 rep9: BROKEN; tsvc_b1/k48 e2v3_k48 rep10: did-not-compile.

## Completeness — trials with a verdict against the plan (a silently missing trial biases what is left)

- `tsvc_b1/k23` · `twin_full_nospeed_v3`: 0 of 10 planned (0 found)
- `tsvc_b1/k23` · `twin_no_evidence_nospeed_v3`: 0 of 10 planned (0 found)
- `tsvc_b1/k31` · `twin_full_nospeed_v3`: 0 of 10 planned (0 found)
- `tsvc_b1/k31` · `twin_no_evidence_nospeed_v3`: 0 of 10 planned (0 found)
- `tsvc_b1/k36` · `twin_full_nospeed_v3`: 0 of 10 planned (0 found)
- `tsvc_b1/k36` · `twin_no_evidence_nospeed_v3`: 0 of 10 planned (0 found)

Trials outside the population or the named arms (not analysed): tsvc_b1/k19 · discopop_capability ×3.
