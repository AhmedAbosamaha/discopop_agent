| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/adi | e7 | none | 2 | FASTER | 1.95x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 1 | BROKEN | 1.13x | —+— | — | — | 0 | — |
| polybench/floyd-warshall | e7 | none | 1 | parallel-not-faster | 0.34x | —+— | — | — | 0 | — |
| polybench/jacobi-2d-imper | e7 | none | 1 | FASTER | 4.35x | —+— | — | — | 0 | — |
| polybench/syrk | e7 | none | 1 | FASTER | 10.29x | —+— | — | — | 0 | — |
| polybench/trisolv | e7 | none | 1 | BROKEN | 2.24x | —+— | — | — | 0 | — |
| rodinia-3.1/pathfinder | e7 | none | 1 | BROKEN | 0.99x | —+— | — | — | 0 | — |
| tsvc_c3/k17 | e7 | none | 2 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 0 | — |
| tsvc_c3/s171 | e7 | none | 1 | FASTER | 3.33x | —+— | — | — | 0 | — |
| tsvc_c3/vas | e7 | none | 2 | FASTER | 3.65x | —+— | — | — | 0 | — |
