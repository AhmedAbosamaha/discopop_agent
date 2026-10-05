| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 1 | BROKEN | — | 1+0 | 1 | 0 | 3 | 290.1 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 2 | BROKEN | — | 1+0 | 1 | 0 | 2 | 215.1 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 3 | parallel-not-faster | 0.97x | 1+0 | 1 | 0 | 1 | 74.0 |
