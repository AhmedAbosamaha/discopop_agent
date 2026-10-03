# Agent experiment run `e1f_bare_sonnet`

- status: finished (created 2026-10-03T05:18:25, finished 2026-10-03T08:29:36)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `ab0e7f4759b982c26184c0efa24f19e97ea795f9` (uncommitted diff sha256 `None`)
- harness: `ab0e7f4759b982c26184c0efa24f19e97ea795f9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v3 | claude-sonnet-5 | 105 | 91 | 12 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 76 | 105 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s000 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.49x | —+— | — | — | 1 | 15.4 |
| tsvc_b1/s112 | bare_llm_v3 | claude-sonnet-5 | 1 | parallel-not-faster | 1.09x | —+— | — | — | 1 | 117.9 |
| tsvc_b1/s112 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 1.65x | —+— | — | — | 1 | 98.2 |
| tsvc_b1/s112 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 1.45x | —+— | — | — | 1 | 144.4 |
| tsvc_b1/s112 | bare_llm_v3 | claude-sonnet-5 | 4 | parallel-not-faster | 0.84x | —+— | — | — | 1 | 126.4 |
| tsvc_b1/s112 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 1.24x | —+— | — | — | 1 | 92.0 |
| tsvc_b1/s121 | bare_llm_v3 | claude-sonnet-5 | 1 | parallel-not-faster | 0.80x | —+— | — | — | 1 | 87.9 |
| tsvc_b1/s121 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 1.37x | —+— | — | — | 1 | 78.6 |
| tsvc_b1/s121 | bare_llm_v3 | claude-sonnet-5 | 3 | parallel-not-faster | 0.85x | —+— | — | — | 1 | 109.0 |
| tsvc_b1/s121 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 1.36x | —+— | — | — | 1 | 87.8 |
| tsvc_b1/s121 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 1.46x | —+— | — | — | 1 | 56.8 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 2.19x | —+— | — | — | 1 | 131.6 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 1.30x | —+— | — | — | 1 | 112.7 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 1.29x | —+— | — | — | 1 | 105.7 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 2.01x | —+— | — | — | 1 | 101.7 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 2.02x | —+— | — | — | 1 | 140.8 |
| tsvc_b1/s127 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.87x | —+— | — | — | 1 | 29.5 |
| tsvc_b1/s127 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 3.72x | —+— | — | — | 1 | 20.2 |
| tsvc_b1/s127 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 3.89x | —+— | — | — | 1 | 27.2 |
| tsvc_b1/s127 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 4.21x | —+— | — | — | 1 | 20.1 |
| tsvc_b1/s127 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 4.27x | —+— | — | — | 1 | 26.4 |
| tsvc_b1/s211 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 2.12x | —+— | — | — | 1 | 89.0 |
| tsvc_b1/s211 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 1.88x | —+— | — | — | 1 | 112.7 |
| tsvc_b1/s211 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 2.50x | —+— | — | — | 1 | 171.4 |
| tsvc_b1/s211 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 2.58x | —+— | — | — | 1 | 102.1 |
| tsvc_b1/s211 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 2.69x | —+— | — | — | 1 | 85.1 |
| tsvc_b1/s212 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.04x | —+— | — | — | 1 | 47.6 |
| tsvc_b1/s212 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 3.02x | —+— | — | — | 1 | 42.6 |
| tsvc_b1/s212 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 2.43x | —+— | — | — | 1 | 63.9 |
| tsvc_b1/s212 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 1.30x | —+— | — | — | 1 | 75.0 |
| tsvc_b1/s212 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 2.26x | —+— | — | — | 1 | 92.2 |
| tsvc_b1/s241 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 1.63x | —+— | — | — | 1 | 89.1 |
| tsvc_b1/s241 | bare_llm_v3 | claude-sonnet-5 | 2 | parallel-not-faster | 0.91x | —+— | — | — | 1 | 76.2 |
| tsvc_b1/s241 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 1.43x | —+— | — | — | 1 | 92.5 |
| tsvc_b1/s241 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 1.52x | —+— | — | — | 1 | 88.9 |
| tsvc_b1/s241 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 1.89x | —+— | — | — | 1 | 79.9 |
| tsvc_b1/s243 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 2.02x | —+— | — | — | 1 | 83.5 |
| tsvc_b1/s243 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 2.07x | —+— | — | — | 1 | 72.5 |
| tsvc_b1/s243 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 1.73x | —+— | — | — | 1 | 68.8 |
| tsvc_b1/s243 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 1.86x | —+— | — | — | 1 | 81.5 |
| tsvc_b1/s243 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 2.00x | —+— | — | — | 1 | 92.5 |
| tsvc_b1/s244 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 4.23x | —+— | — | — | 1 | 93.3 |
| tsvc_b1/s244 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 4.29x | —+— | — | — | 1 | 128.1 |
| tsvc_b1/s244 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 4.04x | —+— | — | — | 1 | 51.7 |
| tsvc_b1/s244 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 4.48x | —+— | — | — | 1 | 62.7 |
| tsvc_b1/s244 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 4.38x | —+— | — | — | 1 | 71.4 |
| tsvc_b1/s252 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.65x | —+— | — | — | 1 | 30.4 |
| tsvc_b1/s252 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 3.66x | —+— | — | — | 1 | 29.7 |
| tsvc_b1/s252 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 3.53x | —+— | — | — | 1 | 38.8 |
| tsvc_b1/s252 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 3.53x | —+— | — | — | 1 | 23.5 |
| tsvc_b1/s252 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 3.53x | —+— | — | — | 1 | 31.6 |
| tsvc_b1/s254 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.38x | —+— | — | — | 1 | 38.9 |
| tsvc_b1/s254 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 3.49x | —+— | — | — | 1 | 30.3 |
| tsvc_b1/s254 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 3.55x | —+— | — | — | 1 | 20.9 |
| tsvc_b1/s254 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 3.42x | —+— | — | — | 1 | 29.3 |
| tsvc_b1/s254 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 3.42x | —+— | — | — | 1 | 21.1 |
| tsvc_b1/s255 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 2.56x | —+— | — | — | 1 | 34.5 |
| tsvc_b1/s255 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 3.43x | —+— | — | — | 1 | 48.0 |
| tsvc_b1/s255 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 2.50x | —+— | — | — | 1 | 63.7 |
| tsvc_b1/s255 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 2.54x | —+— | — | — | 1 | 42.3 |
| tsvc_b1/s255 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 2.58x | —+— | — | — | 1 | 41.5 |
| tsvc_b1/s281 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.13x | —+— | — | — | 1 | 141.5 |
| tsvc_b1/s281 | bare_llm_v3 | claude-sonnet-5 | 2 | parallel-not-faster | 0.82x | —+— | — | — | 1 | 205.3 |
| tsvc_b1/s281 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 1.25x | —+— | — | — | 1 | 144.7 |
| tsvc_b1/s281 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 4.18x | —+— | — | — | 1 | 98.8 |
| tsvc_b1/s281 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 3.28x | —+— | — | — | 1 | 104.8 |
| tsvc_b1/s291 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.41x | —+— | — | — | 1 | 22.0 |
| tsvc_b1/s291 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 2.99x | —+— | — | — | 1 | 39.0 |
| tsvc_b1/s291 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 3.31x | —+— | — | — | 1 | 17.8 |
| tsvc_b1/s291 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 3.42x | —+— | — | — | 1 | 23.5 |
| tsvc_b1/s291 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 3.39x | —+— | — | — | 1 | 18.5 |
| tsvc_b1/s292 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 2.62x | —+— | — | — | 1 | 58.4 |
| tsvc_b1/s292 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 2.76x | —+— | — | — | 1 | 27.5 |
| tsvc_b1/s292 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 2.81x | —+— | — | — | 1 | 26.3 |
| tsvc_b1/s292 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 2.67x | —+— | — | — | 1 | 36.3 |
| tsvc_b1/s292 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 3.68x | —+— | — | — | 1 | 31.6 |
| tsvc_b1/s293 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 2.22x | —+— | — | — | 1 | 28.2 |
| tsvc_b1/s293 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 2.91x | —+— | — | — | 1 | 16.7 |
| tsvc_b1/s293 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 2.68x | —+— | — | — | 1 | 30.3 |
| tsvc_b1/s293 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 3.02x | —+— | — | — | 1 | 23.6 |
| tsvc_b1/s293 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 2.88x | —+— | — | — | 1 | 28.4 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.19x | —+— | — | — | 1 | 205.5 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 3.04x | —+— | — | — | 1 | 146.5 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 3.03x | —+— | — | — | 1 | 182.7 |
| tsvc_b1/s313 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 4.56x | —+— | — | — | 1 | 16.7 |
| tsvc_b1/s321 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.13x | —+— | — | — | 1 | 287.4 |
| tsvc_b1/s321 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 4.24x | —+— | — | — | 1 | 351.3 |
| tsvc_b1/s321 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 4.88x | —+— | — | — | 1 | 375.3 |
| tsvc_b1/s322 | bare_llm_v3 | claude-sonnet-5 | 1 | parallel-not-faster | 1.01x | —+— | — | — | 1 | 371.0 |
| tsvc_b1/s322 | bare_llm_v3 | claude-sonnet-5 | 2 | parallel-not-faster | 1.02x | —+— | — | — | 1 | 318.8 |
| tsvc_b1/s322 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 5.14x | —+— | — | — | 1 | 548.0 |
| tsvc_b1/s323 | bare_llm_v3 | claude-sonnet-5 | 1 | parallel-not-faster | 0.91x | —+— | — | — | 1 | 118.0 |
| tsvc_b1/s323 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 2.35x | —+— | — | — | 1 | 350.4 |
| tsvc_b1/s323 | bare_llm_v3 | claude-sonnet-5 | 3 | parallel-not-faster | 0.92x | —+— | — | — | 1 | 206.3 |
| tsvc_b1/s331 | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 4.59x | —+— | — | — | 1 | 29.5 |
| tsvc_b1/s331 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 4.47x | —+— | — | — | 1 | 34.9 |
| tsvc_b1/s331 | bare_llm_v3 | claude-sonnet-5 | 3 | FASTER | 4.67x | —+— | — | — | 1 | 49.4 |
| tsvc_b1/s331 | bare_llm_v3 | claude-sonnet-5 | 4 | FASTER | 4.56x | —+— | — | — | 1 | 419.7 |
| tsvc_b1/s331 | bare_llm_v3 | claude-sonnet-5 | 5 | FASTER | 4.62x | —+— | — | — | 1 | 39.2 |
| tsvc_b1/s341 | bare_llm_v3 | claude-sonnet-5 | 1 | parallel-not-faster | 0.59x | —+— | — | — | 1 | 166.1 |
| tsvc_b1/s341 | bare_llm_v3 | claude-sonnet-5 | 2 | FASTER | 1.99x | —+— | — | — | 1 | 170.8 |
| tsvc_b1/s341 | bare_llm_v3 | claude-sonnet-5 | 3 | BROKEN | — | —+— | — | — | 1 | 122.8 |
| tsvc_b1/s341 | bare_llm_v3 | claude-sonnet-5 | 4 | parallel-not-faster | 1.02x | —+— | — | — | 1 | 205.0 |
| tsvc_b1/s341 | bare_llm_v3 | claude-sonnet-5 | 5 | BROKEN | — | —+— | — | — | 1 | 140.6 |
| tsvc_b1/vpvtv | bare_llm_v3 | claude-sonnet-5 | 1 | FASTER | 3.82x | —+— | — | — | 1 | 19.8 |
