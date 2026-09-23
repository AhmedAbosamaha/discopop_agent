# Agent experiment run `t0_11_classes_b`

- status: finished (created 2026-09-20T21:15:39, finished 2026-09-21T00:18:19)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `d9ae10c83f0077137e20b11e7806d25e9175f306` (uncommitted diff sha256 `None`)
- harness: `d9ae10c83f0077137e20b11e7806d25e9175f306` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | none | 55 | 14 | 3 | 7 | 0 | 26 | 0 | 0 | 0 | 0 | 0 | 5 | 4 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/atax | discopop_capability | none | 1 | LARGE | 0.30 |
| polybench/gemver | discopop_capability | none | 1 | LARGE | 3.35 |
| polybench/gesummv | discopop_capability | none | 1 | LARGE | 3.41 |
| polybench/jacobi-1d-imper | discopop_capability | none | 1 | EXTRALARGE | 2.71 |
| polybench/mvt | discopop_capability | none | 1 | LARGE | 4.21 |
| polybench/reg_detect | discopop_capability | none | 1 | EXTRALARGE | 0.25 |
| rodinia-3.1/pathfinder | discopop_capability | none | 1 | EXTRALARGE | 4.06 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 650.7 |
| npb/is | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 14.6 |
| polybench/2mm | discopop_capability | none | 1 | FASTER | 10.77x | 2+0 | 0 | 6 | 0 | 5.2 |
| polybench/3mm | discopop_capability | none | 1 | FASTER | 9.89x | 3+0 | 0 | 9 | 0 | 6.5 |
| polybench/atax | discopop_capability | none | 1 | parallel-speed-not-measurable | 0.30x | 1+0 | 0 | 1 | 0 | 4.3 |
| polybench/bicg | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.1 |
| polybench/correlation | discopop_capability | none | 1 | FASTER | 5.79x | 1+0 | 0 | 2 | 0 | 4.8 |
| polybench/covariance | discopop_capability | none | 1 | FASTER | 5.82x | 1+0 | 0 | 3 | 0 | 6.0 |
| polybench/doitgen | discopop_capability | none | 1 | no-change | 1.02x | 0+0 | 0 | 4 | 0 | 5.8 |
| polybench/dynprog | discopop_capability | none | 1 | parallel-not-faster | 0.97x | 1+0 | 0 | 6 | 0 | 4.6 |
| polybench/fdtd-2d | discopop_capability | none | 1 | FASTER | 5.65x | 3+0 | 0 | 7 | 0 | 7.0 |
| polybench/fdtd-apml | discopop_capability | none | 1 | FASTER | 4.33x | 1+0 | 0 | 4 | 0 | 5.0 |
| polybench/floyd-warshall | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 3.6 |
| polybench/gemm | discopop_capability | none | 1 | FASTER | 10.41x | 1+0 | 0 | 3 | 0 | 4.0 |
| polybench/gemver | discopop_capability | none | 1 | parallel-speed-not-measurable | 3.35x | 3+0 | 0 | 6 | 0 | 6.2 |
| polybench/gesummv | discopop_capability | none | 1 | parallel-speed-not-measurable | 3.41x | 1+0 | 0 | 2 | 0 | 3.9 |
| polybench/gramschmidt | discopop_capability | none | 1 | FASTER | 8.56x | 1+0 | 0 | 4 | 0 | 4.2 |
| polybench/jacobi-1d-imper | discopop_capability | none | 1 | parallel-speed-not-measurable | 2.71x | 2+0 | 0 | 3 | 0 | 5.3 |
| polybench/jacobi-2d-imper | discopop_capability | none | 1 | FASTER | 6.04x | 2+0 | 0 | 5 | 0 | 5.9 |
| polybench/lu | discopop_capability | none | 1 | parallel-not-faster | 0.21x | 1+0 | 0 | 0 | 0 | 5.5 |
| polybench/ludcmp | discopop_capability | none | 1 | parallel-not-faster | 0.15x | 2+0 | 0 | 3 | 0 | 10.4 |
| polybench/mvt | discopop_capability | none | 1 | parallel-speed-not-measurable | 4.21x | 2+0 | 0 | 4 | 0 | 4.5 |
| polybench/reg_detect | discopop_capability | none | 1 | parallel-speed-not-measurable | 0.25x | 3+0 | 0 | 9 | 0 | 7.2 |
| polybench/seidel-2d | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 3 | 0 | 4.2 |
| polybench/symm | discopop_capability | none | 1 | FASTER | 1.35x | 1+0 | 0 | 1 | 0 | 15.9 |
| polybench/syr2k | discopop_capability | none | 1 | FASTER | 9.26x | 1+0 | 0 | 3 | 0 | 3.8 |
| polybench/syrk | discopop_capability | none | 1 | FASTER | 6.35x | 1+0 | 0 | 2 | 0 | 4.0 |
| polybench/trisolv | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 3.5 |
| rodinia-3.1/hotspot | discopop_capability | none | 1 | no-change | 1.12x | 0+0 | 0 | 6 | 0 | 480.7 |
| rodinia-3.1/pathfinder | discopop_capability | none | 1 | parallel-speed-not-measurable | 4.06x | 1+0 | 0 | 4 | 0 | 27.8 |
| tsvc/s000 | discopop_capability | none | 1 | FASTER | 3.83x | 1+0 | 0 | 2 | 0 | 4.2 |
| tsvc/s112 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 2.3 |
| tsvc/s121 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 2.2 |
| tsvc/s1213 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc/s127 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 2.6 |
| tsvc/s211 | discopop_capability | none | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 1.9 |
| tsvc/s212 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s241 | discopop_capability | none | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 2.2 |
| tsvc/s243 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc/s244 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 2.4 |
| tsvc/s252 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s254 | discopop_capability | none | 1 | no-change | 1.03x | 0+0 | 0 | 2 | 0 | 2.6 |
| tsvc/s255 | discopop_capability | none | 1 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 2.6 |
| tsvc/s281 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc/s291 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 2.3 |
| tsvc/s292 | discopop_capability | none | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 2.3 |
| tsvc/s293 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s3112 | discopop_capability | none | 1 | no-change | 0.98x | 0+0 | 0 | 2 | 0 | 3.0 |
| tsvc/s313 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s321 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc/s322 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s323 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 2.4 |
| tsvc/s331 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.3 |
| tsvc/s341 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.4 |
| tsvc/vpvtv | discopop_capability | none | 1 | FASTER | 4.11x | 1+0 | 0 | 1 | 0 | 3.8 |
