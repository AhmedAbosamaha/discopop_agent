| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c1/s000 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 3.65x | —+— | — | — | 1 | 15.8 |
| tsvc_c1/s000 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.54x | —+— | — | — | 1 | 22.8 |
| tsvc_c1/s000 | bare_llm_v4 | claude-opus-5-5 | 1 | FASTER | 3.66x | —+— | — | — | 1 | 15.4 |
| tsvc_c1/s000 | bare_llm_v4 | claude-sonnet-5 | 1 | FASTER | 3.42x | —+— | — | — | 1 | 14.4 |
| tsvc_c1/s000 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.57x | 1+0 | 1 | 1 | 1 | 168.7 |
| tsvc_c1/s000 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.60x | 1+0 | 0 | 1 | 0 | 49.1 |
| tsvc_c1/s211 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 2.20x | —+— | — | — | 1 | 54.4 |
| tsvc_c1/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 0.80x | —+— | — | — | 1 | 89.6 |
| tsvc_c1/s211 | bare_llm_v4 | claude-opus-5-5 | 1 | parallel-not-faster | 0.95x | —+— | — | — | 1 | 27.3 |
| tsvc_c1/s211 | bare_llm_v4 | claude-sonnet-5 | 1 | parallel-not-faster | 0.64x | —+— | — | — | 1 | 47.2 |
| tsvc_c1/s211 | default_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.04x | 1+0 | 1 | 0 | 1 | 195.9 |
| tsvc_c1/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.3 |
