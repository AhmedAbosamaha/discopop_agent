# Agent experiment run `e3b_3`

- status: finished (created 2026-10-10T13:15:14, finished 2026-10-10T16:33:13)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `cb921121f56cdae31ede62d3a6a3aaf64ef1ebfc` (uncommitted diff sha256 `None`)
- harness: `cb921121f56cdae31ede62d3a6a3aaf64ef1ebfc` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v5 | claude-haiku-4-5-20251001 | 10 | 7 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 648 | 53 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 10 | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 33 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 225 | 17 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s311 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.55x | 1+0 | 0 | 1 | 1 | 228.2 |
| tsvc_c4/s311 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 8.06x | 1+0 | 0 | 1 | 6 | 816.0 |
| tsvc_c4/s311 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 8.52x | 1+0 | 0 | 1 | 2 | 366.0 |
| tsvc_c4/s311 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 8.75x | 1+0 | 1 | 1 | 1 | 233.0 |
| tsvc_c4/s311 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 8.19x | 2+0 | 1 | 1 | 6 | 1053.9 |
| tsvc_c4/s311 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.54x | 1+0 | 0 | 1 | 0 | 59.4 |
| tsvc_c4/s311 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 8.45x | 1+0 | 0 | 1 | 0 | 59.5 |
| tsvc_c4/s311 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 8.35x | 1+0 | 0 | 1 | 0 | 58.9 |
| tsvc_c4/s311 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 8.70x | 1+0 | 0 | 1 | 0 | 59.4 |
| tsvc_c4/s311 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 8.76x | 1+0 | 0 | 1 | 0 | 63.4 |
| tsvc_c4/s311 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.54x | 0+1 | 1 | 1 | 2 | 310.1 |
| tsvc_c4/s311 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 5.50x | 0+1 | 1 | 1 | 1 | 197.2 |
| tsvc_c4/s311 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 8.60x | 1+0 | 0 | 1 | 1 | 240.8 |
| tsvc_c4/s311 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 8.74x | 0+1 | 1 | 1 | 2 | 294.8 |
| tsvc_c4/s311 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 8.47x | 1+0 | 1 | 1 | 2 | 425.4 |
| tsvc_c4/s315 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.73x | 1+0 | 1 | 0 | 3 | 373.9 |
| tsvc_c4/s315 | default_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 839.5 |
| tsvc_c4/s315 | default_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1017.2 |
| tsvc_c4/s315 | default_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 9 | 785.5 |
| tsvc_c4/s315 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 11.57x | 1+0 | 1 | 0 | 5 | 510.0 |
| tsvc_c4/s315 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.2 |
| tsvc_c4/s315 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.1 |
| tsvc_c4/s315 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.1 |
| tsvc_c4/s315 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc_c4/s315 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.2 |
| tsvc_c4/s315 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 11.05x | 0+3 | 1 | 0 | 1 | 136.2 |
| tsvc_c4/s315 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 11.26x | 0+1 | 1 | 0 | 1 | 147.7 |
| tsvc_c4/s315 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 10.62x | 0+3 | 1 | 0 | 3 | 255.4 |
| tsvc_c4/s315 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.68x | 0+1 | 1 | 0 | 2 | 168.8 |
| tsvc_c4/s315 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 13.53x | 0+1 | 1 | 0 | 2 | 209.7 |
