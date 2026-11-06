| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 112.9 |
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 113.2 |
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 114.3 |
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 112.7 |
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 113.3 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 6.51x | 0+4 | 1 | 5 | 4 | 660.3 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 1.36x | 0+4 | 1 | 5 | 6 | 981.8 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 6.84x | 0+4 | 1 | 5 | 4 | 843.0 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 7.80x | 0+3 | 1 | 5 | 4 | 574.9 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 7.80x | 0+3 | 1 | 5 | 4 | 609.1 |
