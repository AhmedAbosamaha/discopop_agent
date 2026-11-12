# Agent experiment run `e7_a2_judge_1`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 94 | 35 | 6 | 18 | 0 | 0 | 30 | 0 | 5 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/atax | e7 | none | 2 | LARGE | 0.66 |
| polybench/gemver | e7 | none | 1 | LARGE | 2.38 |
| polybench/gemver | e7 | none | 10 | LARGE | 2.39 |
| polybench/gemver | e7 | none | 2 | LARGE | 1.18 |
| polybench/gemver | e7 | none | 4 | LARGE | 1.68 |
| polybench/gemver | e7 | none | 5 | LARGE | 2.37 |
| polybench/gemver | e7 | none | 9 | LARGE | 3.53 |
| polybench/gesummv | e7 | none | 4 | LARGE | 4.00 |
| polybench/jacobi-1d-imper | e7 | none | 2 | EXTRALARGE | 5.16 |
| polybench/mvt | e7 | none | 1 | LARGE | 3.67 |
| polybench/mvt | e7 | none | 7 | LARGE | 1.34 |
| polybench/reg_detect | e7 | none | 1 | EXTRALARGE | 0.38 |
| polybench/reg_detect | e7 | none | 12 | EXTRALARGE | 0.05 |
| polybench/reg_detect | e7 | none | 13 | EXTRALARGE | 1.22 |
| polybench/reg_detect | e7 | none | 2 | EXTRALARGE | 0.05 |
| polybench/reg_detect | e7 | none | 3 | EXTRALARGE | 1.53 |
| polybench/reg_detect | e7 | none | 7 | EXTRALARGE | 0.05 |
| tsvc_c3/k17 | e7 | none | 2 | EXTRALARGE | 0.97 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | e7 | none | 12 | parallel-not-faster | 0.01x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 5 | parallel-not-faster | 0.01x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 8 | BROKEN | 6.32x | —+— | — | — | 0 | — |
| polybench/2mm | e7 | none | 3 | FASTER | 8.29x | —+— | — | — | 0 | — |
| polybench/2mm | e7 | none | 6 | FASTER | 10.00x | —+— | — | — | 0 | — |
| polybench/2mm | e7 | none | 7 | FASTER | 1.68x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 3 | FASTER | 9.60x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 5 | FASTER | 1.38x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 7 | FASTER | 2.47x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 10 | FASTER | 1.92x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 11 | FASTER | 1.94x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 13 | FASTER | 1.78x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 16 | BROKEN | 2.46x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 17 | BROKEN | 2.72x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 18 | FASTER | 1.49x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 2 | FASTER | 1.95x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 3 | BROKEN | 2.49x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 4 | FASTER | 1.92x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 5 | BROKEN | 2.43x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 7 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| polybench/atax | e7 | none | 1 | BROKEN | 1.09x | —+— | — | — | 0 | — |
| polybench/atax | e7 | none | 2 | parallel-speed-not-measurable | 0.66x | —+— | — | — | 0 | — |
| polybench/atax | e7 | none | 5 | BROKEN | 0.73x | —+— | — | — | 0 | — |
| polybench/bicg | e7 | none | 1 | BROKEN | 0.30x | —+— | — | — | 0 | — |
| polybench/bicg | e7 | none | 2 | BROKEN | 0.34x | —+— | — | — | 0 | — |
| polybench/correlation | e7 | none | 1 | FASTER | 5.74x | —+— | — | — | 0 | — |
| polybench/correlation | e7 | none | 3 | FASTER | 5.64x | —+— | — | — | 0 | — |
| polybench/correlation | e7 | none | 4 | FASTER | 5.57x | —+— | — | — | 0 | — |
| polybench/covariance | e7 | none | 1 | FASTER | 5.58x | —+— | — | — | 0 | — |
| polybench/covariance | e7 | none | 2 | FASTER | 5.70x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 10 | BROKEN | 0.24x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 11 | VERIFY_FAILED | 0.23x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 4 | VERIFY_FAILED | 0.24x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 5 | BROKEN | 0.15x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 8 | BROKEN | 0.15x | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 2 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 3 | BROKEN | 0.22x | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 4 | BROKEN | 0.04x | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 5 | BROKEN | 0.04x | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 8 | BROKEN | 0.20x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 10 | FASTER | 1.84x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 2 | FASTER | 4.18x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 5 | FASTER | 1.54x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 7 | FASTER | 3.68x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 8 | FASTER | 1.79x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 9 | BROKEN | 4.00x | —+— | — | — | 0 | — |
| polybench/floyd-warshall | e7 | none | 1 | parallel-not-faster | 0.34x | —+— | — | — | 0 | — |
| polybench/floyd-warshall | e7 | none | 3 | parallel-not-faster | 0.35x | —+— | — | — | 0 | — |
| polybench/floyd-warshall | e7 | none | 4 | FASTER | 7.32x | —+— | — | — | 0 | — |
| polybench/floyd-warshall | e7 | none | 5 | BROKEN | 5.49x | —+— | — | — | 0 | — |
| polybench/gemm | e7 | none | 2 | FASTER | 8.27x | —+— | — | — | 0 | — |
| polybench/gemm | e7 | none | 4 | FASTER | 7.01x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 1 | parallel-speed-not-measurable | 2.38x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 10 | parallel-speed-not-measurable | 2.39x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 2 | parallel-speed-not-measurable | 1.18x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 4 | parallel-speed-not-measurable | 1.68x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 5 | parallel-speed-not-measurable | 2.37x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 9 | parallel-speed-not-measurable | 3.53x | —+— | — | — | 0 | — |
| polybench/gesummv | e7 | none | 4 | parallel-speed-not-measurable | 4.00x | —+— | — | — | 0 | — |
| polybench/gramschmidt | e7 | none | 1 | FASTER | 7.81x | —+— | — | — | 0 | — |
| polybench/gramschmidt | e7 | none | 3 | FASTER | 7.72x | —+— | — | — | 0 | — |
| polybench/jacobi-1d-imper | e7 | none | 2 | parallel-speed-not-measurable | 5.16x | —+— | — | — | 0 | — |
| polybench/jacobi-2d-imper | e7 | none | 2 | FASTER | 1.60x | —+— | — | — | 0 | — |
| polybench/lu | e7 | none | 1 | parallel-not-faster | 0.24x | —+— | — | — | 0 | — |
| polybench/lu | e7 | none | 2 | parallel-not-faster | 0.24x | —+— | — | — | 0 | — |
| polybench/lu | e7 | none | 3 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| polybench/lu | e7 | none | 4 | BROKEN | 2.54x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 1 | FASTER | 5.53x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 7 | FASTER | 1.65x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 9 | BROKEN | 3.87x | —+— | — | — | 0 | — |
| polybench/mvt | e7 | none | 1 | parallel-speed-not-measurable | 3.67x | —+— | — | — | 0 | — |
| polybench/mvt | e7 | none | 7 | parallel-speed-not-measurable | 1.34x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 1 | parallel-speed-not-measurable | 0.38x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 12 | parallel-speed-not-measurable | 0.05x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 13 | parallel-speed-not-measurable | 1.22x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 2 | parallel-speed-not-measurable | 0.05x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 3 | parallel-speed-not-measurable | 1.53x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 7 | parallel-speed-not-measurable | 0.05x | —+— | — | — | 0 | — |
| polybench/seidel-2d | e7 | none | 1 | BROKEN | 10.52x | —+— | — | — | 0 | — |
| polybench/seidel-2d | e7 | none | 3 | BROKEN | 10.69x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 10 | BROKEN | 1.17x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 5 | BROKEN | 1.22x | —+— | — | — | 0 | — |
| polybench/syr2k | e7 | none | 3 | FASTER | 10.02x | —+— | — | — | 0 | — |
| polybench/syrk | e7 | none | 3 | FASTER | 8.07x | —+— | — | — | 0 | — |
| polybench/trisolv | e7 | none | 1 | BROKEN | 1.76x | —+— | — | — | 0 | — |
| polybench/trisolv | e7 | none | 3 | BROKEN | 0.84x | —+— | — | — | 0 | — |
| polybench/trisolv | e7 | none | 4 | BROKEN | 0.79x | —+— | — | — | 0 | — |
| polybench/trisolv | e7 | none | 5 | BROKEN | 2.09x | —+— | — | — | 0 | — |
| rodinia-3.1/pathfinder | e7 | none | 2 | BROKEN | 1.00x | —+— | — | — | 0 | — |
| tsvc_c3/k17 | e7 | none | 2 | parallel-speed-not-measurable | 0.97x | —+— | — | — | 0 | — |
| tsvc_c3/s152 | e7 | none | 1 | FASTER | 3.29x | —+— | — | — | 0 | — |
| tsvc_c3/s313 | e7 | none | 1 | FASTER | 4.59x | —+— | — | — | 0 | — |
| tsvc_c3/s481 | e7 | none | 1 | BROKEN | 4.16x | —+— | — | — | 0 | — |
| tsvc_c3/vpvtv | e7 | none | 2 | FASTER | 3.63x | —+— | — | — | 0 | — |
