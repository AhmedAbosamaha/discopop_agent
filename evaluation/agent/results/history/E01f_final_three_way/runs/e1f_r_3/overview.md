# Agent experiment run `e1f_r_3`

- status: finished (created 2026-10-02T20:44:11, finished 2026-10-02T22:22:44)
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
| default_v3 | claude-haiku-4-5-20251001 | 20 | 15 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 93 | 30 |
| discopop_gate_v3 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s254 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.75x | 1+0 | 1 | 0 | 1 | 90.7 |
| tsvc_b1/s254 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.46x | 1+0 | 1 | 0 | 1 | 97.4 |
| tsvc_b1/s254 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.40x | 1+0 | 1 | 0 | 1 | 95.6 |
| tsvc_b1/s254 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.57x | 1+0 | 1 | 0 | 1 | 83.5 |
| tsvc_b1/s254 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.46x | 1+0 | 1 | 0 | 1 | 84.7 |
| tsvc_b1/s254 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_b1/s254 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_b1/s254 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_b1/s254 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_b1/s254 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_b1/s255 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.45x | 1+0 | 1 | 0 | 1 | 80.8 |
| tsvc_b1/s255 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.71x | 1+0 | 1 | 0 | 2 | 104.1 |
| tsvc_b1/s255 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.88x | 1+0 | 1 | 0 | 1 | 91.2 |
| tsvc_b1/s255 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.54x | 1+0 | 1 | 0 | 1 | 94.9 |
| tsvc_b1/s255 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.32x | 1+0 | 1 | 0 | 1 | 102.1 |
| tsvc_b1/s255 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_b1/s255 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_b1/s255 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.6 |
| tsvc_b1/s255 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.6 |
| tsvc_b1/s255 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 4.6 |
| tsvc_b1/s281 | default_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.07x | 1+0 | 1 | 0 | 2 | 189.8 |
| tsvc_b1/s281 | default_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 3 | 276.8 |
| tsvc_b1/s281 | default_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 3 | 304.2 |
| tsvc_b1/s281 | default_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 3 | 460.7 |
| tsvc_b1/s281 | default_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 3 | 381.1 |
| tsvc_b1/s281 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.2 |
| tsvc_b1/s281 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc_b1/s281 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 0.96x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc_b1/s281 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.2 |
| tsvc_b1/s281 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc_b1/s291 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.47x | 1+0 | 1 | 0 | 1 | 80.9 |
| tsvc_b1/s291 | default_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.42x | 1+0 | 1 | 0 | 1 | 77.5 |
| tsvc_b1/s291 | default_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.44x | 1+0 | 1 | 0 | 1 | 83.4 |
| tsvc_b1/s291 | default_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.39x | 1+0 | 1 | 0 | 1 | 85.6 |
| tsvc_b1/s291 | default_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.41x | 1+0 | 1 | 0 | 1 | 91.2 |
| tsvc_b1/s291 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_b1/s291 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.06x | 0+0 | 0 | 0 | 0 | 4.5 |
| tsvc_b1/s291 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_b1/s291 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 0.98x | 0+0 | 0 | 0 | 0 | 4.6 |
| tsvc_b1/s291 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.08x | 0+0 | 0 | 0 | 0 | 4.8 |
