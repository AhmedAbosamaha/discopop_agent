| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | default | claude-haiku-4-5-20251001 | 1 | FASTER | 10.62x | 1+0 | 1 | 6 | 1 | 410.4 |
| polybench/2mm | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 9.49x | 2+0 | 0 | 6 | 0 | 330.5 |
| polybench/bicg | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 167.5 |
| polybench/bicg | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.7 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.06x | 1+0 | 1 | 0 | 2 | 387.5 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 7.6 |
| tsvc/s321 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1216.6 |
| tsvc/s321 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.8 |
