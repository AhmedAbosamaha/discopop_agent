| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 20 | 12 | 0 | 0 | 0 | 6 | 0 | 0 | 1 | 1 | 0 | 0 | 2.58x (n=18) |
| default | claude-haiku-4-5-20251001 | 20 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 1.23x (n=20) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm | claude-haiku-4-5-20251001 | 4 | 20 | 12 | 0 | 0 | 0 | 6 | 0 | 0 | 1 | 1 | 0 | 0 | 2.58x (n=18) |
| R | default | claude-haiku-4-5-20251001 | 4 | 20 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 1.23x (n=20) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.52x | 2.52x | 5 gained |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.61x | 2.61x | 5 gained |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.84x | 2.84x | 5 gained |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.87x | 2.87x | 5 gained |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,VERIFY_FAILED,parallel-not-faster,parallel-not-faster · 2.28x | 2.28x | 2 gained, 2 worse, 1 invalid |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.43x | 0.43x | 4 worse, 1 unsafe |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |

**Speed ratios withheld for 2 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
