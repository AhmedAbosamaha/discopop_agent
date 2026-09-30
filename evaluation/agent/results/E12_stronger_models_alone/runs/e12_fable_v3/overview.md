# Agent experiment run `e12_fable_v3`

- status: finished (created 2026-09-30T08:38:27, finished 2026-09-30T13:08:20)
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
| bare_llm_nospeed_v3 | claude-fable-5-1 | 10 | 0 | 4 | 0 | 0 | 0 | 3 | 3 | 0 | 0 | 0 | 0 | 134 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | SCAFFOLD_MODIFIED | — | —+— | — | — | 1 | 124.3 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | SCAFFOLD_MODIFIED | 0.30x | —+— | — | — | 1 | 137.4 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 128.8 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | parallel-not-faster | 0.86x | —+— | — | — | 1 | 183.2 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 199.6 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | SCAFFOLD_MODIFIED | 0.01x | —+— | — | — | 1 | 131.0 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | BROKEN | — | —+— | — | — | 1 | 165.8 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | BROKEN | — | —+— | — | — | 1 | 128.7 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 161.6 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | BROKEN | — | —+— | — | — | 1 | 96.7 |
