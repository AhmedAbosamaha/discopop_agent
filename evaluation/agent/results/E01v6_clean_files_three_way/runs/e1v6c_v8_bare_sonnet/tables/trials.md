| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s341 | bare_llm_v4 | claude-sonnet-5 | 1 | FASTER | 2.31x | —+— | — | — | 1 | 119.9 |
| tsvc_c4/s341 | bare_llm_v4 | claude-sonnet-5 | 2 | BROKEN | — | —+— | — | — | 1 | 169.9 |
| tsvc_c4/s341 | bare_llm_v4 | claude-sonnet-5 | 3 | parallel-not-faster | 0.60x | —+— | — | — | 1 | 92.1 |
| tsvc_c4/s341 | bare_llm_v4 | claude-sonnet-5 | 4 | FASTER | 1.64x | —+— | — | — | 1 | 120.7 |
| tsvc_c4/s341 | bare_llm_v4 | claude-sonnet-5 | 5 | BROKEN | — | —+— | — | — | 1 | 88.2 |
