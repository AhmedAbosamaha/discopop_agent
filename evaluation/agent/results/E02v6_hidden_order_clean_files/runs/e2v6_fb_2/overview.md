# Agent experiment run `e2v6_fb_2`

- status: finished (created 2026-10-05T19:01:04, finished 2026-10-06T07:22:59)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `1258cd677fa14c0ff235f7da1cc5bbca41548378` (uncommitted diff sha256 `None`)
- harness: `1258cd677fa14c0ff235f7da1cc5bbca41548378` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 18 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 162 | 54 |
| no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 5 | 1 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 1195 | 180 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.01x | 2+0 | 1 | 0 | 2 | 251.5 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1807.8 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.99x | 2+0 | 1 | 0 | 1 | 173.2 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.02x | 2+0 | 1 | 0 | 4 | 575.1 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.04x | 2+0 | 1 | 0 | 5 | 693.2 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1445.7 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.00x | 2+0 | 1 | 0 | 1 | 181.0 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.98x | 2+0 | 1 | 0 | 5 | 584.5 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.94x | 2+0 | 1 | 0 | 1 | 106.4 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.95x | 2+0 | 1 | 0 | 1 | 86.5 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.66x | 2+0 | 1 | 0 | 4 | 499.8 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1155.7 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1144.5 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1418.3 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 0 | 11 | 1286.4 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 10 | 1486.6 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 0.99x | 0+0 | 0 | 0 | 12 | 1388.2 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.01x | 0+0 | 0 | 0 | 10 | 1513.9 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 0.99x | 0+0 | 0 | 0 | 12 | 1224.7 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1605.4 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.36x | 1+0 | 1 | 0 | 1 | 125.2 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.37x | 1+0 | 1 | 0 | 1 | 160.7 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.37x | 1+0 | 1 | 0 | 1 | 106.9 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.34x | 1+0 | 1 | 0 | 1 | 69.6 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.38x | 1+0 | 1 | 0 | 1 | 121.8 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.32x | 1+0 | 1 | 0 | 4 | 432.1 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.38x | 1+0 | 1 | 0 | 1 | 148.4 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.36x | 1+0 | 1 | 0 | 1 | 116.2 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.38x | 1+0 | 1 | 0 | 1 | 138.3 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.31x | 1+0 | 1 | 0 | 1 | 163.2 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.36x | 1+0 | 1 | 0 | 10 | 858.4 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.36x | 1+0 | 1 | 0 | 2 | 877.5 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1385.9 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.35x | 1+0 | 1 | 0 | 2 | 350.5 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1314.1 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1553.2 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.37x | 1+0 | 1 | 0 | 6 | 651.9 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 905.9 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.36x | 1+0 | 1 | 0 | 3 | 609.0 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1165.9 |
