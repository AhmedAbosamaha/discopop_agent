# Agent experiment run `e1c31_d`

- status: finished (created 2026-09-26T18:35:40, finished 2026-09-27T00:49:50)
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
| default | claude-haiku-4-5-20251001 | 12 | 0 | 0 | 0 | 0 | 11 | 0 | 1 | 0 | 0 | 0 | 0 | 1690 | 107 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s3112 | default | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 7.63x | 1+0 | 1 | 2 | 8 | 1693.3 |
| tsvc/s3112 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 2 | 9 | 1297.6 |
| tsvc/s3112 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 2 | 9 | 1963.9 |
| tsvc/s321 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 2002.7 |
| tsvc/s321 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1687.5 |
| tsvc/s321 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 2555.9 |
| tsvc/s322 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1681.9 |
| tsvc/s322 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1652.7 |
| tsvc/s322 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1585.1 |
| tsvc/s323 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 9 | 1866.7 |
| tsvc/s323 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 9 | 1840.9 |
| tsvc/s323 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 9 | 1563.5 |
