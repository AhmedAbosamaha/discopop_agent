| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 65 | 30 | 0 | 5 | 0 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 206 | 118 |
| discopop_gate | claude-haiku-4-5-20251001 | 65 | 0 | 0 | 0 | 0 | 65 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 1 | LARGE | 0.08 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 2 | LARGE | 0.05 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 3 | LARGE | 0.15 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 4 | LARGE | 0.15 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 5 | LARGE | 0.10 |
