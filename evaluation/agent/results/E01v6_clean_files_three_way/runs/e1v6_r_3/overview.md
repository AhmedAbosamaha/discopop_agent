# Agent experiment run `e1v6_r_3`

- status: finished (created 2026-10-05T00:51:48, finished 2026-10-05T02:46:33)
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
| default_v4 | claude-haiku-4-5-20251001 | 20 | 16 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 106 | 32 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s254 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.32x | 1+0 | 1 | 0 | 1 | 106.3 |
| tsvc_c2/s254 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.36x | 1+0 | 1 | 0 | 1 | 104.6 |
| tsvc_c2/s254 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.67x | 1+0 | 1 | 0 | 1 | 103.1 |
| tsvc_c2/s254 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.45x | 1+0 | 1 | 0 | 1 | 95.9 |
| tsvc_c2/s254 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.32x | 1+0 | 1 | 0 | 1 | 103.0 |
| tsvc_c2/s254 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.07x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s254 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s254 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_c2/s254 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c2/s254 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s255 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.49x | 1+0 | 1 | 0 | 1 | 109.4 |
| tsvc_c2/s255 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.60x | 1+0 | 1 | 0 | 1 | 105.1 |
| tsvc_c2/s255 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.46x | 1+0 | 1 | 0 | 1 | 107.9 |
| tsvc_c2/s255 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.58x | 1+0 | 1 | 0 | 1 | 106.8 |
| tsvc_c2/s255 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.58x | 1+0 | 1 | 0 | 1 | 103.0 |
| tsvc_c2/s255 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s255 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s255 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s255 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s255 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 1 | 254.9 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 2 | 281.7 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.10x | 1+0 | 1 | 0 | 7 | 883.3 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.16x | 1+0 | 1 | 0 | 5 | 567.0 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 2 | 378.4 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.7 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc_c2/s291 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.78x | 1+0 | 1 | 0 | 1 | 104.4 |
| tsvc_c2/s291 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.70x | 1+0 | 1 | 0 | 1 | 91.6 |
| tsvc_c2/s291 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.46x | 1+0 | 1 | 0 | 1 | 92.2 |
| tsvc_c2/s291 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.54x | 1+0 | 1 | 0 | 1 | 96.0 |
| tsvc_c2/s291 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.50x | 1+0 | 1 | 0 | 1 | 107.0 |
| tsvc_c2/s291 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s291 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s291 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.5 |
| tsvc_c2/s291 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s291 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.0 |
