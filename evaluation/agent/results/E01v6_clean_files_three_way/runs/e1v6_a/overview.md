# Agent experiment run `e1v6_a`

- status: finished (created 2026-10-05T06:08:40, finished 2026-10-05T06:39:17)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `70cb05ff3d1ecc75158877a042809fcfdf7d5da8` (uncommitted diff sha256 `None`)
- harness: `70cb05ff3d1ecc75158877a042809fcfdf7d5da8` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v4 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 403 | 7 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 60 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s000 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.86x | 1+0 | 0 | 1 | 2 | 352.4 |
| tsvc_c2/s000 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.67x | 1+0 | 0 | 1 | 0 | 50.5 |
| tsvc_c2/s313 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 164.14x | 1+0 | 1 | 1 | 2 | 402.6 |
| tsvc_c2/s313 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.67x | 1+0 | 0 | 1 | 0 | 59.7 |
| tsvc_c2/vpvtv | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.96x | 1+0 | 0 | 1 | 3 | 425.5 |
| tsvc_c2/vpvtv | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.41x | 1+0 | 0 | 1 | 0 | 63.0 |
