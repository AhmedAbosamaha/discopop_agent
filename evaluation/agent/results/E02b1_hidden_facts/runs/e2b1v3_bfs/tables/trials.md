| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 1 | 238.0 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | — | —+— | — | — | 1 | 110.0 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | — | —+— | — | — | 1 | 107.2 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | — | —+— | — | — | 1 | 161.8 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | — | —+— | — | — | 1 | 210.6 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | — | —+— | — | — | 1 | 219.0 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | — | —+— | — | — | 1 | 118.3 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | — | —+— | — | — | 1 | 212.2 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | — | —+— | — | — | 1 | 119.6 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | — | —+— | — | — | 1 | 139.8 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 1 | 155.7 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.86x | —+— | — | — | 2 | 330.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | — | —+— | — | — | 2 | 292.9 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.20x | —+— | — | — | 2 | 311.1 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | — | —+— | — | — | 2 | 321.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 2 | 280.8 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | changed-not-parallel | 0.98x | —+— | — | — | 1 | 179.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | — | —+— | — | — | 2 | 312.9 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.05x | —+— | — | — | 2 | 234.9 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | changed-not-parallel | 0.04x | —+— | — | — | 2 | 294.1 |
