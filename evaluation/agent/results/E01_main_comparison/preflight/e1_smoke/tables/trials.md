| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/floyd-warshall | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 3 | 1 | 172.2 |
| polybench/floyd-warshall | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 3 | 0 | 18.4 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 251.2 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 1 | 0 | 31.3 |
