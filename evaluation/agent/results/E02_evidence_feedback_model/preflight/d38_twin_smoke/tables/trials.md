| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s121 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 0.51x | —+— | — | — | 0 | 14.2 |
| tsvc/s121 | twin_full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 172.0 |
