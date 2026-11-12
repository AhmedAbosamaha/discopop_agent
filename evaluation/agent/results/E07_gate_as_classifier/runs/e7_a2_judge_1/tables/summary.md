| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 94 | 35 | 6 | 18 | 0 | 0 | 30 | 0 | 5 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/atax | e7 | none | 2 | LARGE | 0.66 |
| polybench/gemver | e7 | none | 1 | LARGE | 2.38 |
| polybench/gemver | e7 | none | 10 | LARGE | 2.39 |
| polybench/gemver | e7 | none | 2 | LARGE | 1.18 |
| polybench/gemver | e7 | none | 4 | LARGE | 1.68 |
| polybench/gemver | e7 | none | 5 | LARGE | 2.37 |
| polybench/gemver | e7 | none | 9 | LARGE | 3.53 |
| polybench/gesummv | e7 | none | 4 | LARGE | 4.00 |
| polybench/jacobi-1d-imper | e7 | none | 2 | EXTRALARGE | 5.16 |
| polybench/mvt | e7 | none | 1 | LARGE | 3.67 |
| polybench/mvt | e7 | none | 7 | LARGE | 1.34 |
| polybench/reg_detect | e7 | none | 1 | EXTRALARGE | 0.38 |
| polybench/reg_detect | e7 | none | 12 | EXTRALARGE | 0.05 |
| polybench/reg_detect | e7 | none | 13 | EXTRALARGE | 1.22 |
| polybench/reg_detect | e7 | none | 2 | EXTRALARGE | 0.05 |
| polybench/reg_detect | e7 | none | 3 | EXTRALARGE | 1.53 |
| polybench/reg_detect | e7 | none | 7 | EXTRALARGE | 0.05 |
| tsvc_c3/k17 | e7 | none | 2 | EXTRALARGE | 0.97 |
