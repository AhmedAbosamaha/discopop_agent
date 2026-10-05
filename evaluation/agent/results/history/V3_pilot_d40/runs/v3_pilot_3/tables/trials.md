| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.03x | 1+0 | 1 | 1 | 3 | 763.0 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 6 | 1282.1 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.99x | 1+0 | 1 | 1 | 6 | 1633.5 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.15x | 1+0 | 1 | 1 | 1 | 539.5 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 2.12x | 2+0 | 1 | 1 | 3 | 1028.9 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.10x | 1+0 | 1 | 1 | 1 | 508.0 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 4.28x | 1+0 | 1 | 0 | 3 | 938.9 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 2249.0 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 9 | 2576.4 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 605.0 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.63x | 1+0 | 1 | 0 | 2 | 485.4 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.34x | 1+0 | 1 | 0 | 5 | 1219.9 |
