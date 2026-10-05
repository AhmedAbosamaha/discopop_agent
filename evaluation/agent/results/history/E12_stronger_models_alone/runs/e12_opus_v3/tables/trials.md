| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-opus-5-5 | 1 | BROKEN | — | —+— | — | — | 1 | 64.4 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-opus-5-5 | 2 | parallel-not-faster | 0.99x | —+— | — | — | 1 | 80.3 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-opus-5-5 | 3 | parallel-not-faster | 0.90x | —+— | — | — | 1 | 108.0 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-opus-5-5 | 4 | parallel-not-faster | 0.96x | —+— | — | — | 1 | 91.7 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-opus-5-5 | 5 | parallel-not-faster | 1.02x | —+— | — | — | 1 | 60.4 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-opus-5-5 | 1 | BROKEN | — | —+— | — | — | 1 | 64.5 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-opus-5-5 | 2 | parallel-not-faster | 0.94x | —+— | — | — | 1 | 80.8 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-opus-5-5 | 3 | parallel-not-faster | 0.97x | —+— | — | — | 1 | 55.5 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-opus-5-5 | 4 | parallel-not-faster | 0.81x | —+— | — | — | 1 | 77.1 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-opus-5-5 | 5 | BROKEN | — | —+— | — | — | 1 | 91.4 |
