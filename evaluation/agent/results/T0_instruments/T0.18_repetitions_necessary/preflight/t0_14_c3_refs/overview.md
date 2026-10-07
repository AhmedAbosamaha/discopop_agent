# Agent experiment run `t0_14_c3_refs`

- status: running (created 2026-10-07T18:41:31, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `bcdae0fd504d6b71ea026382cba421d42a4286fc` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| expert_openmp | none | 28 | 26 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_c3/k17 | expert_openmp | none | 1 | EXTRALARGE | 3.92 |
| tsvc_c3/k42 | expert_openmp | none | 1 | EXTRALARGE | 3.87 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c3/k17 | expert_openmp | none | 1 | parallel-speed-not-measurable | 3.92x | —+— | — | — | 0 | — |
| tsvc_c3/k19 | expert_openmp | none | 1 | FASTER | 4.06x | —+— | — | — | 0 | — |
| tsvc_c3/k23 | expert_openmp | none | 1 | FASTER | 3.29x | —+— | — | — | 0 | — |
| tsvc_c3/k27 | expert_openmp | none | 1 | FASTER | 4.17x | —+— | — | — | 0 | — |
| tsvc_c3/k31 | expert_openmp | none | 1 | FASTER | 3.08x | —+— | — | — | 0 | — |
| tsvc_c3/k42 | expert_openmp | none | 1 | parallel-speed-not-measurable | 3.87x | —+— | — | — | 0 | — |
| tsvc_c3/k48 | expert_openmp | none | 1 | FASTER | 4.10x | —+— | — | — | 0 | — |
| tsvc_c3/s000 | expert_openmp | none | 1 | FASTER | 3.60x | —+— | — | — | 0 | — |
| tsvc_c3/s112 | expert_openmp | none | 1 | FASTER | 1.35x | —+— | — | — | 0 | — |
| tsvc_c3/s121 | expert_openmp | none | 1 | FASTER | 1.42x | —+— | — | — | 0 | — |
| tsvc_c3/s1213 | expert_openmp | none | 1 | FASTER | 2.62x | —+— | — | — | 0 | — |
| tsvc_c3/s127 | expert_openmp | none | 1 | FASTER | 3.96x | —+— | — | — | 0 | — |
| tsvc_c3/s211 | expert_openmp | none | 1 | FASTER | 1.93x | —+— | — | — | 0 | — |
| tsvc_c3/s212 | expert_openmp | none | 1 | FASTER | 3.35x | —+— | — | — | 0 | — |
| tsvc_c3/s241 | expert_openmp | none | 1 | FASTER | 1.84x | —+— | — | — | 0 | — |
| tsvc_c3/s243 | expert_openmp | none | 1 | FASTER | 2.52x | —+— | — | — | 0 | — |
| tsvc_c3/s244 | expert_openmp | none | 1 | FASTER | 5.18x | —+— | — | — | 0 | — |
| tsvc_c3/s252 | expert_openmp | none | 1 | FASTER | 3.64x | —+— | — | — | 0 | — |
| tsvc_c3/s254 | expert_openmp | none | 1 | FASTER | 3.48x | —+— | — | — | 0 | — |
| tsvc_c3/s255 | expert_openmp | none | 1 | FASTER | 1.43x | —+— | — | — | 0 | — |
| tsvc_c3/s281 | expert_openmp | none | 1 | FASTER | 3.29x | —+— | — | — | 0 | — |
| tsvc_c3/s291 | expert_openmp | none | 1 | FASTER | 3.52x | —+— | — | — | 0 | — |
| tsvc_c3/s292 | expert_openmp | none | 1 | FASTER | 2.97x | —+— | — | — | 0 | — |
| tsvc_c3/s293 | expert_openmp | none | 1 | FASTER | 2.80x | —+— | — | — | 0 | — |
| tsvc_c3/s313 | expert_openmp | none | 1 | FASTER | 4.67x | —+— | — | — | 0 | — |
| tsvc_c3/s331 | expert_openmp | none | 1 | FASTER | 4.48x | —+— | — | — | 0 | — |
| tsvc_c3/s341 | expert_openmp | none | 1 | FASTER | 2.36x | —+— | — | — | 0 | — |
| tsvc_c3/vpvtv | expert_openmp | none | 1 | FASTER | 3.63x | —+— | — | — | 0 | — |
