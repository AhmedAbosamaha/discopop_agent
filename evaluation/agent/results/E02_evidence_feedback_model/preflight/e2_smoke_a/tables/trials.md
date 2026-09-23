| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s121 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 308.9 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 268.2 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 1 | 0 | 31.5 |
| tsvc/s121 | full_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 1 | 1 | 231.3 |
| tsvc/s121 | hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 152.2 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 1 | 1 | 185.8 |
| tsvc/s121 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 291.8 |
