# Agent experiment run `p_fable_k19`

- status: finished (created 2026-10-03T23:10:33, finished 2026-10-03T23:53:52)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `74d9328675f523b7c7dd420dbc083e5fc7625612` (uncommitted diff sha256 `None`)
- harness: `74d9328675f523b7c7dd420dbc083e5fc7625612` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed_v3 | claude-fable-5-1 | 3 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 143 | 5 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-fable-5-1 | 1 | FASTER | 1.16x | 2+0 | 1 | 0 | 1 | 131.2 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-fable-5-1 | 2 | BROKEN | — | 1+0 | 1 | 0 | 3 | 396.3 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-fable-5-1 | 3 | FASTER | 1.14x | 1+0 | 1 | 0 | 1 | 142.7 |
