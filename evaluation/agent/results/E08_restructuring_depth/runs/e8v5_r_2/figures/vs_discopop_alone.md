| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| depth1_v5 | claude-haiku-4-5-20251001 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 18 | — |
| depth2_v5 | claude-haiku-4-5-20251001 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 18 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | depth1_v5 | claude-haiku-4-5-20251001 | 6 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 18 | — |
| R | depth2_v5 | claude-haiku-4-5-20251001 | 6 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 18 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/s121 | depth1_v5 | claude-haiku-4-5-20251001 | — · — | BROKEN,no-change,parallel-not-faster · 1.02x | — | 3 no-baseline |
| tsvc_c2/s121 | depth2_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,no-change,no-change · 1.00x | — | 3 no-baseline |
| tsvc_c2/s1213 | depth1_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER · 1.79x | — | 3 no-baseline |
| tsvc_c2/s1213 | depth2_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,no-change,no-change · 1.00x | — | 3 no-baseline |
| tsvc_c2/s244 | depth1_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,no-change · 3.13x | — | 3 no-baseline |
| tsvc_c2/s244 | depth2_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER · 3.31x | — | 3 no-baseline |
| tsvc_c2/s255 | depth1_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER · 2.62x | — | 3 no-baseline |
| tsvc_c2/s255 | depth2_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER · 2.61x | — | 3 no-baseline |
| tsvc_c2/s281 | depth1_v5 | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,no-change · 1.05x | — | 3 no-baseline |
| tsvc_c2/s281 | depth2_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,no-change · 1.66x | — | 3 no-baseline |
| tsvc_c2/s293 | depth1_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER · 2.89x | — | 3 no-baseline |
| tsvc_c2/s293 | depth2_v5 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER · 2.88x | — | 3 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
