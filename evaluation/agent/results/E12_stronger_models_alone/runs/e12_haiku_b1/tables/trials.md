| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 1.61x | —+— | — | — | 1 | 171.2 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 2.23x | —+— | — | — | 1 | 47.0 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 2.21x | —+— | — | — | 1 | 66.0 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.74x | —+— | — | — | 1 | 183.9 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.79x | —+— | — | — | 1 | 170.7 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.48x | —+— | — | — | 1 | 24.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.78x | —+— | — | — | 1 | 27.2 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.54x | —+— | — | — | 1 | 27.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.68x | —+— | — | — | 1 | 42.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 189.9 |
