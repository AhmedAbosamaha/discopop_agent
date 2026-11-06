| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npbc_c1/cg | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | FASTER | 10.00x | —+— | — | — | 1 | 128.3 |
| npbc_c1/cg | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 8.53x | 11+0 | 0 | 20 | 7 | 1372.6 |
| npbc_c1/ep | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | FASTER | 6.19x | —+— | — | — | 1 | 230.8 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 7.93x | 0+3 | 1 | 5 | 4 | 650.5 |
