# Agent experiment run `e1v6_d`

- status: finished (created 2026-10-05T06:22:55, finished 2026-10-05T09:20:54)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `70cb05ff3d1ecc75158877a042809fcfdf7d5da8` (uncommitted diff sha256 `None`)
- harness: `70cb05ff3d1ecc75158877a042809fcfdf7d5da8` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v4 | claude-haiku-4-5-20251001 | 12 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 614 | 123 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 12 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s3112 | default_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 99.8 |
| tsvc_c2/s3112 | default_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 99.3 |
| tsvc_c2/s3112 | default_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 0 | 9 | 99.2 |
| tsvc_c2/s3112 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 0 | 5.6 |
| tsvc_c2/s3112 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.6 |
| tsvc_c2/s3112 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c2/s321 | default_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 12 | 1134.6 |
| tsvc_c2/s321 | default_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1031.7 |
| tsvc_c2/s321 | default_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 11 | 1247.8 |
| tsvc_c2/s321 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s321 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c2/s321 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c2/s322 | default_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1265.2 |
| tsvc_c2/s322 | default_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1981.1 |
| tsvc_c2/s322 | default_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 12 | 1005.3 |
| tsvc_c2/s322 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s322 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s322 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s323 | default_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 223.0 |
| tsvc_c2/s323 | default_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 107.9 |
| tsvc_c2/s323 | default_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 107.7 |
| tsvc_c2/s323 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 14.0 |
| tsvc_c2/s323 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 14.1 |
| tsvc_c2/s323 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 14.2 |
