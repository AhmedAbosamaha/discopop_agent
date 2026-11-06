# Agent experiment run `e11_r_ep`

- status: finished (created 2026-11-06T05:07:58, finished 2026-11-06T06:21:41)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `1cddb8907bd3e7e8fd4184355fe57aad327f7081` (uncommitted diff sha256 `None`)
- harness: `1cddb8907bd3e7e8fd4184355fe57aad327f7081` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 113 | 0 |
| llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 660 | 22 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 112.9 |
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 113.2 |
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 114.3 |
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 112.7 |
| npbc_c1/ep | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | parallel-not-faster | 1.00x | 5+0 | 0 | 5 | 0 | 113.3 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 6.51x | 0+4 | 1 | 5 | 4 | 660.3 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 1.36x | 0+4 | 1 | 5 | 6 | 981.8 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 6.84x | 0+4 | 1 | 5 | 4 | 843.0 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 7.80x | 0+3 | 1 | 5 | 4 | 574.9 |
| npbc_c1/ep | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 7.80x | 0+3 | 1 | 5 | 4 | 609.1 |
