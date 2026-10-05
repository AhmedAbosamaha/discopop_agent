# Agent experiment run `e12_fable_v3b`

- status: finished (created 2026-10-03T04:45:42, finished 2026-10-03T04:58:06)
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
| bare_llm_nospeed_v3 | claude-fable-5-1 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 50 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | FASTER | 2.79x | —+— | — | — | 1 | 38.7 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | FASTER | 2.54x | —+— | — | — | 1 | 44.2 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | FASTER | 2.60x | —+— | — | — | 1 | 39.5 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | FASTER | 2.54x | —+— | — | — | 1 | 53.5 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | FASTER | 2.52x | —+— | — | — | 1 | 23.4 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-fable-5-1 | 1 | FASTER | 2.06x | —+— | — | — | 1 | 46.8 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-fable-5-1 | 2 | FASTER | 1.81x | —+— | — | — | 1 | 79.3 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-fable-5-1 | 3 | FASTER | 1.83x | —+— | — | — | 1 | 67.5 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-fable-5-1 | 4 | FASTER | 1.87x | —+— | — | — | 1 | 61.9 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-fable-5-1 | 5 | FASTER | 2.09x | —+— | — | — | 1 | 60.7 |
