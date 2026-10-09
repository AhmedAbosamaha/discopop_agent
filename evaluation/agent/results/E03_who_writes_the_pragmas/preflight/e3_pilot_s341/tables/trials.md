| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.97x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.24x | 0+4 | 1 | 0 | 12 | 699.4 |
