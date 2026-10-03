# Agent experiment run `e1f_r_1`

- status: finished (created 2026-10-02T20:43:56, finished 2026-10-02T23:34:25)
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
| default_v3 | claude-haiku-4-5-20251001 | 25 | 24 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 202 | 40 |
| discopop_gate_v3 | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s112 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.44x | 2+0 | 1 | 0 | 2 | 210.8 |
| tsvc_b1/s112 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.33x | 2+0 | 1 | 0 | 1 | 202.3 |
| tsvc_b1/s112 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.41x | 2+0 | 1 | 0 | 5 | 753.1 |
| tsvc_b1/s112 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.42x | 2+0 | 1 | 0 | 1 | 179.7 |
| tsvc_b1/s112 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.34x | 2+0 | 1 | 0 | 4 | 411.5 |
| tsvc_b1/s112 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_b1/s112 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_b1/s112 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_b1/s112 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_b1/s112 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_b1/s121 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.38x | 2+0 | 1 | 0 | 1 | 153.6 |
| tsvc_b1/s121 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.52x | 2+0 | 1 | 0 | 4 | 516.2 |
| tsvc_b1/s121 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.39x | 2+0 | 1 | 0 | 1 | 183.6 |
| tsvc_b1/s121 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.43x | 2+0 | 1 | 0 | 1 | 197.2 |
| tsvc_b1/s121 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.35x | 2+0 | 1 | 0 | 2 | 320.5 |
| tsvc_b1/s121 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_b1/s121 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_b1/s121 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_b1/s121 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_b1/s121 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_b1/s1213 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.51x | 2+0 | 1 | 0 | 1 | 267.3 |
| tsvc_b1/s1213 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.61x | 2+0 | 1 | 0 | 2 | 363.2 |
| tsvc_b1/s1213 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.22x | 1+0 | 1 | 0 | 2 | 620.0 |
| tsvc_b1/s1213 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.72x | 2+0 | 1 | 0 | 1 | 198.8 |
| tsvc_b1/s1213 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.61x | 2+0 | 1 | 0 | 1 | 307.5 |
| tsvc_b1/s1213 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.1 |
| tsvc_b1/s1213 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.2 |
| tsvc_b1/s1213 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc_b1/s1213 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.1 |
| tsvc_b1/s1213 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc_b1/s127 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.75x | 1+0 | 1 | 0 | 1 | 98.4 |
| tsvc_b1/s127 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.85x | 1+0 | 1 | 0 | 1 | 97.7 |
| tsvc_b1/s127 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.64x | 1+0 | 1 | 0 | 1 | 96.6 |
| tsvc_b1/s127 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.68x | 1+0 | 1 | 0 | 1 | 88.5 |
| tsvc_b1/s127 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.85x | 1+0 | 1 | 0 | 1 | 94.8 |
| tsvc_b1/s127 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.4 |
| tsvc_b1/s127 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_b1/s127 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.5 |
| tsvc_b1/s127 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.5 |
| tsvc_b1/s127 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.4 |
| tsvc_b1/s211 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.15x | 1+0 | 1 | 0 | 1 | 261.6 |
| tsvc_b1/s211 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.01x | 3+0 | 1 | 0 | 1 | 218.1 |
| tsvc_b1/s211 | default_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 1 | 162.8 |
| tsvc_b1/s211 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.10x | 1+0 | 1 | 0 | 2 | 504.5 |
| tsvc_b1/s211 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.16x | 1+0 | 1 | 0 | 1 | 167.8 |
| tsvc_b1/s211 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.5 |
| tsvc_b1/s211 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc_b1/s211 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.5 |
| tsvc_b1/s211 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc_b1/s211 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.4 |
