| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.39x | 2+0 | 1 | 1 | 1 | 245.9 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.46x | 2+0 | 1 | 1 | 6 | 1184.6 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.33x | 2+0 | 1 | 1 | 1 | 332.5 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.12x | 2+0 | 1 | 1 | 1 | 234.1 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.34x | 2+0 | 1 | 1 | 1 | 199.0 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.33x | 2+0 | 1 | 1 | 4 | 727.0 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.39x | 2+0 | 1 | 0 | 1 | 302.8 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.48x | 2+0 | 1 | 0 | 1 | 244.6 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.39x | 2+0 | 1 | 0 | 1 | 267.1 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.38x | 2+0 | 1 | 0 | 1 | 238.0 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.74x | 2+0 | 1 | 0 | 4 | 840.7 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.19x | 2+0 | 1 | 0 | 1 | 262.7 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.47x | 2+0 | 1 | 0 | 1 | 493.6 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.54x | 2+0 | 1 | 0 | 2 | 426.9 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.53x | 2+0 | 1 | 0 | 3 | 629.0 |
| tsvc/s1213 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 2.80x | 2+0 | 1 | 0 | 2 | 350.2 |
| tsvc/s1213 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.22x | 2+0 | 1 | 0 | 3 | 649.5 |
| tsvc/s1213 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 2.75x | 2+0 | 1 | 0 | 1 | 284.3 |
