# Agent experiment run `e2o3_bare_sonnet`

- status: finished (created 2026-10-03T18:59:17, finished 2026-10-03T20:22:49)
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
| bare_llm_nospeed_v3 | claude-sonnet-5 | 15 | 2 | 0 | 0 | 0 | 0 | 12 | 0 | 1 | 0 | 0 | 0 | 293 | 15 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-sonnet-5 | 1 | BROKEN | 4.10x | —+— | — | — | 1 | 18.0 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-sonnet-5 | 2 | BROKEN | 4.07x | —+— | — | — | 1 | 33.5 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-sonnet-5 | 3 | BROKEN | 4.29x | —+— | — | — | 1 | 20.0 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-sonnet-5 | 4 | BROKEN | 4.33x | —+— | — | — | 1 | 36.2 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-sonnet-5 | 5 | BROKEN | 4.22x | —+— | — | — | 1 | 18.2 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-sonnet-5 | 1 | BROKEN | 3.13x | —+— | — | — | 1 | 590.0 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-sonnet-5 | 2 | FASTER | 1.26x | —+— | — | — | 1 | 530.6 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-sonnet-5 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 569.8 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-sonnet-5 | 4 | FASTER | 3.03x | —+— | — | — | 1 | 615.5 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-sonnet-5 | 5 | BROKEN | 1.85x | —+— | — | — | 1 | 412.7 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-sonnet-5 | 1 | BROKEN | 2.27x | —+— | — | — | 1 | 723.6 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-sonnet-5 | 2 | BROKEN | 2.95x | —+— | — | — | 1 | 153.9 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-sonnet-5 | 3 | BROKEN | 4.00x | —+— | — | — | 1 | 420.5 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-sonnet-5 | 4 | BROKEN | 4.00x | —+— | — | — | 1 | 203.9 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-sonnet-5 | 5 | BROKEN | 3.86x | —+— | — | — | 1 | 293.2 |
