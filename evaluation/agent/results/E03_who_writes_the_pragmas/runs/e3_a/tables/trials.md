| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s000 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 127.70x | 1+0 | 1 | 1 | 6 | 720.2 |
| tsvc_c2/s000 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.57x | 1+0 | 0 | 1 | 0 | 49.5 |
| tsvc_c2/s000 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.49x | 0+1 | 1 | 1 | 1 | 146.7 |
| tsvc_c2/vpvtv | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.59x | 1+0 | 0 | 1 | 3 | 435.1 |
| tsvc_c2/vpvtv | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.65x | 1+0 | 0 | 1 | 0 | 61.0 |
| tsvc_c2/vpvtv | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.63x | 0+1 | 1 | 1 | 1 | 212.4 |
| tsvc_c3/s313 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.62x | 1+0 | 0 | 1 | 1 | 208.9 |
| tsvc_c3/s313 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.60x | 1+0 | 0 | 1 | 0 | 59.6 |
| tsvc_c3/s313 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.63x | 1+0 | 0 | 1 | 1 | 196.0 |
