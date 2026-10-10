# Agent experiment run `t0_11_b23_apps_c`

- status: finished (created 2026-10-10T21:32:01, finished 2026-10-10T22:17:38)
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
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 0.70 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 4.01 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 4.38 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 5.05 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | LARGE | 3.72 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.36 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 3 | 0 | 650.9 |
| npb/is | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 9.4 |
| polybench/2mm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 9.26x | 2+0 | 0 | 6 | 0 | 5.2 |
| polybench/3mm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 10.40x | 3+0 | 0 | 9 | 0 | 6.8 |
| polybench/adi | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 2.04x | 4+0 | 0 | 9 | 0 | 15.2 |
| polybench/atax | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.70x | 1+0 | 0 | 1 | 0 | 3.9 |
| polybench/bicg | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.5 |
| polybench/correlation | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.77x | 1+0 | 0 | 2 | 0 | 5.1 |
| polybench/covariance | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.71x | 1+0 | 0 | 3 | 0 | 6.0 |
| polybench/doitgen | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 4 | 0 | 4.7 |
| polybench/dynprog | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.96x | 1+0 | 0 | 6 | 0 | 5.1 |
| polybench/fdtd-2d | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.31x | 3+0 | 0 | 7 | 0 | 7.3 |
| polybench/fdtd-apml | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.76x | 1+0 | 0 | 4 | 0 | 5.3 |
| polybench/floyd-warshall | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 3.8 |
| polybench/gemm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 9.80x | 1+0 | 0 | 2 | 0 | 4.0 |
| polybench/gemver | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 4.01x | 3+0 | 0 | 6 | 0 | 6.3 |
| polybench/gesummv | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 4.38x | 1+0 | 0 | 2 | 0 | 4.0 |
| polybench/gramschmidt | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 8.46x | 1+0 | 0 | 4 | 0 | 4.3 |
| polybench/jacobi-1d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 5.05x | 2+0 | 0 | 3 | 0 | 5.1 |
| polybench/jacobi-2d-imper | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.71x | 2+0 | 0 | 4 | 0 | 4.9 |
| polybench/lu | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.24x | 1+0 | 0 | 2 | 0 | 5.4 |
| polybench/ludcmp | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.22x | 2+0 | 0 | 4 | 0 | 4.1 |
| polybench/mvt | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 3.72x | 2+0 | 0 | 4 | 0 | 4.6 |
| polybench/reg_detect | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.36x | 3+0 | 0 | 8 | 0 | 5.8 |
| polybench/seidel-2d | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 4.0 |
| polybench/symm | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 1.39x | 1+0 | 0 | 3 | 0 | 7.4 |
| polybench/syr2k | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 7.95x | 1+0 | 0 | 3 | 0 | 3.9 |
| polybench/syrk | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 6.76x | 1+0 | 0 | 3 | 0 | 3.9 |
| polybench/trisolv | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 2.7 |
| rodinia-3.1/hotspot | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 12.9 |
| rodinia-3.1/pathfinder | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 12.6 |
