| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s000 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 927.5 |
| tsvc/s000 | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 4.03x | 1+0 | 0 | 2 | 0 | 44.2 |
| tsvc/s313 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 6.36x | 1+0 | 1 | 2 | 1 | 166.6 |
| tsvc/s313 | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 5.55x | 1+0 | 0 | 2 | 0 | 54.6 |
| tsvc/vpvtv | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.37x | 1+0 | 1 | 1 | 1 | 278.9 |
| tsvc/vpvtv | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 4.08x | 1+0 | 0 | 1 | 0 | 54.3 |
