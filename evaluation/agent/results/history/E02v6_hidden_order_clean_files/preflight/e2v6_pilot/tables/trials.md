| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.42x | 1+0 | 1 | 0 | 1 | 227.2 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.44x | 1+0 | 1 | 0 | 1 | 72.7 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 247.9 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.07x | 0+0 | 0 | 0 | 3 | 184.0 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 480.0 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.88x | 2+0 | 1 | 0 | 1 | 102.7 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 491.0 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 204.3 |
