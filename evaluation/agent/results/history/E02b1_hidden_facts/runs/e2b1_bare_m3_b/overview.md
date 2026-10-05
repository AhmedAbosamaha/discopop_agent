# Agent experiment run `e2b1_bare_m3_b`

- status: finished (created 2026-09-28T20:46:20, finished 2026-09-28T21:43:47)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `f35fac09c616bcc1cbb0e35d10d77541a5182782` (uncommitted diff sha256 `None`)
- harness: `f35fac09c616bcc1cbb0e35d10d77541a5182782` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 25 | 19 | 2 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 40 | 25 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.79x | —+— | — | — | 1 | 30.2 |
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.12x | —+— | — | — | 1 | 40.4 |
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.11x | —+— | — | — | 1 | 31.8 |
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.20x | —+— | — | — | 1 | 22.4 |
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.36x | —+— | — | — | 1 | 31.7 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.44x | —+— | — | — | 1 | 45.3 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 35.2 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 34.8 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 31.2 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.06x | —+— | — | — | 1 | 29.0 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.29x | —+— | — | — | 1 | 446.3 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 6.06x | —+— | — | — | 1 | 73.7 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.30x | —+— | — | — | 1 | 121.9 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.76x | —+— | — | — | 1 | 207.5 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 279.4 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 2.74x | —+— | — | — | 1 | 122.7 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 2.93x | —+— | — | — | 1 | 112.5 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.62x | —+— | — | — | 1 | 48.7 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.24x | —+— | — | — | 1 | 126.6 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.66x | —+— | — | — | 1 | 30.0 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.58x | —+— | — | — | 1 | 35.3 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.68x | —+— | — | — | 1 | 66.0 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.63x | —+— | — | — | 1 | 34.6 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.57x | —+— | — | — | 1 | 76.1 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.79x | —+— | — | — | 1 | 25.8 |
