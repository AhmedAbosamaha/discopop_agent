| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 10.68x | —+— | — | — | 1 | 170.1 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.89x | 1+0 | 1 | 1 | 2 | 572.2 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.98x | 1+0 | 1 | 1 | 3 | 998.7 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 1 | 142.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 2 | 362.8 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.39x | —+— | — | — | 1 | 82.4 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | — | 1+0 | 1 | 0 | 1 | 115.8 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 1.45x | 2+0 | 1 | 0 | 2 | 123.7 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 0.46x | —+— | — | — | 2 | 324.0 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | changed-not-parallel | 1.03x | —+— | — | — | 1 | 67.5 |
