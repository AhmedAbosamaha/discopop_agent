# Agent experiment run `e1_bare_a`

- status: finished (created 2026-09-23T04:59:11, finished 2026-09-23T07:32:30)
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
| bare_llm | claude-haiku-4-5-20251001 | 45 | 21 | 7 | 0 | 0 | 0 | 15 | 1 | 1 | 0 | 0 | 0 | 95 | 45 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.79x | —+— | — | — | 1 | 37.6 |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.86x | —+— | — | — | 1 | 154.2 |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.92x | —+— | — | — | 1 | 80.4 |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.82x | —+— | — | — | 1 | 74.9 |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 81.1 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 87.1 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 1.59x | —+— | — | — | 1 | 77.7 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 1.39x | —+— | — | — | 1 | 106.9 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.13x | —+— | — | — | 1 | 84.6 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 1.60x | —+— | — | — | 1 | 81.2 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.27x | —+— | — | — | 1 | 176.0 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 1.84x | —+— | — | — | 1 | 260.6 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 2.59x | —+— | — | — | 1 | 214.1 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 4 | BROKEN | 0.49x | —+— | — | — | 1 | 148.8 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 1.73x | —+— | — | — | 1 | 185.1 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 4.25x | —+— | — | — | 1 | 33.0 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 4.19x | —+— | — | — | 1 | 46.2 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 4.09x | —+— | — | — | 1 | 43.4 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 4.24x | —+— | — | — | 1 | 37.7 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 3.87x | —+— | — | — | 1 | 35.2 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.11x | —+— | — | — | 1 | 94.1 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.15x | —+— | — | — | 1 | 228.1 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.41x | —+— | — | — | 1 | 42.8 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 4 | BROKEN | 2.43x | —+— | — | — | 1 | 150.5 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.38x | —+— | — | — | 1 | 88.9 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.50x | —+— | — | — | 1 | 92.7 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.44x | —+— | — | — | 1 | 75.7 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 2.39x | —+— | — | — | 1 | 106.6 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 1.17x | —+— | — | — | 1 | 76.4 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 5 | BROKEN | 2.79x | —+— | — | — | 1 | 40.0 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.17x | —+— | — | — | 1 | 113.7 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.18x | —+— | — | — | 1 | 105.2 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 0.99x | —+— | — | — | 1 | 180.6 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 1.86x | —+— | — | — | 1 | 100.7 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.85x | —+— | — | — | 1 | 95.2 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.14x | —+— | — | — | 1 | 145.8 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 1.20x | —+— | — | — | 1 | 140.0 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 1.99x | —+— | — | — | 1 | 91.1 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 4 | SCAFFOLD_MODIFIED | 0.99x | —+— | — | — | 1 | 129.8 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 2.31x | —+— | — | — | 1 | 127.4 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.56x | —+— | — | — | 1 | 159.2 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 178.4 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 4.20x | —+— | — | — | 1 | 97.5 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 4 | BROKEN | 2.86x | —+— | — | — | 1 | 60.4 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 4.20x | —+— | — | — | 1 | 170.0 |
