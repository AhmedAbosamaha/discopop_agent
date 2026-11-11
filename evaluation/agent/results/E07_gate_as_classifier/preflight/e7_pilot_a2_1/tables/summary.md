| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 10 | 2 | 1 | 4 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/gemver | e7 | none | 1 | LARGE | 2.51 |
| polybench/jacobi-1d-imper | e7 | none | 1 | EXTRALARGE | 5.01 |
| polybench/mvt | e7 | none | 1 | LARGE | 4.01 |
| tsvc_c3/k42 | e7 | none | 2 | EXTRALARGE | 0.97 |
