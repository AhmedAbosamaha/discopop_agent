# E2-B1 in numbers — the evidence experiment on hidden facts

Runs: e2v3_k17, e2v3_k42, e2v3_s1213, e2v3_s211, t0_11_v3_a, t0_11_v3_b, t0_11_v3_c. Model: claude-haiku-4-5-20251001. Race files for: bare_llm_nospeed_v3, twin_full_nospeed_v3, twin_no_evidence_nospeed_v3. Continuity correction on; α = 0.05; the campaign's family M = 27.

**The primary outcome** is a race-free verified parallel program whose parallel construct covers the hot loop. A program kept by the gate passed TSan and the schedule matrix; a model-only arm's is race-free only where `race_check.py` found it clean. **Unsafe** = BROKEN, racy or not compiling; with the speed check off in every arm, a correct program slower than the original is reported, not unsafe. A harness edit has its own row and is out of every denominator.

## Confirmatory tests — direction (a), tier 1

Cochran-Mantel-Haenszel, stratified by loop, one-sided in the predicted direction; Mantel-Haenszel common odds ratio with the Robins-Breslow-Greenland 95 % interval; the exact conditional p beside it (not in Holm). The interaction: the difference of the two MH log odds ratios, z-test with the RBG variances added. Holm across the four tests; the campaign family's adjusted p lies between the E2-B1 Holm p (every other hypothesis smaller) and M·p (this one smallest).

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | Holm (E2-B1) | campaign family, M = 27 | established |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed_v3` vs `no_evidence_b1_nospeed_v3` | success, OR > 1 | 3 (1) | 1.00 (0.05–18.57) | 0 | **0.766** | 0.763 | 1 | 1–1: not rejected whatever the other tests | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v3` vs `twin_no_evidence_nospeed_v3` | success, OR > 1 | 3 (3) | 2.54 (1.00–6.43) | 3.68 | **0.0276** | 0.0261 | 0.0828 | 0.0828–0.745: not rejected whatever the other tests | yes |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | ratio 0.39 (0.02–8.45) | z = -0.596 | **0.724** | — | 1 | 1–1: not rejected whatever the other tests | yes |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed_v3` vs `bare_llm_nospeed_v3` | unsafe, OR < 1 | 3 (3) | 0 (no interval) | 28.7 | **4.27e-08** | 1.5e-09 | 1.71e-07 | 1.71e-07–1.15e-06: rejected whatever the other tests | yes |

- E2B1-i: the Mantel-Fleiss criterion is not met (1.00 < 5) — the normal approximation is rough here; the exact conditional p stands beside it.
- E2B1-i: p one-sided without / with the continuity correction 0.5 / 0.766; two-sided 1. Per loop (X with / X without / Y with / Y without): `tsvc_b1/k17` 10/0/10/0; `tsvc_b1/s1213` 9/1/9/1; `tsvc_b1/s211` 10/0/10/0.
- E2B1-ii-twins: p one-sided without / with the continuity correction 0.0146 / 0.0276; two-sided 0.0552. Per loop (X with / X without / Y with / Y without): `tsvc_b1/k17` 10/0/0/10; `tsvc_b1/s1213` 6/4/5/5; `tsvc_b1/s211` 1/8/4/6.
- E2B1-ii-interaction: agent OR 1.00 (0.05–18.57), twins OR 2.54 (1.00–6.43); p two-sided 0.551. The one-sided direction is H12's registered form.
- E2B1-iii: p one-sided without / with the continuity correction 9.38e-09 / 4.27e-08; two-sided 8.54e-08. Per loop (X with / X without / Y with / Y without): `tsvc_b1/k17` 0/10/9/1; `tsvc_b1/s1213` 0/10/5/5; `tsvc_b1/s211` 0/10/7/3.
- (iii) counts a model-only program without a race verdict as not unsafe: conservative for the prediction that the agent ships fewer.

## Sensitivity — strata = loop × run (the trials of one run share one profile)

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | established |
|---|---|---|---:|---:|---:|---:|---:|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed_v3` vs `no_evidence_b1_nospeed_v3` | success, OR > 1 | 3 (1) | 1.00 (0.05–18.57) | 0 | **0.766** | 0.763 | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v3` vs `twin_no_evidence_nospeed_v3` | success, OR > 1 | 3 (3) | 2.54 (1.00–6.43) | 3.68 | **0.0276** | 0.0261 | yes |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | ratio 0.39 (0.02–8.45) | z = -0.596 | **0.724** | — | yes |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed_v3` vs `bare_llm_nospeed_v3` | unsafe, OR < 1 | 3 (3) | 0 (no interval) | 28.7 | **4.27e-08** | 1.5e-09 | yes |

