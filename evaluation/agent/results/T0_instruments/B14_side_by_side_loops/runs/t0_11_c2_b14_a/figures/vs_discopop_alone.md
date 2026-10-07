| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | claude-haiku-4-5-20251001 | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 44 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | discopop_capability | claude-haiku-4-5-20251001 | 29 | 29 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 29 | — |
| A | discopop_capability | claude-haiku-4-5-20251001 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | — |
| D | discopop_capability | claude-haiku-4-5-20251001 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/k17 | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-speed-not-measurable · — | — | 1 no-baseline |
| tsvc_c2/k19 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/k23 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/k27 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/k31 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/k42 | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-speed-not-measurable · — | — | 1 no-baseline |
| tsvc_c2/k48 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/k53 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s000 | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 3.32x | — | 1 no-baseline |
| tsvc_c2/s112 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s121 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s1213 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s127 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s131 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s151 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s152 | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 3.60x | — | 1 no-baseline |
| tsvc_c2/s161 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s171 | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 3.37x | — | 1 no-baseline |
| tsvc_c2/s211 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s212 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s241 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s243 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s244 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s252 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s254 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s255 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s258 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s277 | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 3.78x | — | 1 no-baseline |
| tsvc_c2/s281 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s291 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s292 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s293 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s3112 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s313 | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 4.58x | — | 1 no-baseline |
| tsvc_c2/s321 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s322 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s323 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s331 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s341 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s424 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/s481 | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 3.71x | — | 1 no-baseline |
| tsvc_c2/s482 | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| tsvc_c2/vas | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 2.87x | — | 1 no-baseline |
| tsvc_c2/vpvtv | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 3.65x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
