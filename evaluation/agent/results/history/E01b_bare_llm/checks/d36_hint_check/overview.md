# Agent experiment run `d36_hint_check`

- status: finished (created 2026-09-23T20:46:47, finished 2026-09-23T21:54:30)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `1be54f01ce194c490695549fcc562da17c9c72c1` (uncommitted diff sha256 `None`)
- harness: `1be54f01ce194c490695549fcc562da17c9c72c1` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 9 | 4 | 4 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 104 | 9 |
| bare_llm_contract | claude-haiku-4-5-20251001 | 9 | 4 | 2 | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 111 | 9 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.64x | —+— | — | — | 1 | 32.6 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.07x | —+— | — | — | 1 | 168.9 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.94x | —+— | — | — | 1 | 88.2 |
| tsvc/s241 | bare_llm_contract | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.81x | —+— | — | — | 1 | 120.3 |
| tsvc/s241 | bare_llm_contract | claude-haiku-4-5-20251001 | 2 | FASTER | 1.54x | —+— | — | — | 1 | 110.7 |
| tsvc/s241 | bare_llm_contract | claude-haiku-4-5-20251001 | 3 | FASTER | 1.79x | —+— | — | — | 1 | 177.4 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.93x | —+— | — | — | 1 | 150.6 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.40x | —+— | — | — | 1 | 227.2 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 3.00x | —+— | — | — | 1 | 107.0 |
| tsvc/s281 | bare_llm_contract | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.05x | —+— | — | — | 1 | 89.6 |
| tsvc/s281 | bare_llm_contract | claude-haiku-4-5-20251001 | 2 | BROKEN | 1.95x | —+— | — | — | 1 | 248.9 |
| tsvc/s281 | bare_llm_contract | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | —+— | — | — | 1 | 18.8 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.07x | —+— | — | — | 1 | 65.3 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.07x | —+— | — | — | 1 | 80.0 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 5.33x | —+— | — | — | 1 | 103.7 |
| tsvc/s331 | bare_llm_contract | claude-haiku-4-5-20251001 | 1 | FASTER | 6.38x | —+— | — | — | 1 | 76.3 |
| tsvc/s331 | bare_llm_contract | claude-haiku-4-5-20251001 | 2 | FASTER | 5.44x | —+— | — | — | 1 | 119.5 |
| tsvc/s331 | bare_llm_contract | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.07x | —+— | — | — | 1 | 49.0 |
