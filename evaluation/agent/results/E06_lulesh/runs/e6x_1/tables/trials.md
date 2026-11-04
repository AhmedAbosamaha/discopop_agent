| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.34x | 7+0 | 0 | 14 | 0 | 566.6 |
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.35x | 7+0 | 0 | 14 | 0 | 563.8 |
| llnl_c1/lulesh | llm_pragmas_v5_exact | claude-haiku-4-5-20251001 | 1 | FASTER | 1.48x | 3+19 | 14 | 14 | 30 | 21458.1 |
| llnl_c1/lulesh | llm_pragmas_v5_exact | claude-haiku-4-5-20251001 | 2 | FASTER | 1.81x | 0+16 | 13 | 14 | 40 | 13382.4 |
