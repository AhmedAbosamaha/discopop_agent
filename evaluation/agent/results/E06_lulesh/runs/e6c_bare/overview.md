# Agent experiment run `e6c_bare`

- status: finished (created 2026-11-03T08:42:28, finished 2026-11-03T21:37:03)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `7926675a7c59144ad270c860cb6f1f1af55a57c7` (uncommitted diff sha256 `None`)
- harness: `7926675a7c59144ad270c860cb6f1f1af55a57c7` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-fable-5-1 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 405 | 5 |
| bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 310 | 5 |
| bare_llm_v4 | claude-opus-5-5 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 201 | 5 |
| bare_llm_v4 | claude-sonnet-5 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 576 | 5 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| llnl_c1/lulesh | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 2.02x | —+— | — | — | 1 | 405.3 |
| llnl_c1/lulesh | bare_llm_v4 | claude-fable-5-1 | 2 | FASTER | 1.78x | —+— | — | — | 1 | 471.0 |
| llnl_c1/lulesh | bare_llm_v4 | claude-fable-5-1 | 3 | FASTER | 2.17x | —+— | — | — | 1 | 323.0 |
| llnl_c1/lulesh | bare_llm_v4 | claude-fable-5-1 | 4 | FASTER | 1.97x | —+— | — | — | 1 | 404.1 |
| llnl_c1/lulesh | bare_llm_v4 | claude-fable-5-1 | 5 | FASTER | 2.22x | —+— | — | — | 1 | 534.8 |
| llnl_c1/lulesh | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 202.2 |
| llnl_c1/lulesh | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 431.0 |
| llnl_c1/lulesh | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 406.8 |
| llnl_c1/lulesh | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 235.1 |
| llnl_c1/lulesh | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.95x | —+— | — | — | 1 | 309.9 |
| llnl_c1/lulesh | bare_llm_v4 | claude-opus-5-5 | 1 | FASTER | 1.99x | —+— | — | — | 1 | 198.2 |
| llnl_c1/lulesh | bare_llm_v4 | claude-opus-5-5 | 2 | FASTER | 2.16x | —+— | — | — | 1 | 167.5 |
| llnl_c1/lulesh | bare_llm_v4 | claude-opus-5-5 | 3 | FASTER | 2.16x | —+— | — | — | 1 | 221.6 |
| llnl_c1/lulesh | bare_llm_v4 | claude-opus-5-5 | 4 | FASTER | 2.84x | —+— | — | — | 1 | 205.8 |
| llnl_c1/lulesh | bare_llm_v4 | claude-opus-5-5 | 5 | FASTER | 1.99x | —+— | — | — | 1 | 200.7 |
| llnl_c1/lulesh | bare_llm_v4 | claude-sonnet-5 | 1 | FASTER | 1.99x | —+— | — | — | 1 | 575.7 |
| llnl_c1/lulesh | bare_llm_v4 | claude-sonnet-5 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 693.0 |
| llnl_c1/lulesh | bare_llm_v4 | claude-sonnet-5 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 579.0 |
| llnl_c1/lulesh | bare_llm_v4 | claude-sonnet-5 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 493.0 |
| llnl_c1/lulesh | bare_llm_v4 | claude-sonnet-5 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 524.5 |
