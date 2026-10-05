| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s000 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 4.57x | —+— | — | — | 1 | 33.5 |
| tsvc_b1/s000 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.38x | —+— | — | — | 1 | 30.5 |
| tsvc_b1/s000 | bare_llm_v3 | claude-opus-5-5 | 1 | FASTER | 4.48x | —+— | — | — | 1 | 15.1 |
| tsvc_b1/s000 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 4.55x | —+— | — | — | 1 | 41.4 |
| tsvc_b1/s000 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.49x | 1+0 | 0 | 1 | 4 | 275.5 |
| tsvc_b1/s000 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.46x | 1+0 | 0 | 1 | 0 | 48.0 |
| tsvc_b1/s211 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.76x | —+— | — | — | 1 | 63.6 |
| tsvc_b1/s211 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 178.4 |
| tsvc_b1/s211 | bare_llm_v3 | claude-opus-5-5 | 1 | FASTER | 2.79x | —+— | — | — | 1 | 37.3 |
| tsvc_b1/s211 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 2.86x | —+— | — | — | 1 | 123.7 |
| tsvc_b1/s211 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.54x | 2+0 | 1 | 0 | 5 | 754.9 |
| tsvc_b1/s211 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.3 |
