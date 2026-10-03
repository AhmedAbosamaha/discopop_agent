| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | parallel-not-faster | 1.04x | —+— | — | — | 2 | 321.8 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | parallel-not-faster | 0.93x | —+— | — | — | 1 | 90.0 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | BROKEN | — | —+— | — | — | 1 | 112.5 |
