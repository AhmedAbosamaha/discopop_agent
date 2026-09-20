| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 13 | 7 | 1 | 3 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/gemver | discopop_gate | none | 1 | LARGE | 2.67 |
| polybench/mvt | discopop_gate | none | 1 | LARGE | 2.47 |
| polybench/reg_detect | discopop_gate | none | 1 | EXTRALARGE | 1.28 |
