| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 1 | BROKEN | 4.28x | —+— | — | — | 1 | 14.1 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 2 | BROKEN | 4.21x | —+— | — | — | 1 | 13.5 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 3 | BROKEN | 4.32x | —+— | — | — | 1 | 13.0 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 4 | BROKEN | 4.27x | —+— | — | — | 1 | 24.7 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 5 | BROKEN | 4.16x | —+— | — | — | 1 | 14.0 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 1 | parallel-not-faster | 0.96x | —+— | — | — | 1 | 53.8 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 2 | parallel-not-faster | 1.00x | —+— | — | — | 1 | 54.2 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 3 | FASTER | 2.29x | —+— | — | — | 1 | 50.1 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 4 | parallel-not-faster | 1.01x | —+— | — | — | 1 | 52.1 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 5 | parallel-not-faster | 1.02x | —+— | — | — | 1 | 56.9 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 1 | parallel-not-faster | 0.99x | —+— | — | — | 2 | 86.5 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 2 | BROKEN | 2.97x | —+— | — | — | 1 | 46.2 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 3 | BROKEN | 2.58x | —+— | — | — | 1 | 64.8 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 4 | parallel-not-faster | 0.99x | —+— | — | — | 1 | 78.4 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 5 | FASTER | 3.00x | —+— | — | — | 1 | 46.4 |
