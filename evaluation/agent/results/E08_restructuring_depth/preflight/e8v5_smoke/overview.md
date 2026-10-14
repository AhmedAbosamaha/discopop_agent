# Agent experiment run `e8v5_smoke`

- status: finished (created 2026-10-14T08:07:53, finished 2026-10-14T08:31:22)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `fa56b372464e1cfc10053c92fdc3d40b4a37585c` (uncommitted diff sha256 `None`)
- harness: `fa56b372464e1cfc10053c92fdc3d40b4a37585c` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| depth1_v5 | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 783 | 3 |
| depth2_v5 | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 568 | 4 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c5/s2251 | depth1_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 782.8 |
| tsvc_c5/s2251 | depth2_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 567.5 |
