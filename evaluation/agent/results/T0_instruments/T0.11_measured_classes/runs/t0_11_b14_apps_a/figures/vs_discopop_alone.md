| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | claude-haiku-4-5-20251001 | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | discopop_capability | claude-haiku-4-5-20251001 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | — |
| A | discopop_capability | claude-haiku-4-5-20251001 | 22 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 22 | — |
| unclassified | discopop_capability | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| burkardt/md | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| npb/is | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| polybench/2mm | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 9.59x | — | 1 no-baseline |
| polybench/3mm | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 9.43x | — | 1 no-baseline |
| polybench/adi | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 1.92x | — | 1 no-baseline |
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-speed-not-measurable · — | — | 1 no-baseline |
| polybench/bicg | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| polybench/correlation | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| polybench/covariance | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| polybench/doitgen | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| polybench/dynprog | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-not-faster · 0.97x | — | 1 no-baseline |
| polybench/fdtd-2d | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-not-faster · 0.60x | — | 1 no-baseline |
| polybench/fdtd-apml | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 3.44x | — | 1 no-baseline |
| polybench/floyd-warshall | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| polybench/gemm | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 6.36x | — | 1 no-baseline |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-speed-not-measurable · — | — | 1 no-baseline |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-speed-not-measurable · — | — | 1 no-baseline |
| polybench/gramschmidt | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-not-faster · 0.35x | — | 1 no-baseline |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-speed-not-measurable · — | — | 1 no-baseline |
| polybench/jacobi-2d-imper | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 3.63x | — | 1 no-baseline |
| polybench/lu | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-not-faster · 0.22x | — | 1 no-baseline |
| polybench/ludcmp | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 4.81x | — | 1 no-baseline |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-speed-not-measurable · — | — | 1 no-baseline |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | — · — | parallel-speed-not-measurable · — | — | 1 no-baseline |
| polybench/seidel-2d | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| polybench/symm | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 1.42x | — | 1 no-baseline |
| polybench/syr2k | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 8.03x | — | 1 no-baseline |
| polybench/syrk | discopop_capability | claude-haiku-4-5-20251001 | — · — | FASTER · 7.00x | — | 1 no-baseline |
| polybench/trisolv | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| rodinia-3.1/hotspot | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |
| rodinia-3.1/pathfinder | discopop_capability | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
