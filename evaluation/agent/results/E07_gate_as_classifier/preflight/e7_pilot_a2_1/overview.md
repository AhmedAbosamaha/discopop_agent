# Agent experiment run `e7_pilot_a2_1`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 10 | 2 | 1 | 4 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/gemver | e7 | none | 1 | LARGE | 2.51 |
| polybench/jacobi-1d-imper | e7 | none | 1 | EXTRALARGE | 5.01 |
| polybench/mvt | e7 | none | 1 | LARGE | 4.01 |
| tsvc_c3/k42 | e7 | none | 2 | EXTRALARGE | 0.97 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | e7 | none | 1 | BROKEN | 29.48x | —+— | — | — | 0 | — |
| polybench/bicg | e7 | none | 1 | BROKEN | 0.30x | —+— | — | — | 0 | — |
| polybench/dynprog | e7 | none | 1 | BROKEN | 0.17x | —+— | — | — | 0 | — |
| polybench/gemver | e7 | none | 1 | parallel-speed-not-measurable | 2.51x | —+— | — | — | 0 | — |
| polybench/jacobi-1d-imper | e7 | none | 1 | parallel-speed-not-measurable | 5.01x | —+— | — | — | 0 | — |
| polybench/lu | e7 | none | 1 | parallel-not-faster | 0.26x | —+— | — | — | 0 | — |
| polybench/mvt | e7 | none | 1 | parallel-speed-not-measurable | 4.01x | —+— | — | — | 0 | — |
| tsvc_c3/k42 | e7 | none | 2 | parallel-speed-not-measurable | 0.97x | —+— | — | — | 0 | — |
| tsvc_c3/s000 | e7 | none | 1 | FASTER | 3.39x | —+— | — | — | 0 | — |
| tsvc_c3/s277 | e7 | none | 1 | FASTER | 4.85x | —+— | — | — | 0 | — |
