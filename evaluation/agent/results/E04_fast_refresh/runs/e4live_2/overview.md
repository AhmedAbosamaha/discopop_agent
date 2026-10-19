# Agent experiment run `e4live_2`

- status: finished (created 2026-10-18T23:15:49, finished 2026-10-19T07:52:52)
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
| fast_recon_v5 | claude-haiku-4-5-20251001 | 30 | 19 | 1 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 905 | 168 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s292 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.68x | 1+0 | 1 | 0 | 1 | 262.9 |
| tsvc_c2/s292 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.70x | 1+0 | 1 | 0 | 1 | 179.7 |
| tsvc_c2/s292 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.85x | 1+0 | 1 | 0 | 1 | 206.3 |
| tsvc_c2/s292 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.93x | 1+0 | 1 | 0 | 1 | 164.7 |
| tsvc_c2/s292 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.95x | 1+0 | 1 | 0 | 1 | 206.1 |
| tsvc_c2/s293 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.83x | 1+0 | 1 | 0 | 1 | 172.2 |
| tsvc_c2/s293 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.88x | 1+0 | 1 | 0 | 1 | 103.2 |
| tsvc_c2/s293 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.78x | 1+0 | 1 | 0 | 1 | 176.9 |
| tsvc_c2/s293 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.90x | 1+0 | 1 | 0 | 1 | 148.2 |
| tsvc_c2/s293 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.95x | 1+0 | 1 | 0 | 1 | 149.3 |
| tsvc_c3/s331 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1402.4 |
| tsvc_c3/s331 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.19x | 1+0 | 1 | 0 | 8 | 1039.7 |
| tsvc_c3/s331 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 11 | 1693.1 |
| tsvc_c3/s331 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1486.1 |
| tsvc_c3/s331 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.92x | 1+0 | 1 | 0 | 10 | 1498.2 |
| tsvc_c4/s3113 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.90x | 1+0 | 1 | 0 | 7 | 1181.7 |
| tsvc_c4/s3113 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.35x | 1+0 | 1 | 0 | 8 | 1432.7 |
| tsvc_c4/s3113 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1765.2 |
| tsvc_c4/s3113 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 2016.4 |
| tsvc_c4/s3113 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.42x | 1+0 | 1 | 0 | 2 | 489.5 |
| tsvc_c4/s319 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.02x | 1+0 | 1 | 0 | 5 | 1135.4 |
| tsvc_c4/s319 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.15x | 1+0 | 1 | 0 | 1 | 242.8 |
| tsvc_c4/s319 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.12x | 1+0 | 1 | 0 | 1 | 285.5 |
| tsvc_c4/s319 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.16x | 1+0 | 1 | 0 | 1 | 322.8 |
| tsvc_c4/s319 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.90x | 2+0 | 1 | 0 | 4 | 771.1 |
| tsvc_c4/s341 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1899.4 |
| tsvc_c4/s341 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1689.5 |
| tsvc_c4/s341 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1935.6 |
| tsvc_c4/s341 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1942.8 |
| tsvc_c4/s341 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 12 | 2906.5 |
