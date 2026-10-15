# Agent experiment run `e8v5_r_2`

- status: finished (created 2026-10-14T20:27:10, finished 2026-10-15T03:32:02)
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
| depth1_v5 | claude-haiku-4-5-20251001 | 18 | 12 | 1 | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 562 | 86 |
| depth2_v5 | claude-haiku-4-5-20251001 | 18 | 13 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 616 | 96 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s121 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.03x | 4+0 | 2 | 0 | 4 | 471.5 |
| tsvc_c2/s121 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | BROKEN | 1.44x | 3+0 | 2 | 0 | 5 | 563.9 |
| tsvc_c2/s121 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.03x | 0+0 | 0 | 0 | 8 | 895.3 |
| tsvc_c2/s121 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 4 | 627.1 |
| tsvc_c2/s121 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.50x | 3+0 | 3 | 0 | 4 | 451.9 |
| tsvc_c2/s121 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 4 | 435.5 |
| tsvc_c2/s1213 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.79x | 3+0 | 2 | 0 | 4 | 635.6 |
| tsvc_c2/s1213 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.84x | 3+0 | 2 | 0 | 4 | 561.1 |
| tsvc_c2/s1213 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.20x | 2+0 | 2 | 0 | 4 | 782.0 |
| tsvc_c2/s1213 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 882.1 |
| tsvc_c2/s1213 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1339.4 |
| tsvc_c2/s1213 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.11x | 3+0 | 3 | 0 | 5 | 792.0 |
| tsvc_c2/s244 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.13x | 2+0 | 2 | 0 | 5 | 660.3 |
| tsvc_c2/s244 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.65x | 2+0 | 2 | 0 | 5 | 545.9 |
| tsvc_c2/s244 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 679.2 |
| tsvc_c2/s244 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.31x | 2+0 | 3 | 0 | 7 | 887.3 |
| tsvc_c2/s244 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.47x | 2+0 | 3 | 0 | 7 | 900.3 |
| tsvc_c2/s244 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 5.69x | 1+0 | 3 | 0 | 3 | 550.7 |
| tsvc_c2/s255 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.55x | 2+0 | 2 | 0 | 6 | 688.6 |
| tsvc_c2/s255 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.37x | 2+0 | 2 | 0 | 2 | 271.6 |
| tsvc_c2/s255 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.62x | 1+0 | 2 | 0 | 4 | 357.1 |
| tsvc_c2/s255 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.43x | 1+0 | 3 | 0 | 4 | 604.4 |
| tsvc_c2/s255 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.61x | 2+0 | 3 | 0 | 4 | 477.0 |
| tsvc_c2/s255 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.24x | 2+0 | 3 | 0 | 4 | 475.5 |
| tsvc_c2/s281 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.25x | 4+0 | 2 | 0 | 8 | 867.9 |
| tsvc_c2/s281 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 8 | 984.7 |
| tsvc_c2/s281 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.11x | 1+0 | 2 | 0 | 4 | 559.3 |
| tsvc_c2/s281 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1050.7 |
| tsvc_c2/s281 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.41x | 2+0 | 3 | 0 | 10 | 1378.5 |
| tsvc_c2/s281 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.66x | 2+0 | 3 | 0 | 6 | 792.9 |
| tsvc_c2/s293 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.89x | 1+0 | 2 | 0 | 3 | 406.0 |
| tsvc_c2/s293 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.94x | 1+0 | 2 | 0 | 4 | 436.8 |
| tsvc_c2/s293 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.85x | 1+0 | 2 | 0 | 4 | 444.2 |
| tsvc_c2/s293 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.93x | 1+0 | 3 | 0 | 5 | 550.9 |
| tsvc_c2/s293 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.88x | 1+0 | 3 | 0 | 3 | 413.3 |
| tsvc_c2/s293 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.86x | 1+0 | 3 | 0 | 3 | 298.7 |
