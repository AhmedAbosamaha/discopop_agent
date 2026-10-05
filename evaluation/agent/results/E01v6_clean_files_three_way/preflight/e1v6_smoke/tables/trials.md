| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s000 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 3.44x | —+— | — | — | 1 | 32.7 |
| tsvc_c2/s000 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.43x | —+— | — | — | 1 | 31.5 |
| tsvc_c2/s000 | bare_llm_v4 | claude-opus-5-5 | 1 | FASTER | 3.48x | —+— | — | — | 1 | 16.9 |
| tsvc_c2/s000 | bare_llm_v4 | claude-sonnet-5 | 1 | FASTER | 3.44x | —+— | — | — | 1 | 14.2 |
| tsvc_c2/s000 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.52x | 1+0 | 0 | 1 | 7 | 812.6 |
| tsvc_c2/s000 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.46x | 1+0 | 0 | 1 | 0 | 49.1 |
| tsvc_c2/s211 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 2.18x | —+— | — | — | 1 | 54.0 |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.97x | —+— | — | — | 1 | 332.5 |
| tsvc_c2/s211 | bare_llm_v4 | claude-opus-5-5 | 1 | FASTER | 2.17x | —+— | — | — | 1 | 29.2 |
| tsvc_c2/s211 | bare_llm_v4 | claude-sonnet-5 | 1 | FASTER | 2.40x | —+— | — | — | 1 | 69.0 |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.37x | 2+0 | 1 | 0 | 3 | 264.4 |
| tsvc_c2/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 7.6 |
