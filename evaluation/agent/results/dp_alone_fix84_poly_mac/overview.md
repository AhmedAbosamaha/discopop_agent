# Agent experiment run `dp_alone_fix84_poly_mac`

- status: finished (created 2026-09-19T20:42:56, finished 2026-09-19T23:15:57)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `b5353524c21105d9c4162539b11463e54afecbb3` (uncommitted diff sha256 `None`)
- harness: `b95b3bcdcc1f1299a2def9106b7a6314438c736b` on `agent-experiments`
- verify size `per_kernel`, threads [4], repeats 3

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 13 | 7 | 1 | 3 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/gemver | discopop_gate | none | 1 | LARGE | 2.67 |
| polybench/mvt | discopop_gate | none | 1 | LARGE | 2.47 |
| polybench/reg_detect | discopop_gate | none | 1 | EXTRALARGE | 1.28 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | discopop_gate | none | 1 | FASTER | 3.15x | 2+0 | 0 | 6 | 0 | 47.9 |
| polybench/bicg | discopop_gate | none | 1 | no-change | 1.29x | 0+0 | 0 | 2 | 0 | 47.9 |
| polybench/covariance | discopop_gate | none | 1 | FASTER | 2.15x | 1+0 | 0 | 2 | 0 | 34.0 |
| polybench/fdtd-2d | discopop_gate | none | 1 | parallel-not-faster | 1.07x | 3+0 | 0 | 4 | 0 | 54.3 |
| polybench/floyd-warshall | discopop_gate | none | 1 | no-change | 1.10x | 0+0 | 0 | 3 | 0 | 53.6 |
| polybench/gemm | discopop_gate | none | 1 | FASTER | 3.26x | 1+0 | 0 | 3 | 0 | 28.6 |
| polybench/gemver | discopop_gate | none | 1 | parallel-speed-not-measurable | 2.67x | 3+0 | 0 | 4 | 0 | 40.1 |
| polybench/gramschmidt | discopop_gate | none | 1 | FASTER | 2.75x | 1+0 | 0 | 4 | 0 | 33.5 |
| polybench/lu | discopop_gate | none | 1 | FASTER | 3.39x | 1+0 | 0 | 3 | 0 | 25.9 |
| polybench/mvt | discopop_gate | none | 1 | parallel-speed-not-measurable | 2.47x | 2+0 | 0 | 4 | 0 | 34.2 |
| polybench/reg_detect | discopop_gate | none | 1 | parallel-speed-not-measurable | 1.28x | 3+0 | 0 | 9 | 0 | 143.5 |
| polybench/syr2k | discopop_gate | none | 1 | FASTER | 8.49x | 1+0 | 0 | 3 | 0 | 83.9 |
| polybench/syrk | discopop_gate | none | 1 | FASTER | 2.96x | 1+0 | 0 | 2 | 0 | 57.2 |
