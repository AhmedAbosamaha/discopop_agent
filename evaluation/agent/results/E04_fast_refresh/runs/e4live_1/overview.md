# Agent experiment run `e4live_1`

- status: finished (created 2026-10-18T23:15:43, finished 2026-10-19T05:49:45)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `7bb69f79a558a5cb8041b35aaadbac39dad56839` (uncommitted diff sha256 `None`)
- harness: `7bb69f79a558a5cb8041b35aaadbac39dad56839` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fast_recon_v5 | claude-haiku-4-5-20251001 | 30 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 616 | 123 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s212 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.80x | 2+0 | 1 | 0 | 3 | 601.3 |
| tsvc_c2/s212 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.84x | 3+0 | 1 | 0 | 4 | 596.5 |
| tsvc_c2/s212 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.77x | 2+0 | 1 | 0 | 9 | 841.2 |
| tsvc_c2/s212 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.49x | 2+0 | 1 | 0 | 10 | 1727.0 |
| tsvc_c2/s212 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.48x | 2+0 | 1 | 0 | 5 | 1071.4 |
| tsvc_c2/s243 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.95x | 2+0 | 1 | 0 | 3 | 591.1 |
| tsvc_c2/s243 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.91x | 2+0 | 1 | 0 | 3 | 549.0 |
| tsvc_c2/s243 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.32x | 2+0 | 1 | 0 | 2 | 319.7 |
| tsvc_c2/s243 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.29x | 2+0 | 1 | 0 | 1 | 312.4 |
| tsvc_c2/s243 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.90x | 2+0 | 1 | 0 | 7 | 804.4 |
| tsvc_c2/s244 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.34x | 1+0 | 1 | 0 | 1 | 389.4 |
| tsvc_c2/s244 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.29x | 1+0 | 1 | 0 | 6 | 1447.8 |
| tsvc_c2/s244 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.18x | 1+0 | 1 | 0 | 5 | 1125.5 |
| tsvc_c2/s244 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.94x | 1+0 | 1 | 0 | 7 | 1426.9 |
| tsvc_c2/s244 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.26x | 3+0 | 1 | 0 | 2 | 548.7 |
| tsvc_c2/s252 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.64x | 1+0 | 1 | 0 | 7 | 883.7 |
| tsvc_c2/s252 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.60x | 1+0 | 1 | 0 | 1 | 216.0 |
| tsvc_c2/s252 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.65x | 1+0 | 1 | 0 | 1 | 162.7 |
| tsvc_c2/s252 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.76x | 1+0 | 1 | 0 | 1 | 210.1 |
| tsvc_c2/s252 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.76x | 1+0 | 1 | 0 | 1 | 224.6 |
| tsvc_c3/s241 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.11x | 4+0 | 1 | 0 | 4 | 822.8 |
| tsvc_c3/s241 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.12x | 3+0 | 1 | 0 | 5 | 831.6 |
| tsvc_c3/s241 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.14x | 3+0 | 1 | 0 | 3 | 645.3 |
| tsvc_c3/s241 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.13x | 3+0 | 1 | 0 | 9 | 1923.9 |
| tsvc_c3/s241 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.10x | 3+0 | 1 | 0 | 2 | 630.0 |
| tsvc_c4/s318 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.25x | 1+0 | 1 | 0 | 3 | 423.1 |
| tsvc_c4/s318 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.18x | 1+0 | 1 | 0 | 7 | 1228.1 |
| tsvc_c4/s318 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.19x | 1+0 | 1 | 0 | 4 | 496.0 |
| tsvc_c4/s318 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.26x | 1+0 | 1 | 0 | 5 | 887.3 |
| tsvc_c4/s318 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.19x | 1+0 | 1 | 0 | 2 | 236.1 |
