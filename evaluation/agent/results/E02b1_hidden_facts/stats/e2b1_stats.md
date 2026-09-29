# E2-B1 in numbers — the evidence experiment on hidden facts

Runs: e2b1_a_1, e2b1_a_2, e2b1_a_3, e2b1_b_1, e2b1_bare_m3_a, e2b1_bare_m3_b, e2b1_bare_m3_bfs, t0_11_b1_a, t0_11_b1_b, t0_11_b1_bfs15_a, t0_11_b1_bfs15_b, t0_11_b1_bfs15_c, t0_11_b1_c. Model: claude-haiku-4-5-20251001. Race files for: bare_llm_nospeed, twin_full_nospeed, twin_no_evidence_nospeed. Continuity correction on; α = 0.05; the campaign's family M = 23.

**The primary outcome** is a race-free verified parallel program whose parallel construct covers the hot loop. A program kept by the gate passed TSan and the schedule matrix; a model-only arm's is race-free only where `race_check.py` found it clean. **Unsafe** = BROKEN, racy or not compiling; with the speed check off in every arm, a correct program slower than the original is reported, not unsafe. A harness edit has its own row and is out of every denominator.

## Confirmatory tests — direction (a), tier 1

Cochran-Mantel-Haenszel, stratified by loop, one-sided in the predicted direction; Mantel-Haenszel common odds ratio with the Robins-Breslow-Greenland 95 % interval; the exact conditional p beside it (not in Holm). The interaction: the difference of the two MH log odds ratios, z-test with the RBG variances added. Holm across the four tests; the campaign family's adjusted p lies between the E2-B1 Holm p (every other hypothesis smaller) and M·p (this one smallest).

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | Holm (E2-B1) | campaign family, M = 23 | established |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed` vs `no_evidence_b1_nospeed` | success, OR > 1 | 3 (2) | 0.62 (0.16–2.44) | 0.114 | **0.845** | 0.848 | 1 | 1–1: not rejected whatever the other tests | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed` vs `twin_no_evidence_nospeed` | success, OR > 1 | 3 (2) | 0.19 (0.04–0.86) | 3.49 | **0.994** | 0.996 | 1 | 1–1: not rejected whatever the other tests | yes |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | ratio 3.24 (0.42–25.12) | z = 1.13 | **0.13** | — | 0.39 | 0.39–1: not rejected whatever the other tests | yes |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed` vs `bare_llm_nospeed` | unsafe, OR < 1 | 3 (3) | 0 (no interval) | 8.75 | **0.00155** | 0.000642 | 0.0062 | 0.0062–0.0356: rejected whatever the other tests | yes |

- E2B1-i: p one-sided without / with the continuity correction 0.751 / 0.845; two-sided 0.735. Per loop (X with / X without / Y with / Y without): `rodinia_b1/bfs` 2/8/3/7; `tsvc_b1/s151` 10/0/10/0; `tsvc_b1/s161` 6/4/7/3.
- E2B1-ii-twins: p one-sided without / with the continuity correction 0.986 / 0.994; two-sided 0.0616. Per loop (X with / X without / Y with / Y without): `rodinia_b1/bfs` 0/10/0/10; `tsvc_b1/s151` 2/7/5/5; `tsvc_b1/s161` 1/9/5/5.
- E2B1-ii-interaction: agent OR 0.62 (0.16–2.44), twins OR 0.19 (0.04–0.86); p two-sided 0.26. The one-sided direction is H12's registered form.
- E2B1-iii: the Mantel-Fleiss criterion is not met (4.50 < 5) — the normal approximation is rough here; the exact conditional p stands beside it.
- E2B1-iii: p one-sided without / with the continuity correction 0.000438 / 0.00155; two-sided 0.0031. Per loop (X with / X without / Y with / Y without): `rodinia_b1/bfs` 0/10/2/8; `tsvc_b1/s151` 0/10/1/9; `tsvc_b1/s161` 0/10/6/4.
- (iii) counts a model-only program without a race verdict as not unsafe: conservative for the prediction that the agent ships fewer.

## Sensitivity — strata = loop × run (the trials of one run share one profile)

| test | X vs Y | outcome, predicted | strata (informative) | MH odds ratio (95 % RBG) | CMH χ² | p one-sided | exact p | established |
|---|---|---|---:|---:|---:|---:|---:|---|
| E2B1-i: the evidence effect inside the agent | `full_b1_nospeed` vs `no_evidence_b1_nospeed` | success, OR > 1 | 3 (2) | 0.62 (0.16–2.44) | 0.114 | **0.845** | 0.848 | yes |
| E2B1-ii-twins: the evidence effect on the matched twins | `twin_full_nospeed` vs `twin_no_evidence_nospeed` | success, OR > 1 | 3 (2) | 0.19 (0.04–0.86) | 3.49 | **0.994** | 0.996 | yes |
| E2B1-ii-interaction: the evidence effect inside the agent against on the twins (H12's form) | agent vs twins | success, agent's OR > twins' | — | ratio 3.24 (0.42–25.12) | z = 1.13 | **0.13** | — | yes |
| E2B1-iii: unsafe programs: the agent against the model alone | `full_b1_nospeed` vs `bare_llm_nospeed` | unsafe, OR < 1 | 6 (0) | not estimable | — | **—** | — | **NO** |

## direction (a), tier 1 — CONFIRMATORY — 3 loops: `rodinia_b1/bfs`, `tsvc_b1/s151`, `tsvc_b1/s161`

| per arm | agent, full evidence `full_b1_nospeed` | agent, no evidence `no_evidence_b1_nospeed` | twin, full evidence `twin_full_nospeed` | twin, no evidence `twin_no_evidence_nospeed` | model alone `bare_llm_nospeed` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 18 of 30 (60 %, 95 % CI 42–75 %) | 20 of 30 (67 %, 95 % CI 49–81 %) | 3 of 29 (10 %, 95 % CI 4–26 %) | 10 of 30 (33 %, 95 % CI 19–51 %) | 20 of 30 (67 %, 95 % CI 49–81 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| race-free verified parallel program, any coverage | 26 of 30 (87 %, 95 % CI 70–95 %) | 25 of 30 (83 %, 95 % CI 66–93 %) | 3 of 29 (10 %, 95 % CI 4–26 %) | 11 of 30 (37 %, 95 % CI 22–54 %) | 20 of 30 (67 %, 95 % CI 49–81 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| FASTER (≥ 1.1×, reported beside) | 8 of 30 (27 %, 95 % CI 14–44 %) | 12 of 30 (40 %, 95 % CI 25–58 %) | 2 of 29 (7 %, 95 % CI 2–22 %) | 9 of 30 (30 %, 95 % CI 17–48 %) | 10 of 30 (33 %, 95 % CI 19–51 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 30 (0 %, 95 % CI 0–11 %) | 1 of 30 (3 %, 95 % CI 1–17 %) | 22 of 29 (76 %, 95 % CI 58–88 %) | 13 of 30 (43 %, 95 % CI 27–61 %) | 9 of 30 (30 %, 95 % CI 17–48 %) | 0 of 9 (0 %, 95 % CI 0–30 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 18 | 20 | 3 | 10 | 20 | 0 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 8 | 5 | 0 | 1 | 0 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | 0 | 0 | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | 0 | 1 | 4 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 1 | 20 | 11 | 5 | 0 |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | 2 | 1 | 0 | 0 |
| changed, not parallel | 0 | 0 | 4 | 6 | 0 | 0 |
| left unchanged | 4 | 4 | 0 | 0 | 1 | 9 |
| correct but slower (< 0.91×; not unsafe) | 14 | 6 | 1 | 2 | 10 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | 1 | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 | 0 | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `rodinia_b1/bfs` | 2 / 0 / 10 | 3 / 1 / 10 | 0 / 10 / 10 | 0 / 9 / 10 | 8 / 2 / 10 | 0 / 0 / 3 |
| `tsvc_b1/s151` | 10 / 0 / 10 | 10 / 0 / 10 | 2 / 3 / 9 | 5 / 1 / 10 | 8 / 1 / 10 | 0 / 0 / 3 |
| `tsvc_b1/s161` | 6 / 0 / 10 | 7 / 0 / 10 | 1 / 9 / 10 | 5 / 3 / 10 | 4 / 6 / 10 | 0 / 0 / 3 |

The model alone (`bare_llm_nospeed`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `rodinia_b1/bfs` | 0 / 0 / 3 | 8 of 10 | 2 | 0 | 0 |
| `tsvc_b1/s151` | 0 / 0 / 3 | 8 of 10 | 1 | 1 | 0 |
| `tsvc_b1/s161` | 0 / 0 / 3 | 4 of 10 | 6 | 0 | 0 |
- Unsafe programs, agent, no evidence: rodinia_b1/bfs e2b1_a_2 rep8: BROKEN.
- Unsafe programs, twin, full evidence: rodinia_b1/bfs e2b1_a_2 rep1: BROKEN; rodinia_b1/bfs e2b1_a_2 rep2: BROKEN; rodinia_b1/bfs e2b1_a_2 rep3: BROKEN; rodinia_b1/bfs e2b1_a_2 rep4: BROKEN; rodinia_b1/bfs e2b1_a_2 rep5: BROKEN; rodinia_b1/bfs e2b1_a_2 rep6: BROKEN; rodinia_b1/bfs e2b1_a_2 rep7: BROKEN; rodinia_b1/bfs e2b1_a_2 rep8: BROKEN; rodinia_b1/bfs e2b1_a_2 rep9: BROKEN; rodinia_b1/bfs e2b1_a_2 rep10: BROKEN; tsvc_b1/s151 e2b1_a_1 rep5: BROKEN; tsvc_b1/s151 e2b1_a_1 rep7: BROKEN; tsvc_b1/s151 e2b1_a_1 rep8: BROKEN; tsvc_b1/s161 e2b1_a_1 rep1: BROKEN; tsvc_b1/s161 e2b1_a_1 rep3: did-not-compile; tsvc_b1/s161 e2b1_a_1 rep4: BROKEN; tsvc_b1/s161 e2b1_a_1 rep5: BROKEN; tsvc_b1/s161 e2b1_a_1 rep6: BROKEN; tsvc_b1/s161 e2b1_a_1 rep7: BROKEN; tsvc_b1/s161 e2b1_a_1 rep8: BROKEN; tsvc_b1/s161 e2b1_a_1 rep9: BROKEN; tsvc_b1/s161 e2b1_a_1 rep10: did-not-compile.
- Harness edits, twin, full evidence (not counted): tsvc_b1/s151 e2b1_a_1 rep3.
- Unsafe programs, twin, no evidence: rodinia_b1/bfs e2b1_a_2 rep1: BROKEN; rodinia_b1/bfs e2b1_a_2 rep2: racy; rodinia_b1/bfs e2b1_a_2 rep3: BROKEN; rodinia_b1/bfs e2b1_a_2 rep4: did-not-compile; rodinia_b1/bfs e2b1_a_2 rep5: BROKEN; rodinia_b1/bfs e2b1_a_2 rep6: BROKEN; rodinia_b1/bfs e2b1_a_2 rep7: BROKEN; rodinia_b1/bfs e2b1_a_2 rep8: BROKEN; rodinia_b1/bfs e2b1_a_2 rep10: BROKEN; tsvc_b1/s151 e2b1_a_1 rep7: BROKEN; tsvc_b1/s161 e2b1_a_1 rep1: BROKEN; tsvc_b1/s161 e2b1_a_1 rep2: BROKEN; tsvc_b1/s161 e2b1_a_1 rep5: BROKEN.
- Unsafe programs, model alone: rodinia_b1/bfs e2b1_bare_m3_bfs rep1: racy; rodinia_b1/bfs e2b1_bare_m3_bfs rep7: racy; tsvc_b1/s151 e2b1_bare_m3_a rep1: BROKEN; tsvc_b1/s161 e2b1_bare_m3_a rep3: BROKEN; tsvc_b1/s161 e2b1_bare_m3_a rep4: racy; tsvc_b1/s161 e2b1_bare_m3_a rep6: racy; tsvc_b1/s161 e2b1_bare_m3_a rep8: BROKEN; tsvc_b1/s161 e2b1_bare_m3_a rep9: BROKEN; tsvc_b1/s161 e2b1_bare_m3_a rep10: BROKEN.

## direction (a), tier 2 — descriptive (reported apart) — 2 loops: `tsvc_b1/s131`, `tsvc_b1/s424`

| per arm | agent, full evidence `full_b1_nospeed` | agent, no evidence `no_evidence_b1_nospeed` | twin, full evidence `twin_full_nospeed` | twin, no evidence `twin_no_evidence_nospeed` | model alone `bare_llm_nospeed` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 13 of 20 (65 %, 95 % CI 43–82 %) | 10 of 20 (50 %, 95 % CI 30–70 %) | 12 of 20 (60 %, 95 % CI 39–78 %) | 11 of 20 (55 %, 95 % CI 34–74 %) | 4 of 20 (20 %, 95 % CI 8–42 %) | 0 of 6 (0 %, 95 % CI 0–39 %) |
| race-free verified parallel program, any coverage | 14 of 20 (70 %, 95 % CI 48–85 %) | 10 of 20 (50 %, 95 % CI 30–70 %) | 12 of 20 (60 %, 95 % CI 39–78 %) | 11 of 20 (55 %, 95 % CI 34–74 %) | 6 of 20 (30 %, 95 % CI 15–52 %) | 0 of 6 (0 %, 95 % CI 0–39 %) |
| FASTER (≥ 1.1×, reported beside) | 5 of 20 (25 %, 95 % CI 11–47 %) | 5 of 20 (25 %, 95 % CI 11–47 %) | 7 of 20 (35 %, 95 % CI 18–57 %) | 5 of 20 (25 %, 95 % CI 11–47 %) | 2 of 20 (10 %, 95 % CI 3–30 %) | 0 of 6 (0 %, 95 % CI 0–39 %) |
| **unsafe** (BROKEN, racy, not compiling) | 0 of 20 (0 %, 95 % CI 0–16 %) | 0 of 20 (0 %, 95 % CI 0–16 %) | 5 of 20 (25 %, 95 % CI 11–47 %) | 3 of 20 (15 %, 95 % CI 5–36 %) | 13 of 20 (65 %, 95 % CI 43–82 %) | 0 of 6 (0 %, 95 % CI 0–39 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 13 | 10 | 12 | 11 | 4 | 0 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 1 | 0 | 0 | 0 | 2 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | 0 | 0 | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 0 | 0 | 5 | 3 | 13 | 0 |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | 2 | 0 | 0 | 0 | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| changed, not parallel | 0 | 0 | 3 | 6 | 0 | 0 |
| left unchanged | 4 | 10 | 0 | 0 | 1 | 6 |
| correct but slower (< 0.91×; not unsafe) | 11 | 5 | 4 | 6 | 4 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | 0 | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 | 0 | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_b1/s131` | 9 / 0 / 10 | 10 / 0 / 10 | 10 / 0 / 10 | 10 / 0 / 10 | 4 / 4 / 10 | 0 / 0 / 3 |
| `tsvc_b1/s424` | 4 / 0 / 10 | 0 / 0 / 10 | 2 / 5 / 10 | 1 / 3 / 10 | 0 / 9 / 10 | 0 / 0 / 3 |

