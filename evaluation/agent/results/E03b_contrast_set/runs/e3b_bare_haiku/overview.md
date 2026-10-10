# Agent experiment run `e3b_bare_haiku`

- status: finished (created 2026-10-10T15:12:43, finished 2026-10-10T16:31:36)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `cb921121f56cdae31ede62d3a6a3aaf64ef1ebfc` (uncommitted diff sha256 `None`)
- harness: `cb921121f56cdae31ede62d3a6a3aaf64ef1ebfc` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-haiku-4-5-20251001 | 35 | 33 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 71 | 35 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s311 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.48x | —+— | — | — | 1 | 27.8 |
| tsvc_c4/s311 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 8.62x | —+— | — | — | 1 | 42.2 |
| tsvc_c4/s311 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 5.53x | —+— | — | — | 1 | 38.1 |
| tsvc_c4/s311 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 8.56x | —+— | — | — | 1 | 31.1 |
| tsvc_c4/s311 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 7.33x | —+— | — | — | 1 | 24.8 |
| tsvc_c4/s3113 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.93x | —+— | — | — | 1 | 74.3 |
| tsvc_c4/s3113 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 8.45x | —+— | — | — | 1 | 73.2 |
| tsvc_c4/s3113 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 8.96x | —+— | — | — | 1 | 102.5 |
| tsvc_c4/s3113 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.13x | —+— | — | — | 1 | 103.6 |
| tsvc_c4/s3113 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 8.90x | —+— | — | — | 1 | 42.3 |
| tsvc_c4/s314 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 9.58x | —+— | — | — | 1 | 100.2 |
| tsvc_c4/s314 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 10.04x | —+— | — | — | 1 | 112.3 |
| tsvc_c4/s314 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 8.29x | —+— | — | — | 1 | 76.6 |
| tsvc_c4/s314 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 9.93x | —+— | — | — | 1 | 58.3 |
| tsvc_c4/s314 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 9.21x | —+— | — | — | 1 | 87.6 |
| tsvc_c4/s315 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 9.28x | —+— | — | — | 1 | 82.9 |
| tsvc_c4/s315 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 9.05x | —+— | — | — | 1 | 79.0 |
| tsvc_c4/s315 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 11.14x | —+— | — | — | 1 | 121.7 |
| tsvc_c4/s315 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 10.31x | —+— | — | — | 1 | 70.8 |
| tsvc_c4/s315 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.31x | —+— | — | — | 1 | 104.5 |
| tsvc_c4/s316 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 7.17x | —+— | — | — | 1 | 40.8 |
| tsvc_c4/s316 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 9.03x | —+— | — | — | 1 | 31.0 |
| tsvc_c4/s316 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 8.89x | —+— | — | — | 1 | 46.3 |
| tsvc_c4/s316 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 9.05x | —+— | — | — | 1 | 57.9 |
| tsvc_c4/s316 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 9.05x | —+— | — | — | 1 | 56.0 |
| tsvc_c4/s318 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 5.29x | —+— | — | — | 1 | 83.1 |
| tsvc_c4/s318 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 5.25x | —+— | — | — | 1 | 113.0 |
| tsvc_c4/s318 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 6.46x | —+— | — | — | 1 | 124.5 |
| tsvc_c4/s318 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 6.64x | —+— | — | — | 1 | 107.6 |
| tsvc_c4/s318 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.50x | —+— | — | — | 1 | 176.7 |
| tsvc_c4/s319 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.91x | —+— | — | — | 1 | 33.3 |
| tsvc_c4/s319 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.05x | —+— | — | — | 1 | 31.1 |
| tsvc_c4/s319 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.05x | —+— | — | — | 1 | 38.8 |
| tsvc_c4/s319 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.80x | —+— | — | — | 1 | 21.8 |
| tsvc_c4/s319 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.15x | —+— | — | — | 1 | 37.1 |
