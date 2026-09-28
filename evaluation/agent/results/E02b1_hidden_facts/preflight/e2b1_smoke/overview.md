# Agent experiment run `e2b1_smoke`

- status: finished (created 2026-09-27T21:23:33, finished 2026-09-28T01:27:35)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `afb7d30291516b2d46d922722cdb4024a380c24b` (uncommitted diff sha256 `None`)
- harness: `afb7d30291516b2d46d922722cdb4024a380c24b` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 126 | 2 |
| full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 344 | 3 |
| no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 561 | 5 |
| twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 233 | 3 |
| twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 215 | 3 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| rodinia_b1/bfs | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 10.68x | —+— | — | — | 1 | 170.1 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.89x | 1+0 | 1 | 1 | 2 | 572.2 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.98x | 1+0 | 1 | 1 | 3 | 998.7 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 1 | 142.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 2 | 362.8 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.39x | —+— | — | — | 1 | 82.4 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | — | 1+0 | 1 | 0 | 1 | 115.8 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 1.45x | 2+0 | 1 | 0 | 2 | 123.7 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 0.46x | —+— | — | — | 2 | 324.0 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | changed-not-parallel | 1.03x | —+— | — | — | 1 | 67.5 |
