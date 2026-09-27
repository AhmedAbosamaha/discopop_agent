| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.43x | 2+0 | 1 | 1 | 1 | 217.9 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.30x | 2+0 | 1 | 1 | 1 | 302.8 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.31x | 2+0 | 1 | 1 | 1 | 264.3 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 1.35x | 2+0 | 1 | 1 | 4 | 1122.8 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.98x | 3+0 | 1 | 1 | 7 | 1545.5 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.46x | 2+0 | 1 | 0 | 1 | 232.9 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.37x | 2+0 | 1 | 0 | 1 | 205.8 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.39x | 2+0 | 1 | 0 | 1 | 185.7 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 1.39x | 2+0 | 1 | 0 | 1 | 179.8 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 1.39x | 2+0 | 1 | 0 | 1 | 235.3 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.55x | 2+0 | 1 | 0 | 1 | 205.8 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.36x | 3+0 | 1 | 0 | 1 | 542.6 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1978.8 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 1.77x | 3+0 | 1 | 0 | 3 | 495.5 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.53x | 2+0 | 1 | 0 | 3 | 415.4 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.95x | 1+0 | 1 | 1 | 1 | 220.1 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.93x | 1+0 | 1 | 1 | 1 | 141.4 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.81x | 1+0 | 1 | 1 | 1 | 102.3 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.98x | 1+0 | 1 | 1 | 1 | 143.9 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 4.00x | 1+0 | 1 | 1 | 1 | 99.4 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.96x | 3+0 | 1 | 0 | 1 | 630.7 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.15x | 1+0 | 1 | 0 | 4 | 880.1 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.06x | 1+0 | 1 | 0 | 5 | 1739.0 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 4 | 942.3 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 1.15x | 1+0 | 1 | 0 | 1 | 255.8 |
