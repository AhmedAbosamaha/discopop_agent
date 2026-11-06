# Agent experiment run `e11_r_cg`

- status: finished (created 2026-11-06T05:08:16, finished 2026-11-06T07:55:50)
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
| discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 315 | 0 |
| llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1395 | 35 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npbc_c1/cg | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 9.13x | 10+0 | 0 | 20 | 0 | 318.7 |
| npbc_c1/cg | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 10.14x | 14+0 | 0 | 20 | 0 | 314.7 |
| npbc_c1/cg | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 10.04x | 11+0 | 0 | 20 | 0 | 316.1 |
| npbc_c1/cg | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 9.96x | 14+0 | 0 | 20 | 0 | 301.9 |
| npbc_c1/cg | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 8.48x | 11+0 | 0 | 20 | 0 | 308.3 |
| npbc_c1/cg | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 8.56x | 9+0 | 0 | 20 | 8 | 1560.5 |
| npbc_c1/cg | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 8.60x | 11+0 | 0 | 20 | 9 | 1880.9 |
| npbc_c1/cg | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 9.96x | 10+0 | 0 | 20 | 7 | 1395.3 |
| npbc_c1/cg | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 9.62x | 11+0 | 0 | 20 | 4 | 668.6 |
| npbc_c1/cg | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 8.82x | 11+0 | 0 | 20 | 7 | 1310.4 |
