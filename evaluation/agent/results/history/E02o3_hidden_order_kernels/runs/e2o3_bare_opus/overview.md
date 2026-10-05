# Agent experiment run `e2o3_bare_opus`

- status: finished (created 2026-10-03T19:55:42, finished 2026-10-03T20:14:26)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `8277854d41b94b393e17b452d3f291b3a1c8820a` (uncommitted diff sha256 `None`)
- harness: `8277854d41b94b393e17b452d3f291b3a1c8820a` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-opus-5-5 | 15 | 2 | 6 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 50 | 16 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 1 | BROKEN | 4.28x | —+— | — | — | 1 | 14.1 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 2 | BROKEN | 4.21x | —+— | — | — | 1 | 13.5 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 3 | BROKEN | 4.32x | —+— | — | — | 1 | 13.0 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 4 | BROKEN | 4.27x | —+— | — | — | 1 | 24.7 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-opus-5-5 | 5 | BROKEN | 4.16x | —+— | — | — | 1 | 14.0 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 1 | parallel-not-faster | 0.96x | —+— | — | — | 1 | 53.8 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 2 | parallel-not-faster | 1.00x | —+— | — | — | 1 | 54.2 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 3 | FASTER | 2.29x | —+— | — | — | 1 | 50.1 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 4 | parallel-not-faster | 1.01x | —+— | — | — | 1 | 52.1 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-opus-5-5 | 5 | parallel-not-faster | 1.02x | —+— | — | — | 1 | 56.9 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 1 | parallel-not-faster | 0.99x | —+— | — | — | 2 | 86.5 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 2 | BROKEN | 2.97x | —+— | — | — | 1 | 46.2 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 3 | BROKEN | 2.58x | —+— | — | — | 1 | 64.8 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 4 | parallel-not-faster | 0.99x | —+— | — | — | 1 | 78.4 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-opus-5-5 | 5 | FASTER | 3.00x | —+— | — | — | 1 | 46.4 |
