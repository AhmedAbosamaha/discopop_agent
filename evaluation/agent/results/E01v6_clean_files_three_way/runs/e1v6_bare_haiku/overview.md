# Agent experiment run `e1v6_bare_haiku`

- status: finished (created 2026-10-05T02:48:42, finished 2026-10-05T07:19:02)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `70cb05ff3d1ecc75158877a042809fcfdf7d5da8` (uncommitted diff sha256 `None`)
- harness: `70cb05ff3d1ecc75158877a042809fcfdf7d5da8` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-haiku-4-5-20251001 | 105 | 43 | 12 | 0 | 1 | 0 | 25 | 0 | 24 | 0 | 0 | 0 | 82 | 105 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s000 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 37.6 |
| tsvc_c2/s112 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.75x | —+— | — | — | 1 | 114.8 |
| tsvc_c2/s112 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 120.1 |
| tsvc_c2/s112 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.34x | —+— | — | — | 1 | 87.8 |
| tsvc_c2/s112 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.65x | —+— | — | — | 1 | 141.4 |
| tsvc_c2/s112 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 77.5 |
| tsvc_c2/s121 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.62x | —+— | — | — | 1 | 92.1 |
| tsvc_c2/s121 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.43x | —+— | — | — | 1 | 33.1 |
| tsvc_c2/s121 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 1.36x | —+— | — | — | 1 | 35.1 |
| tsvc_c2/s121 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.84x | —+— | — | — | 1 | 90.5 |
| tsvc_c2/s121 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.67x | —+— | — | — | 1 | 39.2 |
| tsvc_c2/s1213 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.66x | —+— | — | — | 1 | 60.2 |
| tsvc_c2/s1213 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.69x | —+— | — | — | 1 | 77.3 |
| tsvc_c2/s1213 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.45x | —+— | — | — | 1 | 113.0 |
| tsvc_c2/s1213 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 209.7 |
| tsvc_c2/s1213 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 2.62x | —+— | — | — | 1 | 221.2 |
| tsvc_c2/s127 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.89x | —+— | — | — | 1 | 31.5 |
| tsvc_c2/s127 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.83x | —+— | — | — | 1 | 32.0 |
| tsvc_c2/s127 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.04x | —+— | — | — | 1 | 41.6 |
| tsvc_c2/s127 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.87x | —+— | — | — | 1 | 56.4 |
| tsvc_c2/s127 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.03x | —+— | — | — | 1 | 32.5 |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.96x | —+— | — | — | 1 | 138.5 |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.10x | —+— | — | — | 1 | 171.2 |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 189.5 |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | BROKEN | 1.20x | —+— | — | — | 1 | 199.6 |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.13x | —+— | — | — | 1 | 93.1 |
| tsvc_c2/s212 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.28x | —+— | — | — | 1 | 60.6 |
| tsvc_c2/s212 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.99x | —+— | — | — | 1 | 101.6 |
| tsvc_c2/s212 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.22x | —+— | — | — | 1 | 33.9 |
| tsvc_c2/s212 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.05x | —+— | — | — | 1 | 50.1 |
| tsvc_c2/s212 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.46x | —+— | — | — | 1 | 85.3 |
| tsvc_c2/s241 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 88.1 |
| tsvc_c2/s241 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 53.2 |
| tsvc_c2/s241 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.44x | —+— | — | — | 1 | 68.3 |
| tsvc_c2/s241 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.29x | —+— | — | — | 1 | 134.0 |
| tsvc_c2/s241 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.11x | —+— | — | — | 1 | 145.3 |
| tsvc_c2/s243 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 65.3 |
| tsvc_c2/s243 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 94.1 |
| tsvc_c2/s243 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.39x | —+— | — | — | 1 | 83.7 |
| tsvc_c2/s243 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.40x | —+— | — | — | 1 | 116.4 |
| tsvc_c2/s243 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.40x | —+— | — | — | 1 | 139.9 |
| tsvc_c2/s244 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.47x | —+— | — | — | 1 | 110.5 |
| tsvc_c2/s244 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.28x | —+— | — | — | 1 | 309.9 |
| tsvc_c2/s244 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 331.3 |
| tsvc_c2/s244 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 119.9 |
| tsvc_c2/s244 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 214.7 |
| tsvc_c2/s252 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 65.8 |
| tsvc_c2/s252 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.24x | —+— | — | — | 1 | 120.8 |
| tsvc_c2/s252 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.61x | —+— | — | — | 1 | 64.8 |
| tsvc_c2/s252 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.01x | —+— | — | — | 1 | 93.2 |
| tsvc_c2/s252 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.61x | —+— | — | — | 1 | 125.3 |
| tsvc_c2/s254 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.38x | —+— | — | — | 1 | 44.8 |
| tsvc_c2/s254 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.56x | —+— | — | — | 1 | 58.8 |
| tsvc_c2/s254 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.34x | —+— | — | — | 1 | 59.7 |
| tsvc_c2/s254 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.48x | —+— | — | — | 1 | 44.2 |
| tsvc_c2/s254 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 42.2 |
| tsvc_c2/s255 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 41.2 |
| tsvc_c2/s255 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.54x | —+— | — | — | 1 | 70.1 |
| tsvc_c2/s255 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 43.7 |
| tsvc_c2/s255 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.56x | —+— | — | — | 1 | 62.6 |
| tsvc_c2/s255 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.55x | —+— | — | — | 1 | 52.5 |
| tsvc_c2/s281 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.16x | —+— | — | — | 1 | 86.2 |
| tsvc_c2/s281 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.21x | —+— | — | — | 1 | 82.3 |
| tsvc_c2/s281 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.25x | —+— | — | — | 1 | 161.9 |
| tsvc_c2/s281 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.21x | —+— | — | — | 1 | 118.4 |
| tsvc_c2/s281 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 0.88x | —+— | — | — | 1 | 63.8 |
| tsvc_c2/s291 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.46x | —+— | — | — | 1 | 42.9 |
| tsvc_c2/s291 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 41.7 |
| tsvc_c2/s291 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.10x | —+— | — | — | 1 | 51.7 |
| tsvc_c2/s291 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.52x | —+— | — | — | 1 | 41.5 |
| tsvc_c2/s291 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.50x | —+— | — | — | 1 | 41.1 |
| tsvc_c2/s292 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 36.8 |
| tsvc_c2/s292 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 40.3 |
| tsvc_c2/s292 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 45.7 |
| tsvc_c2/s292 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 42.3 |
| tsvc_c2/s292 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.93x | —+— | — | — | 1 | 83.6 |
| tsvc_c2/s293 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.89x | —+— | — | — | 1 | 83.8 |
| tsvc_c2/s293 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.93x | —+— | — | — | 1 | 32.5 |
| tsvc_c2/s293 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.92x | —+— | — | — | 1 | 31.8 |
| tsvc_c2/s293 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.69x | —+— | — | — | 1 | 78.9 |
| tsvc_c2/s293 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.41x | —+— | — | — | 1 | 37.7 |
| tsvc_c2/s3112 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 5.36x | —+— | — | — | 1 | 259.4 |
| tsvc_c2/s3112 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 172.3 |
| tsvc_c2/s3112 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 159.0 |
| tsvc_c2/s313 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.65x | —+— | — | — | 1 | 31.9 |
| tsvc_c2/s321 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 163.5 |
| tsvc_c2/s321 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | changed-not-parallel | 1.00x | —+— | — | — | 1 | 61.4 |
| tsvc_c2/s321 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 5.71x | —+— | — | — | 1 | 252.8 |
| tsvc_c2/s322 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.94x | —+— | — | — | 1 | 280.4 |
| tsvc_c2/s322 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.07x | —+— | — | — | 1 | 164.3 |
| tsvc_c2/s322 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.63x | —+— | — | — | 1 | 81.5 |
| tsvc_c2/s323 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.06x | —+— | — | — | 1 | 166.9 |
| tsvc_c2/s323 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.78x | —+— | — | — | 1 | 54.2 |
| tsvc_c2/s323 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.03x | —+— | — | — | 1 | 45.9 |
| tsvc_c2/s331 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.48x | —+— | — | — | 1 | 126.2 |
| tsvc_c2/s331 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.70x | —+— | — | — | 1 | 102.4 |
| tsvc_c2/s331 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.62x | —+— | — | — | 1 | 108.1 |
| tsvc_c2/s331 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.70x | —+— | — | — | 1 | 42.9 |
| tsvc_c2/s331 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 5.05x | —+— | — | — | 1 | 49.8 |
| tsvc_c2/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.39x | —+— | — | — | 1 | 122.8 |
| tsvc_c2/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.15x | —+— | — | — | 1 | 112.2 |
| tsvc_c2/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 0.01x | —+— | — | — | 1 | 85.4 |
| tsvc_c2/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.31x | —+— | — | — | 1 | 152.4 |
| tsvc_c2/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 111.0 |
| tsvc_c2/vpvtv | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.62x | —+— | — | — | 1 | 31.7 |
