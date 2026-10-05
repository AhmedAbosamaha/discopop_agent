# E2-B1 in numbers — the evidence experiment on hidden facts

Runs: e2b1v3_bfs, e2b1v3_twins. Model: claude-haiku-4-5-20251001. Race files for: twin_full_nospeed_v3, twin_no_evidence_nospeed_v3. Continuity correction on; α = 0.05; the campaign's family M = 23.

> **The confirmatory tests are NOT ESTABLISHED.** E2B1-i: `full_b1_nospeed`: no trial with a verdict; `no_evidence_b1_nospeed`: no trial with a verdict. E2B1-ii-interaction: `full_b1_nospeed`: no trial with a verdict; `no_evidence_b1_nospeed`: no trial with a verdict. E2B1-iii: `full_b1_nospeed`: no trial with a verdict; `bare_llm_nospeed`: no trial with a verdict.

**The primary outcome** is a race-free verified parallel program whose parallel construct covers the hot loop. A program kept by the gate passed TSan and the schedule matrix; a model-only arm's is race-free only where `race_check.py` found it clean. **Unsafe** = BROKEN, racy or not compiling; with the speed check off in every arm, a correct program slower than the original is reported, not unsafe. A harness edit has its own row and is out of every denominator.

## Confirmatory tests — direction (a), tier 1

Cochran-Mantel-Haenszel, stratified by loop, one-sided in the predicted direction; Mantel-Haenszel common odds ratio with the Robins-Breslow-Greenland 95 % interval; the exact conditional p beside it (not in Holm). The interaction: the difference of the two MH log odds ratios, z-test with the RBG variances added. Holm across the four tests; the campaign family's adjusted p lies between the E2-B1 Holm p (every other hypothesis smaller) and M·p (this one smallest).

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | Holm (E2-B1) | campaign family, M = 23 | established |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed` vs `no_evidence_b1_nospeed` | success, OR > 1 | 0 (0) | not estimable | — | **—** | — | 1 | 1–1: no test | **NO** |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v3` vs `twin_no_evidence_nospeed_v3` | success, OR > 1 | 3 (2) | 0.82 (0.24–2.80) | 0 | **0.753** | 0.755 | 1 | 1–1: not rejected whatever the other tests | yes |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | no informative stratum in the first set: no test | z = — | **—** | — | 1 | 1–1: no test | **NO** |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed` vs `bare_llm_nospeed` | unsafe, OR < 1 | 0 (0) | not estimable | — | **—** | — | 1 | 1–1: no test | **NO** |

- E2B1-i: no informative stratum: no test (strata: none).
- E2B1-ii-twins: p one-sided without / with the continuity correction 0.634 / 0.753; two-sided 1. Per loop (X with / X without / Y with / Y without): `rodinia_b1/bfs` 0/10/0/10; `tsvc_b1/s151` 2/8/7/3; `tsvc_b1/s161` 10/0/6/4.
- E2B1-iii: no informative stratum: no test (strata: none).
- (iii) counts a model-only program without a race verdict as not unsafe: conservative for the prediction that the agent ships fewer.

## Sensitivity — strata = loop × run (the trials of one run share one profile)

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | established |
|---|---|---|---:|---:|---:|---:|---:|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed` vs `no_evidence_b1_nospeed` | success, OR > 1 | 0 (0) | not estimable | — | **—** | — | **NO** |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed_v3` vs `twin_no_evidence_nospeed_v3` | success, OR > 1 | 3 (2) | 0.82 (0.24–2.80) | 0 | **0.753** | 0.755 | yes |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | no informative stratum in the first set: no test | z = — | **—** | — | **NO** |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed` vs `bare_llm_nospeed` | unsafe, OR < 1 | 0 (0) | not estimable | — | **—** | — | **NO** |

## direction (a), tier 1 — CONFIRMATORY — 3 loops: `rodinia_b1/bfs`, `tsvc_b1/s151`, `tsvc_b1/s161`

