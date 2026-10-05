# Agent experiment run `pkg_smoke_local`

- status: finished (created 2026-09-18T14:15:49, finished 2026-09-18T15:08:06)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `728d63be7b8c292bca9da53c1700488a6d5107d5` (uncommitted diff sha256 `5248579e2b498a15f3b04ffeed7b34881c155db7c96575e4e130150028c34d61`)
- harness: `a31064928c269d8590b46b38a5b7778c7ff4da13` on `agent-experiments`
- verify size `per_kernel`, threads [8], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 46 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npb/is | discopop_gate | none | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 33.5 |
| polybench/2mm | discopop_gate | none | 1 | FASTER | 2.82x | 2+0 | 0 | 4 | 0 | 58.1 |
