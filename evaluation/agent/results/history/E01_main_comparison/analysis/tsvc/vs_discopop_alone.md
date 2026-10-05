| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 105 | 44 | 2 | 1 | 0 | 1 | 1 | 56 | 0 | 0 | 0 | 0 | 1.00x (n=105) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | default | claude-haiku-4-5-20251001 | 18 | 90 | 44 | 2 | 0 | 0 | 0 | 0 | 44 | 0 | 0 | 0 | 0 | 1.08x (n=90) |
| A | default | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0.58x (n=3) |
| D | default | claude-haiku-4-5-20251001 | 4 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 1.00x (n=12) |

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
| tsvc/s000 | default | claude-haiku-4-5-20251001 | FASTER · 4.03x | no-change · 1.00x | 0.25x | 1 lost |
| tsvc/s313 | default | claude-haiku-4-5-20251001 | FASTER · 5.55x | FASTER · 6.36x | 1.15x | 1 better |
| tsvc/vpvtv | default | claude-haiku-4-5-20251001 | FASTER · 4.08x | FASTER · 2.37x | 0.58x | 1 worse |
| tsvc/s3112 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc/s321 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc/s322 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| tsvc/s323 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
