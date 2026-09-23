# Agent experiment run `e1b_v2_verify`

- status: running (created 2026-09-23T14:32:58, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `ad57f134aca9862a06336618c9f75a20a8fd2e56` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v1_control_r1 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v1_control_slow_r4 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_clause_r2 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_clause_r3 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_clause_r4 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_clause_r5 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_joint_r1 | none | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_joint_r2 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_joint_r3 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_joint_r4 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v2_joint_r5 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s112 | v2_joint_r4 | none | 1 | FASTER | 1.74x | —+— | — | — | 0 | — |
| tsvc/s121 | v1_control_slow_r4 | none | 1 | parallel-not-faster | 0.14x | —+— | — | — | 0 | — |
| tsvc/s121 | v2_joint_r1 | none | 1 | FASTER | 1.75x | —+— | — | — | 0 | — |
| tsvc/s121 | v2_joint_r2 | none | 1 | FASTER | 1.64x | —+— | — | — | 0 | — |
| tsvc/s121 | v2_joint_r5 | none | 1 | FASTER | 1.68x | —+— | — | — | 0 | — |
| tsvc/s1213 | v2_joint_r1 | none | 1 | FASTER | 3.00x | —+— | — | — | 0 | — |
| tsvc/s1213 | v2_joint_r3 | none | 1 | FASTER | 2.70x | —+— | — | — | 0 | — |
| tsvc/s127 | v1_control_r1 | none | 1 | FASTER | 4.48x | —+— | — | — | 0 | — |
| tsvc/s244 | v2_joint_r1 | none | 1 | FASTER | 1.49x | —+— | — | — | 0 | — |
| tsvc/s281 | v2_clause_r2 | none | 1 | FASTER | 3.25x | —+— | — | — | 0 | — |
| tsvc/s281 | v2_clause_r3 | none | 1 | FASTER | 3.02x | —+— | — | — | 0 | — |
| tsvc/s281 | v2_clause_r4 | none | 1 | FASTER | 3.15x | —+— | — | — | 0 | — |
| tsvc/s281 | v2_clause_r5 | none | 1 | FASTER | 2.55x | —+— | — | — | 0 | — |
