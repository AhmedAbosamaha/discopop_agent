# Agent experiment run `e1v6c_v7_bare_fable`

- status: finished (created 2026-10-07T19:55:09, finished 2026-10-07T21:26:55)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `eeee11e74a5e2732ab9e15531d06a43126c6319b` (uncommitted diff sha256 `None`)
- harness: `eeee11e74a5e2732ab9e15531d06a43126c6319b` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-fable-5-1 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 24 | 6 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c3/s313 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 3.56x | —+— | — | — | 1 | 20.2 |
| tsvc_c3/s331 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 3.55x | —+— | — | — | 1 | 36.8 |
| tsvc_c3/s331 | bare_llm_v4 | claude-fable-5-1 | 2 | FASTER | 4.55x | —+— | — | — | 1 | 18.8 |
| tsvc_c3/s331 | bare_llm_v4 | claude-fable-5-1 | 3 | FASTER | 4.41x | —+— | — | — | 1 | 14.4 |
| tsvc_c3/s331 | bare_llm_v4 | claude-fable-5-1 | 4 | FASTER | 4.48x | —+— | — | — | 1 | 28.1 |
| tsvc_c3/s331 | bare_llm_v4 | claude-fable-5-1 | 5 | FASTER | 4.55x | —+— | — | — | 1 | 31.8 |
