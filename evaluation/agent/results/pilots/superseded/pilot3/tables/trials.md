| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | full | claude-haiku-4-5-20251001 | 1 | FASTER | 10.57x | 0+2 | 1 | 6 | 1 | 124.2 |
| polybench/floyd-warshall | full | claude-haiku-4-5-20251001 | 1 | BROKEN | — | 0+2 | 1 | 3 | 2 | 238.0 |
| polybench/jacobi-2d-imper | full | claude-haiku-4-5-20251001 | 1 | FASTER | 2.52x | 0+2 | 1 | 5 | 1 | 86.0 |
| rodinia-3.1/hotspot | full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.08x | 1+0 | 0 | 6 | 4 | 1699.9 |
