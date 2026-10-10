# Agent experiment run `e3_r_4`

- status: finished (created 2026-10-09T17:32:05, finished 2026-10-09T23:51:54)
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
| default_v5 | claude-haiku-4-5-20251001 | 20 | 12 | 1 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 470 | 125 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 20 | 16 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 131 | 80 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s292 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.75x | 1+0 | 1 | 0 | 1 | 113.9 |
| tsvc_c2/s292 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.97x | 1+0 | 1 | 0 | 1 | 108.9 |
| tsvc_c2/s292 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.82x | 1+0 | 1 | 0 | 1 | 97.9 |
| tsvc_c2/s292 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.94x | 1+0 | 1 | 0 | 1 | 115.7 |
| tsvc_c2/s292 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.66x | 1+0 | 1 | 0 | 1 | 109.4 |
| tsvc_c2/s292 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 5.6 |
| tsvc_c2/s292 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.3 |
| tsvc_c2/s292 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.4 |
| tsvc_c2/s292 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.6 |
| tsvc_c2/s292 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 5.4 |
| tsvc_c2/s292 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.90x | 0+1 | 1 | 0 | 1 | 113.7 |
| tsvc_c2/s292 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.96x | 0+1 | 1 | 0 | 1 | 101.1 |
| tsvc_c2/s292 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.87x | 0+1 | 1 | 0 | 1 | 133.6 |
| tsvc_c2/s292 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.98x | 0+1 | 1 | 0 | 1 | 117.0 |
| tsvc_c2/s292 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.91x | 0+1 | 1 | 0 | 1 | 108.0 |
| tsvc_c2/s293 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.89x | 1+0 | 1 | 0 | 1 | 92.9 |
| tsvc_c2/s293 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.90x | 1+0 | 1 | 0 | 1 | 144.3 |
| tsvc_c2/s293 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.90x | 1+0 | 1 | 0 | 1 | 113.2 |
| tsvc_c2/s293 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.88x | 1+0 | 1 | 0 | 1 | 88.0 |
| tsvc_c2/s293 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.89x | 1+0 | 1 | 0 | 1 | 98.6 |
| tsvc_c2/s293 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.96x | 0+0 | 0 | 0 | 0 | 4.5 |
| tsvc_c2/s293 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 4.6 |
| tsvc_c2/s293 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/s293 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.5 |
| tsvc_c2/s293 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 0.98x | 0+0 | 0 | 0 | 0 | 4.5 |
| tsvc_c2/s293 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.01x | 0+1 | 1 | 0 | 1 | 124.0 |
| tsvc_c2/s293 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.30x | 0+1 | 1 | 0 | 1 | 121.9 |
| tsvc_c2/s293 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.10x | 0+1 | 1 | 0 | 1 | 89.4 |
| tsvc_c2/s293 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.90x | 0+1 | 1 | 0 | 1 | 119.3 |
| tsvc_c2/s293 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.81x | 0+1 | 1 | 0 | 1 | 124.0 |
| tsvc_c2/s341 | default_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 12 | 1128.9 |
| tsvc_c2/s341 | default_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1064.6 |
| tsvc_c2/s341 | default_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 12 | 1181.1 |
| tsvc_c2/s341 | default_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 943.8 |
| tsvc_c2/s341 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.19x | 1+0 | 1 | 0 | 11 | 899.0 |
| tsvc_c2/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c2/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c2/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c2/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c2/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c2/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 13 | 920.9 |
| tsvc_c2/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 12 | 849.2 |
| tsvc_c2/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1076.1 |
| tsvc_c2/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 13 | 803.7 |
| tsvc_c2/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.20x | 0+1 | 1 | 0 | 12 | 1200.2 |
| tsvc_c3/s331 | default_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 11 | 795.0 |
| tsvc_c3/s331 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.22x | 1+0 | 1 | 0 | 11 | 950.2 |
| tsvc_c3/s331 | default_v5 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.94x | 1+0 | 1 | 0 | 12 | 887.6 |
| tsvc_c3/s331 | default_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 11 | 959.9 |
| tsvc_c3/s331 | default_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1135.1 |
| tsvc_c3/s331 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c3/s331 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c3/s331 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c3/s331 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c3/s331 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c3/s331 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.67x | 0+2 | 1 | 0 | 1 | 127.6 |
| tsvc_c3/s331 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.42x | 0+1 | 1 | 0 | 1 | 146.6 |
| tsvc_c3/s331 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.82x | 0+2 | 1 | 0 | 1 | 159.2 |
| tsvc_c3/s331 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.83x | 0+3 | 1 | 0 | 4 | 221.5 |
| tsvc_c3/s331 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 5.02x | 0+3 | 1 | 0 | 1 | 168.7 |
