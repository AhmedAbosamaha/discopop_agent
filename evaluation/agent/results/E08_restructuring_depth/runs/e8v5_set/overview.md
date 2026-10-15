# Agent experiment run `e8v5_set`

- status: finished (created 2026-10-14T20:26:41, finished 2026-10-15T06:25:28)
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
| default_v5 | claude-haiku-4-5-20251001 | 15 | 9 | 1 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 411 | 73 |
| depth1_v5 | claude-haiku-4-5-20251001 | 15 | 8 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 515 | 64 |
| depth2_v5 | claude-haiku-4-5-20251001 | 15 | 7 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 902 | 111 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c5/s221 | default_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1199.1 |
| tsvc_c5/s221 | default_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1339.8 |
| tsvc_c5/s221 | default_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 11 | 1338.1 |
| tsvc_c5/s221 | default_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 10 | 1326.5 |
| tsvc_c5/s221 | default_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1304.4 |
| tsvc_c5/s221 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 8 | 1000.7 |
| tsvc_c5/s221 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 4 | 515.1 |
| tsvc_c5/s221 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 0 | 8 | 988.3 |
| tsvc_c5/s221 | depth1_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 635.5 |
| tsvc_c5/s221 | depth1_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 467.1 |
| tsvc_c5/s221 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 6 | 938.2 |
| tsvc_c5/s221 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1658.2 |
| tsvc_c5/s221 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 14 | 1727.0 |
| tsvc_c5/s221 | depth2_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 6 | 826.6 |
| tsvc_c5/s221 | depth2_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 7 | 891.9 |
| tsvc_c5/s2251 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.35x | 2+0 | 1 | 0 | 3 | 364.7 |
| tsvc_c5/s2251 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.27x | 2+0 | 1 | 0 | 3 | 471.9 |
| tsvc_c5/s2251 | default_v5 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.03x | 1+0 | 1 | 0 | 2 | 257.7 |
| tsvc_c5/s2251 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.40x | 2+0 | 1 | 0 | 3 | 453.1 |
| tsvc_c5/s2251 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.39x | 2+0 | 1 | 0 | 3 | 411.1 |
| tsvc_c5/s2251 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.95x | 2+0 | 2 | 0 | 2 | 295.0 |
| tsvc_c5/s2251 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.76x | 2+0 | 3 | 0 | 5 | 614.4 |
| tsvc_c5/s2251 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 1343.5 |
| tsvc_c5/s2251 | depth1_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.36x | 2+0 | 2 | 0 | 3 | 511.0 |
| tsvc_c5/s2251 | depth1_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 865.3 |
| tsvc_c5/s2251 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 6 | 901.6 |
| tsvc_c5/s2251 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 6 | 1355.3 |
| tsvc_c5/s2251 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.29x | 2+0 | 3 | 0 | 6 | 796.5 |
| tsvc_c5/s2251 | depth2_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.49x | 2+0 | 3 | 0 | 5 | 678.3 |
| tsvc_c5/s2251 | depth2_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 8 | 1193.3 |
| tsvc_c5/s257 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.54x | 1+0 | 1 | 0 | 1 | 160.2 |
| tsvc_c5/s257 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.13x | 2+0 | 1 | 0 | 2 | 272.5 |
| tsvc_c5/s257 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.42x | 1+0 | 1 | 0 | 2 | 159.9 |
| tsvc_c5/s257 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.51x | 1+0 | 1 | 0 | 1 | 177.6 |
| tsvc_c5/s257 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.58x | 1+0 | 1 | 0 | 1 | 169.1 |
| tsvc_c5/s257 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.54x | 1+0 | 2 | 0 | 4 | 506.5 |
| tsvc_c5/s257 | depth1_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.10x | 2+0 | 2 | 0 | 4 | 296.2 |
| tsvc_c5/s257 | depth1_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.69x | 1+0 | 2 | 0 | 3 | 664.1 |
| tsvc_c5/s257 | depth1_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.93x | 3+0 | 2 | 0 | 4 | 510.0 |
| tsvc_c5/s257 | depth1_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 7.55x | 1+0 | 2 | 0 | 4 | 422.9 |
| tsvc_c5/s257 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.46x | 1+0 | 3 | 0 | 8 | 909.2 |
| tsvc_c5/s257 | depth2_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.30x | 1+0 | 3 | 0 | 9 | 956.1 |
| tsvc_c5/s257 | depth2_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 7.33x | 2+0 | 3 | 0 | 6 | 727.1 |
| tsvc_c5/s257 | depth2_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 7.57x | 1+0 | 3 | 0 | 8 | 721.0 |
| tsvc_c5/s257 | depth2_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.50x | 1+0 | 3 | 0 | 4 | 568.5 |
