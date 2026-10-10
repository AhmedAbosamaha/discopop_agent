# Agent experiment run `t0_11_b23_apps_b`

- status: finished (created 2026-10-10T21:31:34, finished 2026-10-10T22:19:24)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `c89952852c28b5db3926ac3dcd21f0a1bc913e4a` (uncommitted diff sha256 `None`)
- harness: `c89952852c28b5db3926ac3dcd21f0a1bc913e4a` on `agentic_DiscoPop`
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
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 0.72 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 4.02 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 5.39 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 4.78 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 3.94 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.40 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 652.4 |
| npb/is | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 9.5 |
| polybench/2mm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 9.04x | 2+0 | 0 | 6 | 0 | 5.3 |
| polybench/3mm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 8.43x | 3+0 | 0 | 9 | 0 | 6.8 |
| polybench/adi | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 1.92x | 4+0 | 0 | 9 | 0 | 14.9 |
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.72x | 1+0 | 0 | 3 | 0 | 5.2 |
| polybench/bicg | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.6 |
| polybench/correlation | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.73x | 1+0 | 0 | 3 | 0 | 5.2 |
| polybench/covariance | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.35x | 1+0 | 0 | 3 | 0 | 5.9 |
| polybench/doitgen | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 4.8 |
| polybench/dynprog | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.97x | 1+0 | 0 | 6 | 0 | 5.1 |
| polybench/fdtd-2d | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.27x | 3+0 | 0 | 7 | 0 | 7.6 |
| polybench/fdtd-apml | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.81x | 1+0 | 0 | 4 | 0 | 5.3 |
| polybench/floyd-warshall | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.2 |
| polybench/gemm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 8.50x | 1+0 | 0 | 3 | 0 | 4.1 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 4.02x | 3+0 | 0 | 6 | 0 | 6.0 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 5.39x | 1+0 | 0 | 2 | 0 | 4.0 |
| polybench/gramschmidt | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 7.77x | 1+0 | 0 | 4 | 0 | 4.5 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 4.78x | 2+0 | 0 | 2 | 0 | 4.6 |
| polybench/jacobi-2d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.70x | 2+0 | 0 | 5 | 0 | 6.1 |
| polybench/lu | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.22x | 1+0 | 0 | 2 | 0 | 5.2 |
| polybench/ludcmp | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.30x | 2+0 | 0 | 5 | 0 | 5.1 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 3.94x | 2+0 | 0 | 2 | 0 | 4.7 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.40x | 3+0 | 0 | 8 | 0 | 6.1 |
| polybench/seidel-2d | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 3 | 0 | 4.2 |
| polybench/symm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 1.50x | 1+0 | 0 | 3 | 0 | 7.9 |
| polybench/syr2k | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 10.47x | 1+0 | 0 | 3 | 0 | 4.0 |
| polybench/syrk | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 9.73x | 1+0 | 0 | 2 | 0 | 3.8 |
| polybench/trisolv | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 2.6 |
| rodinia-3.1/hotspot | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 12.9 |
| rodinia-3.1/pathfinder | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 12.5 |
