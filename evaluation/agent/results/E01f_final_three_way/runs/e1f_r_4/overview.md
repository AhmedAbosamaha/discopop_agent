# Agent experiment run `e1f_r_4`

- status: finished (created 2026-10-02T20:44:19, finished 2026-10-03T00:39:35)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `912e3d9b101927b5f4dda588f624f14803211089` (uncommitted diff sha256 `None`)
- harness: `912e3d9b101927b5f4dda588f624f14803211089` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v3 | claude-haiku-4-5-20251001 | 20 | 11 | 1 | 0 | 0 | 7 | 0 | 1 | 0 | 0 | 0 | 0 | 320 | 97 |
| discopop_gate_v3 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s292 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.71x | 1+0 | 1 | 0 | 1 | 99.9 |
| tsvc_b1/s292 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.36x | 1+0 | 1 | 0 | 1 | 83.4 |
| tsvc_b1/s292 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.51x | 1+0 | 1 | 0 | 1 | 91.6 |
| tsvc_b1/s292 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.90x | 1+0 | 1 | 0 | 1 | 81.3 |
| tsvc_b1/s292 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.68x | 1+0 | 1 | 0 | 1 | 88.9 |
| tsvc_b1/s292 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.4 |
| tsvc_b1/s292 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.4 |
| tsvc_b1/s292 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_b1/s292 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_b1/s292 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_b1/s293 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.51x | 1+0 | 1 | 0 | 1 | 70.8 |
| tsvc_b1/s293 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.32x | 1+0 | 1 | 0 | 1 | 74.0 |
| tsvc_b1/s293 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.47x | 1+0 | 1 | 0 | 1 | 101.2 |
| tsvc_b1/s293 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.31x | 1+0 | 1 | 0 | 1 | 81.9 |
| tsvc_b1/s293 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.31x | 1+0 | 1 | 0 | 1 | 93.0 |
| tsvc_b1/s293 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.1 |
| tsvc_b1/s293 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.2 |
| tsvc_b1/s293 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.2 |
| tsvc_b1/s293 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 4.1 |
| tsvc_b1/s293 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.1 |
| tsvc_b1/s331 | default_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 10 | 997.4 |
| tsvc_b1/s331 | default_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 9 | 960.2 |
| tsvc_b1/s331 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.20x | 1+0 | 1 | 1 | 8 | 1133.6 |
| tsvc_b1/s331 | default_v3 | claude-haiku-4-5-20251001 | 4 | SCAFFOLD_MODIFIED | 40.87x | 1+0 | 1 | 1 | 5 | 538.1 |
| tsvc_b1/s331 | default_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 9 | 915.1 |
| tsvc_b1/s331 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.4 |
| tsvc_b1/s331 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 27.5 |
| tsvc_b1/s331 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.3 |
| tsvc_b1/s331 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 27.4 |
| tsvc_b1/s331 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.4 |
| tsvc_b1/s341 | default_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.07x | 3+0 | 1 | 0 | 10 | 1160.9 |
| tsvc_b1/s341 | default_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 9 | 972.2 |
| tsvc_b1/s341 | default_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 0 | 9 | 1020.4 |
| tsvc_b1/s341 | default_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 9 | 984.3 |
| tsvc_b1/s341 | default_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 9 | 1058.7 |
| tsvc_b1/s341 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_b1/s341 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.4 |
| tsvc_b1/s341 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.4 |
| tsvc_b1/s341 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.4 |
| tsvc_b1/s341 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.3 |
