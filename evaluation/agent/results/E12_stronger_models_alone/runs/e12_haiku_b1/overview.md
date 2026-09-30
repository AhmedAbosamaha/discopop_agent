# Agent experiment run `e12_haiku_b1`

- status: finished (created 2026-09-30T07:16:36, finished 2026-09-30T09:47:16)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `adec159f08dffd173c376f24bb372568263e1e39` (uncommitted diff sha256 `None`)
- harness: `adec159f08dffd173c376f24bb372568263e1e39` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | 4 | 0 | 0 | 0 | 0 | 5 | 0 | 1 | 0 | 0 | 0 | 56 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 1.61x | —+— | — | — | 1 | 171.2 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 2.23x | —+— | — | — | 1 | 47.0 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 2.21x | —+— | — | — | 1 | 66.0 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.74x | —+— | — | — | 1 | 183.9 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.79x | —+— | — | — | 1 | 170.7 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.48x | —+— | — | — | 1 | 24.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.78x | —+— | — | — | 1 | 27.2 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.54x | —+— | — | — | 1 | 27.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.68x | —+— | — | — | 1 | 42.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 189.9 |
