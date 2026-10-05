# Agent experiment run `vs_polly`

- status: running (created 2026-09-16T07:16:57, finished None)
- host: `rms14562`, compilers `/usr/lib/llvm-20/bin/clang` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `40fd846c98ae54c05bde7ea48ed04bc02d5840c7` on `agent-experiments`
- verify size `per_kernel`, threads [24], repeats 1

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| polly | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | polly | none | 1 | FASTER | 35.19x | —+— | — | — | 0 | — |
