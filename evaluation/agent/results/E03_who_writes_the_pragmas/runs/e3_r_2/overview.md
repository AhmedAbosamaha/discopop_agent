# Agent experiment run `e3_r_2`

- status: finished (created 2026-10-09T17:31:04, finished 2026-10-10T01:43:00)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `8297abb28e0049561c6bc977e67a8780fc9f6768` (uncommitted diff sha256 `None`)
- harness: `8297abb28e0049561c6bc977e67a8780fc9f6768` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v5 | claude-haiku-4-5-20251001 | 25 | 20 | 3 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 371 | 107 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 25 | 21 | 1 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 348 | 90 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s212 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.63x | 3+0 | 1 | 0 | 2 | 333.0 |
| tsvc_c2/s212 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.29x | 2+0 | 1 | 0 | 3 | 631.0 |
| tsvc_c2/s212 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.37x | 3+0 | 1 | 0 | 2 | 261.4 |
| tsvc_c2/s212 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.72x | 3+0 | 1 | 0 | 2 | 274.4 |
| tsvc_c2/s212 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.38x | 1+0 | 1 | 0 | 3 | 442.1 |
| tsvc_c2/s212 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.9 |
| tsvc_c2/s212 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc_c2/s212 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.5 |
| tsvc_c2/s212 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.1 |
| tsvc_c2/s212 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.2 |
| tsvc_c2/s212 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.28x | 0+3 | 1 | 0 | 4 | 464.1 |
| tsvc_c2/s212 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.29x | 1+1 | 1 | 0 | 6 | 637.2 |
| tsvc_c2/s212 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.13x | 0+2 | 1 | 0 | 2 | 254.0 |
| tsvc_c2/s212 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.32x | 0+2 | 1 | 0 | 3 | 358.3 |
| tsvc_c2/s212 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.19x | 0+5 | 1 | 0 | 3 | 402.9 |
| tsvc_c2/s243 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.30x | 1+0 | 1 | 0 | 2 | 211.5 |
| tsvc_c2/s243 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.37x | 1+0 | 1 | 0 | 3 | 282.0 |
| tsvc_c2/s243 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.27x | 1+0 | 1 | 0 | 1 | 169.2 |
| tsvc_c2/s243 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.44x | 2+0 | 1 | 0 | 2 | 304.0 |
| tsvc_c2/s243 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.77x | 3+0 | 1 | 0 | 3 | 351.5 |
| tsvc_c2/s243 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.90x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/s243 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/s243 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.06x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s243 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.5 |
| tsvc_c2/s243 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/s243 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.33x | 0+1 | 1 | 0 | 2 | 157.2 |
| tsvc_c2/s243 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.29x | 0+1 | 1 | 0 | 4 | 291.3 |
| tsvc_c2/s243 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.18x | 1+1 | 1 | 0 | 2 | 210.7 |
| tsvc_c2/s243 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.30x | 0+1 | 1 | 0 | 4 | 255.1 |
| tsvc_c2/s243 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.02x | 0+2 | 1 | 0 | 3 | 244.3 |
| tsvc_c2/s244 | default_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1156.8 |
| tsvc_c2/s244 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.82x | 2+0 | 1 | 0 | 10 | 1315.6 |
| tsvc_c2/s244 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.87x | 2+0 | 1 | 0 | 9 | 1284.5 |
| tsvc_c2/s244 | default_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 13 | 1332.1 |
| tsvc_c2/s244 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.70x | 2+0 | 1 | 0 | 4 | 611.1 |
| tsvc_c2/s244 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.3 |
| tsvc_c2/s244 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.2 |
| tsvc_c2/s244 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.1 |
| tsvc_c2/s244 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.1 |
| tsvc_c2/s244 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.1 |
| tsvc_c2/s244 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.59x | 1+1 | 1 | 0 | 4 | 528.1 |
| tsvc_c2/s244 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 5.14x | 0+1 | 1 | 0 | 3 | 359.3 |
| tsvc_c2/s244 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.75x | 0+1 | 1 | 0 | 12 | 1640.1 |
| tsvc_c2/s244 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 5.42x | 0+1 | 1 | 0 | 1 | 260.7 |
| tsvc_c2/s244 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 14 | 1683.9 |
| tsvc_c2/s252 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.41x | 1+0 | 1 | 0 | 1 | 147.3 |
| tsvc_c2/s252 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.62x | 1+0 | 1 | 0 | 2 | 370.8 |
| tsvc_c2/s252 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.66x | 1+0 | 1 | 0 | 3 | 327.7 |
| tsvc_c2/s252 | default_v5 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.97x | 1+0 | 1 | 0 | 3 | 369.8 |
| tsvc_c2/s252 | default_v5 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.97x | 1+0 | 1 | 0 | 2 | 205.6 |
| tsvc_c2/s252 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.6 |
| tsvc_c2/s252 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c2/s252 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.6 |
| tsvc_c2/s252 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.8 |
| tsvc_c2/s252 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.8 |
| tsvc_c2/s252 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.66x | 0+1 | 1 | 0 | 1 | 126.4 |
| tsvc_c2/s252 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.62x | 0+1 | 1 | 0 | 1 | 118.1 |
| tsvc_c2/s252 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.59x | 0+1 | 1 | 0 | 1 | 120.1 |
| tsvc_c2/s252 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.64x | 0+1 | 1 | 0 | 1 | 157.3 |
| tsvc_c2/s252 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.58x | 0+1 | 1 | 0 | 1 | 122.2 |
| tsvc_c3/s241 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.21x | 3+0 | 1 | 0 | 6 | 693.8 |
| tsvc_c3/s241 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.47x | 3+0 | 1 | 0 | 7 | 767.2 |
| tsvc_c3/s241 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.42x | 3+0 | 1 | 0 | 3 | 566.1 |
| tsvc_c3/s241 | default_v5 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.96x | 1+0 | 1 | 0 | 3 | 575.3 |
| tsvc_c3/s241 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.11x | 3+0 | 1 | 0 | 6 | 950.9 |
| tsvc_c3/s241 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.93x | 0+0 | 0 | 0 | 0 | 13.2 |
| tsvc_c3/s241 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.9 |
| tsvc_c3/s241 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.2 |
| tsvc_c3/s241 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 14.2 |
| tsvc_c3/s241 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.5 |
| tsvc_c3/s241 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 2 | 450.0 |
| tsvc_c3/s241 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.87x | 0+3 | 1 | 0 | 8 | 954.3 |
| tsvc_c3/s241 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 530.0 |
| tsvc_c3/s241 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.30x | 0+3 | 1 | 0 | 2 | 348.3 |
| tsvc_c3/s241 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.44x | 0+3 | 1 | 0 | 3 | 376.1 |
