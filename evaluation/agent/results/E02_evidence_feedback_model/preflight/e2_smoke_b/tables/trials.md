| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s281 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.88x | 2+0 | 1 | 0 | 1 | 316.5 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 1 | 200.4 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 348.9 |
| tsvc/s281 | hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.26x | 2+0 | 1 | 0 | 1 | 213.1 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.24x | 2+0 | 1 | 0 | 2 | 306.9 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 163.1 |
