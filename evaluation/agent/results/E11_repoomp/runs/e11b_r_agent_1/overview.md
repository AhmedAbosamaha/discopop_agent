# Agent experiment run `e11b_r_agent_1`

- status: finished (created 2026-11-06T09:03:34, finished 2026-11-06T13:19:45)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `4077730ec8ad0a34af7f2967ed17be29ffe5ec5d` (uncommitted diff sha256 `None`)
- harness: `4077730ec8ad0a34af7f2967ed17be29ffe5ec5d` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate_v5 | claude-sonnet-4-5-20250929 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 20 | 18 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 408 | 62 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c2/k19 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c2/k19 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 3.6 |
| tsvc_c2/k19 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c2/k19 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.7 |
| tsvc_c2/k19 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 2.28x | 0+3 | 1 | 0 | 1 | 371.6 |
| tsvc_c2/k19 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 3.95x | 0+2 | 1 | 0 | 1 | 229.3 |
| tsvc_c2/k19 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 4.26x | 0+2 | 1 | 0 | 1 | 266.4 |
| tsvc_c2/k19 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 2.31x | 0+3 | 1 | 0 | 1 | 238.6 |
| tsvc_c2/k19 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 2.32x | 0+3 | 1 | 0 | 1 | 204.9 |
| tsvc_c2/k23 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.8 |
| tsvc_c2/k23 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 8.9 |
| tsvc_c2/k23 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.9 |
| tsvc_c2/k23 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 8.9 |
| tsvc_c2/k23 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.9 |
| tsvc_c2/k23 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 4.15x | 0+1 | 1 | 0 | 3 | 546.9 |
| tsvc_c2/k23 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 3.41x | 0+2 | 1 | 0 | 2 | 349.0 |
| tsvc_c2/k23 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 2.61x | 0+2 | 1 | 0 | 3 | 396.3 |
| tsvc_c2/k23 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 3.37x | 0+2 | 1 | 0 | 5 | 825.5 |
| tsvc_c2/k23 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 3.44x | 0+2 | 1 | 0 | 3 | 419.8 |
| tsvc_c2/k27 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/k27 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/k27 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/k27 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/k27 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/k27 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 2023.3 |
| tsvc_c2/k27 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 4.19x | 0+3 | 1 | 0 | 8 | 1732.1 |
| tsvc_c2/k27 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 2.80x | 0+4 | 1 | 0 | 2 | 437.4 |
| tsvc_c2/k27 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 9 | 2099.8 |
| tsvc_c2/k27 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 4.24x | 0+3 | 1 | 0 | 4 | 742.6 |
| tsvc_c2/k31 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.5 |
| tsvc_c2/k31 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.5 |
| tsvc_c2/k31 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.5 |
| tsvc_c2/k31 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.5 |
| tsvc_c2/k31 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.5 |
| tsvc_c2/k31 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 3.24x | 0+2 | 1 | 0 | 4 | 999.4 |
| tsvc_c2/k31 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 3.26x | 0+2 | 1 | 0 | 2 | 359.1 |
| tsvc_c2/k31 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 3.18x | 0+2 | 1 | 0 | 1 | 281.6 |
| tsvc_c2/k31 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 3.30x | 0+2 | 1 | 0 | 1 | 373.7 |
| tsvc_c2/k31 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 3.32x | 0+2 | 1 | 0 | 1 | 559.0 |
