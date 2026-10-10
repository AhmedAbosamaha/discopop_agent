# Agent experiment run `e2v6_bare_opus`

- status: finished (created 2026-10-06T05:44:20, finished 2026-10-06T20:30:10)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `4adf76ec2aa5419aa268da8a8f895a55f39507bd` (uncommitted diff sha256 `None`)
- harness: `4adf76ec2aa5419aa268da8a8f895a55f39507bd` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v4 | claude-opus-5-5 | 35 | 8 | 10 | 0 | 0 | 0 | 17 | 0 | 0 | 0 | 0 | 0 | 63 | 35 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-opus-5-5 | 1 | BROKEN | — | —+— | — | — | 1 | 56.5 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-opus-5-5 | 2 | BROKEN | — | —+— | — | — | 1 | 100.6 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-opus-5-5 | 3 | BROKEN | — | —+— | — | — | 1 | 63.9 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-opus-5-5 | 4 | BROKEN | — | —+— | — | — | 1 | 65.9 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-opus-5-5 | 5 | BROKEN | — | —+— | — | — | 1 | 66.7 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-opus-5-5 | 1 | BROKEN | 4.32x | —+— | — | — | 1 | 16.2 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-opus-5-5 | 2 | BROKEN | 4.25x | —+— | — | — | 1 | 19.3 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-opus-5-5 | 3 | BROKEN | 4.29x | —+— | — | — | 1 | 15.6 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-opus-5-5 | 4 | BROKEN | 4.28x | —+— | — | — | 1 | 17.0 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-opus-5-5 | 5 | BROKEN | 4.17x | —+— | — | — | 1 | 19.5 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-opus-5-5 | 1 | BROKEN | — | —+— | — | — | 1 | 60.2 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-opus-5-5 | 2 | BROKEN | — | —+— | — | — | 1 | 56.2 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-opus-5-5 | 3 | BROKEN | — | —+— | — | — | 1 | 54.4 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-opus-5-5 | 4 | BROKEN | — | —+— | — | — | 1 | 58.3 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-opus-5-5 | 5 | BROKEN | — | —+— | — | — | 1 | 72.7 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-opus-5-5 | 1 | parallel-not-faster | 1.00x | —+— | — | — | 1 | 55.4 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-opus-5-5 | 2 | FASTER | 2.27x | —+— | — | — | 1 | 60.9 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-opus-5-5 | 3 | FASTER | 2.45x | —+— | — | — | 1 | 64.9 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-opus-5-5 | 4 | FASTER | 2.33x | —+— | — | — | 1 | 71.8 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-opus-5-5 | 5 | parallel-not-faster | 1.00x | —+— | — | — | 1 | 46.8 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-opus-5-5 | 1 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 66.7 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-opus-5-5 | 2 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 74.5 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-opus-5-5 | 3 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 64.2 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-opus-5-5 | 4 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 75.5 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-opus-5-5 | 5 | BROKEN | — | —+— | — | — | 1 | 72.2 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-opus-5-5 | 1 | parallel-not-faster | 0.00x | —+— | — | — | 1 | 71.6 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-opus-5-5 | 2 | parallel-not-faster | 0.03x | —+— | — | — | 1 | 71.0 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-opus-5-5 | 3 | parallel-not-faster | 0.03x | —+— | — | — | 1 | 64.0 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-opus-5-5 | 4 | BROKEN | 0.01x | —+— | — | — | 1 | 63.4 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-opus-5-5 | 5 | parallel-not-faster | 0.00x | —+— | — | — | 1 | 68.8 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-opus-5-5 | 1 | FASTER | 1.66x | —+— | — | — | 1 | 130.7 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-opus-5-5 | 2 | FASTER | 1.71x | —+— | — | — | 1 | 24.1 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-opus-5-5 | 3 | FASTER | 1.67x | —+— | — | — | 1 | 24.2 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-opus-5-5 | 4 | FASTER | 2.26x | —+— | — | — | 1 | 28.0 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-opus-5-5 | 5 | FASTER | 2.21x | —+— | — | — | 1 | 25.8 |
