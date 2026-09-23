| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | none | 55 | 14 | 3 | 7 | 0 | 26 | 0 | 0 | 0 | 0 | 0 | 5 | 4 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/atax | discopop_capability | none | 1 | LARGE | 0.26 |
| polybench/gemver | discopop_capability | none | 1 | LARGE | 2.98 |
| polybench/gesummv | discopop_capability | none | 1 | LARGE | 3.59 |
| polybench/jacobi-1d-imper | discopop_capability | none | 1 | EXTRALARGE | 3.15 |
| polybench/mvt | discopop_capability | none | 1 | LARGE | 3.60 |
| polybench/reg_detect | discopop_capability | none | 1 | EXTRALARGE | 0.19 |
| rodinia-3.1/pathfinder | discopop_capability | none | 1 | EXTRALARGE | 3.23 |
