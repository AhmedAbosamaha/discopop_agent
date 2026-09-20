# Agent experiment run `pilot4`

- status: finished (created 2026-09-18T21:37:44, finished 2026-09-18T23:52:21)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `8035099ef8a1ef0c3179495024b6aa4d951adfb9` (uncommitted diff sha256 `None`)
- harness: `f765bcecbb8127385bf05eefed9d0fda0e9230ae` on `agent-experiments`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | claude-haiku-4-5-20251001 | 8 | 4 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 186 | 22 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/trisolv | full | claude-haiku-4-5-20251001 | 1 | LARGE | 0.44 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | full | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 1.00x | 0+2 | 1 | 4 | 12 | 3173.8 |
| polybench/2mm | full | claude-haiku-4-5-20251001 | 1 | FASTER | 9.47x | 0+2 | 1 | 6 | 1 | 137.5 |
| polybench/floyd-warshall | full | claude-haiku-4-5-20251001 | 1 | FASTER | 2.92x | 0+1 | 1 | 3 | 2 | 233.6 |
| polybench/jacobi-2d-imper | full | claude-haiku-4-5-20251001 | 1 | FASTER | 5.85x | 0+2 | 1 | 5 | 1 | 129.2 |
| polybench/lu | full | claude-haiku-4-5-20251001 | 1 | FASTER | 2.85x | 0+2 | 1 | 0 | 1 | 75.8 |
| polybench/seidel-2d | full | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 3 | 3 | 299.0 |
| polybench/trisolv | full | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.44x | 0+1 | 1 | 2 | 1 | 88.0 |
| rodinia-3.1/hotspot | full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.08x | 1+0 | 0 | 6 | 1 | 1120.3 |
