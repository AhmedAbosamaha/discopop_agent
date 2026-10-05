# Agent experiment run `e12_opus_b1`

- status: finished (created 2026-09-30T07:16:31, finished 2026-09-30T12:38:06)
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
| bare_llm_nospeed | claude-opus-5-5 | 10 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 32 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s161 | bare_llm_nospeed | claude-opus-5-5 | 1 | FASTER | 3.49x | —+— | — | — | 1 | 33.2 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-opus-5-5 | 2 | FASTER | 3.63x | —+— | — | — | 1 | 26.3 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-opus-5-5 | 3 | FASTER | 2.17x | —+— | — | — | 1 | 32.2 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-opus-5-5 | 4 | FASTER | 2.17x | —+— | — | — | 1 | 31.5 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-opus-5-5 | 5 | FASTER | 3.79x | —+— | — | — | 1 | 31.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-opus-5-5 | 1 | parallel-not-faster | 0.27x | —+— | — | — | 1 | 40.7 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-opus-5-5 | 2 | parallel-not-faster | 0.25x | —+— | — | — | 1 | 31.1 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-opus-5-5 | 3 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 37.2 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-opus-5-5 | 4 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 31.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-opus-5-5 | 5 | parallel-not-faster | 0.30x | —+— | — | — | 1 | 28.9 |
