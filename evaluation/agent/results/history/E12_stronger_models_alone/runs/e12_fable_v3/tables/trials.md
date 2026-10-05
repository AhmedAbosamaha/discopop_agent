| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | SCAFFOLD_MODIFIED | — | —+— | — | — | 1 | 124.3 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | SCAFFOLD_MODIFIED | 0.30x | —+— | — | — | 1 | 137.4 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 128.8 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | parallel-not-faster | 0.86x | —+— | — | — | 1 | 183.2 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 199.6 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | SCAFFOLD_MODIFIED | 0.01x | —+— | — | — | 1 | 131.0 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | BROKEN | — | —+— | — | — | 1 | 165.8 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | BROKEN | — | —+— | — | — | 1 | 128.7 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 161.6 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | BROKEN | — | —+— | — | — | 1 | 96.7 |
