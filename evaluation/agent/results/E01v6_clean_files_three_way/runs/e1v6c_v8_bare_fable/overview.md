# Agent experiment run `e1v6c_v8_bare_fable`

- status: finished (created 2026-10-10T16:47:54, finished 2026-10-10T16:58:34)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `cb921121f56cdae31ede62d3a6a3aaf64ef1ebfc` (uncommitted diff sha256 `None`)
- harness: `cb921121f56cdae31ede62d3a6a3aaf64ef1ebfc` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-fable-5-1 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 56 | 5 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s341 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 2.32x | —+— | — | — | 1 | 45.5 |
| tsvc_c4/s341 | bare_llm_v4 | claude-fable-5-1 | 2 | FASTER | 2.36x | —+— | — | — | 1 | 64.4 |
| tsvc_c4/s341 | bare_llm_v4 | claude-fable-5-1 | 3 | FASTER | 2.25x | —+— | — | — | 1 | 35.0 |
| tsvc_c4/s341 | bare_llm_v4 | claude-fable-5-1 | 4 | FASTER | 2.31x | —+— | — | — | 1 | 55.7 |
| tsvc_c4/s341 | bare_llm_v4 | claude-fable-5-1 | 5 | FASTER | 2.37x | —+— | — | — | 1 | 62.3 |
