# Agent experiment run `mac_v5_preflight`

- status: finished (created 2026-10-04T09:02:04, finished 2026-10-04T09:03:15)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `0d29a599bc3a8a1d7ba5f940f065303dd11ee55c` (uncommitted diff sha256 `579d23989ce48e8e32ef2dfee534d31cd0bfe9fc10056e0b6c1ce7fabcc65754`)
- harness: `0d29a599bc3a8a1d7ba5f940f065303dd11ee55c` on `agentic_DiscoPop`
- verify size `SMALL`, threads [2, 4], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate_v3 | haiku | 2 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c1/k19 | discopop_gate_v3 | haiku | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 17.7 |
| tsvc_c1/s000 | discopop_gate_v3 | haiku | 1 | parallel-not-faster | 0.42x | 1+0 | 0 | 1 | 0 | 28.1 |
