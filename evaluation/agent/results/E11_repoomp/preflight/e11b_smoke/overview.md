# Agent experiment run `e11b_smoke`

- status: finished (created 2026-11-06T08:31:24, finished 2026-11-06T08:38:48)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `f08f7f3d6709fcc7f3b93c73be2fc26cd35b1acb` (uncommitted diff sha256 `None`)
- harness: `f08f7f3d6709fcc7f3b93c73be2fc26cd35b1acb` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 31 | 1 |
| expert_ref | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 362 | 1 |
| repoomp_release | none | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 18 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | repoomp_release | none | 1 | parallel-not-faster | 1.00x | —+— | — | — | 6 | — |
| tsvc_c2/k23 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | BROKEN | 4.22x | —+— | — | — | 1 | 30.7 |
| tsvc_c2/k23 | expert_ref | none | 1 | FASTER | 3.46x | —+— | — | — | 0 | — |
| tsvc_c2/k23 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 3.42x | 0+2 | 1 | 0 | 1 | 361.9 |
| tsvc_c2/k23 | repoomp_release | none | 1 | parallel-not-faster | 1.01x | —+— | — | — | 12 | — |
