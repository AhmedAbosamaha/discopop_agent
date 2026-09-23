# Agent experiment run `move_smoke`

- status: finished (created 2026-09-20T02:11:38, finished 2026-09-20T02:12:43)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `58d959f2e7dd2e86f6cb2931f9767a68df22307e` (uncommitted diff sha256 `88989b6c01357a06109026ec4343766cd00d139ceaf16d6dd6993d427c6a0a59`)
- harness: `58d959f2e7dd2e86f6cb2931f9767a68df22307e` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [4], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 37 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/atax | discopop_gate | none | 1 | LARGE | 1.00 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/atax | discopop_gate | none | 1 | parallel-speed-not-measurable | 1.00x | 1+0 | 0 | 3 | 0 | 37.2 |
