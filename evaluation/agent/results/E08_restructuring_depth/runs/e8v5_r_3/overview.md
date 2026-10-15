# Agent experiment run `e8v5_r_3`

- status: finished (created 2026-10-14T20:27:27, finished 2026-10-15T03:19:13)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `305edbdef8e081e530b86f74c1f5035d4bd99122` (uncommitted diff sha256 `None`)
- harness: `305edbdef8e081e530b86f74c1f5035d4bd99122` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| depth1_v5 | claude-haiku-4-5-20251001 | 18 | 9 | 3 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 486 | 81 |
| depth2_v5 | claude-haiku-4-5-20251001 | 18 | 7 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 622 | 84 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s211 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 550.8 |
| tsvc_c2/s211 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.77x | 4+0 | 2 | 0 | 7 | 1060.0 |
| tsvc_c2/s211 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 608.4 |
| tsvc_c2/s211 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 1179.2 |
| tsvc_c2/s211 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.27x | 3+0 | 4 | 0 | 5 | 728.5 |
| tsvc_c2/s211 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.35x | 2+0 | 3 | 0 | 4 | 701.5 |
| tsvc_c2/s243 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 295.5 |
| tsvc_c2/s243 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.08x | 3+0 | 2 | 0 | 4 | 410.8 |
| tsvc_c2/s243 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.70x | 2+0 | 2 | 0 | 3 | 313.0 |
| tsvc_c2/s243 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.98x | 3+0 | 3 | 0 | 4 | 424.9 |
| tsvc_c2/s243 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 7 | 717.4 |
| tsvc_c2/s243 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.22x | 3+0 | 3 | 0 | 3 | 528.9 |
| tsvc_c2/s291 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.40x | 1+0 | 1 | 0 | 9 | 847.8 |
| tsvc_c2/s291 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.44x | 1+0 | 2 | 0 | 4 | 349.6 |
| tsvc_c2/s291 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.45x | 1+0 | 2 | 0 | 2 | 321.2 |
| tsvc_c2/s291 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 5 | 583.1 |
| tsvc_c2/s291 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.42x | 1+0 | 3 | 0 | 3 | 502.8 |
| tsvc_c2/s291 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.06x | 0+0 | 0 | 0 | 5 | 653.2 |
| tsvc_c2/s292 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.54x | 2+0 | 2 | 0 | 8 | 852.6 |
| tsvc_c2/s292 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.98x | 1+0 | 2 | 0 | 5 | 655.6 |
| tsvc_c2/s292 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.95x | 2+0 | 2 | 0 | 4 | 392.8 |
| tsvc_c2/s292 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.93x | 1+0 | 3 | 0 | 4 | 487.6 |
| tsvc_c2/s292 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.01x | 2+0 | 3 | 0 | 3 | 424.2 |
| tsvc_c2/s292 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.95x | 0+0 | 0 | 0 | 4 | 383.4 |
| tsvc_c3/s241 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.18x | 5+0 | 2 | 0 | 5 | 782.2 |
| tsvc_c3/s241 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.00x | 4+0 | 2 | 0 | 4 | 910.3 |
| tsvc_c3/s241 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 5 | 1121.0 |
| tsvc_c3/s241 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 4 | 1013.0 |
| tsvc_c3/s241 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 887.9 |
| tsvc_c3/s241 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 4 | 732.7 |
| tsvc_c3/s331 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 333.6 |
| tsvc_c3/s331 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 370.3 |
| tsvc_c3/s331 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.97x | 1+0 | 2 | 0 | 3 | 422.2 |
| tsvc_c3/s331 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 7 | 634.8 |
| tsvc_c3/s331 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 6 | 608.2 |
| tsvc_c3/s331 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 6 | 549.8 |
