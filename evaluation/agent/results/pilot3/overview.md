# Agent experiment run `pilot3`

- status: running (created 2026-09-18T19:31:30, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `96f173ae6b5554fb99f587006af4057c3f1ee03b` (uncommitted diff sha256 `None`)
- harness: `7c93853f3e7d6b7b0a3aa84b41e3b518c911eef7` on `agent-experiments`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | claude-haiku-4-5-20251001 | 4 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 181 | 8 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | full | claude-haiku-4-5-20251001 | 1 | FASTER | 10.57x | 0+2 | 1 | 6 | 1 | 124.2 |
| polybench/floyd-warshall | full | claude-haiku-4-5-20251001 | 1 | BROKEN | — | 0+2 | 1 | 3 | 2 | 238.0 |
| polybench/jacobi-2d-imper | full | claude-haiku-4-5-20251001 | 1 | FASTER | 2.52x | 0+2 | 1 | 5 | 1 | 86.0 |
| rodinia-3.1/hotspot | full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.08x | 1+0 | 0 | 6 | 4 | 1699.9 |
