# Agent experiment run `e11_bare`

- status: finished (created 2026-11-06T05:08:23, finished 2026-11-06T06:29:39)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `1cddb8907bd3e7e8fd4184355fe57aad327f7081` (uncommitted diff sha256 `None`)
- harness: `1cddb8907bd3e7e8fd4184355fe57aad327f7081` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-sonnet-4-5-20250929 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 166 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npbc_c1/cg | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | FASTER | 10.27x | —+— | — | — | 1 | 143.5 |
| npbc_c1/cg | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | FASTER | 10.05x | —+— | — | — | 1 | 140.9 |
| npbc_c1/cg | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | FASTER | 10.16x | —+— | — | — | 1 | 168.3 |
| npbc_c1/cg | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | FASTER | 10.03x | —+— | — | — | 1 | 174.9 |
| npbc_c1/cg | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | FASTER | 10.34x | —+— | — | — | 1 | 163.5 |
| npbc_c1/ep | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | FASTER | 9.14x | —+— | — | — | 1 | 191.2 |
| npbc_c1/ep | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | FASTER | 8.88x | —+— | — | — | 1 | 157.8 |
| npbc_c1/ep | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | FASTER | 8.59x | —+— | — | — | 1 | 231.1 |
| npbc_c1/ep | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | FASTER | 8.39x | —+— | — | — | 1 | 138.1 |
| npbc_c1/ep | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | FASTER | 7.85x | —+— | — | — | 1 | 216.8 |
