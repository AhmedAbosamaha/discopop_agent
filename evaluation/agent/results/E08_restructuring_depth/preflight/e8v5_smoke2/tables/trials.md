| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c5/s2251 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.96x | 2+0 | 2 | 0 | 4 | 650.4 |
| tsvc_c5/s2251 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 10 | 1109.4 |
