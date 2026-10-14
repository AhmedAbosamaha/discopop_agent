# Agent experiment run `e8_c5_refs`

- status: running (created 2026-10-14T01:32:01, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `335c0bd845adbf44a6f95a6dcfe36504e54f55d0` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| expert_openmp | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| step1 | none | 5 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c5/s123 | expert_openmp | none | 1 | FASTER | 2.63x | —+— | — | — | 0 | — |
| tsvc_c5/s123 | step1 | none | 1 | FASTER | 1.23x | —+— | — | — | 0 | — |
| tsvc_c5/s221 | expert_openmp | none | 1 | FASTER | 2.98x | —+— | — | — | 0 | — |
| tsvc_c5/s221 | step1 | none | 1 | parallel-not-faster | 0.90x | —+— | — | — | 0 | — |
| tsvc_c5/s2251 | expert_openmp | none | 1 | FASTER | 2.36x | —+— | — | — | 0 | — |
| tsvc_c5/s2251 | step1 | none | 1 | parallel-not-faster | 0.65x | —+— | — | — | 0 | — |
| tsvc_c5/s233 | expert_openmp | none | 1 | FASTER | 12.53x | —+— | — | — | 0 | — |
| tsvc_c5/s233 | step1 | none | 1 | FASTER | 1.75x | —+— | — | — | 0 | — |
| tsvc_c5/s257 | expert_openmp | none | 1 | FASTER | 7.44x | —+— | — | — | 0 | — |
| tsvc_c5/s257 | step1 | none | 1 | FASTER | 4.45x | —+— | — | — | 0 | — |
