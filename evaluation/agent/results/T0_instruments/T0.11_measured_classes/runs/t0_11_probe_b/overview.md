# Agent experiment run `t0_11_probe_b`

- status: finished (created 2026-09-25T21:03:54, finished 2026-09-25T21:24:41)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `fe373504c50a6a2cd2711138627dfc4f5907f348` (uncommitted diff sha256 `None`)
- harness: `fe373504c50a6a2cd2711138627dfc4f5907f348` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | none | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s353 | discopop_capability | none | 1 | FASTER | 2.91x | 1+0 | 0 | 1 | 0 | 3.1 |
| tsvc/s4112 | discopop_capability | none | 1 | FASTER | 3.93x | 1+0 | 0 | 1 | 0 | 3.3 |
| tsvc/s4113 | discopop_capability | none | 1 | FASTER | 3.76x | 1+0 | 0 | 2 | 0 | 3.7 |
| tsvc/s4114 | discopop_capability | none | 1 | FASTER | 3.26x | 1+0 | 0 | 2 | 0 | 3.7 |
| tsvc/s4115 | discopop_capability | none | 1 | FASTER | 3.67x | 1+0 | 0 | 2 | 0 | 3.6 |
| tsvc/s4117 | discopop_capability | none | 1 | FASTER | 3.71x | 1+0 | 0 | 2 | 0 | 3.6 |
| tsvc/s4121 | discopop_capability | none | 1 | FASTER | 3.63x | 1+0 | 0 | 1 | 0 | 3.5 |
| tsvc/s491 | discopop_capability | none | 1 | FASTER | 3.09x | 1+0 | 0 | 2 | 0 | 3.7 |
