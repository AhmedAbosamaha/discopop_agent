| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.09x | 2+0 | 1 | 0 | 1 | 386.1 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.24x | 1+0 | 1 | 0 | 2 | 572.0 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.36x | 2+0 | 1 | 0 | 3 | 566.2 |
| tsvc/s211 | no_evidence | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 5 | 959.3 |
| tsvc/s211 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.57x | 3+0 | 1 | 0 | 1 | 532.6 |
| tsvc/s211 | no_evidence | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.06x | 1+0 | 1 | 0 | 1 | 346.9 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.19x | 2+0 | 1 | 1 | 5 | 819.6 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.05x | 3+0 | 1 | 1 | 2 | 501.1 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.34x | 1+0 | 1 | 1 | 2 | 545.4 |
| tsvc/s212 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.19x | 2+0 | 1 | 1 | 2 | 505.2 |
| tsvc/s212 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.34x | 1+0 | 1 | 1 | 1 | 284.9 |
| tsvc/s212 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 2.09x | 3+0 | 1 | 1 | 1 | 415.2 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.53x | 3+0 | 1 | 1 | 1 | 675.7 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.66x | 3+0 | 1 | 1 | 1 | 904.1 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.33x | 1+0 | 1 | 1 | 5 | 1232.4 |
| tsvc/s241 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.39x | 3+0 | 1 | 1 | 4 | 978.6 |
| tsvc/s241 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.81x | 2+0 | 1 | 1 | 2 | 719.0 |
| tsvc/s241 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.42x | 3+0 | 1 | 1 | 2 | 591.5 |
