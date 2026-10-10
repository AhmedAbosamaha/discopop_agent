| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s314 | default_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 916.4 |
| tsvc_c4/s314 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s314 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.96x | 0+1 | 1 | 0 | 1 | 139.0 |
