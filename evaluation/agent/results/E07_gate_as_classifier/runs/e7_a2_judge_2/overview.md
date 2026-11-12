# Agent experiment run `e7_a2_judge_2`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 93 | 37 | 8 | 19 | 0 | 0 | 28 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/gemver | e7 | none | 3 | LARGE | 3.92 |
| polybench/gemver | e7 | none | 6 | LARGE | 3.85 |
| polybench/gemver | e7 | none | 8 | LARGE | 1.58 |
| polybench/gesummv | e7 | none | 2 | LARGE | 3.99 |
| polybench/gesummv | e7 | none | 3 | LARGE | 4.10 |
| polybench/jacobi-1d-imper | e7 | none | 1 | EXTRALARGE | 1.67 |
| polybench/jacobi-1d-imper | e7 | none | 3 | EXTRALARGE | 0.58 |
| polybench/jacobi-1d-imper | e7 | none | 5 | EXTRALARGE | 0.74 |
| polybench/mvt | e7 | none | 2 | LARGE | 2.04 |
| polybench/mvt | e7 | none | 3 | LARGE | 2.09 |
| polybench/mvt | e7 | none | 4 | LARGE | 1.16 |
| polybench/mvt | e7 | none | 5 | LARGE | 2.10 |
| polybench/reg_detect | e7 | none | 10 | EXTRALARGE | 1.85 |
| polybench/reg_detect | e7 | none | 11 | EXTRALARGE | 0.38 |
| polybench/reg_detect | e7 | none | 4 | EXTRALARGE | 0.89 |
| polybench/reg_detect | e7 | none | 5 | EXTRALARGE | 0.56 |
| polybench/reg_detect | e7 | none | 6 | EXTRALARGE | 0.46 |
| polybench/reg_detect | e7 | none | 9 | EXTRALARGE | 1.67 |
| tsvc_c3/k42 | e7 | none | 2 | EXTRALARGE | 0.99 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | e7 | none | 1 | BROKEN | 29.38x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 10 | BROKEN | 7.27x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 11 | BROKEN | 7.21x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 13 | parallel-not-faster | 0.02x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 2 | BROKEN | 28.31x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 3 | BROKEN | 29.37x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 4 | parallel-not-faster | 0.02x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 7 | parallel-not-faster | 0.01x | —+— | — | — | 0 | — |
| burkardt/md | e7 | none | 9 | parallel-not-faster | 0.01x | —+— | — | — | 0 | — |
| polybench/2mm | e7 | none | 1 | FASTER | 1.78x | —+— | — | — | 0 | — |
| polybench/2mm | e7 | none | 2 | FASTER | 1.70x | —+— | — | — | 0 | — |
| polybench/2mm | e7 | none | 5 | FASTER | 8.68x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 1 | FASTER | 1.35x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 10 | FASTER | 2.54x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 4 | FASTER | 10.85x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 6 | FASTER | 9.54x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 8 | FASTER | 1.45x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 9 | FASTER | 2.35x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 12 | FASTER | 1.88x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 14 | BROKEN | 2.21x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 15 | FASTER | 1.61x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 19 | FASTER | 1.51x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 20 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 6 | FASTER | 1.96x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 8 | FASTER | 1.86x | —+— | — | — | 0 | — |
| polybench/adi | e7 | none | 9 | FASTER | 1.98x | —+— | — | — | 0 | — |
| polybench/atax | e7 | none | 3 | BROKEN | 0.78x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 1 | BROKEN | 0.24x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 12 | FASTER | 1.56x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 3 | FASTER | 1.70x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 6 | BROKEN | 0.26x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 7 | BROKEN | 0.15x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 9 | BROKEN | 0.24x | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 1 | BROKEN | 0.20x | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 7 | BROKEN | 0.24x | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 9 | parallel-not-faster | 0.98x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 1 | parallel-not-faster | 0.99x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 3 | parallel-not-faster | 0.80x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 4 | FASTER | 4.18x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 6 | parallel-not-faster | 0.99x | —+— | — | — | 0 | — |
| polybench/fdtd-apml | e7 | none | 1 | FASTER | 3.19x | —+— | — | — | 0 | — |
| polybench/fdtd-apml | e7 | none | 2 | FASTER | 3.97x | —+— | — | — | 0 | — |
| polybench/fdtd-apml | e7 | none | 3 | FASTER | 3.41x | —+— | — | — | 0 | — |
| polybench/floyd-warshall | e7 | none | 6 | BROKEN | 4.69x | —+— | — | — | 0 | — |
| polybench/gemm | e7 | none | 3 | FASTER | 9.36x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 3 | parallel-speed-not-measurable | 3.92x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 6 | parallel-speed-not-measurable | 3.85x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 8 | parallel-speed-not-measurable | 1.58x | —+— | — | — | 0 | — |
| polybench/gesummv | e7 | none | 2 | parallel-speed-not-measurable | 3.99x | —+— | — | — | 0 | — |
| polybench/gesummv | e7 | none | 3 | parallel-speed-not-measurable | 4.10x | —+— | — | — | 0 | — |
| polybench/gramschmidt | e7 | none | 2 | BROKEN | 3.21x | —+— | — | — | 0 | — |
| polybench/gramschmidt | e7 | none | 4 | BROKEN | 2.62x | —+— | — | — | 0 | — |
| polybench/gramschmidt | e7 | none | 5 | FASTER | 7.58x | —+— | — | — | 0 | — |
| polybench/gramschmidt | e7 | none | 7 | BROKEN | 2.66x | —+— | — | — | 0 | — |
| polybench/jacobi-1d-imper | e7 | none | 1 | parallel-speed-not-measurable | 1.67x | —+— | — | — | 0 | — |
| polybench/jacobi-1d-imper | e7 | none | 3 | parallel-speed-not-measurable | 0.58x | —+— | — | — | 0 | — |
| polybench/jacobi-1d-imper | e7 | none | 5 | parallel-speed-not-measurable | 0.74x | —+— | — | — | 0 | — |
| polybench/jacobi-1d-imper | e7 | none | 6 | BROKEN | 0.58x | —+— | — | — | 0 | — |
| polybench/jacobi-2d-imper | e7 | none | 1 | FASTER | 4.70x | —+— | — | — | 0 | — |
| polybench/jacobi-2d-imper | e7 | none | 3 | BROKEN | 2.92x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 2 | FASTER | 1.72x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 3 | FASTER | 4.97x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 4 | BROKEN | 5.48x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 6 | BROKEN | 5.31x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 8 | BROKEN | 5.04x | —+— | — | — | 0 | — |
| polybench/mvt | e7 | none | 2 | parallel-speed-not-measurable | 2.04x | —+— | — | — | 0 | — |
| polybench/mvt | e7 | none | 3 | parallel-speed-not-measurable | 2.09x | —+— | — | — | 0 | — |
| polybench/mvt | e7 | none | 4 | parallel-speed-not-measurable | 1.16x | —+— | — | — | 0 | — |
| polybench/mvt | e7 | none | 5 | parallel-speed-not-measurable | 2.10x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 10 | parallel-speed-not-measurable | 1.85x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 11 | parallel-speed-not-measurable | 0.38x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 4 | parallel-speed-not-measurable | 0.89x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 5 | parallel-speed-not-measurable | 0.56x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 6 | parallel-speed-not-measurable | 0.46x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 9 | parallel-speed-not-measurable | 1.67x | —+— | — | — | 0 | — |
| polybench/seidel-2d | e7 | none | 4 | BROKEN | 4.55x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 1 | FASTER | 1.50x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 2 | FASTER | 1.50x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 3 | BROKEN | 1.22x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 4 | BROKEN | 1.20x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 6 | BROKEN | 1.15x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 8 | BROKEN | 1.24x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 9 | FASTER | 1.50x | —+— | — | — | 0 | — |
| polybench/syr2k | e7 | none | 1 | FASTER | 9.72x | —+— | — | — | 0 | — |
| polybench/syr2k | e7 | none | 4 | FASTER | 11.01x | —+— | — | — | 0 | — |
| polybench/syrk | e7 | none | 1 | FASTER | 9.95x | —+— | — | — | 0 | — |
| rodinia-3.1/pathfinder | e7 | none | 1 | BROKEN | 0.99x | —+— | — | — | 0 | — |
| tsvc_c3/k42 | e7 | none | 2 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 0 | — |
| tsvc_c3/s000 | e7 | none | 1 | FASTER | 3.42x | —+— | — | — | 0 | — |
| tsvc_c3/s171 | e7 | none | 1 | FASTER | 3.70x | —+— | — | — | 0 | — |
| tsvc_c3/s277 | e7 | none | 1 | FASTER | 4.76x | —+— | — | — | 0 | — |
| tsvc_c3/s481 | e7 | none | 3 | FASTER | 4.00x | —+— | — | — | 0 | — |
| tsvc_c3/vas | e7 | none | 2 | FASTER | 3.65x | —+— | — | — | 0 | — |
