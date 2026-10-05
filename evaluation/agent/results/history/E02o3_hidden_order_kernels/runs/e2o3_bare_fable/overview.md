# Agent experiment run `e2o3_bare_fable`

- status: finished (created 2026-10-03T20:36:11, finished 2026-10-03T21:06:20)
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
| bare_llm_nospeed_v3 | claude-fable-5-1 | 15 | 5 | 1 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 96 | 15 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | BROKEN | 4.31x | —+— | — | — | 1 | 21.4 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | BROKEN | 4.26x | —+— | — | — | 1 | 16.0 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | BROKEN | 4.22x | —+— | — | — | 1 | 15.1 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | BROKEN | 4.21x | —+— | — | — | 1 | 13.9 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | BROKEN | 4.25x | —+— | — | — | 1 | 22.7 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | FASTER | 2.38x | —+— | — | — | 1 | 144.8 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | FASTER | 3.22x | —+— | — | — | 1 | 132.5 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | FASTER | 3.16x | —+— | — | — | 1 | 121.0 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | FASTER | 3.17x | —+— | — | — | 1 | 203.1 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | BROKEN | 1.61x | —+— | — | — | 1 | 66.3 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | FASTER | 1.46x | —+— | — | — | 1 | 141.7 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | BROKEN | — | —+— | — | — | 1 | 168.6 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | BROKEN | 3.22x | —+— | — | — | 1 | 95.6 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | parallel-not-faster | 0.97x | —+— | — | — | 1 | 186.3 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | BROKEN | 3.10x | —+— | — | — | 1 | 66.7 |
