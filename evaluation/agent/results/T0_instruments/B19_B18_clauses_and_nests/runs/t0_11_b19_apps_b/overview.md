# Agent experiment run `t0_11_b19_apps_b`

- status: finished (created 2026-10-08T15:32:57, finished 2026-10-08T16:19:12)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `855dd0093f7a370ec3559da4f88831a44d7b631d` (uncommitted diff sha256 `None`)
- harness: `855dd0093f7a370ec3559da4f88831a44d7b631d` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | claude-haiku-4-5-20251001 | 31 | 14 | 2 | 6 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 0.71 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 3.90 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 4.04 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 4.56 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 2.80 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.36 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 648.2 |
| npb/is | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 9.5 |
| polybench/2mm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 9.88x | 2+0 | 0 | 6 | 0 | 5.3 |
| polybench/3mm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 10.16x | 3+0 | 0 | 9 | 0 | 7.0 |
| polybench/adi | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 1.93x | 4+0 | 0 | 9 | 0 | 14.8 |
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.71x | 1+0 | 0 | 3 | 0 | 4.9 |
| polybench/bicg | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.3 |
| polybench/correlation | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.71x | 1+0 | 0 | 2 | 0 | 5.0 |
| polybench/covariance | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.31x | 1+0 | 0 | 3 | 0 | 5.9 |
| polybench/doitgen | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 4 | 0 | 4.5 |
| polybench/dynprog | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.95x | 1+0 | 0 | 6 | 0 | 4.9 |
| polybench/fdtd-2d | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.17x | 3+0 | 0 | 6 | 0 | 6.7 |
| polybench/fdtd-apml | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.62x | 1+0 | 0 | 4 | 0 | 5.2 |
| polybench/floyd-warshall | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.1 |
| polybench/gemm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 6.43x | 1+0 | 0 | 3 | 0 | 4.0 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 3.90x | 3+0 | 0 | 6 | 0 | 5.8 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 4.04x | 1+0 | 0 | 2 | 0 | 3.8 |
| polybench/gramschmidt | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 7.76x | 1+0 | 0 | 4 | 0 | 4.3 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 4.56x | 2+0 | 0 | 2 | 0 | 4.6 |
| polybench/jacobi-2d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.32x | 2+0 | 0 | 4 | 0 | 5.1 |
| polybench/lu | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.22x | 1+0 | 0 | 0 | 0 | 5.2 |
| polybench/ludcmp | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.28x | 2+0 | 0 | 4 | 0 | 4.6 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 2.80x | 2+0 | 0 | 4 | 0 | 4.9 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.36x | 3+0 | 0 | 7 | 0 | 5.7 |
| polybench/seidel-2d | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| polybench/symm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 1.32x | 1+0 | 0 | 3 | 0 | 9.9 |
| polybench/syr2k | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 10.50x | 1+0 | 0 | 3 | 0 | 4.3 |
| polybench/syrk | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 8.50x | 1+0 | 0 | 2 | 0 | 4.0 |
| polybench/trisolv | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 2.9 |
| rodinia-3.1/hotspot | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 13.1 |
| rodinia-3.1/pathfinder | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 12.6 |
