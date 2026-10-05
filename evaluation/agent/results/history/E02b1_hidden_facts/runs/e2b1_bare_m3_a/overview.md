# Agent experiment run `e2b1_bare_m3_a`

- status: finished (created 2026-09-28T20:45:32, finished 2026-09-28T22:59:41)
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
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 40 | 8 | 12 | 0 | 0 | 2 | 18 | 0 | 0 | 0 | 0 | 0 | 89 | 40 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 96.0 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | BROKEN | 3.76x | —+— | — | — | 1 | 56.9 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 1.40x | —+— | — | — | 1 | 88.9 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.40x | —+— | — | — | 1 | 34.2 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.35x | —+— | — | — | 1 | 84.5 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 1.47x | —+— | — | — | 1 | 114.4 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 6 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 132.1 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 7 | BROKEN | 3.54x | —+— | — | — | 1 | 24.1 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | 3.64x | —+— | — | — | 1 | 54.3 |
| tsvc_b1/s131 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.69x | —+— | — | — | 1 | 66.3 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.67x | —+— | — | — | 1 | 36.4 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 73.2 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.44x | —+— | — | — | 1 | 106.1 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.44x | —+— | — | — | 1 | 114.6 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.41x | —+— | — | — | 1 | 87.8 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 123.1 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 6 | parallel-not-faster | 0.44x | —+— | — | — | 1 | 78.0 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.41x | —+— | — | — | 1 | 88.3 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | —+— | — | — | 1 | 44.6 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.44x | —+— | — | — | 1 | 126.5 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 1.84x | —+— | — | — | 1 | 253.8 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | BROKEN | 2.15x | —+— | — | — | 1 | 134.1 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 1.85x | —+— | — | — | 1 | 101.2 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.51x | —+— | — | — | 1 | 276.3 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.62x | —+— | — | — | 1 | 149.3 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 2.21x | —+— | — | — | 1 | 202.9 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 6 | FASTER | 3.55x | —+— | — | — | 1 | 115.8 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 7 | FASTER | 2.22x | —+— | — | — | 1 | 116.7 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | 2.15x | —+— | — | — | 1 | 101.6 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 9 | BROKEN | 2.21x | —+— | — | — | 1 | 128.6 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.87x | —+— | — | — | 1 | 46.7 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | BROKEN | 3.89x | —+— | — | — | 1 | 24.1 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | 0.71x | —+— | — | — | 1 | 146.6 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | 1.53x | —+— | — | — | 1 | 145.1 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.85x | —+— | — | — | 1 | 40.2 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.85x | —+— | — | — | 1 | 34.3 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 6 | BROKEN | 3.91x | —+— | — | — | 1 | 43.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 7 | no-change | 1.02x | —+— | — | — | 1 | 41.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | 3.83x | —+— | — | — | 1 | 35.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 9 | BROKEN | 3.90x | —+— | — | — | 1 | 26.6 |
