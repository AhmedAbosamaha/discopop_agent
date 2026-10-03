# Agent experiment run `e12_sonnet_b1`

- status: finished (created 2026-10-03T04:35:16, finished 2026-10-03T05:17:17)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `ab0e7f4759b982c26184c0efa24f19e97ea795f9` (uncommitted diff sha256 `None`)
- harness: `ab0e7f4759b982c26184c0efa24f19e97ea795f9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed | claude-sonnet-5 | 10 | 3 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 132 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 1 | FASTER | 3.56x | —+— | — | — | 1 | 148.7 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 2 | FASTER | 2.64x | —+— | — | — | 1 | 219.9 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 3 | FASTER | 3.48x | —+— | — | — | 1 | 86.7 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 4 | parallel-not-faster | 0.81x | —+— | — | — | 1 | 114.3 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-sonnet-5 | 5 | parallel-not-faster | 1.07x | —+— | — | — | 1 | 145.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 1 | parallel-not-faster | 0.29x | —+— | — | — | 1 | 118.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 2 | parallel-not-faster | 0.32x | —+— | — | — | 1 | 116.1 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 3 | parallel-not-faster | 0.26x | —+— | — | — | 1 | 170.9 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 4 | parallel-not-faster | 0.35x | —+— | — | — | 1 | 147.5 |
| tsvc_b1/s424 | bare_llm_nospeed | claude-sonnet-5 | 5 | parallel-not-faster | 0.35x | —+— | — | — | 1 | 97.7 |
