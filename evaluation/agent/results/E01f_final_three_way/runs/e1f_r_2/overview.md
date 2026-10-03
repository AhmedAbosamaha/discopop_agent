# Agent experiment run `e1f_r_2`

- status: finished (created 2026-10-02T20:44:03, finished 2026-10-03T01:39:21)
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
| default_v3 | claude-haiku-4-5-20251001 | 25 | 14 | 10 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 391 | 72 |
| discopop_gate_v3 | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s212 | default_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.01x | 1+0 | 1 | 0 | 2 | 383.1 |
| tsvc_b1/s212 | default_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.95x | 2+0 | 1 | 0 | 1 | 267.4 |
| tsvc_b1/s212 | default_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.00x | 2+0 | 1 | 0 | 1 | 197.1 |
| tsvc_b1/s212 | default_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.94x | 2+0 | 1 | 0 | 3 | 383.4 |
| tsvc_b1/s212 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.91x | 1+0 | 1 | 0 | 2 | 388.0 |
| tsvc_b1/s212 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc_b1/s212 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc_b1/s212 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 0.96x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc_b1/s212 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc_b1/s212 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc_b1/s241 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.39x | 3+0 | 1 | 0 | 2 | 391.3 |
| tsvc_b1/s241 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.34x | 3+0 | 1 | 0 | 8 | 1546.8 |
| tsvc_b1/s241 | default_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1649.2 |
| tsvc_b1/s241 | default_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.04x | 3+0 | 1 | 0 | 5 | 1101.8 |
| tsvc_b1/s241 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.56x | 3+0 | 1 | 0 | 2 | 604.3 |
| tsvc_b1/s241 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.14x | 0+0 | 0 | 0 | 0 | 12.8 |
| tsvc_b1/s241 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 12.9 |
| tsvc_b1/s241 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 0.87x | 0+0 | 0 | 0 | 0 | 12.9 |
| tsvc_b1/s241 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.1 |
| tsvc_b1/s241 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.2 |
| tsvc_b1/s243 | default_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 1 | 333.2 |
| tsvc_b1/s243 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.48x | 3+0 | 1 | 0 | 3 | 629.8 |
| tsvc_b1/s243 | default_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 1 | 373.8 |
| tsvc_b1/s243 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.62x | 3+0 | 1 | 0 | 5 | 883.2 |
| tsvc_b1/s243 | default_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.02x | 1+0 | 1 | 0 | 2 | 588.6 |
| tsvc_b1/s243 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 13.3 |
| tsvc_b1/s243 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 13.5 |
| tsvc_b1/s243 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.5 |
| tsvc_b1/s243 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 14.3 |
| tsvc_b1/s243 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 14.7 |
| tsvc_b1/s244 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.06x | 1+0 | 1 | 0 | 3 | 421.1 |
| tsvc_b1/s244 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.82x | 2+0 | 1 | 0 | 8 | 1873.6 |
| tsvc_b1/s244 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.17x | 1+0 | 1 | 0 | 2 | 457.6 |
| tsvc_b1/s244 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.44x | 1+0 | 1 | 0 | 2 | 618.8 |
| tsvc_b1/s244 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.28x | 2+0 | 1 | 0 | 3 | 474.9 |
| tsvc_b1/s244 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.7 |
| tsvc_b1/s244 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.7 |
| tsvc_b1/s244 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.7 |
| tsvc_b1/s244 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.8 |
| tsvc_b1/s244 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.8 |
| tsvc_b1/s252 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.62x | 1+0 | 1 | 0 | 1 | 128.9 |
| tsvc_b1/s252 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.60x | 1+0 | 1 | 0 | 1 | 135.7 |
| tsvc_b1/s252 | default_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.98x | 1+0 | 1 | 0 | 2 | 345.1 |
| tsvc_b1/s252 | default_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.96x | 1+0 | 1 | 0 | 2 | 293.6 |
| tsvc_b1/s252 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.62x | 1+0 | 1 | 0 | 1 | 115.2 |
| tsvc_b1/s252 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.4 |
| tsvc_b1/s252 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_b1/s252 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_b1/s252 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_b1/s252 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.2 |
