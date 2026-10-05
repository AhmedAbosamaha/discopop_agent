| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 90 | 44 | 2 | 0 | 0 | 0 | 0 | 44 | 0 | 0 | 0 | 0 | 1.08x (n=90) |
| bare_llm | claude-haiku-4-5-20251001 | 90 | 58 | 1 | 0 | 0 | 12 | 0 | 0 | 17 | 2 | 0 | 0 | 2.78x (n=71) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | default | claude-haiku-4-5-20251001 | 18 | 90 | 44 | 2 | 0 | 0 | 0 | 0 | 44 | 0 | 0 | 0 | 0 | 1.08x (n=90) |
| R | bare_llm | claude-haiku-4-5-20251001 | 18 | 90 | 58 | 1 | 0 | 0 | 12 | 0 | 0 | 17 | 2 | 0 | 0 | 2.78x (n=71) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s112 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 4.26x | 4.26x | 5 gained |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,parallel-not-faster · 1.00x | 1.00x | 1 gained, 1 gained-not-faster, 3 neither |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 1.36x | 1.36x | 3 gained, 2 neither |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,parallel-not-faster · 1.17x | 1.17x | 3 gained, 1 gained-not-faster, 1 neither |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 2.35x | 2.35x | 3 gained, 2 neither |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.80x | 3.80x | 5 gained |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 2.29x | 2.29x | 4 gained, 1 neither |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.76x | 3.76x | 5 gained |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.34x | 2.34x | 5 gained |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.30x | 3.30x | 5 gained |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.82x | 0.82x | 3 worse, 2 unsafe |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 1.39x | 1.39x | 3 gained, 2 worse |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,FASTER,FASTER,parallel-not-faster · 1.73x | 1.73x | 2 gained, 1 worse, 2 unsafe |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 4.19x | 4.19x | 5 gained |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 unsafe |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,FASTER,FASTER,FASTER · 2.41x | 2.41x | 4 gained, 1 unsafe |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,FASTER,parallel-not-faster · 1.36x | 1.36x | 1 gained, 1 worse, 3 unsafe |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,FASTER,FASTER,SCAFFOLD_MODIFIED · 2.14x | 2.14x | 3 gained, 1 unsafe, 1 invalid |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,FASTER,FASTER,VERIFY_FAILED · 4.20x | 4.20x | 3 gained, 1 unsafe, 1 invalid |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.90x | 0.90x | 1 gained, 1 gained-not-faster, 2 worse, 1 unsafe |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.84x | 3.84x | 5 gained |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.31x | 2.31x | 5 gained |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.05x | 3.05x | 5 gained |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.77x | 3.77x | 5 gained |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.91x | 3.91x | 5 gained |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.95x | 2.95x | 5 gained |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 5.44x | 5.44x | 5 gained |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.63x | 0.63x | 1 gained, 3 worse, 1 unsafe |

**Speed ratios withheld for 2 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
