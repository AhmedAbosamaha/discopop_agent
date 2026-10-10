| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.68x | —+— | — | — | 1 | 71.8 |
| tsvc_c4/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 120.7 |
| tsvc_c4/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 171.7 |
| tsvc_c4/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.66x | —+— | — | — | 1 | 49.8 |
| tsvc_c4/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.43x | —+— | — | — | 1 | 88.1 |
