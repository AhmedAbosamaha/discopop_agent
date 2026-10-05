# Agent experiment run `smoke_local_seidel2d_c`

- status: finished (created 2026-09-14T18:11:13, finished 2026-09-14T18:27:00)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `4927898c8ebe4245bc1326a712402759c0941126` (uncommitted diff sha256 `4a949a7eeb2e5349fef0885fbf6fa238bdbef8343ff8ebcd5022f2a7a1aa57d9`)
- harness: `4d7e3ce865ea108e96ebd3d489cc102bc0498cbb` on `agent-experiments`
- verify size `STANDARD`, threads [8], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | haiku | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 925 | 22 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/seidel-2d | full | haiku | 1 | FASTER | 2.91x | 1+3 | 2 | 7 | 22 | 925.0 |
