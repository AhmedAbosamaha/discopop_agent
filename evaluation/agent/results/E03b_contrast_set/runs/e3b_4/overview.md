# Agent experiment run `e3b_4`

- status: finished (created 2026-10-10T13:15:44, finished 2026-10-10T14:21:41)
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
| default_v5 | claude-haiku-4-5-20251001 | 5 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 494 | 32 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 178 | 9 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 8 | 472.7 |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.20x | 1+0 | 1 | 0 | 4 | 209.0 |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.10x | 1+0 | 1 | 0 | 8 | 494.4 |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.38x | 1+0 | 1 | 0 | 6 | 555.6 |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.16x | 1+0 | 1 | 0 | 6 | 514.5 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.6 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.6 |
| tsvc_c4/s318 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 20.31x | 0+3 | 1 | 0 | 2 | 178.5 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 17.32x | 0+2 | 1 | 0 | 1 | 262.9 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 5.55x | 0+2 | 1 | 0 | 3 | 375.2 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 6.53x | 0+1 | 1 | 0 | 1 | 117.0 |
| tsvc_c4/s318 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 19.67x | 0+3 | 1 | 0 | 2 | 166.4 |
