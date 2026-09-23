# Agent experiment run `dp_alone_look_mac`

- status: finished (created 2026-09-19T19:31:16, finished 2026-09-19T23:43:15)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `6eefbdf04627f666d34f4b17c560e432e17db232` (uncommitted diff sha256 `None`)
- harness: `13af1efe815fbfbf2d20e9be8bb90d20339ad603` on `agent-experiments`
- verify size `SMALL`, threads [4], repeats 1

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 31 | 7 | 15 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 1 | 32 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | discopop_gate | none | 1 | no-change | 0.95x | 0+0 | 0 | 4 | 0 | 692.2 |
| npb/is | discopop_gate | none | 1 | no-change | 1.33x | 0+0 | 0 | 1 | 0 | 48.6 |
| polybench/2mm | discopop_gate | none | 1 | FASTER | 1.49x | 2+0 | 0 | 6 | 0 | 36.0 |
| polybench/3mm | discopop_gate | none | 1 | FASTER | 1.97x | 3+0 | 0 | 9 | 0 | 42.2 |
| polybench/adi | discopop_gate | none | 1 | PROFILE_ERROR | — | —+— | — | — | 0 | — |
| polybench/atax | discopop_gate | none | 1 | no-change | 1.30x | 0+0 | 0 | 3 | 0 | 24.0 |
| polybench/bicg | discopop_gate | none | 1 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 23.2 |
| polybench/correlation | discopop_gate | none | 1 | FASTER | 1.93x | 1+0 | 0 | 3 | 0 | 26.6 |
| polybench/covariance | discopop_gate | none | 1 | FASTER | 2.18x | 1+0 | 0 | 3 | 0 | 32.2 |
| polybench/doitgen | discopop_gate | none | 1 | parallel-not-faster | 0.36x | 1+0 | 0 | 5 | 0 | 43.1 |
| polybench/dynprog | discopop_gate | none | 1 | parallel-not-faster | 0.42x | 1+0 | 0 | 6 | 0 | 34.0 |
| polybench/fdtd-2d | discopop_gate | none | 1 | parallel-not-faster | 0.44x | 3+0 | 0 | 3 | 0 | 39.6 |
| polybench/fdtd-apml | discopop_gate | none | 1 | FASTER | 1.53x | 1+0 | 0 | 4 | 0 | 30.7 |
| polybench/floyd-warshall | discopop_gate | none | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 16.9 |
| polybench/gemm | discopop_gate | none | 1 | parallel-not-faster | 1.08x | 1+0 | 0 | 3 | 0 | 29.1 |
| polybench/gemver | discopop_gate | none | 1 | parallel-not-faster | 0.29x | 2+0 | 0 | 4 | 0 | 35.4 |
| polybench/gesummv | discopop_gate | none | 1 | parallel-not-faster | 0.41x | 1+0 | 0 | 2 | 0 | 28.7 |
| polybench/gramschmidt | discopop_gate | none | 1 | FASTER | 1.24x | 1+0 | 0 | 2 | 0 | 24.1 |
| polybench/jacobi-1d-imper | discopop_gate | none | 1 | parallel-not-faster | 0.00x | 2+0 | 0 | 2 | 0 | 32.7 |
| polybench/jacobi-2d-imper | discopop_gate | none | 1 | parallel-not-faster | 1.09x | 2+0 | 0 | 4 | 0 | 34.9 |
| polybench/lu | discopop_gate | none | 1 | parallel-not-faster | 0.26x | 1+0 | 0 | 1 | 0 | 22.1 |
| polybench/ludcmp | discopop_gate | none | 1 | parallel-not-faster | 0.04x | 2+0 | 0 | 2 | 0 | 33.0 |
| polybench/mvt | discopop_gate | none | 1 | parallel-not-faster | 0.33x | 2+0 | 0 | 4 | 0 | 33.6 |
| polybench/reg_detect | discopop_gate | none | 1 | parallel-not-faster | 0.03x | 3+0 | 0 | 9 | 0 | 40.5 |
| polybench/seidel-2d | discopop_gate | none | 1 | no-change | 0.99x | 0+0 | 0 | 3 | 0 | 30.1 |
| polybench/symm | discopop_gate | none | 1 | parallel-not-faster | 0.19x | 1+0 | 0 | 1 | 0 | 46.9 |
| polybench/syr2k | discopop_gate | none | 1 | parallel-not-faster | 0.75x | 1+0 | 0 | 3 | 0 | 28.9 |
| polybench/syrk | discopop_gate | none | 1 | parallel-not-faster | 0.56x | 1+0 | 0 | 3 | 0 | 30.3 |
| polybench/trisolv | discopop_gate | none | 1 | no-change | 0.86x | 0+0 | 0 | 2 | 0 | 18.9 |
| rodinia-3.1/hotspot | discopop_gate | none | 1 | FASTER | 2.01x | 1+0 | 0 | 6 | 0 | 86.8 |
| rodinia-3.1/pathfinder | discopop_gate | none | 1 | no-change | 0.97x | 0+0 | 0 | 3 | 0 | 26.4 |
