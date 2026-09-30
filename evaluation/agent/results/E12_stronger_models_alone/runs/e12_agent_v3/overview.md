# Agent experiment run `e12_agent_v3`

- status: finished (created 2026-09-30T09:42:16, finished 2026-09-30T11:28:27)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `adec159f08dffd173c376f24bb372568263e1e39` (uncommitted diff sha256 `None`)
- harness: `adec159f08dffd173c376f24bb372568263e1e39` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 20 | 10 | 2 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 253 | 39 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.29x | 2+0 | 1 | 0 | 1 | 228.5 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.16x | 2+0 | 1 | 0 | 1 | 107.0 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.21x | 2+0 | 1 | 0 | 1 | 127.4 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.05x | 2+0 | 1 | 0 | 1 | 112.6 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.30x | 2+0 | 1 | 0 | 1 | 138.1 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.15x | 2+0 | 1 | 0 | 1 | 93.3 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.84x | 2+0 | 1 | 0 | 1 | 135.3 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.94x | 2+0 | 1 | 0 | 1 | 181.3 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.00x | 2+0 | 1 | 0 | 1 | 92.3 |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.18x | 2+0 | 1 | 0 | 1 | 156.7 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 311.5 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 388.7 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 276.6 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 316.1 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.93x | 1+0 | 1 | 0 | 2 | 342.0 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 345.2 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 413.8 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.32x | 1+0 | 1 | 0 | 3 | 343.2 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 481.5 |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 309.1 |
