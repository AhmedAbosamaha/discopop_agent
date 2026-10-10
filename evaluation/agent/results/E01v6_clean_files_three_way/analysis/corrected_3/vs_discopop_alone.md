| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v4 | claude-haiku-4-5-20251001 | 105 | 75 | 6 | 1 | 1 | 1 | 0 | 21 | 0 | 0 | 0 | 0 | 1.45x (n=105) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | default_v4 | claude-haiku-4-5-20251001 | 18 | 90 | 75 | 6 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 2.06x (n=90) |
| A | default_v4 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.98x (n=3) |
| D | default_v4 | claude-haiku-4-5-20251001 | 4 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 1.00x (n=12) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/s112 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 1.40x | 1.40x | 5 gained |
| tsvc_c2/s121 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 1.39x | 1.39x | 4 gained, 1 gained-not-faster |
| tsvc_c2/s1213 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.47x | 2.47x | 5 gained |
| tsvc_c2/s127 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.74x | 3.74x | 5 gained |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 1.15x | 1.15x | 4 gained, 1 gained-not-faster |
| tsvc_c2/s212 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 1.37x | 1.37x | 5 gained |
| tsvc_c2/s243 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 1.21x | 1.21x | 5 gained |
| tsvc_c2/s244 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 4.95x | 4.95x | 5 gained |
| tsvc_c2/s252 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster · 1.01x | 1.01x | 2 gained, 3 gained-not-faster |
| tsvc_c2/s254 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.36x | 3.36x | 5 gained |
| tsvc_c2/s255 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.49x | 2.49x | 5 gained |
| tsvc_c2/s291 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.46x | 3.46x | 5 gained |
| tsvc_c2/s292 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.93x | 2.93x | 5 gained |
| tsvc_c2/s293 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.00x | 3.00x | 5 gained |
| tsvc_c2/s000 | default_v4 | claude-haiku-4-5-20251001 | FASTER · 3.67x | FASTER · 2.86x | 0.78x | 1 worse |
| tsvc_c2/vpvtv | default_v4 | claude-haiku-4-5-20251001 | FASTER · 3.41x | FASTER · 3.96x | 1.16x | 1 better |
| tsvc_c2/s3112 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc_c2/s321 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc_c2/s322 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc_c2/s323 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.30x | 3.30x | 5 gained |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,parallel-not-faster · 1.00x | 1.00x | 1 gained-not-faster, 4 neither |
| tsvc_c3/s313 | default_v4 | claude-haiku-4-5-20251001 | FASTER · 4.65x | FASTER · 4.58x | 0.98x | 1 equal |
| tsvc_c3/s241 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 1.40x | 1.40x | 5 gained |
| tsvc_c4/s341 | default_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
