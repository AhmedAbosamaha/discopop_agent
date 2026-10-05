# Agent experiment run `pilot2`

- status: finished (created 2026-09-16T19:44:16, finished 2026-09-16T19:55:53)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `3b5ab817f67e1fec458dfa4697e8cd78f62f0ed6` (uncommitted diff sha256 `None`)
- harness: `ee9fe07f3781ab05717e082be79491c4ee75f4b5` on `agent-experiments`
- verify size `per_kernel`, threads [6, 12], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 588 | 8 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/seidel-2d | full | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 1.00x | 0+1 | 1 | 0 | 8 | 587.6 |
