| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.26x | 1+0 | 1 | 0 | 4 | 471.5 |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.28x | 1+0 | 1 | 0 | 1 | 213.5 |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 9.66x | 1+0 | 1 | 0 | 4 | 356.3 |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1023.9 |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.26x | 1+0 | 1 | 0 | 1 | 235.0 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.6 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 9.00x | 0+1 | 1 | 0 | 2 | 319.9 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 8.99x | 0+1 | 1 | 0 | 3 | 450.9 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 9.04x | 0+1 | 1 | 0 | 1 | 117.9 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 9.03x | 0+1 | 1 | 0 | 1 | 139.3 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 8.94x | 0+1 | 1 | 0 | 1 | 151.2 |
