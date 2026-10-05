# Agent experiment run `e1f_bare_haiku`

- status: finished (created 2026-10-03T04:37:33, finished 2026-10-03T08:06:53)
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
| bare_llm_v3 | claude-haiku-4-5-20251001 | 105 | 45 | 24 | 0 | 2 | 2 | 24 | 0 | 8 | 0 | 0 | 0 | 70 | 105 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s000 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.17x | —+— | — | — | 1 | 24.8 |
| tsvc_b1/s112 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.54x | —+— | — | — | 1 | 49.6 |
| tsvc_b1/s112 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.38x | —+— | — | — | 1 | 28.9 |
| tsvc_b1/s112 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.67x | —+— | — | — | 1 | 133.7 |
| tsvc_b1/s112 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.44x | —+— | — | — | 1 | 54.2 |
| tsvc_b1/s112 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.15x | —+— | — | — | 1 | 98.2 |
| tsvc_b1/s121 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.50x | —+— | — | — | 1 | 24.9 |
| tsvc_b1/s121 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.61x | —+— | — | — | 1 | 130.2 |
| tsvc_b1/s121 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.62x | —+— | — | — | 1 | 34.3 |
| tsvc_b1/s121 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 42.3 |
| tsvc_b1/s121 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.76x | —+— | — | — | 1 | 77.5 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 188.5 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.31x | —+— | — | — | 1 | 69.5 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 1.18x | —+— | — | — | 1 | 68.1 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 1.87x | —+— | — | — | 1 | 143.9 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 0.27x | —+— | — | — | 1 | 281.1 |
| tsvc_b1/s127 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.48x | —+— | — | — | 1 | 26.9 |
| tsvc_b1/s127 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.34x | —+— | — | — | 1 | 34.7 |
| tsvc_b1/s127 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.32x | —+— | — | — | 1 | 31.7 |
| tsvc_b1/s127 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.23x | —+— | — | — | 1 | 25.8 |
| tsvc_b1/s127 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 26.9 |
| tsvc_b1/s211 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.09x | —+— | — | — | 1 | 130.6 |
| tsvc_b1/s211 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.00x | —+— | — | — | 1 | 139.1 |
| tsvc_b1/s211 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.97x | —+— | — | — | 1 | 129.6 |
| tsvc_b1/s211 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 172.2 |
| tsvc_b1/s211 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.22x | —+— | — | — | 1 | 210.5 |
| tsvc_b1/s212 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.51x | —+— | — | — | 1 | 37.0 |
| tsvc_b1/s212 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.29x | —+— | — | — | 1 | 73.3 |
| tsvc_b1/s212 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.28x | —+— | — | — | 1 | 90.3 |
| tsvc_b1/s212 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 2.94x | —+— | — | — | 1 | 89.6 |
| tsvc_b1/s212 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.68x | —+— | — | — | 1 | 161.9 |
| tsvc_b1/s241 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.89x | —+— | — | — | 1 | 52.7 |
| tsvc_b1/s241 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.79x | —+— | — | — | 1 | 82.9 |
| tsvc_b1/s241 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.42x | —+— | — | — | 1 | 106.7 |
| tsvc_b1/s241 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 4.02x | —+— | — | — | 1 | 47.0 |
| tsvc_b1/s241 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.33x | —+— | — | — | 1 | 93.5 |
| tsvc_b1/s243 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.33x | —+— | — | — | 1 | 152.7 |
| tsvc_b1/s243 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.45x | —+— | — | — | 1 | 71.7 |
| tsvc_b1/s243 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.53x | —+— | — | — | 1 | 34.7 |
| tsvc_b1/s243 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.04x | —+— | — | — | 1 | 86.8 |
| tsvc_b1/s243 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.36x | —+— | — | — | 1 | 115.7 |
| tsvc_b1/s244 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.50x | —+— | — | — | 1 | 116.9 |
| tsvc_b1/s244 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.20x | —+— | — | — | 1 | 190.6 |
| tsvc_b1/s244 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.87x | —+— | — | — | 1 | 244.8 |
| tsvc_b1/s244 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 0.30x | —+— | — | — | 1 | 300.9 |
| tsvc_b1/s244 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 2.33x | —+— | — | — | 1 | 166.6 |
| tsvc_b1/s252 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.01x | —+— | — | — | 1 | 62.2 |
| tsvc_b1/s252 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.65x | —+— | — | — | 1 | 62.8 |
| tsvc_b1/s252 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.60x | —+— | — | — | 1 | 54.0 |
| tsvc_b1/s252 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.98x | —+— | — | — | 1 | 79.3 |
| tsvc_b1/s252 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 42.2 |
| tsvc_b1/s254 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 32.9 |
| tsvc_b1/s254 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.33x | —+— | — | — | 1 | 38.8 |
| tsvc_b1/s254 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.85x | —+— | — | — | 1 | 32.8 |
| tsvc_b1/s254 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.34x | —+— | — | — | 1 | 46.4 |
| tsvc_b1/s254 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.93x | —+— | — | — | 1 | 28.9 |
| tsvc_b1/s255 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.52x | —+— | — | — | 1 | 32.9 |
| tsvc_b1/s255 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.41x | —+— | — | — | 1 | 59.1 |
| tsvc_b1/s255 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.78x | —+— | — | — | 1 | 68.2 |
| tsvc_b1/s255 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.05x | —+— | — | — | 1 | 37.0 |
| tsvc_b1/s255 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.54x | —+— | — | — | 1 | 55.7 |
| tsvc_b1/s281 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.21x | —+— | — | — | 1 | 227.0 |
| tsvc_b1/s281 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.26x | —+— | — | — | 1 | 167.4 |
| tsvc_b1/s281 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.19x | —+— | — | — | 1 | 121.8 |
| tsvc_b1/s281 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 1.38x | —+— | — | — | 1 | 57.5 |
| tsvc_b1/s281 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.06x | —+— | — | — | 1 | 106.8 |
| tsvc_b1/s291 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.44x | —+— | — | — | 1 | 25.9 |
| tsvc_b1/s291 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 24.3 |
| tsvc_b1/s291 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.41x | —+— | — | — | 1 | 27.9 |
| tsvc_b1/s291 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.37x | —+— | — | — | 1 | 35.5 |
| tsvc_b1/s291 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.65x | —+— | — | — | 1 | 39.2 |
| tsvc_b1/s292 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.93x | —+— | — | — | 1 | 40.2 |
| tsvc_b1/s292 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.67x | —+— | — | — | 1 | 41.4 |
| tsvc_b1/s292 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.21x | —+— | — | — | 1 | 40.6 |
| tsvc_b1/s292 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.62x | —+— | — | — | 1 | 52.1 |
| tsvc_b1/s292 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.45x | —+— | — | — | 1 | 48.0 |
| tsvc_b1/s293 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.85x | —+— | — | — | 1 | 77.7 |
| tsvc_b1/s293 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.37x | —+— | — | — | 1 | 36.4 |
| tsvc_b1/s293 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.57x | —+— | — | — | 1 | 26.3 |
| tsvc_b1/s293 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.57x | —+— | — | — | 1 | 83.7 |
| tsvc_b1/s293 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.89x | —+— | — | — | 1 | 19.0 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | —+— | — | — | 1 | 59.1 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.07x | —+— | — | — | 1 | 88.2 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.08x | —+— | — | — | 1 | 161.3 |
| tsvc_b1/s313 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.96x | —+— | — | — | 1 | 28.1 |
| tsvc_b1/s321 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | changed-not-parallel | 1.01x | —+— | — | — | 1 | 164.0 |
| tsvc_b1/s321 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 0.65x | —+— | — | — | 1 | 185.9 |
| tsvc_b1/s321 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | changed-not-parallel | 1.00x | —+— | — | — | 1 | 68.6 |
| tsvc_b1/s322 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.38x | —+— | — | — | 1 | 90.6 |
| tsvc_b1/s322 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 5.74x | —+— | — | — | 1 | 71.8 |
| tsvc_b1/s322 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | —+— | — | — | 1 | 82.2 |
| tsvc_b1/s323 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 101.4 |
| tsvc_b1/s323 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 129.8 |
| tsvc_b1/s323 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.50x | —+— | — | — | 1 | 185.1 |
| tsvc_b1/s331 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.72x | —+— | — | — | 1 | 86.0 |
| tsvc_b1/s331 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.68x | —+— | — | — | 1 | 99.7 |
| tsvc_b1/s331 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.50x | —+— | — | — | 1 | 91.0 |
| tsvc_b1/s331 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.08x | —+— | — | — | 1 | 67.7 |
| tsvc_b1/s331 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.48x | —+— | — | — | 1 | 126.1 |
| tsvc_b1/s341 | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.59x | —+— | — | — | 1 | 53.6 |
| tsvc_b1/s341 | bare_llm_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.55x | —+— | — | — | 1 | 75.2 |
| tsvc_b1/s341 | bare_llm_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.58x | —+— | — | — | 1 | 62.9 |
| tsvc_b1/s341 | bare_llm_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.60x | —+— | — | — | 1 | 74.4 |
| tsvc_b1/s341 | bare_llm_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.50x | —+— | — | — | 1 | 85.6 |
| tsvc_b1/vpvtv | bare_llm_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.41x | —+— | — | — | 1 | 25.9 |
