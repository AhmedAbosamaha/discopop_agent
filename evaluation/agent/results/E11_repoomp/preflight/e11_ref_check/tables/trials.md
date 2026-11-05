| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npbc_c1/cg | claude_code | none | 1 | BROKEN | 10.38x | —+— | — | — | 0 | — |
| npbc_c1/cg | expert_openmp | none | 1 | FASTER | 10.33x | —+— | — | — | 0 | — |
| npbc_c1/cg | repoomp_claude | none | 1 | FASTER | 10.05x | —+— | — | — | 0 | — |
| npbc_c1/ep | claude_code | none | 1 | SCAFFOLD_MODIFIED | — | —+— | — | — | 0 | — |
| npbc_c1/ep | expert_openmp | none | 1 | BROKEN | 8.68x | —+— | — | — | 0 | — |
| npbc_c1/ep | repoomp_claude | none | 1 | FASTER | 8.61x | —+— | — | — | 0 | — |
