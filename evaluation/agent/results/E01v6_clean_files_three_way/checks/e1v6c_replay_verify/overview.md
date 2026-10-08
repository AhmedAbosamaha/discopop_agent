# Agent experiment run `e1v6c_replay_verify`

- status: running (created 2026-10-08T06:34:47, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `3fb070390bd956fa16e25774c2b7eb8983c0ab80` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| replay_s241_r1_c05 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r1_c07 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r4_c01 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r4_c05 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r4_c09 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r4_c11 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r5_c07 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r5_c14 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r5_c16 | none | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r5_c20 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s241_r5_c25 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s252_r1_c01 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s252_r1_c03 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s252_r2_c02 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s341_r2_c01 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s341_r2_c10 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s341_r2_c12 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s341_r2_c16 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s341_r2_c19 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s341_r2_c22 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay_s341_r2_c25 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s241 | replay_s241_r1_c05 | none | 1 | parallel-not-faster | 0.29x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r1_c07 | none | 1 | parallel-not-faster | 0.96x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r4_c01 | none | 1 | parallel-not-faster | 0.38x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r4_c05 | none | 1 | FASTER | 1.81x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r4_c09 | none | 1 | parallel-not-faster | 0.28x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r4_c11 | none | 1 | parallel-not-faster | 0.96x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r5_c07 | none | 1 | parallel-not-faster | 0.62x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r5_c14 | none | 1 | parallel-not-faster | 0.78x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r5_c16 | none | 1 | FASTER | 1.84x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r5_c20 | none | 1 | parallel-not-faster | 0.63x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | replay_s241_r5_c25 | none | 1 | parallel-not-faster | 0.57x | —+— | — | — | 0 | — |
| tsvc_c2/s252 | replay_s252_r1_c01 | none | 1 | parallel-not-faster | 0.43x | —+— | — | — | 0 | — |
| tsvc_c2/s252 | replay_s252_r1_c03 | none | 1 | parallel-not-faster | 0.98x | —+— | — | — | 0 | — |
| tsvc_c2/s252 | replay_s252_r2_c02 | none | 1 | parallel-not-faster | 1.01x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | replay_s341_r2_c01 | none | 1 | parallel-not-faster | 0.66x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | replay_s341_r2_c10 | none | 1 | parallel-not-faster | 0.65x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | replay_s341_r2_c12 | none | 1 | parallel-not-faster | 0.35x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | replay_s341_r2_c16 | none | 1 | parallel-not-faster | 0.66x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | replay_s341_r2_c19 | none | 1 | parallel-not-faster | 0.20x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | replay_s341_r2_c22 | none | 1 | parallel-not-faster | 0.64x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | replay_s341_r2_c25 | none | 1 | parallel-not-faster | 0.64x | —+— | — | — | 0 | — |
