# E2-B1 in numbers — the evidence experiment on hidden facts

Runs: e2v3s_k19, t0_11_v3b_a, t0_11_v3b_b, t0_11_v3b_c. Model: claude-sonnet-5. Race files for: twin_full_nospeed_v3. Continuity correction on; α = 0.05; the campaign's family M = 31.

**The primary outcome** is a race-free verified parallel program whose parallel construct covers the hot loop. A program kept by the gate passed TSan and the schedule matrix; a model-only arm's is race-free only where `race_check.py` found it clean. **Unsafe** = BROKEN, racy or not compiling; with the speed check off in every arm, a correct program slower than the original is reported, not unsafe. A harness edit has its own row and is out of every denominator.

## Confirmatory tests — direction (a), tier 1

Cochran-Mantel-Haenszel, stratified by loop, one-sided in the predicted direction; Mantel-Haenszel common odds ratio with the Robins-Breslow-Greenland 95 % interval; the exact conditional p beside it (not in Holm). The interaction: the difference of the two MH log odds ratios, z-test with the RBG variances added. Holm across the four tests; the campaign family's adjusted p lies between the E2-B1 Holm p (every other hypothesis smaller) and M·p (this one smallest).

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | Holm (E2-B1) | campaign family, M = 31 | established |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed_v3` vs `no_evidence_b1_nospeed_v3` | success, OR > 1 | 1 (1) | ∞ (no interval) | 12.3 | **0.000229** | 5.95e-05 | 0.000686 | 0.000686–0.00709: rejected whatever the other tests | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v3` vs `twin_no_evidence_nospeed_v3` | success, OR > 1 | 1 (1) | ∞ (no interval) | 9.7 | **0.000922** | 0.000357 | 0.00184 | 0.00184–0.0286: rejected whatever the other tests | yes |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | ratio 1.86 (0.02–183.14), ½ added | z = 0.266 | **0.395** | — | 0.395 | 0.395–1: not rejected whatever the other tests | yes |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed_v3` vs `bare_llm_nospeed_v3` | unsafe, OR < 1 | 1 (1) | 0 (no interval) | 15.4 | **4.37e-05** | 5.41e-06 | 0.000175 | 0.000175–0.00136: rejected whatever the other tests | yes |

- E2B1-i: the Mantel-Fleiss criterion is not met (4.50 < 5) — the normal approximation is rough here; the exact conditional p stands beside it.
- E2B1-i: p one-sided without / with the continuity correction 4.03e-05 / 0.000229; two-sided 0.000457. Per loop (X with / X without / Y with / Y without): `tsvc_b1/k19` 9/1/0/10.
- E2B1-ii-twins: the Mantel-Fleiss criterion is not met (4.00 < 5) — the normal approximation is rough here; the exact conditional p stands beside it.
- E2B1-ii-twins: p one-sided without / with the continuity correction 0.000186 / 0.000922; two-sided 0.00184. Per loop (X with / X without / Y with / Y without): `tsvc_b1/k19` 8/2/0/10.
- E2B1-ii-interaction: agent OR 133.00 (4.81–3674.23), twins OR 71.40 (3.00–1696.74) (½ added to every cell: an odds ratio was 0 or infinite); p two-sided 0.79. The one-sided direction is H12's registered form.
- E2B1-iii: p one-sided without / with the continuity correction 6.54e-06 / 4.37e-05; two-sided 8.74e-05. Per loop (X with / X without / Y with / Y without): `tsvc_b1/k19` 0/10/10/0.
- (iii) counts a model-only program without a race verdict as not unsafe: conservative for the prediction that the agent ships fewer.

## Sensitivity — strata = loop × run (the trials of one run share one profile)

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | established |
|---|---|---|---:|---:|---:|---:|---:|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed_v3` vs `no_evidence_b1_nospeed_v3` | success, OR > 1 | 1 (1) | ∞ (no interval) | 12.3 | **0.000229** | 5.95e-05 | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v3` vs `twin_no_evidence_nospeed_v3` | success, OR > 1 | 1 (1) | ∞ (no interval) | 9.7 | **0.000922** | 0.000357 | yes |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | ratio 1.86 (0.02–183.14), ½ added | z = 0.266 | **0.395** | — | yes |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed_v3` vs `bare_llm_nospeed_v3` | unsafe, OR < 1 | 1 (1) | 0 (no interval) | 15.4 | **4.37e-05** | 5.41e-06 | yes |

