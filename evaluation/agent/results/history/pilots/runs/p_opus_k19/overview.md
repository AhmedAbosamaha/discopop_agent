# Agent experiment run `p_opus_k19`

- status: finished (created 2026-10-03T21:58:38, finished 2026-10-03T23:10:00)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `fb7b8eb7fdd9c3e346d495b456b8b365fb2968db` (uncommitted diff sha256 `None`)
- harness: `fb7b8eb7fdd9c3e346d495b456b8b365fb2968db` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed_v3 | claude-opus-5-5 | 3 | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 215 | 6 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 1 | BROKEN | — | 1+0 | 1 | 0 | 3 | 290.1 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 2 | BROKEN | — | 1+0 | 1 | 0 | 2 | 215.1 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 3 | parallel-not-faster | 0.97x | 1+0 | 1 | 0 | 1 | 74.0 |
