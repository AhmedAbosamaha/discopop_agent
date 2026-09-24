| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.02x | —+— | — | — | 1 | 50.6 |
| tsvc/s121 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 1 | 750.3 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 1 | 189.8 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s121 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.50x | 2+0 | 1 | 0 | 1 | 243.8 |
| tsvc/s121 | hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.66x | 2+0 | 1 | 0 | 1 | 244.5 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 0.97x | 0+0 | 0 | 0 | 1 | 171.4 |
| tsvc/s121 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.56x | 2+0 | 1 | 0 | 1 | 196.8 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.50x | —+— | — | — | 1 | 121.0 |
| tsvc/s281 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 425.1 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 318.3 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.02x | 2+0 | 1 | 0 | 1 | 309.2 |
| tsvc/s281 | hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 531.3 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.02x | 2+0 | 1 | 0 | 1 | 310.5 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 861.2 |
