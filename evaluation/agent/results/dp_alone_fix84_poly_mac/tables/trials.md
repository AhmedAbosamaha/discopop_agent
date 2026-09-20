| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | discopop_gate | none | 1 | FASTER | 3.15x | 2+0 | 0 | 6 | 0 | 47.9 |
| polybench/bicg | discopop_gate | none | 1 | no-change | 1.29x | 0+0 | 0 | 2 | 0 | 47.9 |
| polybench/covariance | discopop_gate | none | 1 | FASTER | 2.15x | 1+0 | 0 | 2 | 0 | 34.0 |
| polybench/fdtd-2d | discopop_gate | none | 1 | parallel-not-faster | 1.07x | 3+0 | 0 | 4 | 0 | 54.3 |
| polybench/floyd-warshall | discopop_gate | none | 1 | no-change | 1.10x | 0+0 | 0 | 3 | 0 | 53.6 |
| polybench/gemm | discopop_gate | none | 1 | FASTER | 3.26x | 1+0 | 0 | 3 | 0 | 28.6 |
| polybench/gemver | discopop_gate | none | 1 | parallel-speed-not-measurable | 2.67x | 3+0 | 0 | 4 | 0 | 40.1 |
| polybench/gramschmidt | discopop_gate | none | 1 | FASTER | 2.75x | 1+0 | 0 | 4 | 0 | 33.5 |
| polybench/lu | discopop_gate | none | 1 | FASTER | 3.39x | 1+0 | 0 | 3 | 0 | 25.9 |
| polybench/mvt | discopop_gate | none | 1 | parallel-speed-not-measurable | 2.47x | 2+0 | 0 | 4 | 0 | 34.2 |
| polybench/reg_detect | discopop_gate | none | 1 | parallel-speed-not-measurable | 1.28x | 3+0 | 0 | 9 | 0 | 143.5 |
| polybench/syr2k | discopop_gate | none | 1 | FASTER | 8.49x | 1+0 | 0 | 3 | 0 | 83.9 |
| polybench/syrk | discopop_gate | none | 1 | FASTER | 2.96x | 1+0 | 0 | 2 | 0 | 57.2 |
