# Agent experiment run `t0_11_c2_a`

- status: finished (created 2026-10-04T22:28:55, finished 2026-10-04T23:26:43)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `a30dd1bf5cb758659d090dad6eb5a4956f7f6ac7` (uncommitted diff sha256 `None`)
- harness: `a30dd1bf5cb758659d090dad6eb5a4956f7f6ac7` on `agentic_DiscoPop`
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
| tsvc_c2/k17 | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.99 |
| tsvc_c2/k42 | discopop_capability | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.94 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k17 | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.99x | 1+0 | 0 | 1 | 0 | 4.3 |
| tsvc_c2/k19 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.7 |
| tsvc_c2/k23 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c2/k27 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.8 |
| tsvc_c2/k31 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.8 |
| tsvc_c2/k42 | discopop_capability | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.94x | 1+0 | 0 | 1 | 0 | 4.5 |
| tsvc_c2/k48 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.7 |
| tsvc_c2/k53 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 3.0 |
| tsvc_c2/s000 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.46x | 1+0 | 0 | 1 | 0 | 4.2 |
| tsvc_c2/s112 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s121 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s1213 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c2/s127 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c2/s131 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s151 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c2/s152 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.60x | 1+0 | 0 | 1 | 0 | 4.7 |
| tsvc_c2/s161 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 2.7 |
| tsvc_c2/s171 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.43x | 1+0 | 0 | 1 | 0 | 4.3 |
| tsvc_c2/s211 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s212 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s241 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c2/s243 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c2/s244 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s252 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s254 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s255 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s258 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c2/s277 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.54x | 1+0 | 0 | 1 | 0 | 4.1 |
| tsvc_c2/s281 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s291 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c2/s292 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.97x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c2/s293 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.97x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s3112 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.5 |
| tsvc_c2/s313 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 4.64x | 1+0 | 0 | 1 | 0 | 4.2 |
| tsvc_c2/s321 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s322 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s323 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/s331 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 3.4 |
| tsvc_c2/s341 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 0 | 2.3 |
| tsvc_c2/s424 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 2.6 |
| tsvc_c2/s481 | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 2.69x | 1+0 | 0 | 2 | 0 | 5.1 |
| tsvc_c2/s482 | discopop_capability | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 2.4 |
| tsvc_c2/vas | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.63x | 1+0 | 0 | 1 | 0 | 4.3 |
| tsvc_c2/vpvtv | discopop_capability | claude-haiku-4-5-20251001 | 1 | FASTER | 3.61x | 1+0 | 0 | 1 | 0 | 4.1 |
