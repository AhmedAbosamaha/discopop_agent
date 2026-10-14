| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c5/s123 | expert_openmp | none | 1 | FASTER | 2.63x | —+— | — | — | 0 | — |
| tsvc_c5/s123 | step1 | none | 1 | FASTER | 1.23x | —+— | — | — | 0 | — |
| tsvc_c5/s221 | expert_openmp | none | 1 | FASTER | 2.98x | —+— | — | — | 0 | — |
| tsvc_c5/s221 | step1 | none | 1 | parallel-not-faster | 0.90x | —+— | — | — | 0 | — |
| tsvc_c5/s2251 | expert_openmp | none | 1 | FASTER | 2.36x | —+— | — | — | 0 | — |
| tsvc_c5/s2251 | step1 | none | 1 | parallel-not-faster | 0.65x | —+— | — | — | 0 | — |
| tsvc_c5/s233 | expert_openmp | none | 1 | FASTER | 12.53x | —+— | — | — | 0 | — |
| tsvc_c5/s233 | step1 | none | 1 | FASTER | 1.75x | —+— | — | — | 0 | — |
| tsvc_c5/s257 | expert_openmp | none | 1 | FASTER | 7.44x | —+— | — | — | 0 | — |
| tsvc_c5/s257 | step1 | none | 1 | FASTER | 4.45x | —+— | — | — | 0 | — |
