# Agent experiment run `t0_11_b19_apps_c`

- status: finished (created 2026-10-08T15:33:24, finished 2026-10-08T16:24:10)
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
| discopop_capability | claude-haiku-4-5-20251001 | 31 | 13 | 3 | 6 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 0.69 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 3.97 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 5.21 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 4.51 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 3.76 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.40 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 646.9 |
| npb/is | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 9.4 |
| polybench/2mm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 6.66x | 2+0 | 0 | 6 | 0 | 5.1 |
| polybench/3mm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 10.14x | 3+0 | 0 | 9 | 0 | 6.6 |
| polybench/adi | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 1.84x | 4+0 | 0 | 6 | 0 | 13.4 |
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.69x | 1+0 | 0 | 3 | 0 | 4.7 |
| polybench/bicg | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.3 |
| polybench/correlation | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.68x | 1+0 | 0 | 3 | 0 | 5.0 |
| polybench/covariance | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.70x | 1+0 | 0 | 3 | 0 | 5.7 |
| polybench/doitgen | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 3 | 0 | 4.1 |
| polybench/dynprog | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.96x | 1+0 | 0 | 6 | 0 | 5.0 |
| polybench/fdtd-2d | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.34x | 3+0 | 0 | 7 | 0 | 7.5 |
| polybench/fdtd-apml | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.57x | 1+0 | 0 | 4 | 0 | 5.0 |
| polybench/floyd-warshall | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 3.6 |
| polybench/gemm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 9.72x | 1+0 | 0 | 3 | 0 | 4.2 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 3.97x | 3+0 | 0 | 6 | 0 | 5.8 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 5.21x | 1+0 | 0 | 2 | 0 | 3.9 |
| polybench/gramschmidt | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.35x | 1+0 | 0 | 1 | 0 | 5.5 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 4.51x | 2+0 | 0 | 3 | 0 | 5.0 |
| polybench/jacobi-2d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.78x | 2+0 | 0 | 4 | 0 | 5.0 |
| polybench/lu | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.23x | 1+0 | 0 | 0 | 0 | 4.7 |
| polybench/ludcmp | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.65x | 2+0 | 0 | 4 | 0 | 4.5 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 3.76x | 2+0 | 0 | 4 | 0 | 5.0 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.40x | 3+0 | 0 | 8 | 0 | 6.2 |
| polybench/seidel-2d | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.7 |
| polybench/symm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 1.30x | 1+0 | 0 | 3 | 0 | 7.5 |
| polybench/syr2k | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 7.91x | 1+0 | 0 | 3 | 0 | 4.1 |
| polybench/syrk | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 6.49x | 1+0 | 0 | 2 | 0 | 3.9 |
| polybench/trisolv | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 2.6 |
| rodinia-3.1/hotspot | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 12.9 |
| rodinia-3.1/pathfinder | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 18.7 |
