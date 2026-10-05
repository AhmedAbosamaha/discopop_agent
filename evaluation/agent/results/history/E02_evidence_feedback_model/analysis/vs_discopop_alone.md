| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 90 | 44 | 3 | 0 | 0 | 17 | 0 | 2 | 16 | 8 | 0 | 0 | 2.45x (n=66) |
| full_b1 | claude-haiku-4-5-20251001 | 90 | 48 | 3 | 0 | 0 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 1.31x (n=90) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm | claude-haiku-4-5-20251001 | 18 | 90 | 44 | 3 | 0 | 0 | 17 | 0 | 2 | 16 | 8 | 0 | 0 | 2.45x (n=66) |
| R | full_b1 | claude-haiku-4-5-20251001 | 18 | 90 | 48 | 3 | 0 | 0 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 1.31x (n=90) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.70x | 0.70x | 4 worse, 1 unsafe |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,parallel-not-faster,parallel-not-faster · 0.69x | 0.69x | 2 worse, 3 unsafe |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,VERIFY_FAILED,VERIFY_FAILED · — | — | 3 unsafe, 2 invalid |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 3.72x | 3.72x | 4 gained, 1 neither |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,FASTER,VERIFY_FAILED · 1.56x | 1.56x | 1 gained, 3 unsafe, 1 invalid |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 1.32x | 1.32x | 5 gained |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,no-change,parallel-not-faster,parallel-not-faster · 1.00x | 1.00x | 1 gained-not-faster, 1 worse, 1 neither, 2 unsafe |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.36x | 0.36x | 1 gained-not-faster, 4 worse |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,FASTER,FASTER,FASTER · 3.52x | 3.52x | 4 gained, 1 unsafe |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,VERIFY_FAILED,parallel-not-faster · 2.04x | 2.04x | 3 gained, 1 gained-not-faster, 1 invalid |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 3.50x | 3.50x | 4 gained, 1 invalid |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 2.58x | 2.58x | 4 gained, 1 invalid |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,FASTER,FASTER,VERIFY_FAILED · 3.02x | 3.02x | 2 gained, 2 unsafe, 1 invalid |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.70x | 2.70x | 5 gained |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.52x | 2.52x | 5 gained |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.84x | 2.84x | 5 gained |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,VERIFY_FAILED,parallel-not-faster,parallel-not-faster · 2.28x | 2.28x | 2 gained, 2 worse, 1 invalid |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.43x | 0.43x | 4 worse, 1 unsafe |
| tsvc/s112 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc/s121 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s1213 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 2.47x | 2.47x | 4 gained, 1 neither |
| tsvc/s127 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.74x | 3.74x | 5 gained |
| tsvc/s211 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,parallel-not-faster · 1.00x | 1.00x | 1 gained, 1 gained-not-faster, 3 neither |
| tsvc/s212 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 1.29x | 1.29x | 3 gained, 2 neither |
| tsvc/s241 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc/s243 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,parallel-not-faster · 1.00x | 1.00x | 1 gained, 1 gained-not-faster, 3 neither |
| tsvc/s244 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s254 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.51x | 3.51x | 5 gained |
| tsvc/s255 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.77x | 2.77x | 5 gained |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,parallel-not-faster · 1.16x | 1.16x | 3 gained, 1 gained-not-faster, 1 neither |
| tsvc/s291 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.56x | 3.56x | 5 gained |
| tsvc/s292 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.44x | 3.44x | 5 gained |
| tsvc/s293 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.93x | 2.93x | 5 gained |
| tsvc/s331 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s341 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |

**Speed ratios withheld for 9 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
