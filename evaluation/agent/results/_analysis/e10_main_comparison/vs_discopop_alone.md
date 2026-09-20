| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | claude-haiku-4-5-20251001 | 21 | 1 | 1 | 4 | 5 | 5 | 0 | 4 | 1 | 0 | 0 | 0 | 0.99x (n=20) |
| speed_gate_large | claude-haiku-4-5-20251001 | 21 | 2 | 0 | 6 | 2 | 4 | 0 | 7 | 0 | 0 | 0 | 0 | 1.00x (n=21) |
| speed_gate_small | claude-haiku-4-5-20251001 | 21 | 0 | 0 | 0 | 0 | 2 | 10 | 9 | 0 | 0 | 0 | 0 | 1.00x (n=21) |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| polybench/2mm | full | claude-haiku-4-5-20251001 | FASTER,FASTER,FASTER · 10.31x | FASTER,FASTER,FASTER · 10.15x | 0.98x | 2 equal, 1 worse |
| polybench/2mm | speed_gate_large | claude-haiku-4-5-20251001 | FASTER,FASTER,FASTER · 10.31x | FASTER,FASTER,FASTER · 10.24x | 0.99x | 2 equal, 1 worse |
| polybench/2mm | speed_gate_small | claude-haiku-4-5-20251001 | FASTER,FASTER,FASTER · 10.31x | FASTER,FASTER,no-change · 6.78x | 0.66x | 2 worse, 1 lost |
| polybench/floyd-warshall | full | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,FASTER,no-change · 2.83x | 2.83x | 1 gained, 1 neither, 1 unsafe |
| polybench/floyd-warshall | speed_gate_large | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change · 1.87x | 1.87x | 2 gained, 1 neither |
| polybench/floyd-warshall | speed_gate_small | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| polybench/jacobi-2d-imper | full | claude-haiku-4-5-20251001 | FASTER,FASTER,FASTER · 5.89x | FASTER,FASTER,FASTER · 2.53x | 0.43x | 1 equal, 2 worse |
| polybench/jacobi-2d-imper | speed_gate_large | claude-haiku-4-5-20251001 | FASTER,FASTER,FASTER · 5.89x | FASTER,FASTER,FASTER · 2.57x | 0.44x | 3 worse |
| polybench/jacobi-2d-imper | speed_gate_small | claude-haiku-4-5-20251001 | FASTER,FASTER,FASTER · 5.89x | no-change,no-change,no-change · 1.00x | 0.17x | 3 lost |
| polybench/lu | full | claude-haiku-4-5-20251001 | parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.21x | FASTER,FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 2.81x | 13.26x | 4 better, 2 equal |
| polybench/lu | speed_gate_large | claude-haiku-4-5-20251001 | parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.21x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 2.59x | 12.23x | 6 better |
| polybench/lu | speed_gate_small | claude-haiku-4-5-20251001 | parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.21x | no-change,no-change,no-change,no-change,no-change,no-change · 1.00x | 4.72x | 6 lost |
| polybench/seidel-2d | full | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| polybench/seidel-2d | speed_gate_large | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| polybench/seidel-2d | speed_gate_small | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| rodinia-3.1/hotspot | full | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.09x | 0.09x | 1 gained-not-faster, 2 worse |
| rodinia-3.1/hotspot | speed_gate_large | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |
| rodinia-3.1/hotspot | speed_gate_small | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change · 1.00x | 1.00x | 3 neither |

**Speed ratios withheld for 1 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
