| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s1213 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.61x | 2+0 | 1 | 0 | 2 | 274.8 |
| tsvc_c2/s1213 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.80x | 3+0 | 1 | 0 | 4 | 568.6 |
| tsvc_c2/s1213 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.9 |
| tsvc_c2/s1213 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc_c2/s1213 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.55x | 0+2 | 1 | 0 | 1 | 233.4 |
| tsvc_c2/s1213 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.56x | 0+2 | 1 | 0 | 1 | 250.2 |
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.50x | 1+0 | 1 | 0 | 1 | 108.1 |
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.45x | 1+0 | 1 | 0 | 1 | 109.0 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.50x | 0+1 | 1 | 0 | 1 | 120.1 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.76x | 0+1 | 1 | 0 | 1 | 105.7 |
