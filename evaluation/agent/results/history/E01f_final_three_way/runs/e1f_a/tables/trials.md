| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s000 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.61x | 1+0 | 0 | 1 | 3 | 329.2 |
| tsvc_b1/s000 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.73x | 1+0 | 0 | 1 | 0 | 49.4 |
| tsvc_b1/s313 | default_v3 | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 147.01x | 1+0 | 1 | 1 | 1 | 205.7 |
| tsvc_b1/s313 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.61x | 1+0 | 0 | 1 | 0 | 59.9 |
| tsvc_b1/vpvtv | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.62x | 1+0 | 0 | 1 | 2 | 503.7 |
| tsvc_b1/vpvtv | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.95x | 1+0 | 0 | 1 | 0 | 61.0 |
