| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/floyd-warshall | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 3 | 490.9 |
| polybench/floyd-warshall | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 3 | 0 | 18.4 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 1 | 358.4 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 7.7 |
