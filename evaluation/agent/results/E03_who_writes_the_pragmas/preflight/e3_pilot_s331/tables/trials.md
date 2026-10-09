| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c3/s331 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_c3/s331 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.53x | 0+1 | 1 | 0 | 1 | 185.5 |
