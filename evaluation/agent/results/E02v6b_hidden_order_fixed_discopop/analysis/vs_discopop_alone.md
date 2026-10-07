| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 70 | 54 | 0 | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 0 | 0 | 3.06x (n=70) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | 60 | 54 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 3.18x (n=60) |
| D | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 1.00x (n=10) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 4.07x | 4.07x | 10 gained |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,no-change · 3.27x | 3.27x | 9 gained, 1 neither |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,no-change,no-change,no-change,no-change,no-change · 1.07x | 1.07x | 5 gained, 5 neither |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 3.06x | 3.06x | 10 gained |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 3.85x | 3.85x | 10 gained |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change,no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 10 neither |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 2.14x | 2.14x | 10 gained |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
