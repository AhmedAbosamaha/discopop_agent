# Agent experiment run `e8_fix106_verify_mac`

- status: running (created 2026-10-14T15:58:35, finished None)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `2dbe2c0b3760a2770f89e04ee8cffba910a4ec20` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [2, 4], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fix106_replay_depth1 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fix106_replay_depth2 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c5/s2251 | fix106_replay_depth1 | none | 1 | parallel-not-faster | 0.38x | —+— | — | — | 0 | — |
| tsvc_c5/s2251 | fix106_replay_depth2 | none | 1 | parallel-not-faster | 0.78x | —+— | — | — | 0 | — |
