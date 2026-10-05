| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | full | claude-haiku-4-5-20251001 | 1 | FASTER | 3.41x | 0+2 | 1 | 4 | 4 | 358.7 |
| polybench/jacobi-2d-imper | full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.80x | 0+2 | 1 | 4 | 3 | 207.2 |
| polybench/seidel-2d | full | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 1.00x | 0+1 | 1 | 3 | 4 | 473.8 |
