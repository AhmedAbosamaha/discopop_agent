| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 8 | 472.7 |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.20x | 1+0 | 1 | 0 | 4 | 209.0 |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.10x | 1+0 | 1 | 0 | 8 | 494.4 |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.38x | 1+0 | 1 | 0 | 6 | 555.6 |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.16x | 1+0 | 1 | 0 | 6 | 514.5 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.6 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.6 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 20.31x | 0+3 | 1 | 0 | 2 | 178.5 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 17.32x | 0+2 | 1 | 0 | 1 | 262.9 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 5.55x | 0+2 | 1 | 0 | 3 | 375.2 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 6.53x | 0+1 | 1 | 0 | 1 | 117.0 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 19.67x | 0+3 | 1 | 0 | 2 | 166.4 |
