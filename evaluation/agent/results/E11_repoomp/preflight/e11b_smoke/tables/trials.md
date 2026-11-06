| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | repoomp_release | none | 1 | parallel-not-faster | 1.00x | —+— | — | — | 6 | — |
| tsvc_c2/k23 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | BROKEN | 4.22x | —+— | — | — | 1 | 30.7 |
| tsvc_c2/k23 | expert_ref | none | 1 | FASTER | 3.46x | —+— | — | — | 0 | — |
| tsvc_c2/k23 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 3.42x | 0+2 | 1 | 0 | 1 | 361.9 |
| tsvc_c2/k23 | repoomp_release | none | 1 | parallel-not-faster | 1.01x | —+— | — | — | 12 | — |
