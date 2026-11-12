| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 93 | 37 | 8 | 19 | 0 | 0 | 28 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/gemver | e7 | none | 3 | LARGE | 3.92 |
| polybench/gemver | e7 | none | 6 | LARGE | 3.85 |
| polybench/gemver | e7 | none | 8 | LARGE | 1.58 |
| polybench/gesummv | e7 | none | 2 | LARGE | 3.99 |
| polybench/gesummv | e7 | none | 3 | LARGE | 4.10 |
| polybench/jacobi-1d-imper | e7 | none | 1 | EXTRALARGE | 1.67 |
| polybench/jacobi-1d-imper | e7 | none | 3 | EXTRALARGE | 0.58 |
| polybench/jacobi-1d-imper | e7 | none | 5 | EXTRALARGE | 0.74 |
| polybench/mvt | e7 | none | 2 | LARGE | 2.04 |
| polybench/mvt | e7 | none | 3 | LARGE | 2.09 |
| polybench/mvt | e7 | none | 4 | LARGE | 1.16 |
| polybench/mvt | e7 | none | 5 | LARGE | 2.10 |
| polybench/reg_detect | e7 | none | 10 | EXTRALARGE | 1.85 |
| polybench/reg_detect | e7 | none | 11 | EXTRALARGE | 0.38 |
| polybench/reg_detect | e7 | none | 4 | EXTRALARGE | 0.89 |
| polybench/reg_detect | e7 | none | 5 | EXTRALARGE | 0.56 |
| polybench/reg_detect | e7 | none | 6 | EXTRALARGE | 0.46 |
| polybench/reg_detect | e7 | none | 9 | EXTRALARGE | 1.67 |
| tsvc_c3/k42 | e7 | none | 2 | EXTRALARGE | 0.99 |
