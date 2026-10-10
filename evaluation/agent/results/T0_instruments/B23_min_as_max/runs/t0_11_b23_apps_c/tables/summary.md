| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | claude-haiku-4-5-20251001 | 31 | 14 | 2 | 6 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 0.70 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 4.01 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 4.38 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 5.05 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 3.72 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.36 |
