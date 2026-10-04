# Agent experiment run `e1v5_smoke`

- status: finished (created 2026-10-04T14:53:16, finished 2026-10-04T15:03:44)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `bcc496e919a80cbb601952712fefa8234f161f50` (uncommitted diff sha256 `None`)
- harness: `bcc496e919a80cbb601952712fefa8234f161f50` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-fable-5-1 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 35 | 2 |
| bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 56 | 2 |
| bare_llm_v4 | claude-opus-5-5 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 21 | 2 |
| bare_llm_v4 | claude-sonnet-5 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | 2 |
| default_v4 | claude-haiku-4-5-20251001 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 182 | 2 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 29 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c1/s000 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 3.65x | —+— | — | — | 1 | 15.8 |
| tsvc_c1/s000 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.54x | —+— | — | — | 1 | 22.8 |
| tsvc_c1/s000 | bare_llm_v4 | claude-opus-5-5 | 1 | FASTER | 3.66x | —+— | — | — | 1 | 15.4 |
| tsvc_c1/s000 | bare_llm_v4 | claude-sonnet-5 | 1 | FASTER | 3.42x | —+— | — | — | 1 | 14.4 |
| tsvc_c1/s000 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.57x | 1+0 | 1 | 1 | 1 | 168.7 |
| tsvc_c1/s000 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.60x | 1+0 | 0 | 1 | 0 | 49.1 |
| tsvc_c1/s211 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 2.20x | —+— | — | — | 1 | 54.4 |
| tsvc_c1/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 0.80x | —+— | — | — | 1 | 89.6 |
| tsvc_c1/s211 | bare_llm_v4 | claude-opus-5-5 | 1 | parallel-not-faster | 0.95x | —+— | — | — | 1 | 27.3 |
| tsvc_c1/s211 | bare_llm_v4 | claude-sonnet-5 | 1 | parallel-not-faster | 0.64x | —+— | — | — | 1 | 47.2 |
| tsvc_c1/s211 | default_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.04x | 1+0 | 1 | 0 | 1 | 195.9 |
| tsvc_c1/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.3 |
