# Agent experiment run `e10_dp_alone`

- status: finished (created 2026-09-20T00:05:18, finished 2026-09-20T00:49:02)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `58d959f2e7dd2e86f6cb2931f9767a68df22307e` (uncommitted diff sha256 `None`)
- harness: `1514ceb83d2345ac3cc5e4313e1653e45bd31015` on `agent-experiments`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 15 | 6 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | discopop_gate | none | 1 | FASTER | 10.09x | 2+0 | 0 | 6 | 0 | 5.6 |
| polybench/2mm | discopop_gate | none | 2 | FASTER | 10.31x | 2+0 | 0 | 6 | 0 | 5.9 |
| polybench/2mm | discopop_gate | none | 3 | FASTER | 10.50x | 2+0 | 0 | 6 | 0 | 5.9 |
| polybench/floyd-warshall | discopop_gate | none | 1 | no-change | 1.01x | 0+0 | 0 | 3 | 0 | 4.4 |
| polybench/floyd-warshall | discopop_gate | none | 2 | no-change | 1.05x | 0+0 | 0 | 3 | 0 | 4.5 |
| polybench/floyd-warshall | discopop_gate | none | 3 | no-change | 1.03x | 0+0 | 0 | 3 | 0 | 4.3 |
| polybench/jacobi-2d-imper | discopop_gate | none | 1 | FASTER | 6.45x | 2+0 | 0 | 5 | 0 | 6.1 |
| polybench/jacobi-2d-imper | discopop_gate | none | 2 | FASTER | 5.89x | 2+0 | 0 | 5 | 0 | 6.2 |
| polybench/jacobi-2d-imper | discopop_gate | none | 3 | FASTER | 5.00x | 2+0 | 0 | 5 | 0 | 6.1 |
| polybench/seidel-2d | discopop_gate | none | 1 | no-change | 1.02x | 0+0 | 0 | 3 | 0 | 6.7 |
| polybench/seidel-2d | discopop_gate | none | 2 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 4.2 |
| polybench/seidel-2d | discopop_gate | none | 3 | no-change | 0.99x | 0+0 | 0 | 3 | 0 | 5.9 |
| rodinia-3.1/hotspot | discopop_gate | none | 1 | no-change | 1.01x | 0+0 | 0 | 6 | 0 | 479.0 |
| rodinia-3.1/hotspot | discopop_gate | none | 2 | no-change | 0.97x | 0+0 | 0 | 6 | 0 | 485.4 |
| rodinia-3.1/hotspot | discopop_gate | none | 3 | no-change | 0.99x | 0+0 | 0 | 6 | 0 | 480.4 |
