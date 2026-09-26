# Agent experiment run `v3_pilot_1`

- status: finished (created 2026-09-25T22:42:47, finished 2026-09-26T06:13:55)
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
| default | claude-haiku-4-5-20251001 | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 332 | 17 |
| no_evidence | claude-haiku-4-5-20251001 | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 284 | 18 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.39x | 2+0 | 1 | 1 | 1 | 245.9 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.46x | 2+0 | 1 | 1 | 6 | 1184.6 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.33x | 2+0 | 1 | 1 | 1 | 332.5 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.12x | 2+0 | 1 | 1 | 1 | 234.1 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.34x | 2+0 | 1 | 1 | 1 | 199.0 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.33x | 2+0 | 1 | 1 | 4 | 727.0 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.39x | 2+0 | 1 | 0 | 1 | 302.8 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.48x | 2+0 | 1 | 0 | 1 | 244.6 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.39x | 2+0 | 1 | 0 | 1 | 267.1 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.38x | 2+0 | 1 | 0 | 1 | 238.0 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.74x | 2+0 | 1 | 0 | 4 | 840.7 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.19x | 2+0 | 1 | 0 | 1 | 262.7 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.47x | 2+0 | 1 | 0 | 1 | 493.6 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.54x | 2+0 | 1 | 0 | 2 | 426.9 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.53x | 2+0 | 1 | 0 | 3 | 629.0 |
| tsvc/s1213 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 2.80x | 2+0 | 1 | 0 | 2 | 350.2 |
| tsvc/s1213 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.22x | 2+0 | 1 | 0 | 3 | 649.5 |
| tsvc/s1213 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 2.75x | 2+0 | 1 | 0 | 1 | 284.3 |
