| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 11 | 996.7 |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.08x | 1+0 | 1 | 1 | 9 | 911.2 |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 10 | 1274.2 |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 11 | 1138.8 |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 10 | 929.7 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 27.7 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.7 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.6 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 27.6 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.8 |
