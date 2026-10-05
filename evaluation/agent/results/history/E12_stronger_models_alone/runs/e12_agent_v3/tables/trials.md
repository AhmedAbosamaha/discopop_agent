| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.29x | 2+0 | 1 | 0 | 1 | 228.5 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.16x | 2+0 | 1 | 0 | 1 | 107.0 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.21x | 2+0 | 1 | 0 | 1 | 127.4 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.05x | 2+0 | 1 | 0 | 1 | 112.6 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.30x | 2+0 | 1 | 0 | 1 | 138.1 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.15x | 2+0 | 1 | 0 | 1 | 93.3 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.84x | 2+0 | 1 | 0 | 1 | 135.3 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.94x | 2+0 | 1 | 0 | 1 | 181.3 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.00x | 2+0 | 1 | 0 | 1 | 92.3 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.18x | 2+0 | 1 | 0 | 1 | 156.7 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 311.5 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 388.7 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 276.6 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 316.1 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.93x | 1+0 | 1 | 0 | 2 | 342.0 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 345.2 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 413.8 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.32x | 1+0 | 1 | 0 | 3 | 343.2 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 481.5 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 309.1 |
