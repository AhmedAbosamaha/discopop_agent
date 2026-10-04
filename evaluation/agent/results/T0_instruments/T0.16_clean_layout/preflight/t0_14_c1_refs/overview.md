# Agent experiment run `t0_14_c1_refs`

- status: running (created 2026-10-04T14:23:07, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `9db3d15719d09d40e3f57b3c7aae80711b52ba15` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| expert_openmp | none | 28 | 26 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_c1/k17 | expert_openmp | none | 1 | EXTRALARGE | 3.33 |
| tsvc_c1/k42 | expert_openmp | none | 1 | EXTRALARGE | 4.04 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c1/k17 | expert_openmp | none | 1 | parallel-speed-not-measurable | 3.33x | —+— | — | — | 0 | — |
| tsvc_c1/k19 | expert_openmp | none | 1 | FASTER | 4.16x | —+— | — | — | 0 | — |
| tsvc_c1/k23 | expert_openmp | none | 1 | FASTER | 3.23x | —+— | — | — | 0 | — |
| tsvc_c1/k27 | expert_openmp | none | 1 | FASTER | 4.12x | —+— | — | — | 0 | — |
| tsvc_c1/k31 | expert_openmp | none | 1 | FASTER | 3.21x | —+— | — | — | 0 | — |
| tsvc_c1/k42 | expert_openmp | none | 1 | parallel-speed-not-measurable | 4.04x | —+— | — | — | 0 | — |
| tsvc_c1/k48 | expert_openmp | none | 1 | FASTER | 4.02x | —+— | — | — | 0 | — |
| tsvc_c1/s000 | expert_openmp | none | 1 | FASTER | 3.62x | —+— | — | — | 0 | — |
| tsvc_c1/s112 | expert_openmp | none | 1 | FASTER | 1.13x | —+— | — | — | 0 | — |
| tsvc_c1/s121 | expert_openmp | none | 1 | FASTER | 1.54x | —+— | — | — | 0 | — |
| tsvc_c1/s1213 | expert_openmp | none | 1 | FASTER | 2.60x | —+— | — | — | 0 | — |
| tsvc_c1/s127 | expert_openmp | none | 1 | FASTER | 3.96x | —+— | — | — | 0 | — |
| tsvc_c1/s211 | expert_openmp | none | 1 | FASTER | 2.06x | —+— | — | — | 0 | — |
| tsvc_c1/s212 | expert_openmp | none | 1 | FASTER | 3.36x | —+— | — | — | 0 | — |
| tsvc_c1/s241 | expert_openmp | none | 1 | FASTER | 2.15x | —+— | — | — | 0 | — |
| tsvc_c1/s243 | expert_openmp | none | 1 | FASTER | 2.92x | —+— | — | — | 0 | — |
| tsvc_c1/s244 | expert_openmp | none | 1 | FASTER | 5.29x | —+— | — | — | 0 | — |
| tsvc_c1/s252 | expert_openmp | none | 1 | FASTER | 3.67x | —+— | — | — | 0 | — |
| tsvc_c1/s254 | expert_openmp | none | 1 | FASTER | 3.51x | —+— | — | — | 0 | — |
| tsvc_c1/s255 | expert_openmp | none | 1 | FASTER | 2.54x | —+— | — | — | 0 | — |
| tsvc_c1/s281 | expert_openmp | none | 1 | FASTER | 3.40x | —+— | — | — | 0 | — |
| tsvc_c1/s291 | expert_openmp | none | 1 | FASTER | 3.53x | —+— | — | — | 0 | — |
| tsvc_c1/s292 | expert_openmp | none | 1 | FASTER | 3.05x | —+— | — | — | 0 | — |
| tsvc_c1/s293 | expert_openmp | none | 1 | FASTER | 2.90x | —+— | — | — | 0 | — |
| tsvc_c1/s313 | expert_openmp | none | 1 | FASTER | 4.67x | —+— | — | — | 0 | — |
| tsvc_c1/s331 | expert_openmp | none | 1 | FASTER | 4.54x | —+— | — | — | 0 | — |
| tsvc_c1/s341 | expert_openmp | none | 1 | FASTER | 2.40x | —+— | — | — | 0 | — |
| tsvc_c1/vpvtv | expert_openmp | none | 1 | FASTER | 3.69x | —+— | — | — | 0 | — |
