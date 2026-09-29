| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 1 | 9 | 0 | 0 | 0 | 0 | 0 | 83 | 10 |
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 138 | 10 |
| no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 147 | 20 |
| twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 105 | 10 |
| twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 60 | 10 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 1.02 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 0.97 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 1.00 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 1.00 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.97 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.97 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 1.04 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 1.01 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 0.97 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 1.00 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 0.99 |
