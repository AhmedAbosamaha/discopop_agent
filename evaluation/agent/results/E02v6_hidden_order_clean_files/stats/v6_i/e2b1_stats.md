# E2-B1 in numbers — the evidence experiment on hidden facts

Runs: e2v6_agent_1, e2v6_agent_2, e2v6_agent_3, e2v6_bare_haiku, t0_11_c2_a, t0_11_c2_b, t0_11_c2_c. Model: claude-haiku-4-5-20251001. Race files for: bare_llm_nospeed_v4, full_b1_nospeed_v4, no_evidence_b1_nospeed_v4. Continuity correction on; α = 0.05; the campaign's family M = 52.

> **The confirmatory tests are NOT ESTABLISHED.** E2B1-ii-twins: `twin_full_nospeed_v4`: no trial with a verdict; `twin_no_evidence_nospeed_v4`: no trial with a verdict. E2B1-ii-interaction: `twin_full_nospeed_v4`: no trial with a verdict; `twin_no_evidence_nospeed_v4`: no trial with a verdict.

**The primary outcome** is a race-free verified parallel program whose parallel construct covers the hot loop. A program kept by the gate passed TSan and the schedule matrix; a model-only arm's is race-free only where `race_check.py` found it clean. **Unsafe** = BROKEN, racy or not compiling; with the speed check off in every arm, a correct program slower than the original is reported, not unsafe. A harness edit has its own row and is out of every denominator.

## Confirmatory tests — direction (a), tier 1

Cochran-Mantel-Haenszel, stratified by loop, one-sided in the predicted direction; Mantel-Haenszel common odds ratio with the Robins-Breslow-Greenland 95 % interval; the exact conditional p beside it (not in Holm). The interaction: the difference of the two MH log odds ratios, z-test with the RBG variances added. Holm across the four tests; the campaign family's adjusted p lies between the E2-B1 Holm p (every other hypothesis smaller) and M·p (this one smallest).

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | Holm (E2-B1) | campaign family, M = 52 | established |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed_v4` vs `no_evidence_b1_nospeed_v4` | success, OR > 1 | 5 (5) | 351.00 (26.20–4702.21) | 54.5 | **7.77e-14** | 1.35e-16 | 2.33e-13 | 2.33e-13–4.04e-12: rejected whatever the other tests | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v4` vs `twin_no_evidence_nospeed_v4` | success, OR > 1 | 0 (0) | not estimable | — | **—** | — | 1 | 1–1: no test | **NO** |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | no informative stratum in the second set: no test | z = — | **—** | — | 1 | 1–1: no test | **NO** |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed_v4` vs `bare_llm_nospeed_v4` | unsafe, OR < 1 | 5 (5) | 0 (no interval) | 81.9 | **7.22e-20** | 1.33e-24 | 2.89e-19 | 2.89e-19–3.76e-18: rejected whatever the other tests | yes |

- E2B1-i: p one-sided without / with the continuity correction 1.49e-14 / 7.77e-14; two-sided 1.55e-13. Per loop (X with / X without / Y with / Y without): `tsvc_c2/k19` 10/0/0/10; `tsvc_c2/k23` 9/1/1/9; `tsvc_c2/k27` 6/4/0/10; `tsvc_c2/k31` 10/0/0/10; `tsvc_c2/s161` 10/0/9/1.
- E2B1-ii-twins: no informative stratum: no test (strata: none).
- E2B1-iii: p one-sided without / with the continuity correction 1.17e-20 / 7.22e-20; two-sided 1.44e-19. Per loop (X with / X without / Y with / Y without): `tsvc_c2/k19` 0/10/10/0; `tsvc_c2/k23` 0/10/10/0; `tsvc_c2/k27` 0/10/10/0; `tsvc_c2/k31` 0/10/10/0; `tsvc_c2/s161` 0/10/7/3.
- (iii) counts a model-only program without a race verdict as not unsafe: conservative for the prediction that the agent ships fewer.

## Sensitivity — strata = loop × run (the trials of one run share one profile)

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | established |
|---|---|---|---:|---:|---:|---:|---:|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed_v4` vs `no_evidence_b1_nospeed_v4` | success, OR > 1 | 5 (5) | 351.00 (26.20–4702.21) | 54.5 | **7.77e-14** | 1.35e-16 | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v4` vs `twin_no_evidence_nospeed_v4` | success, OR > 1 | 0 (0) | not estimable | — | **—** | — | **NO** |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | no informative stratum in the second set: no test | z = — | **—** | — | **NO** |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed_v4` vs `bare_llm_nospeed_v4` | unsafe, OR < 1 | 10 (0) | not estimable | — | **—** | — | **NO** |

