# Agent experiment run `e3_r_3`

- status: finished (created 2026-10-09T17:31:35, finished 2026-10-09T20:44:55)
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
| default_v5 | claude-haiku-4-5-20251001 | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 110 | 33 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 119 | 26 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.45x | 1+0 | 1 | 0 | 1 | 94.1 |
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.27x | 1+0 | 1 | 0 | 1 | 92.2 |
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.40x | 1+0 | 1 | 0 | 1 | 110.0 |
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.40x | 1+0 | 1 | 0 | 1 | 119.9 |
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.45x | 1+0 | 1 | 0 | 1 | 101.4 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.17x | 0+1 | 1 | 0 | 1 | 127.2 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.65x | 0+1 | 1 | 0 | 1 | 109.8 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.66x | 0+1 | 1 | 0 | 2 | 114.3 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.38x | 0+1 | 1 | 0 | 1 | 118.4 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.23x | 0+1 | 1 | 0 | 1 | 148.4 |
| tsvc_c2/s255 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.45x | 1+0 | 1 | 0 | 1 | 119.8 |
| tsvc_c2/s255 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.72x | 1+0 | 1 | 0 | 1 | 109.9 |
| tsvc_c2/s255 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.42x | 1+0 | 1 | 0 | 1 | 109.7 |
| tsvc_c2/s255 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.64x | 1+0 | 1 | 0 | 4 | 299.6 |
| tsvc_c2/s255 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.48x | 1+0 | 1 | 0 | 1 | 115.8 |
| tsvc_c2/s255 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s255 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s255 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s255 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s255 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.2 |
| tsvc_c2/s255 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.46x | 0+1 | 1 | 0 | 1 | 115.0 |
| tsvc_c2/s255 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.75x | 0+1 | 1 | 0 | 1 | 106.4 |
| tsvc_c2/s255 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.68x | 0+1 | 1 | 0 | 1 | 117.1 |
| tsvc_c2/s255 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.65x | 0+1 | 1 | 0 | 1 | 143.5 |
| tsvc_c2/s255 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.38x | 0+1 | 1 | 0 | 1 | 148.6 |
| tsvc_c2/s281 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.25x | 2+0 | 1 | 0 | 1 | 389.3 |
| tsvc_c2/s281 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.27x | 2+0 | 1 | 0 | 4 | 579.6 |
| tsvc_c2/s281 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.29x | 2+0 | 1 | 0 | 4 | 691.8 |
| tsvc_c2/s281 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.97x | 2+0 | 1 | 0 | 3 | 307.4 |
| tsvc_c2/s281 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.27x | 2+0 | 1 | 0 | 3 | 303.5 |
| tsvc_c2/s281 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.7 |
| tsvc_c2/s281 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc_c2/s281 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.9 |
| tsvc_c2/s281 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc_c2/s281 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.7 |
| tsvc_c2/s281 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.78x | 0+2 | 1 | 0 | 1 | 269.9 |
| tsvc_c2/s281 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.78x | 0+2 | 1 | 0 | 4 | 320.6 |
| tsvc_c2/s281 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.66x | 0+3 | 1 | 0 | 2 | 385.9 |
| tsvc_c2/s281 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.55x | 0+1 | 1 | 0 | 1 | 369.7 |
| tsvc_c2/s281 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.06x | 0+2 | 1 | 0 | 1 | 214.2 |
| tsvc_c2/s291 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.40x | 1+0 | 1 | 0 | 1 | 98.7 |
| tsvc_c2/s291 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.54x | 1+0 | 1 | 0 | 1 | 90.5 |
| tsvc_c2/s291 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.49x | 1+0 | 1 | 0 | 1 | 98.7 |
| tsvc_c2/s291 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.56x | 1+0 | 1 | 0 | 1 | 102.9 |
| tsvc_c2/s291 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.42x | 1+0 | 1 | 0 | 1 | 109.2 |
| tsvc_c2/s291 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.1 |
| tsvc_c2/s291 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s291 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_c2/s291 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s291 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.0 |
| tsvc_c2/s291 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.49x | 0+1 | 1 | 0 | 1 | 105.0 |
| tsvc_c2/s291 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.46x | 0+1 | 1 | 0 | 1 | 117.6 |
| tsvc_c2/s291 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.52x | 0+1 | 1 | 0 | 1 | 120.0 |
| tsvc_c2/s291 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.42x | 0+1 | 1 | 0 | 2 | 106.6 |
| tsvc_c2/s291 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.48x | 0+1 | 1 | 0 | 1 | 93.8 |
