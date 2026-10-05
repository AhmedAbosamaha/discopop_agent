| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.57x | 1+0 | 1 | 1 | 1 | 233.7 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.02x | 2+0 | 1 | 1 | 1 | 242.5 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.02x | 1+0 | 1 | 1 | 1 | 303.3 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.03x | 1+0 | 1 | 1 | 1 | 263.0 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 2.18x | 2+0 | 1 | 1 | 1 | 200.1 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 2.07x | 2+0 | 1 | 1 | 1 | 206.1 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.22x | 2+0 | 1 | 0 | 1 | 259.8 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.58x | 2+0 | 1 | 0 | 1 | 235.6 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.06x | 1+0 | 1 | 0 | 2 | 413.0 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.15x | 1+0 | 1 | 0 | 8 | 1413.6 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 3.30x | 2+0 | 1 | 0 | 2 | 405.5 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 2.54x | 2+0 | 1 | 0 | 2 | 603.5 |
