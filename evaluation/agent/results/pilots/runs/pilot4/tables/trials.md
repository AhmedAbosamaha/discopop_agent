| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | full | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 1.00x | 0+2 | 1 | 4 | 12 | 3173.8 |
| polybench/2mm | full | claude-haiku-4-5-20251001 | 1 | FASTER | 9.47x | 0+2 | 1 | 6 | 1 | 137.5 |
| polybench/floyd-warshall | full | claude-haiku-4-5-20251001 | 1 | FASTER | 2.92x | 0+1 | 1 | 3 | 2 | 233.6 |
| polybench/jacobi-2d-imper | full | claude-haiku-4-5-20251001 | 1 | FASTER | 5.85x | 0+2 | 1 | 5 | 1 | 129.2 |
| polybench/lu | full | claude-haiku-4-5-20251001 | 1 | FASTER | 2.85x | 0+2 | 1 | 0 | 1 | 75.8 |
| polybench/seidel-2d | full | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 3 | 299.0 |
| polybench/trisolv | full | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.44x | 0+1 | 1 | 2 | 1 | 88.0 |
| rodinia-3.1/hotspot | full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.08x | 1+0 | 0 | 6 | 1 | 1120.3 |
