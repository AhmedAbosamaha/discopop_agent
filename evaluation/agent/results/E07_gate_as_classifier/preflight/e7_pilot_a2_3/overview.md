# Agent experiment run `e7_pilot_a2_3`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 10 | 7 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/gesummv | e7 | none | 2 | LARGE | 5.14 |
| polybench/reg_detect | e7 | none | 1 | EXTRALARGE | 0.38 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/correlation | e7 | none | 1 | FASTER | 5.43x | —+— | — | — | 0 | — |
| polybench/covariance | e7 | none | 1 | FASTER | 6.84x | —+— | — | — | 0 | — |
| polybench/fdtd-2d | e7 | none | 1 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| polybench/gemm | e7 | none | 2 | FASTER | 9.33x | —+— | — | — | 0 | — |
| polybench/gesummv | e7 | none | 2 | parallel-speed-not-measurable | 5.14x | —+— | — | — | 0 | — |
| polybench/ludcmp | e7 | none | 1 | FASTER | 6.38x | —+— | — | — | 0 | — |
| polybench/reg_detect | e7 | none | 1 | parallel-speed-not-measurable | 0.38x | —+— | — | — | 0 | — |
| polybench/symm | e7 | none | 1 | FASTER | 1.35x | —+— | — | — | 0 | — |
| polybench/syr2k | e7 | none | 1 | FASTER | 8.06x | —+— | — | — | 0 | — |
| tsvc_c3/s313 | e7 | none | 1 | FASTER | 4.38x | —+— | — | — | 0 | — |
