# Agent experiment run `e11_retime`

- status: running (created 2026-11-06T22:59:55, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `8b2defa309e93a0671f8a42b343d7457012ce373` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | none | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| claude_code | none | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| discopop_gate_v5 | none | 10 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| expert_openmp | none | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| llm_pragmas_v5 | none | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| repoomp_claude | none | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| npbc_c1/cg | bare_llm_v4 | none | 1 | FASTER | 10.36x | —+— | — | — | 0 | — |
| npbc_c1/cg | bare_llm_v4 | none | 2 | FASTER | 10.37x | —+— | — | — | 0 | — |
| npbc_c1/cg | bare_llm_v4 | none | 3 | FASTER | 10.02x | —+— | — | — | 0 | — |
| npbc_c1/cg | bare_llm_v4 | none | 4 | FASTER | 9.75x | —+— | — | — | 0 | — |
| npbc_c1/cg | bare_llm_v4 | none | 5 | FASTER | 10.29x | —+— | — | — | 0 | — |
| npbc_c1/cg | claude_code | none | 1 | BROKEN | 10.21x | —+— | — | — | 0 | — |
| npbc_c1/cg | discopop_gate_v5 | none | 1 | FASTER | 9.16x | —+— | — | — | 0 | — |
| npbc_c1/cg | discopop_gate_v5 | none | 2 | FASTER | 10.30x | —+— | — | — | 0 | — |
| npbc_c1/cg | discopop_gate_v5 | none | 3 | FASTER | 9.96x | —+— | — | — | 0 | — |
| npbc_c1/cg | discopop_gate_v5 | none | 4 | FASTER | 9.97x | —+— | — | — | 0 | — |
| npbc_c1/cg | discopop_gate_v5 | none | 5 | FASTER | 8.54x | —+— | — | — | 0 | — |
| npbc_c1/cg | expert_openmp | none | 1 | FASTER | 10.21x | —+— | — | — | 0 | — |
| npbc_c1/cg | llm_pragmas_v5 | none | 1 | FASTER | 8.72x | —+— | — | — | 0 | — |
| npbc_c1/cg | llm_pragmas_v5 | none | 2 | FASTER | 8.50x | —+— | — | — | 0 | — |
| npbc_c1/cg | llm_pragmas_v5 | none | 3 | FASTER | 9.94x | —+— | — | — | 0 | — |
| npbc_c1/cg | llm_pragmas_v5 | none | 4 | FASTER | 9.56x | —+— | — | — | 0 | — |
| npbc_c1/cg | llm_pragmas_v5 | none | 5 | FASTER | 8.67x | —+— | — | — | 0 | — |
| npbc_c1/cg | repoomp_claude | none | 1 | FASTER | 9.78x | —+— | — | — | 0 | — |
| npbc_c1/ep | bare_llm_v4 | none | 1 | FASTER | 7.95x | —+— | — | — | 0 | — |
| npbc_c1/ep | bare_llm_v4 | none | 2 | FASTER | 7.80x | —+— | — | — | 0 | — |
| npbc_c1/ep | bare_llm_v4 | none | 3 | FASTER | 6.26x | —+— | — | — | 0 | — |
| npbc_c1/ep | bare_llm_v4 | none | 4 | FASTER | 6.29x | —+— | — | — | 0 | — |
| npbc_c1/ep | bare_llm_v4 | none | 5 | FASTER | 8.38x | —+— | — | — | 0 | — |
| npbc_c1/ep | claude_code | none | 1 | SCAFFOLD_MODIFIED | — | —+— | — | — | 0 | — |
| npbc_c1/ep | discopop_gate_v5 | none | 1 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| npbc_c1/ep | discopop_gate_v5 | none | 2 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| npbc_c1/ep | discopop_gate_v5 | none | 3 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| npbc_c1/ep | discopop_gate_v5 | none | 4 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| npbc_c1/ep | discopop_gate_v5 | none | 5 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| npbc_c1/ep | expert_openmp | none | 1 | BROKEN | 8.01x | —+— | — | — | 0 | — |
| npbc_c1/ep | llm_pragmas_v5 | none | 1 | FASTER | 6.24x | —+— | — | — | 0 | — |
| npbc_c1/ep | llm_pragmas_v5 | none | 2 | FASTER | 1.37x | —+— | — | — | 0 | — |
| npbc_c1/ep | llm_pragmas_v5 | none | 3 | FASTER | 8.65x | —+— | — | — | 0 | — |
| npbc_c1/ep | llm_pragmas_v5 | none | 4 | FASTER | 9.03x | —+— | — | — | 0 | — |
| npbc_c1/ep | llm_pragmas_v5 | none | 5 | FASTER | 8.58x | —+— | — | — | 0 | — |
| npbc_c1/ep | repoomp_claude | none | 1 | FASTER | 6.78x | —+— | — | — | 0 | — |
