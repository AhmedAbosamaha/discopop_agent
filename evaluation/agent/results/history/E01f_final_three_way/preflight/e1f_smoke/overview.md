# Agent experiment run `e1f_smoke`

- status: finished (created 2026-10-02T20:14:26, finished 2026-10-02T20:40:28)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `b56a086a814002481f586472a8564dfe66053154` (uncommitted diff sha256 `None`)
- harness: `b56a086a814002481f586472a8564dfe66053154` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v3 | claude-fable-5-1 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 49 | 2 |
| bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 104 | 2 |
| bare_llm_v3 | claude-opus-5-5 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 26 | 2 |
| bare_llm_v3 | claude-sonnet-5 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 83 | 2 |
| default_v3 | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 515 | 9 |
| discopop_gate_v3 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 28 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s000 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 4.57x | —+— | — | — | 1 | 33.5 |
| tsvc_b1/s000 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.38x | —+— | — | — | 1 | 30.5 |
| tsvc_b1/s000 | bare_llm_v3 | claude-opus-5-5 | 1 | FASTER | 4.48x | —+— | — | — | 1 | 15.1 |
| tsvc_b1/s000 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 4.55x | —+— | — | — | 1 | 41.4 |
| tsvc_b1/s000 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.49x | 1+0 | 0 | 1 | 4 | 275.5 |
| tsvc_b1/s000 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.46x | 1+0 | 0 | 1 | 0 | 48.0 |
| tsvc_b1/s211 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.76x | —+— | — | — | 1 | 63.6 |
| tsvc_b1/s211 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 178.4 |
| tsvc_b1/s211 | bare_llm_v3 | claude-opus-5-5 | 1 | FASTER | 2.79x | —+— | — | — | 1 | 37.3 |
| tsvc_b1/s211 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 2.86x | —+— | — | — | 1 | 123.7 |
| tsvc_b1/s211 | default_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.54x | 2+0 | 1 | 0 | 5 | 754.9 |
| tsvc_b1/s211 | discopop_gate_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.3 |
