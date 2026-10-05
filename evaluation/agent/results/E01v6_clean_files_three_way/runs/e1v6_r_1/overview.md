# Agent experiment run `e1v6_r_1`

- status: finished (created 2026-10-05T00:51:31, finished 2026-10-05T03:46:08)
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
| default_v4 | claude-haiku-4-5-20251001 | 25 | 23 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 245 | 49 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s112 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.40x | 2+0 | 1 | 0 | 5 | 664.3 |
| tsvc_c2/s112 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.45x | 2+0 | 1 | 0 | 2 | 325.7 |
| tsvc_c2/s112 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.35x | 2+0 | 1 | 0 | 5 | 636.6 |
| tsvc_c2/s112 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.34x | 2+0 | 1 | 0 | 3 | 424.7 |
| tsvc_c2/s112 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.41x | 2+0 | 1 | 0 | 1 | 248.8 |
| tsvc_c2/s112 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.05x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s112 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.05x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s112 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.06x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s112 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s112 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.05x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s121 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.41x | 2+0 | 1 | 0 | 3 | 427.1 |
| tsvc_c2/s121 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.39x | 2+0 | 1 | 0 | 2 | 198.0 |
| tsvc_c2/s121 | default_v4 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.09x | 2+0 | 1 | 0 | 2 | 222.5 |
| tsvc_c2/s121 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.46x | 2+0 | 1 | 0 | 2 | 179.2 |
| tsvc_c2/s121 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.33x | 2+0 | 1 | 0 | 2 | 168.0 |
| tsvc_c2/s121 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.07x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_c2/s121 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s121 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s121 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s121 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s1213 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.90x | 2+0 | 1 | 0 | 2 | 429.5 |
| tsvc_c2/s1213 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.68x | 2+0 | 1 | 0 | 1 | 261.7 |
| tsvc_c2/s1213 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.18x | 2+0 | 1 | 0 | 2 | 341.2 |
| tsvc_c2/s1213 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.47x | 2+0 | 1 | 0 | 1 | 244.8 |
| tsvc_c2/s1213 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.54x | 2+0 | 1 | 0 | 2 | 240.3 |
| tsvc_c2/s1213 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc_c2/s1213 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 0.97x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc_c2/s1213 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc_c2/s1213 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc_c2/s1213 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc_c2/s127 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.97x | 1+0 | 1 | 0 | 1 | 118.5 |
| tsvc_c2/s127 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.63x | 1+0 | 1 | 0 | 1 | 105.7 |
| tsvc_c2/s127 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.74x | 1+0 | 1 | 0 | 1 | 107.8 |
| tsvc_c2/s127 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.42x | 1+0 | 1 | 0 | 1 | 108.8 |
| tsvc_c2/s127 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.93x | 1+0 | 1 | 0 | 1 | 114.9 |
| tsvc_c2/s127 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.8 |
| tsvc_c2/s127 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.8 |
| tsvc_c2/s127 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.93x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c2/s127 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.08x | 0+0 | 0 | 0 | 0 | 5.9 |
| tsvc_c2/s127 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.9 |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.98x | 3+0 | 1 | 0 | 3 | 426.8 |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.11x | 1+0 | 1 | 0 | 1 | 299.7 |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 1 | 182.9 |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.94x | 3+0 | 1 | 0 | 3 | 254.6 |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.15x | 1+0 | 1 | 0 | 1 | 190.7 |
| tsvc_c2/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.6 |
| tsvc_c2/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.7 |
| tsvc_c2/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.7 |
| tsvc_c2/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.7 |
| tsvc_c2/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.7 |
