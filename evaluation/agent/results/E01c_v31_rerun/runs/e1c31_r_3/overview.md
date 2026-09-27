# Agent experiment run `e1c31_r_3`

- status: finished (created 2026-09-26T13:26:00, finished 2026-09-26T15:01:06)
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
| default | claude-haiku-4-5-20251001 | 20 | 16 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 150 | 23 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.48x | 1+0 | 1 | 2 | 1 | 157.9 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.49x | 1+0 | 1 | 2 | 1 | 255.3 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.32x | 1+0 | 1 | 2 | 1 | 229.2 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.32x | 1+0 | 1 | 2 | 1 | 108.7 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.93x | 1+0 | 1 | 2 | 1 | 248.8 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.72x | 1+0 | 1 | 1 | 1 | 137.5 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.54x | 1+0 | 1 | 1 | 1 | 223.4 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.55x | 1+0 | 1 | 1 | 1 | 105.7 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.21x | 1+0 | 1 | 1 | 1 | 136.1 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 3.30x | 1+0 | 1 | 1 | 1 | 130.2 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.07x | 1+0 | 1 | 0 | 1 | 278.0 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.23x | 2+0 | 1 | 0 | 1 | 263.4 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.06x | 1+0 | 1 | 0 | 2 | 272.8 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.07x | 1+0 | 1 | 0 | 1 | 191.7 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 3 | 470.2 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.36x | 1+0 | 1 | 1 | 1 | 109.3 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.34x | 1+0 | 1 | 1 | 1 | 110.4 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.39x | 1+0 | 1 | 1 | 1 | 142.9 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.40x | 1+0 | 1 | 1 | 1 | 138.8 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.66x | 1+0 | 1 | 1 | 1 | 122.3 |
