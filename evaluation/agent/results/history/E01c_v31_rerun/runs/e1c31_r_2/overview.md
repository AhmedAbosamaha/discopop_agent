# Agent experiment run `e1c31_r_2`

- status: finished (created 2026-09-26T13:25:56, finished 2026-09-26T20:09:58)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `5935bded2c68c58828e236d9645087f658d17e4e` (uncommitted diff sha256 `None`)
- harness: `5935bded2c68c58828e236d9645087f658d17e4e` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 25 | 21 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 533 | 81 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.12x | 2+0 | 1 | 0 | 1 | 249.4 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.27x | 1+0 | 1 | 0 | 2 | 533.2 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.01x | 2+0 | 1 | 0 | 5 | 1230.5 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.17x | 2+0 | 1 | 0 | 2 | 438.8 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 1.27x | 1+0 | 1 | 0 | 3 | 770.5 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.38x | 3+0 | 1 | 1 | 4 | 1558.8 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.39x | 3+0 | 1 | 1 | 4 | 950.5 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.35x | 3+0 | 1 | 1 | 2 | 459.5 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 1.14x | 2+0 | 1 | 1 | 1 | 469.9 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 1.34x | 3+0 | 1 | 1 | 3 | 705.2 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.08x | 1+0 | 1 | 1 | 1 | 516.7 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.47x | 1+0 | 1 | 1 | 8 | 2155.0 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.08x | 2+0 | 1 | 1 | 1 | 461.8 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 1.54x | 1+0 | 1 | 1 | 1 | 431.2 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 1.10x | 1+0 | 1 | 1 | 2 | 701.7 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.85x | 2+0 | 1 | 0 | 6 | 1699.7 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.18x | 1+0 | 1 | 0 | 2 | 629.5 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 4.07x | 1+0 | 1 | 0 | 9 | 2526.0 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 9 | 2820.4 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 2526.3 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.58x | 1+0 | 1 | 1 | 1 | 283.9 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.62x | 1+0 | 1 | 1 | 1 | 191.1 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.64x | 1+0 | 1 | 1 | 1 | 122.1 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.62x | 1+0 | 1 | 1 | 1 | 159.5 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.18x | 2+0 | 1 | 1 | 2 | 348.5 |
