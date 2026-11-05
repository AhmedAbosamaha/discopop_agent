# Agent experiment run `e11_ref_check`

- status: running (created 2026-11-05T21:49:57, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `43f8214394bbf4d7123701fc197822c4fb4ef053` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| claude_code | none | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| expert_openmp | none | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| repoomp_claude | none | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npbc_c1/cg | claude_code | none | 1 | BROKEN | 10.38x | —+— | — | — | 0 | — |
| npbc_c1/cg | expert_openmp | none | 1 | FASTER | 10.33x | —+— | — | — | 0 | — |
| npbc_c1/cg | repoomp_claude | none | 1 | FASTER | 10.05x | —+— | — | — | 0 | — |
| npbc_c1/ep | claude_code | none | 1 | SCAFFOLD_MODIFIED | — | —+— | — | — | 0 | — |
| npbc_c1/ep | expert_openmp | none | 1 | BROKEN | 8.68x | —+— | — | — | 0 | — |
| npbc_c1/ep | repoomp_claude | none | 1 | FASTER | 8.61x | —+— | — | — | 0 | — |
