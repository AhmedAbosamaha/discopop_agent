# Agent experiment run `e7_pilot_a2_2`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 10 | 5 | 1 | 1 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_c3/k17 | e7 | none | 2 | EXTRALARGE | 0.99 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/adi | e7 | none | 2 | FASTER | 1.95x | —+— | — | — | 0 | — |
| polybench/doitgen | e7 | none | 1 | BROKEN | 1.13x | —+— | — | — | 0 | — |
| polybench/floyd-warshall | e7 | none | 1 | parallel-not-faster | 0.34x | —+— | — | — | 0 | — |
| polybench/jacobi-2d-imper | e7 | none | 1 | FASTER | 4.35x | —+— | — | — | 0 | — |
| polybench/syrk | e7 | none | 1 | FASTER | 10.29x | —+— | — | — | 0 | — |
| polybench/trisolv | e7 | none | 1 | BROKEN | 2.24x | —+— | — | — | 0 | — |
| rodinia-3.1/pathfinder | e7 | none | 1 | BROKEN | 0.99x | —+— | — | — | 0 | — |
| tsvc_c3/k17 | e7 | none | 2 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 0 | — |
| tsvc_c3/s171 | e7 | none | 1 | FASTER | 3.33x | —+— | — | — | 0 | — |
| tsvc_c3/vas | e7 | none | 2 | FASTER | 3.65x | —+— | — | — | 0 | — |
