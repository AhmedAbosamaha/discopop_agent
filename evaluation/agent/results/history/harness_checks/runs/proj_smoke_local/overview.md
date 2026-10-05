# Agent experiment run `proj_smoke_local`

- status: finished (created 2026-09-18T07:23:18, finished 2026-09-18T07:25:02)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `728d63be7b8c292bca9da53c1700488a6d5107d5` (uncommitted diff sha256 `6518d09d94cd8acf5c9a78e42f122083ab1da2be5dc4da015c5048fbea923668`)
- harness: `a31064928c269d8590b46b38a5b7778c7ff4da13` on `agent-experiments`
- verify size `STANDARD`, threads [8], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| calib/privtemp_proj | discopop_gate | none | 1 | FASTER | 2.17x | 1+0 | 0 | 2 | 0 | 32.3 |
| calib/vecsum_proj | discopop_gate | none | 1 | FASTER | 1.58x | 1+0 | 0 | 2 | 0 | 32.1 |
