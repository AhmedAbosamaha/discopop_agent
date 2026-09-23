# Agent experiment run `local_obs1`

- status: running (created 2026-09-16T23:29:49, finished None)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `3b5ab817f67e1fec458dfa4697e8cd78f62f0ed6` (uncommitted diff sha256 `2339a14df3e66c9b9cd999aac9008ea38d7bb3f53f51a2159a0370521ccd557c`)
- harness: `ee9fe07f3781ab05717e082be79491c4ee75f4b5` on `agent-experiments`
- verify size `per_kernel`, threads [2, 4], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | claude-haiku-4-5-20251001 | 3 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 359 | 11 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | full | claude-haiku-4-5-20251001 | 1 | FASTER | 3.41x | 0+2 | 1 | 4 | 4 | 358.7 |
| polybench/jacobi-2d-imper | full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.80x | 0+2 | 1 | 4 | 3 | 207.2 |
| polybench/seidel-2d | full | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 1.00x | 0+1 | 1 | 3 | 4 | 473.8 |
