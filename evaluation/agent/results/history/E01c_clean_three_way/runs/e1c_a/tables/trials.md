| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s000 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.50x | —+— | — | — | 1 | 45.5 |
| tsvc/s000 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.62x | 1+0 | 0 | 2 | 1 | 356.9 |
| tsvc/s000 | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 3.60x | 1+0 | 0 | 2 | 0 | 48.9 |
| tsvc/s313 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 4.98x | —+— | — | — | 1 | 72.3 |
| tsvc/s313 | default | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 4.70x | 1+0 | 1 | 2 | 1 | 346.2 |
| tsvc/s313 | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 4.68x | 1+0 | 0 | 2 | 0 | 59.3 |
| tsvc/vpvtv | bare_llm | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 22.0 |
| tsvc/vpvtv | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.65x | 1+0 | 0 | 1 | 1 | 401.5 |
| tsvc/vpvtv | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 3.67x | 1+0 | 0 | 1 | 0 | 59.7 |
