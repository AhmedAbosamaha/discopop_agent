| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.64x | —+— | — | — | 1 | 32.6 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.07x | —+— | — | — | 1 | 168.9 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.94x | —+— | — | — | 1 | 88.2 |
| tsvc/s241 | bare_llm_contract | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.81x | —+— | — | — | 1 | 120.3 |
| tsvc/s241 | bare_llm_contract | claude-haiku-4-5-20251001 | 2 | FASTER | 1.54x | —+— | — | — | 1 | 110.7 |
| tsvc/s241 | bare_llm_contract | claude-haiku-4-5-20251001 | 3 | FASTER | 1.79x | —+— | — | — | 1 | 177.4 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.93x | —+— | — | — | 1 | 150.6 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.40x | —+— | — | — | 1 | 227.2 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 3.00x | —+— | — | — | 1 | 107.0 |
| tsvc/s281 | bare_llm_contract | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.05x | —+— | — | — | 1 | 89.6 |
| tsvc/s281 | bare_llm_contract | claude-haiku-4-5-20251001 | 2 | BROKEN | 1.95x | —+— | — | — | 1 | 248.9 |
| tsvc/s281 | bare_llm_contract | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | —+— | — | — | 1 | 18.8 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.07x | —+— | — | — | 1 | 65.3 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.07x | —+— | — | — | 1 | 80.0 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 5.33x | —+— | — | — | 1 | 103.7 |
| tsvc/s331 | bare_llm_contract | claude-haiku-4-5-20251001 | 1 | FASTER | 6.38x | —+— | — | — | 1 | 76.3 |
| tsvc/s331 | bare_llm_contract | claude-haiku-4-5-20251001 | 2 | FASTER | 5.44x | —+— | — | — | 1 | 119.5 |
| tsvc/s331 | bare_llm_contract | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.07x | —+— | — | — | 1 | 49.0 |