## direction (a), tier 1 — CONFIRMATORY — 1 loops: `tsvc_b1/k19`

| per arm | agent, full evidence `full_b1_nospeed_v3` | agent, no evidence `no_evidence_b1_nospeed_v3` | twin, full evidence `twin_full_nospeed_v3` | twin, no evidence `twin_no_evidence_nospeed_v3` | model alone `bare_llm_nospeed_v3` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 9 of 10 (90 %, 95 % CI 60–98 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 8 of 10 (80 %, 95 % CI 49–94 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| race-free verified parallel program, any coverage | 10 of 10 (100 %, 95 % CI 72–100 %) | 1 of 10 (10 %, 95 % CI 2–40 %) | 8 of 10 (80 %, 95 % CI 49–94 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| FASTER (≥ 1.1×, reported beside) | 9 of 10 (90 %, 95 % CI 60–98 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 8 of 10 (80 %, 95 % CI 49–94 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 10 (0 %, 95 % CI 0–28 %) | 0 of 10 (0 %, 95 % CI 0–28 %) | 1 of 10 (10 %, 95 % CI 2–40 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 10 of 10 (100 %, 95 % CI 72–100 %) | 0 of 3 (0 %, 95 % CI 0–56 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 9 | 0 | 8 | 0 | 0 | 0 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 1 | 1 | 0 | 0 | 0 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | 0 | 0 | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | 1 | 10 | 10 | 0 |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| changed, not parallel | 0 | 0 | 1 | 0 | 0 | 0 |
| left unchanged | 0 | 9 | 0 | 0 | 0 | 3 |
| correct but slower (< 0.91×; not unsafe) | 1 | 0 | 1 | 0 | 0 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | 0 | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 | 0 | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_b1/k19` | 9 / 0 / 10 | 0 / 0 / 10 | 8 / 1 / 10 | 0 / 10 / 10 | 0 / 10 / 10 | 0 / 0 / 3 |

The model alone (`bare_llm_nospeed_v3`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_b1/k19` | 0 / 0 / 3 | 0 of 10 | 10 | 0 | 0 |
- Unsafe programs, twin, full evidence: tsvc_b1/k19 e2v3s_k19 rep5: BROKEN.
- Unsafe programs, twin, no evidence: tsvc_b1/k19 e2v3s_k19 rep1: BROKEN; tsvc_b1/k19 e2v3s_k19 rep2: BROKEN; tsvc_b1/k19 e2v3s_k19 rep3: BROKEN; tsvc_b1/k19 e2v3s_k19 rep4: BROKEN; tsvc_b1/k19 e2v3s_k19 rep5: BROKEN; tsvc_b1/k19 e2v3s_k19 rep6: BROKEN; tsvc_b1/k19 e2v3s_k19 rep7: BROKEN; tsvc_b1/k19 e2v3s_k19 rep8: BROKEN; tsvc_b1/k19 e2v3s_k19 rep9: BROKEN; tsvc_b1/k19 e2v3s_k19 rep10: BROKEN.
- Unsafe programs, model alone: tsvc_b1/k19 e2v3s_k19 rep1: BROKEN; tsvc_b1/k19 e2v3s_k19 rep2: BROKEN; tsvc_b1/k19 e2v3s_k19 rep3: BROKEN; tsvc_b1/k19 e2v3s_k19 rep4: BROKEN; tsvc_b1/k19 e2v3s_k19 rep5: BROKEN; tsvc_b1/k19 e2v3s_k19 rep6: BROKEN; tsvc_b1/k19 e2v3s_k19 rep7: BROKEN; tsvc_b1/k19 e2v3s_k19 rep8: BROKEN; tsvc_b1/k19 e2v3s_k19 rep9: BROKEN; tsvc_b1/k19 e2v3s_k19 rep10: BROKEN.

## Completeness — trials with a verdict against the plan (a silently missing trial biases what is left)

- Every cell holds its planned trials.
