# Agent experiment run `integrity_smoke_local`

- status: finished (created 2026-09-18T16:24:46, finished 2026-09-18T16:27:30)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `243c274b0f6fd4fb9dfbb26eb9821ee00d265d77` (uncommitted diff sha256 `None`)
- harness: `d48d0d90e8c240a8cb1e8e86d2a49e8aa974ba35` on `agent-experiments`
- verify size `SMALL`, threads [2], repeats 1

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 26 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| calib/vecsum | discopop_gate | none | 1 | FASTER | 1.18x | 1+0 | 0 | 1 | 0 | 23.7 |
| calib/vecsum | discopop_gate | none | 2 | FASTER | 1.48x | 1+0 | 0 | 1 | 0 | 21.9 |
| calib/vecsum_proj | discopop_gate | none | 1 | FASTER | 1.32x | 1+0 | 0 | 1 | 0 | 27.8 |
| calib/vecsum_proj | discopop_gate | none | 2 | FASTER | 1.37x | 1+0 | 0 | 1 | 0 | 27.4 |
