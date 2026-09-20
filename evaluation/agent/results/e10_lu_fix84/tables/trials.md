| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/lu | discopop_gate | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.21x | 1+0 | 0 | 2 | 0 | 5.7 |
| polybench/lu | discopop_gate | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.54x | 1+0 | 0 | 2 | 0 | 5.6 |
| polybench/lu | discopop_gate | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.21x | 1+0 | 0 | 2 | 0 | 5.6 |
| polybench/lu | full | claude-haiku-4-5-20251001 | 1 | FASTER | 2.72x | 0+2 | 1 | 2 | 1 | 161.7 |
| polybench/lu | full | claude-haiku-4-5-20251001 | 2 | FASTER | 2.90x | 0+2 | 1 | 2 | 1 | 132.1 |
| polybench/lu | full | claude-haiku-4-5-20251001 | 3 | FASTER | 10.17x | 0+2 | 1 | 2 | 1 | 98.1 |
| polybench/lu | speed_gate_large | claude-haiku-4-5-20251001 | 1 | FASTER | 2.80x | 0+2 | 1 | 2 | 1 | 135.7 |
| polybench/lu | speed_gate_large | claude-haiku-4-5-20251001 | 2 | FASTER | 4.21x | 0+2 | 1 | 2 | 1 | 176.7 |
| polybench/lu | speed_gate_large | claude-haiku-4-5-20251001 | 3 | FASTER | 1.69x | 0+2 | 1 | 2 | 1 | 142.2 |
| polybench/lu | speed_gate_small | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 7 | 784.2 |
| polybench/lu | speed_gate_small | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 2 | 6 | 559.2 |
| polybench/lu | speed_gate_small | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 2 | 6 | 567.4 |
