# Agent experiment run `t0_14_c4_refs`

- status: running (created 2026-10-10T12:12:28, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `f2f22effa2db5a93a1868a332bb6c96a8b94292b` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| expert_openmp | none | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s311 | expert_openmp | none | 1 | FASTER | 8.77x | —+— | — | — | 0 | — |
| tsvc_c4/s3111 | expert_openmp | none | 1 | FASTER | 28.31x | —+— | — | — | 0 | — |
| tsvc_c4/s3113 | expert_openmp | none | 1 | FASTER | 8.72x | —+— | — | — | 0 | — |
| tsvc_c4/s314 | expert_openmp | none | 1 | FASTER | 8.98x | —+— | — | — | 0 | — |
| tsvc_c4/s315 | expert_openmp | none | 1 | FASTER | 10.62x | —+— | — | — | 0 | — |
| tsvc_c4/s316 | expert_openmp | none | 1 | FASTER | 9.03x | —+— | — | — | 0 | — |
| tsvc_c4/s318 | expert_openmp | none | 1 | FASTER | 20.58x | —+— | — | — | 0 | — |
| tsvc_c4/s319 | expert_openmp | none | 1 | FASTER | 4.13x | —+— | — | — | 0 | — |
| tsvc_c4/s341 | expert_openmp | none | 1 | FASTER | 2.37x | —+— | — | — | 0 | — |
