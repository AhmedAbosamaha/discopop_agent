| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.35x | 6+0 | 0 | 14 | 0 | 562.4 |
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.33x | 7+0 | 0 | 14 | 0 | 571.4 |
| llnl_c1/lulesh | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.10x | 2+63 | 11 | 14 | 45 | 18319.2 |
| llnl_c1/lulesh | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | BROKEN | 1.84x | 0+51 | 13 | 14 | 29 | 17110.8 |
