# Agent experiment run `e6x_1`

- status: finished (created 2026-11-03T21:33:11, finished 2026-11-04T07:39:19)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `2f2e7d5359e92265bb464e8f50473136f3385861` (uncommitted diff sha256 `None`)
- harness: `2f2e7d5359e92265bb464e8f50473136f3385861` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 565 | 0 |
| llm_pragmas_v5_exact | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 17420 | 70 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.34x | 7+0 | 0 | 14 | 0 | 566.6 |
| llnl_c1/lulesh | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.35x | 7+0 | 0 | 14 | 0 | 563.8 |
| llnl_c1/lulesh | llm_pragmas_v5_exact | claude-haiku-4-5-20251001 | 1 | FASTER | 1.48x | 3+19 | 14 | 14 | 30 | 21458.1 |
| llnl_c1/lulesh | llm_pragmas_v5_exact | claude-haiku-4-5-20251001 | 2 | FASTER | 1.81x | 0+16 | 13 | 14 | 40 | 13382.4 |
