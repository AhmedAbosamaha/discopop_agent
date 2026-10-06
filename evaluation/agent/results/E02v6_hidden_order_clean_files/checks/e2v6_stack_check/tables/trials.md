| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k23 | k23_rep10_as_run | none | 1 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| tsvc_c2/k23 | k23_rep10_stack_lifted | none | 1 | parallel-not-faster | 0.43x | —+— | — | — | 0 | — |
| tsvc_c2/k53 | k53_rep10_as_run | none | 1 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| tsvc_c2/k53 | k53_rep10_stack_lifted | none | 1 | parallel-not-faster | 0.74x | —+— | — | — | 0 | — |
| tsvc_c2/k53 | k53_rep3_as_run | none | 1 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| tsvc_c2/k53 | k53_rep3_stack_lifted | none | 1 | parallel-not-faster | 0.81x | —+— | — | — | 0 | — |
