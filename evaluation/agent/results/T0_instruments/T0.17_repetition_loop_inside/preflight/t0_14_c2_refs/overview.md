# Agent experiment run `t0_14_c2_refs`

- status: running (created 2026-10-04T23:27:30, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `a30dd1bf5cb758659d090dad6eb5a4956f7f6ac7` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| expert_openmp | none | 28 | 26 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_c2/k17 | expert_openmp | none | 1 | EXTRALARGE | 3.28 |
| tsvc_c2/k42 | expert_openmp | none | 1 | EXTRALARGE | 3.63 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k17 | expert_openmp | none | 1 | parallel-speed-not-measurable | 3.28x | —+— | — | — | 0 | — |
| tsvc_c2/k19 | expert_openmp | none | 1 | FASTER | 4.14x | —+— | — | — | 0 | — |
| tsvc_c2/k23 | expert_openmp | none | 1 | FASTER | 3.33x | —+— | — | — | 0 | — |
| tsvc_c2/k27 | expert_openmp | none | 1 | FASTER | 4.17x | —+— | — | — | 0 | — |
| tsvc_c2/k31 | expert_openmp | none | 1 | FASTER | 3.09x | —+— | — | — | 0 | — |
| tsvc_c2/k42 | expert_openmp | none | 1 | parallel-speed-not-measurable | 3.63x | —+— | — | — | 0 | — |
| tsvc_c2/k48 | expert_openmp | none | 1 | FASTER | 4.13x | —+— | — | — | 0 | — |
| tsvc_c2/s000 | expert_openmp | none | 1 | FASTER | 3.67x | —+— | — | — | 0 | — |
| tsvc_c2/s112 | expert_openmp | none | 1 | FASTER | 1.33x | —+— | — | — | 0 | — |
| tsvc_c2/s121 | expert_openmp | none | 1 | FASTER | 1.40x | —+— | — | — | 0 | — |
| tsvc_c2/s1213 | expert_openmp | none | 1 | FASTER | 2.62x | —+— | — | — | 0 | — |
| tsvc_c2/s127 | expert_openmp | none | 1 | FASTER | 3.91x | —+— | — | — | 0 | — |
| tsvc_c2/s211 | expert_openmp | none | 1 | FASTER | 2.12x | —+— | — | — | 0 | — |
| tsvc_c2/s212 | expert_openmp | none | 1 | FASTER | 3.35x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | expert_openmp | none | 1 | FASTER | 1.85x | —+— | — | — | 0 | — |
| tsvc_c2/s243 | expert_openmp | none | 1 | FASTER | 2.55x | —+— | — | — | 0 | — |
| tsvc_c2/s244 | expert_openmp | none | 1 | FASTER | 5.51x | —+— | — | — | 0 | — |
| tsvc_c2/s252 | expert_openmp | none | 1 | FASTER | 3.62x | —+— | — | — | 0 | — |
| tsvc_c2/s254 | expert_openmp | none | 1 | FASTER | 3.46x | —+— | — | — | 0 | — |
| tsvc_c2/s255 | expert_openmp | none | 1 | FASTER | 2.59x | —+— | — | — | 0 | — |
| tsvc_c2/s281 | expert_openmp | none | 1 | FASTER | 3.28x | —+— | — | — | 0 | — |
| tsvc_c2/s291 | expert_openmp | none | 1 | FASTER | 3.52x | —+— | — | — | 0 | — |
| tsvc_c2/s292 | expert_openmp | none | 1 | FASTER | 3.02x | —+— | — | — | 0 | — |
| tsvc_c2/s293 | expert_openmp | none | 1 | FASTER | 2.88x | —+— | — | — | 0 | — |
| tsvc_c2/s313 | expert_openmp | none | 1 | FASTER | 4.64x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | expert_openmp | none | 1 | FASTER | 4.50x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | expert_openmp | none | 1 | FASTER | 2.40x | —+— | — | — | 0 | — |
| tsvc_c2/vpvtv | expert_openmp | none | 1 | FASTER | 3.72x | —+— | — | — | 0 | — |
