# Agent experiment run `v3_pilot_3`

- status: finished (created 2026-09-25T22:42:56, finished 2026-09-26T07:50:25)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `701bf895522d0fa866380a0ddcbefcdccd5ef82f` (uncommitted diff sha256 `None`)
- harness: `701bf895522d0fa866380a0ddcbefcdccd5ef82f` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 6 | 1 | 2 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 1458 | 36 |
| no_evidence | claude-haiku-4-5-20251001 | 6 | 5 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 572 | 14 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.03x | 1+0 | 1 | 1 | 3 | 763.0 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 6 | 1282.1 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.99x | 1+0 | 1 | 1 | 6 | 1633.5 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.15x | 1+0 | 1 | 1 | 1 | 539.5 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 2.12x | 2+0 | 1 | 1 | 3 | 1028.9 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.10x | 1+0 | 1 | 1 | 1 | 508.0 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 4.28x | 1+0 | 1 | 0 | 3 | 938.9 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 2249.0 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 9 | 2576.4 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 605.0 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.63x | 1+0 | 1 | 0 | 2 | 485.4 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.34x | 1+0 | 1 | 0 | 5 | 1219.9 |
