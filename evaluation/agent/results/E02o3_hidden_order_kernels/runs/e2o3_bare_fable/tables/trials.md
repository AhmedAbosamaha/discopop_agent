| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | BROKEN | 4.31x | —+— | — | — | 1 | 21.4 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | BROKEN | 4.26x | —+— | — | — | 1 | 16.0 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | BROKEN | 4.22x | —+— | — | — | 1 | 15.1 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | BROKEN | 4.21x | —+— | — | — | 1 | 13.9 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | BROKEN | 4.25x | —+— | — | — | 1 | 22.7 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | FASTER | 2.38x | —+— | — | — | 1 | 144.8 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | FASTER | 3.22x | —+— | — | — | 1 | 132.5 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | FASTER | 3.16x | —+— | — | — | 1 | 121.0 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | FASTER | 3.17x | —+— | — | — | 1 | 203.1 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | BROKEN | 1.61x | —+— | — | — | 1 | 66.3 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | FASTER | 1.46x | —+— | — | — | 1 | 141.7 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | BROKEN | — | —+— | — | — | 1 | 168.6 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | BROKEN | 3.22x | —+— | — | — | 1 | 95.6 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | parallel-not-faster | 0.97x | —+— | — | — | 1 | 186.3 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | BROKEN | 3.10x | —+— | — | — | 1 | 66.7 |
