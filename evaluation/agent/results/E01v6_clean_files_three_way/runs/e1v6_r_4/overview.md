# Agent experiment run `e1v6_r_4`

- status: finished (created 2026-10-05T00:51:57, finished 2026-10-05T03:46:58)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `70cb05ff3d1ecc75158877a042809fcfdf7d5da8` (uncommitted diff sha256 `None`)
- harness: `70cb05ff3d1ecc75158877a042809fcfdf7d5da8` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v4 | claude-haiku-4-5-20251001 | 20 | 15 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 126 | 71 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s292 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.73x | 1+0 | 1 | 0 | 1 | 112.0 |
| tsvc_c2/s292 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.73x | 1+0 | 1 | 0 | 1 | 104.1 |
| tsvc_c2/s292 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.32x | 1+0 | 1 | 0 | 1 | 92.3 |
| tsvc_c2/s292 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.93x | 1+0 | 1 | 0 | 1 | 115.3 |
| tsvc_c2/s292 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.96x | 1+0 | 1 | 0 | 1 | 96.3 |
| tsvc_c2/s292 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s292 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.5 |
| tsvc_c2/s292 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.97x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s292 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_c2/s292 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.4 |
| tsvc_c2/s293 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.91x | 1+0 | 1 | 0 | 1 | 89.0 |
| tsvc_c2/s293 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.97x | 1+0 | 1 | 0 | 1 | 87.8 |
| tsvc_c2/s293 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.18x | 1+0 | 1 | 0 | 1 | 106.6 |
| tsvc_c2/s293 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.00x | 1+0 | 1 | 0 | 1 | 88.2 |
| tsvc_c2/s293 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.02x | 1+0 | 1 | 0 | 1 | 91.6 |
| tsvc_c2/s293 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.07x | 0+0 | 0 | 0 | 0 | 4.6 |
| tsvc_c2/s293 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.5 |
| tsvc_c2/s293 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/s293 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.4 |
| tsvc_c2/s293 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.4 |
| tsvc_c2/s331 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 6.53x | 1+0 | 1 | 1 | 3 | 304.2 |
| tsvc_c2/s331 | default_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 276.8 |
| tsvc_c2/s331 | default_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 1 | 7 | 761.6 |
| tsvc_c2/s331 | default_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 365.2 |
| tsvc_c2/s331 | default_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 7 | 579.3 |
| tsvc_c2/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 28.4 |
| tsvc_c2/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 28.5 |
| tsvc_c2/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 28.8 |
| tsvc_c2/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 28.4 |
| tsvc_c2/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 29.6 |
| tsvc_c2/s341 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.01x | 1+0 | 1 | 0 | 12 | 1188.5 |
| tsvc_c2/s341 | default_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 0.93x | 0+0 | 0 | 0 | 12 | 1043.3 |
| tsvc_c2/s341 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.15x | 1+0 | 1 | 0 | 3 | 312.5 |
| tsvc_c2/s341 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.09x | 1+0 | 1 | 0 | 11 | 1010.6 |
| tsvc_c2/s341 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.80x | 1+0 | 1 | 0 | 2 | 136.9 |
| tsvc_c2/s341 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.11x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c2/s341 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c2/s341 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.95x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s341 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s341 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.7 |
