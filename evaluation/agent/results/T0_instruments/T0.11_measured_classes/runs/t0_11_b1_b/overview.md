# Agent experiment run `t0_11_b1_b`

- status: finished (created 2026-09-27T16:25:41, finished 2026-09-27T16:46:38)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `ef2263200969b0cecbb282f2432cba1538516fbb` (uncommitted diff sha256 `None`)
- harness: `ef2263200969b0cecbb282f2432cba1538516fbb` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | none | 11 | 5 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| rodinia_b1/bfs | discopop_capability | none | 1 | no-change | 0.99x | 0+0 | 0 | 3 | 0 | 303.3 |
| tsvc_b1/s131 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc_b1/s151 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.3 |
| tsvc_b1/s152 | discopop_capability | none | 1 | FASTER | 2.67x | 1+0 | 0 | 1 | 0 | 3.5 |
| tsvc_b1/s161 | discopop_capability | none | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_b1/s171 | discopop_capability | none | 1 | FASTER | 3.48x | 1+0 | 0 | 1 | 0 | 3.5 |
| tsvc_b1/s277 | discopop_capability | none | 1 | FASTER | 8.69x | 1+0 | 0 | 1 | 0 | 3.3 |
| tsvc_b1/s424 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.7 |
| tsvc_b1/s481 | discopop_capability | none | 1 | FASTER | 3.39x | 1+0 | 0 | 2 | 0 | 4.0 |
| tsvc_b1/s482 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 1.9 |
| tsvc_b1/vas | discopop_capability | none | 1 | FASTER | 3.22x | 1+0 | 0 | 1 | 0 | 3.3 |
