| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.30x | 7+0 | 0 | 14 | 0 | 586.4 |
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.34x | 7+0 | 0 | 14 | 0 | 583.9 |
| llnl_c1/lulesh | llm_pragmas_v5_exact | claude-haiku-4-5-20251001 | 1 | FASTER | 1.74x | 2+16 | 16 | 14 | 51 | 22832.9 |
| llnl_c1/lulesh | llm_pragmas_v5_exact | claude-haiku-4-5-20251001 | 2 | FASTER | 1.93x | 2+19 | 14 | 14 | 42 | 21803.9 |
