# Agent experiment run `d38_twin_smoke`

- status: finished (created 2026-09-24T23:05:10, finished 2026-09-24T23:18:45)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `ba67684bc3ae466d248abd2035ee338491494cd5` (uncommitted diff sha256 `47f605822d97b7eaa643a742434c191680249c6a0b85f0ab39bfa82e95964006`)
- harness: `ba67684bc3ae466d248abd2035ee338491494cd5` on `agentic_DiscoPop`
- verify size `SMALL`, threads [2], repeats 1

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| twin_dp | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 14 | 0 |
| twin_full | claude-haiku-4-5-20251001 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 172 | 1 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s121 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 0.51x | —+— | — | — | 0 | 14.2 |
| tsvc/s121 | twin_full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 172.0 |
