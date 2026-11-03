| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.34x | 7+0 | 0 | 14 | 0 | 569.4 |
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.28x | 7+0 | 0 | 14 | 0 | 570.3 |
| llnl_c1/lulesh | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | BROKEN | 1.86x | 1+30 | 11 | 14 | 43 | 18709.1 |
| llnl_c1/lulesh | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.08x | 2+52 | 15 | 14 | 35 | 24300.1 |
