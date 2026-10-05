| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1 | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| no_evidence | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| twin_dp | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| twin_full | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| twin_no_evidence | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | full_b1 | claude-haiku-4-5-20251001 | 5 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| R | no_evidence | claude-haiku-4-5-20251001 | 5 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| R | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| R | twin_dp | claude-haiku-4-5-20251001 | 5 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| R | twin_full | claude-haiku-4-5-20251001 | 5 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| R | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s112 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,no-change,no-change,no-change,no-change · 1.00x | — | 5 no-baseline |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,no-change,no-change · 1.16x | — | 5 no-baseline |
| tsvc/s112 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,no-change,no-change,no-change · 1.00x | — | 5 no-baseline |
| tsvc/s112 | twin_dp | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s112 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,FASTER · 1.37x | — | 5 no-baseline |
| tsvc/s112 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,FASTER,FASTER,VERIFY_FAILED · 1.41x | — | 5 no-baseline |
| tsvc/s121 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,no-change,no-change,no-change · 1.00x | — | 5 no-baseline |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,no-change,no-change · 1.12x | — | 5 no-baseline |
| tsvc/s121 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,no-change,no-change,no-change · 1.00x | — | 5 no-baseline |
| tsvc/s121 | twin_dp | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s121 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,FASTER,FASTER,FASTER · 1.37x | — | 5 no-baseline |
| tsvc/s121 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,FASTER · 1.39x | — | 5 no-baseline |
| tsvc/s1213 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,no-change · 2.47x | — | 5 no-baseline |
| tsvc/s1213 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,no-change,no-change · 1.15x | — | 5 no-baseline |
| tsvc/s1213 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,no-change,no-change · 1.12x | — | 5 no-baseline |
| tsvc/s1213 | twin_dp | claude-haiku-4-5-20251001 | — · — | no-change,no-change,no-change,no-change,no-change · 1.00x | — | 5 no-baseline |
| tsvc/s1213 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,FASTER · 2.37x | — | 5 no-baseline |
| tsvc/s1213 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,FASTER,FASTER,FASTER · 2.52x | — | 5 no-baseline |
| tsvc/s127 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.74x | — | 5 no-baseline |
| tsvc/s127 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.76x | — | 5 no-baseline |
| tsvc/s127 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.88x | — | 5 no-baseline |
| tsvc/s127 | twin_dp | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s127 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s127 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s211 | full_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,no-change,no-change,no-change,parallel-not-faster · 1.00x | — | 5 no-baseline |
| tsvc/s211 | no_evidence | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,no-change,parallel-not-faster · 1.58x | — | 5 no-baseline |
| tsvc/s211 | no_evidence_b1 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,no-change,parallel-not-faster,parallel-not-faster · 1.09x | — | 5 no-baseline |
| tsvc/s211 | twin_dp | claude-haiku-4-5-20251001 | — · — | no-change,no-change,no-change,no-change,no-change · 1.00x | — | 5 no-baseline |
| tsvc/s211 | twin_full | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |
| tsvc/s211 | twin_no_evidence | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 5 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
