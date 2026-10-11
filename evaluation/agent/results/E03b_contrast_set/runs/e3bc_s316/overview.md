# Agent experiment run `e3bc_s316`

- status: finished (created 2026-10-10T22:46:10, finished 2026-10-11T00:08:24)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `cc66dff23edf9e25b380ac397db12ed867034016` (uncommitted diff sha256 `None`)
- harness: `cc66dff23edf9e25b380ac397db12ed867034016` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v5 | claude-haiku-4-5-20251001 | 5 | 4 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 356 | 21 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 151 | 8 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.26x | 1+0 | 1 | 0 | 4 | 471.5 |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.28x | 1+0 | 1 | 0 | 1 | 213.5 |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 9.66x | 1+0 | 1 | 0 | 4 | 356.3 |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1023.9 |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.26x | 1+0 | 1 | 0 | 1 | 235.0 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.7 |
| tsvc_c4/s316 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.6 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 9.00x | 0+1 | 1 | 0 | 2 | 319.9 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 8.99x | 0+1 | 1 | 0 | 3 | 450.9 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 9.04x | 0+1 | 1 | 0 | 1 | 117.9 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 9.03x | 0+1 | 1 | 0 | 1 | 139.3 |
| tsvc_c4/s316 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 8.94x | 0+1 | 1 | 0 | 1 | 151.2 |
