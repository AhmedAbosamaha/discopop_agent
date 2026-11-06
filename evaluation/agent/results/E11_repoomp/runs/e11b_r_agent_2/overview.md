# Agent experiment run `e11b_r_agent_2`

- status: finished (created 2026-11-06T09:03:42, finished 2026-11-06T12:35:49)
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
| discopop_gate_v5 | claude-sonnet-4-5-20250929 | 15 | 0 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 15 | 10 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 206 | 64 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k48 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 0.97x | 0+0 | 0 | 0 | 0 | 4.0 |
| tsvc_c2/k48 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_c2/k48 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.0 |
| tsvc_c2/k48 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc_c2/k48 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.0 |
| tsvc_c2/k48 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 4.04x | 0+2 | 1 | 0 | 1 | 189.4 |
| tsvc_c2/k48 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 4.08x | 0+2 | 1 | 0 | 1 | 141.1 |
| tsvc_c2/k48 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 2.34x | 0+3 | 1 | 0 | 1 | 168.7 |
| tsvc_c2/k48 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 2.37x | 0+3 | 1 | 0 | 1 | 254.4 |
| tsvc_c2/k48 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 2.07x | 0+5 | 1 | 0 | 2 | 410.7 |
| tsvc_c2/k53 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.7 |
| tsvc_c2/k53 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.3 |
| tsvc_c2/k53 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.3 |
| tsvc_c2/k53 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.3 |
| tsvc_c2/k53 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc_c2/k53 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 2462.8 |
| tsvc_c2/k53 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 2017.5 |
| tsvc_c2/k53 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1637.7 |
| tsvc_c2/k53 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1672.9 |
| tsvc_c2/k53 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1940.7 |
| tsvc_c2/s161 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 3.5 |
| tsvc_c2/s161 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.5 |
| tsvc_c2/s161 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.5 |
| tsvc_c2/s161 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.4 |
| tsvc_c2/s161 | discopop_gate_v5 | claude-sonnet-4-5-20250929 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.5 |
| tsvc_c2/s161 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 1 | FASTER | 2.22x | 0+2 | 1 | 0 | 1 | 136.2 |
| tsvc_c2/s161 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 2 | FASTER | 2.34x | 0+2 | 1 | 0 | 1 | 205.5 |
| tsvc_c2/s161 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 3 | FASTER | 2.27x | 0+2 | 1 | 0 | 1 | 141.0 |
| tsvc_c2/s161 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 4 | FASTER | 2.31x | 0+2 | 1 | 0 | 1 | 143.7 |
| tsvc_c2/s161 | llm_pragmas_v5 | claude-sonnet-4-5-20250929 | 5 | FASTER | 2.30x | 0+2 | 1 | 0 | 1 | 146.6 |