The model alone (`bare_llm_nospeed`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_b1/s131` | 0 / 0 / 3 | 4 of 10 | 4 | 2 | 0 |
| `tsvc_b1/s424` | 0 / 0 / 3 | 0 of 10 | 9 | 1 | 0 |
- Unsafe programs, twin, full evidence: tsvc_b1/s424 e2b1_a_3 rep1: BROKEN; tsvc_b1/s424 e2b1_a_3 rep3: BROKEN; tsvc_b1/s424 e2b1_a_3 rep4: BROKEN; tsvc_b1/s424 e2b1_a_3 rep5: BROKEN; tsvc_b1/s424 e2b1_a_3 rep10: BROKEN.
- Unsafe programs, twin, no evidence: tsvc_b1/s424 e2b1_a_3 rep2: BROKEN; tsvc_b1/s424 e2b1_a_3 rep3: BROKEN; tsvc_b1/s424 e2b1_a_3 rep9: BROKEN.
- Unsafe programs, model alone: tsvc_b1/s131 e2b1_bare_m3_a rep3: BROKEN; tsvc_b1/s131 e2b1_bare_m3_a rep7: BROKEN; tsvc_b1/s131 e2b1_bare_m3_a rep8: BROKEN; tsvc_b1/s131 e2b1_bare_m3_a rep10: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep1: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep2: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep3: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep4: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep5: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep6: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep8: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep9: BROKEN; tsvc_b1/s424 e2b1_bare_m3_a rep10: BROKEN.

## direction (b) — descriptive — 5 loops: `tsvc_b1/s152`, `tsvc_b1/s171`, `tsvc_b1/s277`, `tsvc_b1/s481`, `tsvc_b1/vas`

| per arm | agent, full evidence `full_b1_nospeed` | agent, no evidence `no_evidence_b1_nospeed` | twin, full evidence `twin_full_nospeed` | twin, no evidence `twin_no_evidence_nospeed` | model alone `bare_llm_nospeed` | DiscoPoP alone (selected on) `discopop_capability` |
|---|---:|---:|---:|---:|---:|---:|
| **primary outcome** (covers the hot loop) | 21 of 25 (84 %, 95 % CI 65–94 %) | 23 of 25 (92 %, 95 % CI 75–98 %) | 13 of 22 (59 %, 95 % CI 39–77 %) | 19 of 25 (76 %, 95 % CI 57–89 %) | 20 of 25 (80 %, 95 % CI 61–91 %) | 15 of 15 (100 %, 95 % CI 80–100 %) |
| race-free verified parallel program, any coverage | 22 of 25 (88 %, 95 % CI 70–96 %) | 25 of 25 (100 %, 95 % CI 87–100 %) | 15 of 22 (68 %, 95 % CI 47–84 %) | 19 of 25 (76 %, 95 % CI 57–89 %) | 21 of 25 (84 %, 95 % CI 65–94 %) | 15 of 15 (100 %, 95 % CI 80–100 %) |
| FASTER (≥ 1.1×, reported beside) | 12 of 25 (48 %, 95 % CI 30–67 %) | 19 of 25 (76 %, 95 % CI 57–89 %) | 10 of 22 (45 %, 95 % CI 27–65 %) | 16 of 25 (64 %, 95 % CI 45–80 %) | 19 of 25 (76 %, 95 % CI 57–89 %) | 15 of 15 (100 %, 95 % CI 80–100 %) |
| **unsafe** (BROKEN, racy, not compiling) | 1 of 25 (4 %, 95 % CI 1–20 %) | 0 of 25 (0 %, 95 % CI 0–13 %) | 7 of 22 (32 %, 95 % CI 16–53 %) | 6 of 25 (24 %, 95 % CI 11–43 %) | 4 of 25 (16 %, 95 % CI 6–35 %) | 0 of 15 (0 %, 95 % CI 0–20 %) |
| race-free verified parallel program covering the hot loop (PRIMARY) | 21 | 23 | 13 | 19 | 20 | 15 |
| race-free verified parallel program, coverage not recorded — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| race-free verified parallel program, the hot loop not covered | 1 | 2 | 2 | 0 | 1 | 0 |
| verified parallel program, no race verdict (model-only arm) — not a success | 0 | 0 | 0 | 0 | 0 | 0 |
| verified parallel program the race check could not judge | 0 | 0 | 0 | 0 | 0 | 0 |
| racy (TSan or the schedule matrix) — unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| BROKEN (wrong output shipped, or a crash at the verification size) — unsafe | 1 | 0 | 5 | 4 | 0 | 0 |
| correct, but a verification run did not finish at one thread count (verified exact at another) — correct but slower: reported, not unsafe | 0 | 0 | 0 | 0 | 0 | 0 |
| shipped a program that does not compile — unsafe | 0 | 0 | 2 | 2 | 4 | 0 |
| changed, not parallel | 0 | 0 | 0 | 0 | 0 | 0 |
| left unchanged | 2 | 0 | 0 | 0 | 0 | 0 |
| correct but slower (< 0.91×; not unsafe) | 9 | 6 | 4 | 3 | 2 | 0 |
| touched the harness — own row, no valid measurement | 0 | 0 | 3 | 0 | 0 | 0 |
| no verdict | 0 | 0 | 0 | 0 | 0 | 0 |

| loop: success / unsafe / with a verdict | agent, full evidence | agent, no evidence | twin, full evidence | twin, no evidence | model alone | DiscoPoP alone (selected on) |
|---|---:|---:|---:|---:|---:|---:|
| `tsvc_b1/s152` | 3 / 0 / 5 | 5 / 0 / 5 | 4 / 1 / 5 | 5 / 0 / 5 | 5 / 0 / 5 | 3 / 0 / 3 |
| `tsvc_b1/s171` | 3 / 1 / 5 | 3 / 0 / 5 | 1 / 2 / 4 | 4 / 1 / 5 | 2 / 3 / 5 | 3 / 0 / 3 |
| `tsvc_b1/s277` | 5 / 0 / 5 | 5 / 0 / 5 | 4 / 0 / 5 | 4 / 1 / 5 | 3 / 1 / 5 | 3 / 0 / 3 |
| `tsvc_b1/s481` | 5 / 0 / 5 | 5 / 0 / 5 | 1 / 4 / 5 | 1 / 4 / 5 | 5 / 0 / 5 | 3 / 0 / 3 |
| `tsvc_b1/vas` | 5 / 0 / 5 | 5 / 0 / 5 | 3 / 0 / 3 | 5 / 0 / 5 | 5 / 0 / 5 | 3 / 0 / 3 |

The model alone (`bare_llm_nospeed`) against DiscoPoP alone (`discopop_capability`, **selected on** — the unit was admitted because of what DiscoPoP alone does on it; no test):

| loop | DiscoPoP alone: primary / parallel / with a verdict | model alone: correctly (primary) | wrongly (unsafe) | not at all (unchanged, not parallel, hot loop not covered) | not established (coverage or race unknown) |
|---|---:|---:|---:|---:|---:|
| `tsvc_b1/s152` | 3 / 3 / 3 | 5 of 5 | 0 | 0 | 0 |
| `tsvc_b1/s171` | 3 / 3 / 3 | 2 of 5 | 3 | 0 | 0 |
| `tsvc_b1/s277` | 3 / 3 / 3 | 3 of 5 | 1 | 1 | 0 |
| `tsvc_b1/s481` | 3 / 3 / 3 | 5 of 5 | 0 | 0 | 0 |
| `tsvc_b1/vas` | 3 / 3 / 3 | 5 of 5 | 0 | 0 | 0 |
- Unsafe programs, agent, full evidence: tsvc_b1/s171 e2b1_b_1 rep5: BROKEN.
- Unsafe programs, twin, full evidence: tsvc_b1/s152 e2b1_b_1 rep5: BROKEN; tsvc_b1/s171 e2b1_b_1 rep2: BROKEN; tsvc_b1/s171 e2b1_b_1 rep3: BROKEN; tsvc_b1/s481 e2b1_b_1 rep1: did-not-compile; tsvc_b1/s481 e2b1_b_1 rep2: BROKEN; tsvc_b1/s481 e2b1_b_1 rep4: did-not-compile; tsvc_b1/s481 e2b1_b_1 rep5: BROKEN.
- Harness edits, twin, full evidence (not counted): tsvc_b1/s171 e2b1_b_1 rep1; tsvc_b1/vas e2b1_b_1 rep1; tsvc_b1/vas e2b1_b_1 rep3.
- Unsafe programs, twin, no evidence: tsvc_b1/s171 e2b1_b_1 rep5: BROKEN; tsvc_b1/s277 e2b1_b_1 rep2: did-not-compile; tsvc_b1/s481 e2b1_b_1 rep1: BROKEN; tsvc_b1/s481 e2b1_b_1 rep2: BROKEN; tsvc_b1/s481 e2b1_b_1 rep4: did-not-compile; tsvc_b1/s481 e2b1_b_1 rep5: BROKEN.
- Unsafe programs, model alone: tsvc_b1/s171 e2b1_bare_m3_b rep2: did-not-compile; tsvc_b1/s171 e2b1_bare_m3_b rep3: did-not-compile; tsvc_b1/s171 e2b1_bare_m3_b rep4: did-not-compile; tsvc_b1/s277 e2b1_bare_m3_b rep5: did-not-compile.

## Completeness — trials with a verdict against the plan (a silently missing trial biases what is left)

- `tsvc_b1/s151` · `twin_full_nospeed`: 9 of 10 planned (10 found)
- `tsvc_b1/s171` · `twin_full_nospeed`: 4 of 5 planned (5 found)
- `tsvc_b1/vas` · `twin_full_nospeed`: 3 of 5 planned (5 found)

Trials outside the population or the named arms (not analysed): tsvc_b1/s482 · discopop_capability ×3.
