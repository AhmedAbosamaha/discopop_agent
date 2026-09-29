# Agent experiment run `e2b1_bare_m3_bfs`

- status: finished (created 2026-09-28T20:46:53, finished 2026-09-28T21:51:20)
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
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 124 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 6.86x | —+— | — | — | 1 | 95.9 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | FASTER | 6.46x | —+— | — | — | 1 | 168.7 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.12x | —+— | — | — | 1 | 142.1 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 6.53x | —+— | — | — | 1 | 113.4 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.08x | —+— | — | — | 1 | 94.2 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 6.65x | —+— | — | — | 1 | 157.0 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 6 | FASTER | 9.65x | —+— | — | — | 1 | 100.2 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 7 | FASTER | 6.08x | —+— | — | — | 1 | 74.0 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 8 | FASTER | 6.95x | —+— | — | — | 1 | 133.8 |
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 9 | FASTER | 6.45x | —+— | — | — | 1 | 138.8 |
