# Agent experiment run `t0_11_classes_c`

- status: finished (created 2026-09-21T00:18:20, finished 2026-09-21T03:22:49)
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
| polybench/atax | discopop_capability | none | 1 | LARGE | 0.26 |
| polybench/gemver | discopop_capability | none | 1 | LARGE | 2.98 |
| polybench/gesummv | discopop_capability | none | 1 | LARGE | 3.59 |
| polybench/jacobi-1d-imper | discopop_capability | none | 1 | EXTRALARGE | 3.15 |
| polybench/mvt | discopop_capability | none | 1 | LARGE | 3.60 |
| polybench/reg_detect | discopop_capability | none | 1 | EXTRALARGE | 0.19 |
| rodinia-3.1/pathfinder | discopop_capability | none | 1 | EXTRALARGE | 3.23 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 652.5 |
| npb/is | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 15.3 |
| polybench/2mm | discopop_capability | none | 1 | FASTER | 9.76x | 2+0 | 0 | 6 | 0 | 5.6 |
| polybench/3mm | discopop_capability | none | 1 | FASTER | 10.09x | 3+0 | 0 | 9 | 0 | 7.0 |
| polybench/atax | discopop_capability | none | 1 | parallel-speed-not-measurable | 0.26x | 1+0 | 0 | 3 | 0 | 6.1 |
| polybench/bicg | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.3 |
| polybench/correlation | discopop_capability | none | 1 | FASTER | 5.48x | 1+0 | 0 | 3 | 0 | 5.1 |
| polybench/covariance | discopop_capability | none | 1 | FASTER | 5.61x | 1+0 | 0 | 3 | 0 | 6.0 |
| polybench/doitgen | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 4.8 |
| polybench/dynprog | discopop_capability | none | 1 | parallel-not-faster | 0.98x | 1+0 | 0 | 6 | 0 | 5.0 |
| polybench/fdtd-2d | discopop_capability | none | 1 | FASTER | 4.48x | 3+0 | 0 | 7 | 0 | 7.7 |
| polybench/fdtd-apml | discopop_capability | none | 1 | FASTER | 3.77x | 1+0 | 0 | 4 | 0 | 5.4 |
| polybench/floyd-warshall | discopop_capability | none | 1 | no-change | 1.02x | 0+0 | 0 | 3 | 0 | 3.8 |
| polybench/gemm | discopop_capability | none | 1 | FASTER | 9.09x | 1+0 | 0 | 2 | 0 | 4.1 |
| polybench/gemver | discopop_capability | none | 1 | parallel-speed-not-measurable | 2.98x | 3+0 | 0 | 6 | 0 | 6.2 |
| polybench/gesummv | discopop_capability | none | 1 | parallel-speed-not-measurable | 3.59x | 1+0 | 0 | 2 | 0 | 4.0 |
| polybench/gramschmidt | discopop_capability | none | 1 | FASTER | 8.63x | 1+0 | 0 | 4 | 0 | 4.5 |
| polybench/jacobi-1d-imper | discopop_capability | none | 1 | parallel-speed-not-measurable | 3.15x | 2+0 | 0 | 3 | 0 | 5.3 |
| polybench/jacobi-2d-imper | discopop_capability | none | 1 | FASTER | 4.54x | 2+0 | 0 | 5 | 0 | 5.8 |
| polybench/lu | discopop_capability | none | 1 | parallel-not-faster | 0.22x | 1+0 | 0 | 2 | 0 | 7.0 |
| polybench/ludcmp | discopop_capability | none | 1 | parallel-not-faster | 0.15x | 2+0 | 0 | 3 | 0 | 10.9 |
| polybench/mvt | discopop_capability | none | 1 | parallel-speed-not-measurable | 3.60x | 2+0 | 0 | 4 | 0 | 4.8 |
| polybench/reg_detect | discopop_capability | none | 1 | parallel-speed-not-measurable | 0.19x | 3+0 | 0 | 9 | 0 | 7.1 |
| polybench/seidel-2d | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 5.9 |
| polybench/symm | discopop_capability | none | 1 | FASTER | 1.37x | 1+0 | 0 | 1 | 0 | 15.3 |
| polybench/syr2k | discopop_capability | none | 1 | FASTER | 10.04x | 1+0 | 0 | 3 | 0 | 4.1 |
| polybench/syrk | discopop_capability | none | 1 | FASTER | 7.88x | 1+0 | 0 | 2 | 0 | 4.0 |
| polybench/trisolv | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.4 |
| rodinia-3.1/hotspot | discopop_capability | none | 1 | no-change | 1.02x | 0+0 | 0 | 6 | 0 | 481.8 |
| rodinia-3.1/pathfinder | discopop_capability | none | 1 | parallel-speed-not-measurable | 3.23x | 1+0 | 0 | 4 | 0 | 22.3 |
| tsvc/s000 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s112 | discopop_capability | none | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 2.4 |
| tsvc/s121 | discopop_capability | none | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 2.5 |
| tsvc/s1213 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc/s127 | discopop_capability | none | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 2.4 |
| tsvc/s211 | discopop_capability | none | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc/s212 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 2.4 |
| tsvc/s241 | discopop_capability | none | 1 | no-change | 1.02x | 0+0 | 0 | 1 | 0 | 2.5 |
| tsvc/s243 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 2.5 |
| tsvc/s244 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 2.4 |
| tsvc/s252 | discopop_capability | none | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 2.5 |
| tsvc/s254 | discopop_capability | none | 1 | no-change | 1.03x | 0+0 | 0 | 2 | 0 | 2.9 |
| tsvc/s255 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s281 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s291 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s292 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 2.4 |
| tsvc/s293 | discopop_capability | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| tsvc/s3112 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.1 |
| tsvc/s313 | discopop_capability | none | 1 | FASTER | 6.88x | 1+0 | 0 | 2 | 0 | 4.0 |
| tsvc/s321 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc/s322 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.0 |
| tsvc/s323 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 2.4 |
| tsvc/s331 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.3 |
| tsvc/s341 | discopop_capability | none | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 2.9 |
| tsvc/vpvtv | discopop_capability | none | 1 | FASTER | 4.34x | 1+0 | 0 | 1 | 0 | 3.6 |
