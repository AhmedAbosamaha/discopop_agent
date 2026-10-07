| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | claude-haiku-4-5-20251001 | 44 | 8 | 0 | 2 | 0 | 34 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_c2/k17 | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.97 |
| tsvc_c2/k42 | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.96 |
