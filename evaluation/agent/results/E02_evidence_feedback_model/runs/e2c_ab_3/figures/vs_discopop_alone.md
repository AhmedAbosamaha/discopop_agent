| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| no_evidence | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| twin_dp | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| twin_full | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| twin_no_evidence | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | full_b1 | claude-haiku-4-5-20251001 | 4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| R | no_evidence | claude-haiku-4-5-20251001 | 4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| R | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| R | twin_dp | claude-haiku-4-5-20251001 | 4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| R | twin_full | claude-haiku-4-5-20251001 | 4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| R | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s254 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.51x | — | 5 no-baseline |
| tsvc/s254 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.48x | — | 5 no-baseline |
| tsvc/s254 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.29x | — | 5 no-baseline |
| tsvc/s254 | twin_dp | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s254 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s254 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s255 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.77x | — | 5 no-baseline |
| tsvc/s255 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.52x | — | 5 no-baseline |
| tsvc/s255 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.77x | — | 5 no-baseline |
| tsvc/s255 | twin_dp | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s255 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s255 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,no-change,parallel-not-faster · 1.16x | — | 5 no-baseline |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 1.07x | — | 5 no-baseline |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,no-change,parallel-not-faster,parallel-not-faster · 1.09x | — | 5 no-baseline |
| tsvc/s281 | twin_dp | claude-haiku-4-5-20251001 | — · — | no-change,no-change,no-change,no-change,no-change · 1.00x | — | 5 no-baseline |
| tsvc/s281 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,FASTER · 3.20x | — | 5 no-baseline |
| tsvc/s281 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,parallel-not-faster · 2.17x | — | 5 no-baseline |
| tsvc/s291 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.56x | — | 5 no-baseline |
| tsvc/s291 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.42x | — | 5 no-baseline |
| tsvc/s291 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.79x | — | 5 no-baseline |
| tsvc/s291 | twin_dp | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s291 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s291 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
