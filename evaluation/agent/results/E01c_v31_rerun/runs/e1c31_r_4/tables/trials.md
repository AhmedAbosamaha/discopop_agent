| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.51x | 1+0 | 1 | 1 | 1 | 149.2 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.67x | 1+0 | 1 | 1 | 1 | 179.0 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.51x | 1+0 | 1 | 1 | 1 | 163.8 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.46x | 1+0 | 1 | 1 | 1 | 202.1 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.45x | 1+0 | 1 | 1 | 1 | 184.5 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.98x | 1+0 | 1 | 1 | 1 | 114.6 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.88x | 1+0 | 1 | 1 | 1 | 89.6 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.83x | 1+0 | 1 | 1 | 1 | 129.6 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 2.86x | 1+0 | 1 | 1 | 1 | 156.6 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.87x | 1+0 | 1 | 1 | 1 | 97.8 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.95x | 1+0 | 1 | 2 | 7 | 1519.3 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 2 | 3 | 642.2 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.69x | 1+0 | 1 | 2 | 5 | 779.4 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 2 | 9 | 2137.5 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 6.06x | 1+0 | 1 | 2 | 7 | 1215.0 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.08x | 3+0 | 1 | 2 | 4 | 802.0 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 2 | 9 | 1693.2 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 2 | 9 | 1674.5 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 2 | 9 | 1628.1 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.28x | 1+0 | 1 | 2 | 2 | 330.6 |
