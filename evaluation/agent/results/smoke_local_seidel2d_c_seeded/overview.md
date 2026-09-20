# Agent experiment run `smoke_local_seidel2d_c_seeded`

- status: finished (created 2026-09-14T22:05:19, finished 2026-09-14T22:55:35)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `4927898c8ebe4245bc1326a712402759c0941126` (uncommitted diff sha256 `0a73a1eb48e327607d36fb1b146d7f2c820573b449ce9142d8de241dbb46459a`)
- harness: `4d7e3ce865ea108e96ebd3d489cc102bc0498cbb` on `agent-experiments`
- verify size `STANDARD`, threads [8], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | haiku | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2991 | 35 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/seidel-2d | full | haiku | 1 | no-change | 0.97x | 0+0 | 0 | 7 | 35 | 2990.9 |
