# Agent experiment run `e1_bare_b`

- status: finished (created 2026-09-23T04:59:13, finished 2026-09-23T08:12:09)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `cf0d5d9603b8fd60635b47c8769fb42d60006be7` (uncommitted diff sha256 `None`)
- harness: `cf0d5d9603b8fd60635b47c8769fb42d60006be7` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 45 | 37 | 6 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 58 | 45 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.36x | —+— | — | — | 1 | 117.0 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.02x | —+— | — | — | 1 | 97.4 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 0.12x | —+— | — | — | 1 | 111.3 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.77x | —+— | — | — | 1 | 85.4 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.79x | —+— | — | — | 1 | 88.4 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.84x | —+— | — | — | 1 | 51.3 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 3.58x | —+— | — | — | 1 | 44.7 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 4.01x | —+— | — | — | 1 | 52.8 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 3.75x | —+— | — | — | 1 | 53.8 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 4.04x | —+— | — | — | 1 | 47.1 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.31x | —+— | — | — | 1 | 41.9 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 3.12x | —+— | — | — | 1 | 56.5 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 2.29x | —+— | — | — | 1 | 56.5 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 2.21x | —+— | — | — | 1 | 57.8 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 3.87x | —+— | — | — | 1 | 66.7 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.03x | —+— | — | — | 1 | 133.7 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 3.11x | —+— | — | — | 1 | 59.4 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 3.05x | —+— | — | — | 1 | 92.2 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 3.04x | —+— | — | — | 1 | 56.5 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 3.15x | —+— | — | — | 1 | 123.7 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.59x | —+— | — | — | 1 | 44.8 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 3.74x | —+— | — | — | 1 | 42.7 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 3.96x | —+— | — | — | 1 | 66.4 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 3.90x | —+— | — | — | 1 | 34.5 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 3.77x | —+— | — | — | 1 | 34.0 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.91x | —+— | — | — | 1 | 40.3 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.35x | —+— | — | — | 1 | 41.8 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 4.00x | —+— | — | — | 1 | 43.3 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 4.01x | —+— | — | — | 1 | 44.9 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 2.44x | —+— | — | — | 1 | 48.7 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.31x | —+— | — | — | 1 | 24.3 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.95x | —+— | — | — | 1 | 21.5 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 2.78x | —+— | — | — | 1 | 31.0 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 2.65x | —+— | — | — | 1 | 24.6 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 3.22x | —+— | — | — | 1 | 72.8 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 5.29x | —+— | — | — | 1 | 89.8 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 6.01x | —+— | — | — | 1 | 96.0 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 5.07x | —+— | — | — | 1 | 103.6 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 5.65x | —+— | — | — | 1 | 106.2 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 5.44x | —+— | — | — | 1 | 62.3 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.65x | —+— | — | — | 1 | 120.3 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | — | —+— | — | — | 1 | 106.1 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.60x | —+— | — | — | 1 | 63.6 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.61x | —+— | — | — | 1 | 78.1 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 2.41x | —+— | — | — | 1 | 97.2 |
