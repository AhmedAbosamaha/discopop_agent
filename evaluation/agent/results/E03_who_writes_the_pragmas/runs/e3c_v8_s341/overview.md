# Agent experiment run `e3c_v8_s341`

- status: finished (created 2026-10-10T14:24:21, finished 2026-10-10T17:42:48)
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
| default_v5 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 892 | 59 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 923 | 63 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s341 | default_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.08x | 0+0 | 0 | 0 | 11 | 752.0 |
| tsvc_c4/s341 | default_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 892.3 |
| tsvc_c4/s341 | default_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 786.9 |
| tsvc_c4/s341 | default_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 12 | 1844.2 |
| tsvc_c4/s341 | default_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1370.3 |
| tsvc_c4/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c4/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.08x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c4/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_c4/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_c4/s341 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc_c4/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.97x | 0+0 | 0 | 0 | 12 | 876.5 |
| tsvc_c4/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 14 | 917.8 |
| tsvc_c4/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 12 | 1014.2 |
| tsvc_c4/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 13 | 922.9 |
| tsvc_c4/s341 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 12 | 1175.0 |
