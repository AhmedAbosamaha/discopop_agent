# Agent experiment run `e8v5_r_1`

- status: finished (created 2026-10-14T20:26:55, finished 2026-10-15T06:37:19)
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
| depth1_v5 | claude-haiku-4-5-20251001 | 18 | 13 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 518 | 93 |
| depth2_v5 | claude-haiku-4-5-20251001 | 18 | 8 | 0 | 0 | 0 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | 813 | 123 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s112 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 9 | 770.1 |
| tsvc_c2/s112 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.51x | 2+0 | 2 | 0 | 2 | 397.4 |
| tsvc_c2/s112 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 4 | 976.0 |
| tsvc_c2/s112 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 4 | 648.9 |
| tsvc_c2/s112 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 740.6 |
| tsvc_c2/s112 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.25x | 2+0 | 3 | 0 | 6 | 567.4 |
| tsvc_c2/s127 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.25x | 2+0 | 2 | 0 | 8 | 610.2 |
| tsvc_c2/s127 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.94x | 1+0 | 2 | 0 | 4 | 478.9 |
| tsvc_c2/s127 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.21x | 1+0 | 2 | 0 | 3 | 260.3 |
| tsvc_c2/s127 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 6 | 734.2 |
| tsvc_c2/s127 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.15x | 3+0 | 3 | 0 | 6 | 662.1 |
| tsvc_c2/s127 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.18x | 3+0 | 3 | 0 | 7 | 1300.0 |
| tsvc_c2/s212 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.32x | 3+0 | 2 | 0 | 3 | 460.4 |
| tsvc_c2/s212 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.31x | 3+0 | 2 | 0 | 3 | 492.5 |
| tsvc_c2/s212 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.14x | 3+0 | 2 | 0 | 3 | 441.4 |
| tsvc_c2/s212 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 10 | 1359.4 |
| tsvc_c2/s212 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 6 | 1025.6 |
| tsvc_c2/s212 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.34x | 4+0 | 3 | 0 | 6 | 810.2 |
| tsvc_c2/s252 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.17x | 3+0 | 2 | 0 | 4 | 491.1 |
| tsvc_c2/s252 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.25x | 3+0 | 2 | 0 | 5 | 755.1 |
| tsvc_c2/s252 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.61x | 2+0 | 2 | 0 | 2 | 301.4 |
| tsvc_c2/s252 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.22x | 2+0 | 3 | 0 | 7 | 778.1 |
| tsvc_c2/s252 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.65x | 2+0 | 3 | 0 | 4 | 506.7 |
| tsvc_c2/s252 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.24x | 2+0 | 3 | 0 | 5 | 535.3 |
| tsvc_c2/s254 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.47x | 1+0 | 2 | 0 | 4 | 391.0 |
| tsvc_c2/s254 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.48x | 1+0 | 2 | 0 | 6 | 543.3 |
| tsvc_c2/s254 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.45x | 1+0 | 2 | 0 | 4 | 572.5 |
| tsvc_c2/s254 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.56x | 2+0 | 3 | 0 | 5 | 815.1 |
| tsvc_c2/s254 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 5 | 892.7 |
| tsvc_c2/s254 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.45x | 1+0 | 3 | 0 | 9 | 1208.9 |
| tsvc_c4/s341 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1398.0 |
| tsvc_c4/s341 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 0.97x | 0+0 | 0 | 0 | 8 | 789.4 |
| tsvc_c4/s341 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 9 | 1562.3 |
| tsvc_c4/s341 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 9 | 1621.9 |
| tsvc_c4/s341 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1345.7 |
| tsvc_c4/s341 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 11 | 1125.4 |