## direction (a), tier 1 — CONFIRMATORY — 3 loops: `tsvc_b1/k17`, `tsvc_b1/s1213`, `tsvc_b1/s211`

| per arm | agent, full evidence `full_b1_nospeed_v3` | agent, no evidence `no_evidence_b1_nospeed_v3` | twin, full evidence `twin_full_nospeed_v3` | twin, no evidence `twin_no_evidence_nospeed_v3` | model alone `bare_llm_nospeed_v3` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 29 of 30 (97 %, 95 % CI 83–99 %) | 29 of 30 (97 %, 95 % CI 83–99 %) | 17 of 29 (59 %, 95 % CI 41–74 %) | 9 of 30 (30 %, 95 % CI 17–48 %) | 8 of 30 (27 %, 95 % CI 14–44 %) | 3 of 9 (33 %, 95 % CI 12–65 %) |
| race-free verified parallel program, any coverage | 29 of 30 (97 %, 95 % CI 83–99 %) | 29 of 30 (97 %, 95 % CI 83–99 %) | 17 of 29 (59 %, 95 % CI 41–74 %) | 9 of 30 (30 %, 95 % CI 17–48 %) | 8 of 30 (27 %, 95 % CI 14–44 %) | 3 of 9 (33 %, 95 % CI 12–65 %) |
| FASTER (≥ 1.1×, reported beside) | 15 of 30 (50 %, 95 % CI 33–67 %) | 15 of 30 (50 %, 95 % CI 33–67 %) | 6 of 29 (21 %, 95 % CI 10–38 %) | 6 of 30 (20 %, 95 % CI 10–37 %) | 4 of 30 (13 %, 95 % CI 5–30 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 30 (0 %, 95 % CI 0–11 %) | 0 of 30 (0 %, 95 % CI 0–11 %) | 12 of 29 (41 %, 95 % CI 26–59 %) | 21 of 30 (70 %, 95 % CI 52–83 %) | 21 of 30 (70 %, 95 % CI 52–83 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 29 | 29 | 17 | 9 | 8 | 3 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | 0 | 0 | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | 12 | 21 | 18 | 0 |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | 0 | 0 | 3 | 0 |
| changed, not parallel | 0 | 0 | 0 | 0 | 0 | 0 |
| left unchanged | 1 | 1 | 0 | 0 | 1 | 6 |
| correct but slower (< 0.91×; not unsafe) | 2 | 3 | 1 | 2 | 2 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | 1 | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 | 0 | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_b1/k17` | 10 / 0 / 10 | 10 / 0 / 10 | 10 / 0 / 10 | 0 / 10 / 10 | 0 / 9 / 10 | 3 / 0 / 3 |
| `tsvc_b1/s1213` | 9 / 0 / 10 | 9 / 0 / 10 | 6 / 4 / 10 | 5 / 5 / 10 | 5 / 5 / 10 | 0 / 0 / 3 |
| `tsvc_b1/s211` | 10 / 0 / 10 | 10 / 0 / 10 | 1 / 8 / 9 | 4 / 6 / 10 | 3 / 7 / 10 | 0 / 0 / 3 |

The model alone (`bare_llm_nospeed_v3`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_b1/k17` | 3 / 3 / 3 | 0 of 10 | 9 | 1 | 0 |
| `tsvc_b1/s1213` | 0 / 0 / 3 | 5 of 10 | 5 | 0 | 0 |
| `tsvc_b1/s211` | 0 / 0 / 3 | 3 of 10 | 7 | 0 | 0 |
- Unsafe programs, twin, full evidence: tsvc_b1/s1213 e2v3_s1213 rep3: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep4: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep5: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep6: BROKEN; tsvc_b1/s211 e2v3_s211 rep1: BROKEN; tsvc_b1/s211 e2v3_s211 rep2: BROKEN; tsvc_b1/s211 e2v3_s211 rep3: BROKEN; tsvc_b1/s211 e2v3_s211 rep4: BROKEN; tsvc_b1/s211 e2v3_s211 rep6: BROKEN; tsvc_b1/s211 e2v3_s211 rep8: BROKEN; tsvc_b1/s211 e2v3_s211 rep9: BROKEN; tsvc_b1/s211 e2v3_s211 rep10: BROKEN.
- Harness edits, twin, full evidence (not counted): tsvc_b1/s211 e2v3_s211 rep7.
- Unsafe programs, twin, no evidence: tsvc_b1/k17 e2v3_k17 rep1: BROKEN; tsvc_b1/k17 e2v3_k17 rep2: BROKEN; tsvc_b1/k17 e2v3_k17 rep3: BROKEN; tsvc_b1/k17 e2v3_k17 rep4: BROKEN; tsvc_b1/k17 e2v3_k17 rep5: BROKEN; tsvc_b1/k17 e2v3_k17 rep6: BROKEN; tsvc_b1/k17 e2v3_k17 rep7: BROKEN; tsvc_b1/k17 e2v3_k17 rep8: BROKEN; tsvc_b1/k17 e2v3_k17 rep9: BROKEN; tsvc_b1/k17 e2v3_k17 rep10: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep1: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep3: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep5: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep8: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep9: BROKEN; tsvc_b1/s211 e2v3_s211 rep1: BROKEN; tsvc_b1/s211 e2v3_s211 rep3: BROKEN; tsvc_b1/s211 e2v3_s211 rep6: BROKEN; tsvc_b1/s211 e2v3_s211 rep7: BROKEN; tsvc_b1/s211 e2v3_s211 rep9: BROKEN; tsvc_b1/s211 e2v3_s211 rep10: BROKEN.
- Unsafe programs, model alone: tsvc_b1/k17 e2v3_k17 rep1: BROKEN; tsvc_b1/k17 e2v3_k17 rep2: BROKEN; tsvc_b1/k17 e2v3_k17 rep3: BROKEN; tsvc_b1/k17 e2v3_k17 rep4: BROKEN; tsvc_b1/k17 e2v3_k17 rep6: BROKEN; tsvc_b1/k17 e2v3_k17 rep7: BROKEN; tsvc_b1/k17 e2v3_k17 rep8: BROKEN; tsvc_b1/k17 e2v3_k17 rep9: BROKEN; tsvc_b1/k17 e2v3_k17 rep10: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep1: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep5: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep8: BROKEN; tsvc_b1/s1213 e2v3_s1213 rep9: did-not-compile; tsvc_b1/s1213 e2v3_s1213 rep10: did-not-compile; tsvc_b1/s211 e2v3_s211 rep1: BROKEN; tsvc_b1/s211 e2v3_s211 rep2: BROKEN; tsvc_b1/s211 e2v3_s211 rep3: did-not-compile; tsvc_b1/s211 e2v3_s211 rep4: BROKEN; tsvc_b1/s211 e2v3_s211 rep6: BROKEN; tsvc_b1/s211 e2v3_s211 rep8: BROKEN; tsvc_b1/s211 e2v3_s211 rep10: BROKEN.

## direction (b) — descriptive — 1 loops: `tsvc_b1/k42`

| per arm | agent, full evidence `full_b1_nospeed_v3` | agent, no evidence `no_evidence_b1_nospeed_v3` | twin, full evidence `twin_full_nospeed_v3` | twin, no evidence `twin_no_evidence_nospeed_v3` | model alone `bare_llm_nospeed_v3` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 1 of 10 (10 %, 95 % CI 2–40 %) | 3 of 3 (100 %, 95 % CI 44–100 %) |
| race-free verified parallel program, any coverage | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 1 of 10 (10 %, 95 % CI 2–40 %) | 3 of 3 (100 %, 95 % CI 44–100 %) |
| FASTER (≥ 1.1×, reported beside) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 9 of 10 (90 %, 95 % CI 60–98 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 10 | 10 | 10 | 10 | 1 | 3 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | 0 | 0 | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | 0 | 0 | 8 | 0 |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | 0 | 0 | 1 | 0 |
| changed, not parallel | 0 | 0 | 0 | 0 | 0 | 0 |
| left unchanged | 0 | 0 | 0 | 0 | 0 | 0 |
| correct but slower (< 0.91×; not unsafe) | 0 | 0 | 0 | 0 | 0 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | 0 | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 | 0 | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_b1/k42` | 10 / 0 / 10 | 10 / 0 / 10 | 10 / 0 / 10 | 10 / 0 / 10 | 1 / 9 / 10 | 3 / 0 / 3 |

The model alone (`bare_llm_nospeed_v3`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_b1/k42` | 3 / 3 / 3 | 1 of 10 | 9 | 0 | 0 |
- Unsafe programs, model alone: tsvc_b1/k42 e2v3_k42 rep1: BROKEN; tsvc_b1/k42 e2v3_k42 rep2: BROKEN; tsvc_b1/k42 e2v3_k42 rep3: BROKEN; tsvc_b1/k42 e2v3_k42 rep4: BROKEN; tsvc_b1/k42 e2v3_k42 rep6: did-not-compile; tsvc_b1/k42 e2v3_k42 rep7: BROKEN; tsvc_b1/k42 e2v3_k42 rep8: BROKEN; tsvc_b1/k42 e2v3_k42 rep9: BROKEN; tsvc_b1/k42 e2v3_k42 rep10: BROKEN.

## Completeness — trials with a verdict against the plan (a silently missing trial biases what is left)

- `tsvc_b1/s211` · `twin_full_nospeed_v3`: 9 of 10 planned (10 found)