## direction (a), tier 1 — CONFIRMATORY — 5 loops: `tsvc_c2/k19`, `tsvc_c2/k23`, `tsvc_c2/k27`, `tsvc_c2/k31`, `tsvc_c2/s161`

| per arm | agent, full evidence `full_b1_nospeed_v4` | agent, no evidence `no_evidence_b1_nospeed_v4` | twin, full evidence `twin_full_nospeed_v4` | twin, no evidence `twin_no_evidence_nospeed_v4` | model alone `bare_llm_nospeed_v4` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 45 of 50 (90 %, 95 % CI 79–96 %) | 10 of 50 (20 %, 95 % CI 11–33 %) | — | — | 3 of 50 (6 %, 95 % CI 2–16 %) | 0 of 15 (0 %, 95 % CI 0–20 %) |
| race-free verified parallel program, any coverage | 45 of 50 (90 %, 95 % CI 79–96 %) | 10 of 50 (20 %, 95 % CI 11–33 %) | — | — | 3 of 50 (6 %, 95 % CI 2–16 %) | 0 of 15 (0 %, 95 % CI 0–20 %) |
| FASTER (≥ 1.1×, reported beside) | 45 of 50 (90 %, 95 % CI 79–96 %) | 8 of 50 (16 %, 95 % CI 8–29 %) | — | — | 3 of 50 (6 %, 95 % CI 2–16 %) | 0 of 15 (0 %, 95 % CI 0–20 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 50 (0 %, 95 % CI 0–7 %) | 0 of 50 (0 %, 95 % CI 0–7 %) | — | — | 47 of 50 (94 %, 95 % CI 84–98 %) | 0 of 15 (0 %, 95 % CI 0–20 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 45 | 10 | — | — | 3 | 0 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | — | — | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 0 | 0 | — | — | 0 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | — | — | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | — | — | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | — | — | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | — | — | 42 | 0 |
| correct, but a verification run did not finish in 30 minutes (output verified exact beforehand) — correct but slower: reported, not unsafe | 0 | 0 | — | — | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | — | — | 5 | 0 |
| still edits the measurement lines after every redo (3 Oct) — counted, unsafe | 0 | 0 | — | — | 0 | 0 |
| changed, not parallel | 0 | 0 | — | — | 0 | 0 |
| left unchanged | 5 | 40 | — | — | 0 | 15 |
| correct but slower (< 0.91×; not unsafe) | 0 | 2 | — | — | 0 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | — | — | 0 | 0 |
| no verdict | 0 | 0 | — | — | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_c2/k19` | 10 / 0 / 10 | 0 / 0 / 10 | — | — | 0 / 10 / 10 | 0 / 0 / 3 |
| `tsvc_c2/k23` | 9 / 0 / 10 | 1 / 0 / 10 | — | — | 0 / 10 / 10 | 0 / 0 / 3 |
| `tsvc_c2/k27` | 6 / 0 / 10 | 0 / 0 / 10 | — | — | 0 / 10 / 10 | 0 / 0 / 3 |
| `tsvc_c2/k31` | 10 / 0 / 10 | 0 / 0 / 10 | — | — | 0 / 10 / 10 | 0 / 0 / 3 |
| `tsvc_c2/s161` | 10 / 0 / 10 | 9 / 0 / 10 | — | — | 3 / 7 / 10 | 0 / 0 / 3 |

The model alone (`bare_llm_nospeed_v4`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_c2/k19` | 0 / 0 / 3 | 0 of 10 | 10 | 0 | 0 |
| `tsvc_c2/k23` | 0 / 0 / 3 | 0 of 10 | 10 | 0 | 0 |
| `tsvc_c2/k27` | 0 / 0 / 3 | 0 of 10 | 10 | 0 | 0 |
| `tsvc_c2/k31` | 0 / 0 / 3 | 0 of 10 | 10 | 0 | 0 |
| `tsvc_c2/s161` | 0 / 0 / 3 | 3 of 10 | 7 | 0 | 0 |
- Unsafe programs, model alone: tsvc_c2/k19 e2v6_bare_haiku rep1: BROKEN; tsvc_c2/k19 e2v6_bare_haiku rep2: did-not-compile; tsvc_c2/k19 e2v6_bare_haiku rep3: BROKEN; tsvc_c2/k19 e2v6_bare_haiku rep4: BROKEN; tsvc_c2/k19 e2v6_bare_haiku rep5: BROKEN; tsvc_c2/k19 e2v6_bare_haiku rep6: BROKEN; tsvc_c2/k19 e2v6_bare_haiku rep7: BROKEN; tsvc_c2/k19 e2v6_bare_haiku rep8: BROKEN; tsvc_c2/k19 e2v6_bare_haiku rep9: BROKEN; tsvc_c2/k19 e2v6_bare_haiku rep10: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep1: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep2: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep3: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep4: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep5: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep6: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep7: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep8: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep9: BROKEN; tsvc_c2/k23 e2v6_bare_haiku rep10: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep1: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep2: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep3: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep4: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep5: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep6: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep7: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep8: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep9: BROKEN; tsvc_c2/k27 e2v6_bare_haiku rep10: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep1: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep2: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep3: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep4: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep5: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep6: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep7: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep8: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep9: BROKEN; tsvc_c2/k31 e2v6_bare_haiku rep10: did-not-compile; tsvc_c2/s161 e2v6_bare_haiku rep1: BROKEN; tsvc_c2/s161 e2v6_bare_haiku rep2: BROKEN; tsvc_c2/s161 e2v6_bare_haiku rep3: did-not-compile; tsvc_c2/s161 e2v6_bare_haiku rep4: did-not-compile; tsvc_c2/s161 e2v6_bare_haiku rep6: did-not-compile; tsvc_c2/s161 e2v6_bare_haiku rep7: BROKEN; tsvc_c2/s161 e2v6_bare_haiku rep8: BROKEN.

## direction (b) — descriptive — 1 loops: `tsvc_c2/k48`

| per arm | agent, full evidence `full_b1_nospeed_v4` | agent, no evidence `no_evidence_b1_nospeed_v4` | twin, full evidence `twin_full_nospeed_v4` | twin, no evidence `twin_no_evidence_nospeed_v4` | model alone `bare_llm_nospeed_v4` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | — | — | 1 of 10 (10 %, 95 % CI 2–40 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| race-free verified parallel program, any coverage | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | — | — | 1 of 10 (10 %, 95 % CI 2–40 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| FASTER (≥ 1.1×, reported beside) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | — | — | 1 of 10 (10 %, 95 % CI 2–40 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | — | — | 9 of 10 (90 %, 95 % CI 60–98 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 10 | 10 | — | — | 1 | 0 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | — | — | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 0 | 0 | — | — | 0 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | — | — | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | — | — | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | — | — | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | — | — | 9 | 0 |
| correct, but a verification run did not finish in 30 minutes (output verified exact beforehand) — correct but slower: reported, not unsafe | 0 | 0 | — | — | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | — | — | 0 | 0 |
| still edits the measurement lines after every redo (3 Oct) — counted, unsafe | 0 | 0 | — | — | 0 | 0 |
| changed, not parallel | 0 | 0 | — | — | 0 | 0 |
| left unchanged | 0 | 0 | — | — | 0 | 3 |
| correct but slower (< 0.91×; not unsafe) | 0 | 0 | — | — | 0 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | — | — | 0 | 0 |
| no verdict | 0 | 0 | — | — | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_c2/k48` | 10 / 0 / 10 | 10 / 0 / 10 | — | — | 1 / 9 / 10 | 0 / 0 / 3 |

The model alone (`bare_llm_nospeed_v4`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_c2/k48` | 0 / 0 / 3 | 1 of 10 | 9 | 0 | 0 |
- Unsafe programs, model alone: tsvc_c2/k48 e2v6_bare_haiku rep1: BROKEN; tsvc_c2/k48 e2v6_bare_haiku rep2: BROKEN; tsvc_c2/k48 e2v6_bare_haiku rep3: BROKEN; tsvc_c2/k48 e2v6_bare_haiku rep4: BROKEN; tsvc_c2/k48 e2v6_bare_haiku rep5: BROKEN; tsvc_c2/k48 e2v6_bare_haiku rep7: BROKEN; tsvc_c2/k48 e2v6_bare_haiku rep8: BROKEN; tsvc_c2/k48 e2v6_bare_haiku rep9: BROKEN; tsvc_c2/k48 e2v6_bare_haiku rep10: BROKEN.

## Completeness — trials with a verdict against the plan (a silently missing trial biases what is left)

- `tsvc_c2/k19` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k19` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k23` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k23` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k27` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k27` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k31` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k31` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k48` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/k48` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/s161` · `twin_full_nospeed_v4`: 0 of 10 planned (0 found)
- `tsvc_c2/s161` · `twin_no_evidence_nospeed_v4`: 0 of 10 planned (0 found)

Trials outside the population or the named arms (not analysed): tsvc_c2/k17 · discopop_capability ×3, tsvc_c2/k42 · discopop_capability ×3, tsvc_c2/k53 · bare_llm_nospeed_v4 ×10, tsvc_c2/k53 · discopop_capability ×3, tsvc_c2/k53 · full_b1_nospeed_v4 ×10, tsvc_c2/k53 · no_evidence_b1_nospeed_v4 ×10, tsvc_c2/s000 · discopop_capability ×3, tsvc_c2/s112 · discopop_capability ×3, tsvc_c2/s121 · discopop_capability ×3, tsvc_c2/s1213 · discopop_capability ×3, tsvc_c2/s127 · discopop_capability ×3, tsvc_c2/s131 · discopop_capability ×3, tsvc_c2/s151 · discopop_capability ×3, tsvc_c2/s152 · discopop_capability ×3, tsvc_c2/s171 · discopop_capability ×3, tsvc_c2/s211 · discopop_capability ×3, tsvc_c2/s212 · discopop_capability ×3, tsvc_c2/s241 · discopop_capability ×3, tsvc_c2/s243 · discopop_capability ×3, tsvc_c2/s244 · discopop_capability ×3, tsvc_c2/s252 · discopop_capability ×3, tsvc_c2/s254 · discopop_capability ×3, tsvc_c2/s255 · discopop_capability ×3, tsvc_c2/s258 · discopop_capability ×3, tsvc_c2/s277 · discopop_capability ×3, tsvc_c2/s281 · discopop_capability ×3, tsvc_c2/s291 · discopop_capability ×3, tsvc_c2/s292 · discopop_capability ×3, tsvc_c2/s293 · discopop_capability ×3, tsvc_c2/s3112 · discopop_capability ×3, tsvc_c2/s313 · discopop_capability ×3, tsvc_c2/s321 · discopop_capability ×3, tsvc_c2/s322 · discopop_capability ×3, tsvc_c2/s323 · discopop_capability ×3, tsvc_c2/s331 · discopop_capability ×3, tsvc_c2/s341 · discopop_capability ×3, tsvc_c2/s424 · discopop_capability ×3, tsvc_c2/s481 · discopop_capability ×3, tsvc_c2/s482 · discopop_capability ×3, tsvc_c2/vas · discopop_capability ×3, tsvc_c2/vpvtv · discopop_capability ×3.
