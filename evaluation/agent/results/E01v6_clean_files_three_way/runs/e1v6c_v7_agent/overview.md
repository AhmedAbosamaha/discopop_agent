# Agent experiment run `e1v6c_v7_agent`

- status: finished (created 2026-10-07T19:36:13, finished 2026-10-07T21:19:56)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `eeee11e74a5e2732ab9e15531d06a43126c6319b` (uncommitted diff sha256 `None`)
- harness: `eeee11e74a5e2732ab9e15531d06a43126c6319b` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v4 | claude-haiku-4-5-20251001 | 5 | 0 | 1 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 997 | 51 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 28 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 11 | 996.7 |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.08x | 1+0 | 1 | 1 | 9 | 911.2 |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 10 | 1274.2 |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 11 | 1138.8 |
| tsvc_c3/s331 | default_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 10 | 929.7 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 27.7 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.7 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.6 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 27.6 |
| tsvc_c3/s331 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 27.8 |
