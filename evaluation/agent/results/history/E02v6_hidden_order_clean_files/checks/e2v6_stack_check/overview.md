# Agent experiment run `e2v6_stack_check`

- status: running (created 2026-10-06T20:58:51, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `0758ef82ad136cde97ec0e0afd2b70511c0cba42` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| k23_rep10_as_run | none | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| k23_rep10_stack_lifted | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| k53_rep10_as_run | none | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| k53_rep10_stack_lifted | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| k53_rep3_as_run | none | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| k53_rep3_stack_lifted | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k23 | k23_rep10_as_run | none | 1 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| tsvc_c2/k23 | k23_rep10_stack_lifted | none | 1 | parallel-not-faster | 0.43x | —+— | — | — | 0 | — |
| tsvc_c2/k53 | k53_rep10_as_run | none | 1 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| tsvc_c2/k53 | k53_rep10_stack_lifted | none | 1 | parallel-not-faster | 0.74x | —+— | — | — | 0 | — |
| tsvc_c2/k53 | k53_rep3_as_run | none | 1 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| tsvc_c2/k53 | k53_rep3_stack_lifted | none | 1 | parallel-not-faster | 0.81x | —+— | — | — | 0 | — |
