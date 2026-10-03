| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-fable-5-1 | 1 | FASTER | 1.16x | 2+0 | 1 | 0 | 1 | 131.2 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-fable-5-1 | 2 | BROKEN | — | 1+0 | 1 | 0 | 3 | 396.3 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-fable-5-1 | 3 | FASTER | 1.14x | 1+0 | 1 | 0 | 1 | 142.7 |
