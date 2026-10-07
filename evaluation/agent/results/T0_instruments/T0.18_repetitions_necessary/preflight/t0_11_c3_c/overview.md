# Agent experiment run `t0_11_c3_c`

- status: finished (created 2026-10-07T17:41:44, finished 2026-10-07T18:38:45)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `bcdae0fd504d6b71ea026382cba421d42a4286fc` (uncommitted diff sha256 `None`)
- harness: `bcdae0fd504d6b71ea026382cba421d42a4286fc` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | claude-haiku-4-5-20251001 | 44 | 8 | 0 | 2 | 0 | 34 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_c3/k17 | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 1.00 |
| tsvc_c3/k42 | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.97 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c3/k17 | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 1.00x | 1+0 | 0 | 1 | 0 | 4.5 |
| tsvc_c3/k19 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.0 |
| tsvc_c3/k23 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 3.0 |
| tsvc_c3/k27 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.8 |
| tsvc_c3/k31 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.7 |
| tsvc_c3/k42 | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.97x | 1+0 | 0 | 1 | 0 | 4.4 |
| tsvc_c3/k48 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 2.9 |
| tsvc_c3/k53 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.0 |
| tsvc_c3/s000 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.37x | 1+0 | 0 | 1 | 0 | 4.2 |
| tsvc_c3/s112 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.11x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s121 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s1213 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s127 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.06x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c3/s131 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c3/s151 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s152 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.81x | 1+0 | 0 | 1 | 0 | 4.4 |
| tsvc_c3/s161 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c3/s171 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.69x | 1+0 | 0 | 1 | 0 | 4.5 |
| tsvc_c3/s211 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s212 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c3/s241 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c3/s243 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c3/s244 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c3/s252 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c3/s254 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c3/s255 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s258 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s277 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 5.03x | 1+0 | 0 | 1 | 0 | 4.1 |
| tsvc_c3/s281 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s291 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s292 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c3/s293 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c3/s3112 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c3/s313 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.93x | 1+0 | 0 | 1 | 0 | 4.0 |
| tsvc_c3/s321 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s322 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s323 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c3/s331 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 3.3 |
| tsvc_c3/s341 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c3/s424 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c3/s481 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.93x | 1+0 | 0 | 2 | 0 | 4.9 |
| tsvc_c3/s482 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c3/vas | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.50x | 1+0 | 0 | 1 | 0 | 4.2 |
| tsvc_c3/vpvtv | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.85x | 1+0 | 0 | 1 | 0 | 4.4 |
