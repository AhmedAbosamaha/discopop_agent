| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | none | 56 | 16 | 3 | 6 | 0 | 29 | 0 | 0 | 0 | 0 | 0 | 2 | 4 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/gemver | discopop_capability | none | 1 | LARGE | 4.08 |
| polybench/gesummv | discopop_capability | none | 1 | LARGE | 4.10 |
| polybench/jacobi-1d-imper | discopop_capability | none | 1 | EXTRALARGE | 2.11 |
| polybench/mvt | discopop_capability | none | 1 | LARGE | 3.47 |
| polybench/reg_detect | discopop_capability | none | 1 | EXTRALARGE | 0.28 |
| rodinia-3.1/pathfinder | discopop_capability | none | 1 | EXTRALARGE | 4.59 |
