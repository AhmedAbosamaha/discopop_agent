| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 1 | FASTER | 3.56x | —+— | — | — | 1 | 148.7 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 2 | FASTER | 2.64x | —+— | — | — | 1 | 219.9 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 3 | FASTER | 3.48x | —+— | — | — | 1 | 86.7 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 4 | parallel-not-faster | 0.81x | —+— | — | — | 1 | 114.3 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 5 | parallel-not-faster | 1.07x | —+— | — | — | 1 | 145.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 1 | parallel-not-faster | 0.29x | —+— | — | — | 1 | 118.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 2 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 116.1 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 3 | parallel-not-faster | 0.26x | —+— | — | — | 1 | 170.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 4 | parallel-not-faster | 0.35x | —+— | — | — | 1 | 147.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 5 | parallel-not-faster | 0.35x | —+— | — | — | 1 | 97.7 |
