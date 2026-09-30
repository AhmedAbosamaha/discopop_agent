# Agent experiment run `e12_fable_b1`

- status: finished (created 2026-09-30T08:38:50, finished 2026-09-30T09:03:37)
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
| bare_llm_nospeed | claude-fable-5-1 | 10 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 38 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s161 | bare_llm_nospeed | claude-fable-5-1 | 1 | FASTER | 2.20x | —+— | — | — | 1 | 28.8 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-fable-5-1 | 2 | FASTER | 2.11x | —+— | — | — | 1 | 36.6 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-fable-5-1 | 3 | FASTER | 2.03x | —+— | — | — | 1 | 30.4 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-fable-5-1 | 4 | FASTER | 2.19x | —+— | — | — | 1 | 44.0 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-fable-5-1 | 5 | FASTER | 2.15x | —+— | — | — | 1 | 42.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-fable-5-1 | 1 | parallel-not-faster | 0.34x | —+— | — | — | 1 | 41.8 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-fable-5-1 | 2 | parallel-not-faster | 0.31x | —+— | — | — | 1 | 34.8 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-fable-5-1 | 3 | parallel-not-faster | 0.33x | —+— | — | — | 1 | 28.7 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-fable-5-1 | 4 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 38.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-fable-5-1 | 5 | parallel-not-faster | 0.22x | —+— | — | — | 1 | 40.1 |
