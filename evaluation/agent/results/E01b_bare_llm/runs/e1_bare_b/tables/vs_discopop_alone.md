| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 45 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 45 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm | claude-haiku-4-5-20251001 | 9 | 45 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 45 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.90x | — | 5 no-baseline |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.84x | — | 5 no-baseline |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.31x | — | 5 no-baseline |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.05x | — | 5 no-baseline |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.77x | — | 5 no-baseline |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.91x | — | 5 no-baseline |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.95x | — | 5 no-baseline |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 5.44x | — | 5 no-baseline |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.63x | — | 5 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
