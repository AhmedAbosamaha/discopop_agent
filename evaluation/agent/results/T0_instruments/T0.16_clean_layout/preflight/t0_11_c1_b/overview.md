# Agent experiment run `t0_11_c1_b`

- status: finished (created 2026-10-04T13:13:49, finished 2026-10-04T14:09:45)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `2ec3e796629c6bbe32d5ec6e3c46d6d9a9c62e41` (uncommitted diff sha256 `None`)
- harness: `2ec3e796629c6bbe32d5ec6e3c46d6d9a9c62e41` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | claude-haiku-4-5-20251001 | 42 | 8 | 0 | 0 | 0 | 34 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c1/k17 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.7 |
| tsvc_c1/k19 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.7 |
| tsvc_c1/k23 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.7 |
| tsvc_c1/k31 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c1/k42 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.8 |
| tsvc_c1/k48 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c1/s000 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.25x | 1+0 | 0 | 1 | 0 | 4.5 |
| tsvc_c1/s112 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c1/s121 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c1/s1213 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c1/s127 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s131 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.97x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c1/s151 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c1/s152 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 2.91x | 1+0 | 0 | 1 | 0 | 4.7 |
| tsvc_c1/s161 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c1/s171 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.39x | 1+0 | 0 | 1 | 0 | 4.3 |
| tsvc_c1/s211 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c1/s212 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c1/s241 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c1/s243 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c1/s244 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s252 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s254 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c1/s255 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s258 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s277 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.58x | 1+0 | 0 | 1 | 0 | 4.1 |
| tsvc_c1/s281 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s291 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c1/s292 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s293 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c1/s3112 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s313 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.34x | 1+0 | 0 | 1 | 0 | 3.9 |
| tsvc_c1/s321 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c1/s322 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.2 |
| tsvc_c1/s323 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c1/s331 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 3.3 |
| tsvc_c1/s341 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c1/s424 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c1/s481 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.02x | 1+0 | 0 | 1 | 0 | 4.6 |
| tsvc_c1/s482 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.8 |
| tsvc_c1/vas | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.71x | 1+0 | 0 | 1 | 0 | 4.4 |
| tsvc_c1/vpvtv | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.85x | 1+0 | 0 | 1 | 0 | 4.3 |