| per arm | agent, full evidence `full_b1_nospeed` | agent, no evidence `no_evidence_b1_nospeed` | twin, full evidence `twin_full_nospeed_v3` | twin, no evidence `twin_no_evidence_nospeed_v3` | model alone `bare_llm_nospeed` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | — | — | 12 of 30 (40 %, 95 % CI 25–58 %) | 13 of 30 (43 %, 95 % CI 27–61 %) | — | — |
| race-free verified parallel program, any coverage | — | — | 12 of 30 (40 %, 95 % CI 25–58 %) | 15 of 30 (50 %, 95 % CI 33–67 %) | — | — |
| FASTER (≥ 1.1×, reported beside) | — | — | 10 of 30 (33 %, 95 % CI 19–51 %) | 13 of 30 (43 %, 95 % CI 27–61 %) | — | — |
| **unsafe** (BROKEN, racy, not compiling) | — | — | 14 of 30 (47 %, 95 % CI 30–64 %) | 9 of 30 (30 %, 95 % CI 17–48 %) | — | — |
| race-free verified parallel program covering the hot loop (PRIMARY) | — | — | 12 | 13 | — | — |
| race-free verified parallel program, coverage not recorded — not a success | — | — | 0 | 0 | — | — |
| race-free verified parallel program, the hot loop not covered | — | — | 0 | 2 | — | — |
| verified parallel program, no race verdict (model-only arm) — not a success | — | — | 0 | 0 | — | — |
| verified parallel program the race check could not judge | — | — | 0 | 0 | — | — |
| racy (TSan or the schedule matrix) — unsafe | — | — | 0 | 1 | — | — |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | — | — | 14 | 7 | — | — |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | — | — | 0 | 0 | — | — |
| shipped a program that does not compile — unsafe | — | — | 0 | 1 | — | — |
| changed, not parallel | — | — | 4 | 6 | — | — |
| left unchanged | — | — | 0 | 0 | — | — |
| correct but slower (< 0.91×; not unsafe) | — | — | 2 | 3 | — | — |
| touched the harness — own row, no valid measurement | — | — | 0 | 0 | — | — |
| no verdict | — | — | 0 | 0 | — | — |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `rodinia_b1/bfs` | — | — | 0 / 10 / 10 | 0 / 6 / 10 | — | — |
| `tsvc_b1/s151` | — | — | 2 / 4 / 10 | 7 / 1 / 10 | — | — |
| `tsvc_b1/s161` | — | — | 10 / 0 / 10 | 6 / 2 / 10 | — | — |

The model alone (`bare_llm_nospeed`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `rodinia_b1/bfs` | — | — | — | — | — |
| `tsvc_b1/s151` | — | — | — | — | — |
| `tsvc_b1/s161` | — | — | — | — | — |
- Unsafe programs, twin, full evidence: rodinia_b1/bfs e2b1v3_bfs rep1: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep2: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep3: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep4: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep5: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep6: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep7: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep8: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep9: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep10: BROKEN; tsvc_b1/s151 e2b1v3_twins rep2: BROKEN; tsvc_b1/s151 e2b1v3_twins rep5: BROKEN; tsvc_b1/s151 e2b1v3_twins rep7: BROKEN; tsvc_b1/s151 e2b1v3_twins rep9: BROKEN.
- Unsafe programs, twin, no evidence: rodinia_b1/bfs e2b1v3_bfs rep1: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep2: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep4: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep5: did-not-compile; rodinia_b1/bfs e2b1v3_bfs rep7: BROKEN; rodinia_b1/bfs e2b1v3_bfs rep8: racy; tsvc_b1/s151 e2b1v3_twins rep1: BROKEN; tsvc_b1/s161 e2b1v3_twins rep5: BROKEN; tsvc_b1/s161 e2b1v3_twins rep7: BROKEN.

## Completeness — trials with a verdict against the plan (a silently missing trial biases what is left)

- `rodinia_b1/bfs` · `full_b1_nospeed`: 0 of 10 planned (0 found)
- `rodinia_b1/bfs` · `no_evidence_b1_nospeed`: 0 of 10 planned (0 found)
- `rodinia_b1/bfs` · `bare_llm_nospeed`: 0 of 10 planned (0 found)
- `rodinia_b1/bfs` · `discopop_capability`: 0 of 3 planned (0 found)
- `tsvc_b1/s151` · `full_b1_nospeed`: 0 of 10 planned (0 found)
- `tsvc_b1/s151` · `no_evidence_b1_nospeed`: 0 of 10 planned (0 found)
- `tsvc_b1/s151` · `bare_llm_nospeed`: 0 of 10 planned (0 found)
- `tsvc_b1/s151` · `discopop_capability`: 0 of 3 planned (0 found)
- `tsvc_b1/s161` · `full_b1_nospeed`: 0 of 10 planned (0 found)
- `tsvc_b1/s161` · `no_evidence_b1_nospeed`: 0 of 10 planned (0 found)
- `tsvc_b1/s161` · `bare_llm_nospeed`: 0 of 10 planned (0 found)
- `tsvc_b1/s161` · `discopop_capability`: 0 of 3 planned (0 found)
