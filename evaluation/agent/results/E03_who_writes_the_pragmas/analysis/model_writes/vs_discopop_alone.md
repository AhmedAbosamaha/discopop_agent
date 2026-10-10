| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 105 | 81 | 2 | 0 | 3 | 0 | 0 | 19 | 0 | 0 | 0 | 0 | 2.30x (n=105) |
| bare_llm_v4 | claude-haiku-4-5-20251001 | 105 | 41 | 2 | 0 | 2 | 10 | 0 | 1 | 25 | 24 | 0 | 0 | 2.69x (n=56) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 18 | 90 | 81 | 2 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 2.67x (n=90) |
| R | bare_llm_v4 | claude-haiku-4-5-20251001 | 18 | 90 | 41 | 2 | 0 | 0 | 10 | 0 | 0 | 17 | 20 | 0 | 0 | 2.89x (n=53) |
| A | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.99x (n=3) |
| A | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0.99x (n=2) |
| D | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 1.00x (n=12) |
| D | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 8 | 3 | 0 | 0 | 1.00x (n=1) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/s112 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 1.30x | 1.30x | 4 gained, 1 gained-not-faster |
| tsvc_c2/s121 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 1.38x | 1.38x | 5 gained |
| tsvc_c2/s1213 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.62x | 2.62x | 5 gained |
| tsvc_c2/s127 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.75x | 3.75x | 5 gained |
| tsvc_c2/s211 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.00x | 2.00x | 5 gained |
| tsvc_c2/s212 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.29x | 2.29x | 5 gained |
| tsvc_c2/s243 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 1.30x | 1.30x | 4 gained, 1 gained-not-faster |
| tsvc_c2/s244 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 3.59x | 3.59x | 4 gained, 1 neither |
| tsvc_c2/s252 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.62x | 3.62x | 5 gained |
| tsvc_c3/s241 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 1.30x | 1.30x | 3 gained, 2 neither |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.17x | 3.17x | 5 gained |
| tsvc_c2/s255 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.68x | 2.68x | 5 gained |
| tsvc_c2/s281 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.78x | 2.78x | 5 gained |
| tsvc_c2/s291 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.48x | 3.48x | 5 gained |
| tsvc_c2/s292 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.91x | 2.91x | 5 gained |
| tsvc_c2/s293 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.90x | 2.90x | 5 gained |
| tsvc_c2/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc_c3/s331 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 4.42x | 4.42x | 5 gained |
| tsvc_c2/s321 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc_c2/s322 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc_c2/s323 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc_c2/s3112 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc_c2/s000 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | FASTER · 3.57x | FASTER · 3.49x | 0.98x | 1 equal |
| tsvc_c2/vpvtv | llm_pragmas_v5 | claude-haiku-4-5-20251001 | FASTER · 3.65x | FASTER · 3.63x | 0.99x | 1 equal |
| tsvc_c3/s313 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | FASTER · 4.60x | FASTER · 4.63x | 1.01x | 1 equal |
| tsvc_c2/s000 | bare_llm_v4 | claude-haiku-4-5-20251001 | FASTER · 3.57x | VERIFY_FAILED · — | — | 1 invalid |
| tsvc_c2/s112 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,VERIFY_FAILED,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.65x | 0.65x | 3 worse, 1 unsafe, 1 invalid |
| tsvc_c2/s121 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.67x | 0.67x | 3 worse, 2 unsafe |
| tsvc_c2/s1213 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,FASTER,FASTER,VERIFY_FAILED · 2.57x | 2.57x | 2 gained, 2 unsafe, 1 invalid |
| tsvc_c2/s127 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.89x | 3.89x | 5 gained |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,VERIFY_FAILED,parallel-not-faster · 1.10x | 1.10x | 1 gained-not-faster, 3 unsafe, 1 invalid |
| tsvc_c2/s212 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,FASTER,FASTER · 1.73x | 1.73x | 2 gained, 3 unsafe |
| tsvc_c3/s241 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,VERIFY_FAILED,VERIFY_FAILED,parallel-not-faster · 1.20x | 1.20x | 1 gained, 1 worse, 1 unsafe, 2 invalid |
| tsvc_c2/s243 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,VERIFY_FAILED,VERIFY_FAILED,parallel-not-faster · 1.39x | 1.39x | 2 gained, 1 worse, 2 invalid |
| tsvc_c2/s244 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED · — | — | 2 unsafe, 3 invalid |
| tsvc_c2/s252 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,VERIFY_FAILED,parallel-not-faster · 2.92x | 2.92x | 3 gained, 1 gained-not-faster, 1 invalid |
| tsvc_c2/s254 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 3.43x | 3.43x | 4 gained, 1 invalid |
| tsvc_c2/s255 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,VERIFY_FAILED,VERIFY_FAILED · 2.55x | 2.55x | 3 gained, 2 invalid |
| tsvc_c2/s281 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,FASTER,FASTER,FASTER · 3.21x | 3.21x | 3 gained, 2 unsafe |
| tsvc_c2/s291 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 3.48x | 3.48x | 4 gained, 1 invalid |
| tsvc_c2/s292 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED · 2.93x | 2.93x | 1 gained, 4 invalid |
| tsvc_c2/s293 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.89x | 2.89x | 5 gained |
| tsvc_c2/s3112 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,VERIFY_FAILED,VERIFY_FAILED · — | — | 1 unsafe, 2 invalid |
| tsvc_c2/s321 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,VERIFY_FAILED,changed-not-parallel · 1.00x | 1.00x | 1 neither, 1 unsafe, 1 invalid |
| tsvc_c2/s322 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN · — | — | 3 unsafe |
| tsvc_c2/s323 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN · — | — | 3 unsafe |
| tsvc_c2/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,VERIFY_FAILED,parallel-not-faster,parallel-not-faster · 0.39x | 0.39x | 1 gained, 2 worse, 1 unsafe, 1 invalid |
| tsvc_c2/vpvtv | bare_llm_v4 | claude-haiku-4-5-20251001 | FASTER · 3.65x | FASTER · 3.62x | 0.99x | 1 equal |
| tsvc_c3/s313 | bare_llm_v4 | claude-haiku-4-5-20251001 | FASTER · 4.60x | FASTER · 4.52x | 0.98x | 1 equal |
| tsvc_c3/s331 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 4.43x | 4.43x | 5 gained |

**Speed ratios withheld for 24 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
