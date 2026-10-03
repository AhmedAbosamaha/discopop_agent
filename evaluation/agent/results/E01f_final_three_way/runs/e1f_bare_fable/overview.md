# Agent experiment run `e1f_bare_fable`

- status: finished (created 2026-10-03T08:25:07, finished 2026-10-03T09:41:19)
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
| bare_llm_v3 | claude-fable-5-1 | 105 | 103 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 40 | 107 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s000 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.48x | —+— | — | — | 1 | 28.8 |
| tsvc_b1/s112 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 1.43x | —+— | — | — | 1 | 33.6 |
| tsvc_b1/s112 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 1.32x | —+— | — | — | 1 | 47.6 |
| tsvc_b1/s112 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 1.32x | —+— | — | — | 1 | 45.8 |
| tsvc_b1/s112 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 1.33x | —+— | — | — | 1 | 37.2 |
| tsvc_b1/s112 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 1.52x | —+— | — | — | 1 | 36.1 |
| tsvc_b1/s121 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 1.30x | —+— | — | — | 1 | 62.3 |
| tsvc_b1/s121 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 1.44x | —+— | — | — | 1 | 44.5 |
| tsvc_b1/s121 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 1.52x | —+— | — | — | 1 | 43.4 |
| tsvc_b1/s121 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 1.34x | —+— | — | — | 1 | 60.6 |
| tsvc_b1/s121 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 1.33x | —+— | — | — | 1 | 38.3 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.65x | —+— | — | — | 1 | 48.4 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 2.52x | —+— | — | — | 1 | 25.0 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 2.60x | —+— | — | — | 1 | 34.4 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 2.69x | —+— | — | — | 1 | 53.0 |
| tsvc_b1/s1213 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 2.59x | —+— | — | — | 1 | 58.2 |
| tsvc_b1/s127 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 4.12x | —+— | — | — | 1 | 35.1 |
| tsvc_b1/s127 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.75x | —+— | — | — | 1 | 29.5 |
| tsvc_b1/s127 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.85x | —+— | — | — | 1 | 35.8 |
| tsvc_b1/s127 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 4.02x | —+— | — | — | 1 | 28.7 |
| tsvc_b1/s127 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 3.89x | —+— | — | — | 1 | 41.3 |
| tsvc_b1/s211 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.10x | —+— | — | — | 1 | 82.7 |
| tsvc_b1/s211 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 2.19x | —+— | — | — | 1 | 39.7 |
| tsvc_b1/s211 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 2.38x | —+— | — | — | 1 | 91.4 |
| tsvc_b1/s211 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 2.12x | —+— | — | — | 1 | 44.2 |
| tsvc_b1/s211 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 2.29x | —+— | — | — | 1 | 47.1 |
| tsvc_b1/s212 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.02x | —+— | — | — | 1 | 33.6 |
| tsvc_b1/s212 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.02x | —+— | — | — | 1 | 52.2 |
| tsvc_b1/s212 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.05x | —+— | — | — | 1 | 47.6 |
| tsvc_b1/s212 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 3.11x | —+— | — | — | 1 | 59.7 |
| tsvc_b1/s212 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 2.94x | —+— | — | — | 1 | 56.9 |
| tsvc_b1/s241 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 1.82x | —+— | — | — | 1 | 66.7 |
| tsvc_b1/s241 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 1.70x | —+— | — | — | 1 | 51.9 |
| tsvc_b1/s241 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 2.18x | —+— | — | — | 1 | 73.4 |
| tsvc_b1/s241 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 1.48x | —+— | — | — | 1 | 35.3 |
| tsvc_b1/s241 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 1.81x | —+— | — | — | 1 | 49.4 |
| tsvc_b1/s243 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.05x | —+— | — | — | 1 | 37.2 |
| tsvc_b1/s243 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 2.13x | —+— | — | — | 1 | 52.6 |
| tsvc_b1/s243 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 2.14x | —+— | — | — | 1 | 40.1 |
| tsvc_b1/s243 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 2.29x | —+— | — | — | 1 | 58.5 |
| tsvc_b1/s243 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 2.09x | —+— | — | — | 1 | 38.3 |
| tsvc_b1/s244 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 4.24x | —+— | — | — | 1 | 49.5 |
| tsvc_b1/s244 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.93x | —+— | — | — | 1 | 34.3 |
| tsvc_b1/s244 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 4.26x | —+— | — | — | 1 | 51.7 |
| tsvc_b1/s244 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 3.88x | —+— | — | — | 1 | 25.7 |
| tsvc_b1/s244 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 4.13x | —+— | — | — | 1 | 35.5 |
| tsvc_b1/s252 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.79x | —+— | — | — | 1 | 28.0 |
| tsvc_b1/s252 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.54x | —+— | — | — | 1 | 22.4 |
| tsvc_b1/s252 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.60x | —+— | — | — | 1 | 38.7 |
| tsvc_b1/s252 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 3.60x | —+— | — | — | 1 | 31.6 |
| tsvc_b1/s252 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 3.60x | —+— | — | — | 1 | 30.6 |
| tsvc_b1/s254 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.46x | —+— | — | — | 1 | 30.3 |
| tsvc_b1/s254 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.43x | —+— | — | — | 1 | 24.0 |
| tsvc_b1/s254 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 2.71x | —+— | — | — | 1 | 43.9 |
| tsvc_b1/s254 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 3.48x | —+— | — | — | 1 | 21.1 |
| tsvc_b1/s254 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 3.52x | —+— | — | — | 1 | 46.5 |
| tsvc_b1/s255 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.38x | —+— | — | — | 1 | 35.9 |
| tsvc_b1/s255 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.44x | —+— | — | — | 1 | 37.7 |
| tsvc_b1/s255 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.40x | —+— | — | — | 1 | 35.3 |
| tsvc_b1/s255 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 3.39x | —+— | — | — | 1 | 34.2 |
| tsvc_b1/s255 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 3.46x | —+— | — | — | 1 | 42.7 |
| tsvc_b1/s281 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.26x | —+— | — | — | 1 | 47.1 |
| tsvc_b1/s281 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.29x | —+— | — | — | 1 | 60.3 |
| tsvc_b1/s281 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.44x | —+— | — | — | 1 | 29.7 |
| tsvc_b1/s281 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 3.41x | —+— | — | — | 1 | 39.6 |
| tsvc_b1/s281 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 3.08x | —+— | — | — | 1 | 34.3 |
| tsvc_b1/s291 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.52x | —+— | — | — | 1 | 28.4 |
| tsvc_b1/s291 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.46x | —+— | — | — | 1 | 35.4 |
| tsvc_b1/s291 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.43x | —+— | — | — | 1 | 28.4 |
| tsvc_b1/s291 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 3.37x | —+— | — | — | 1 | 18.8 |
| tsvc_b1/s291 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 3.43x | —+— | — | — | 1 | 22.3 |
| tsvc_b1/s292 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.62x | —+— | — | — | 1 | 48.6 |
| tsvc_b1/s292 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 3.47x | —+— | — | — | 1 | 36.5 |
| tsvc_b1/s292 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.56x | —+— | — | — | 1 | 35.7 |
| tsvc_b1/s292 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 3.52x | —+— | — | — | 1 | 32.2 |
| tsvc_b1/s292 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 3.72x | —+— | — | — | 1 | 39.7 |
| tsvc_b1/s293 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.88x | —+— | — | — | 1 | 17.2 |
| tsvc_b1/s293 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 2.89x | —+— | — | — | 1 | 25.3 |
| tsvc_b1/s293 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 2.90x | —+— | — | — | 1 | 20.5 |
| tsvc_b1/s293 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 2.82x | —+— | — | — | 1 | 38.0 |
| tsvc_b1/s293 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 2.82x | —+— | — | — | 1 | 40.9 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.41x | —+— | — | — | 1 | 77.1 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 2.92x | —+— | — | — | 1 | 72.6 |
| tsvc_b1/s3112 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.40x | —+— | — | — | 1 | 128.4 |
| tsvc_b1/s313 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 5.61x | —+— | — | — | 1 | 54.1 |
| tsvc_b1/s321 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 4.89x | —+— | — | — | 1 | 117.0 |
| tsvc_b1/s321 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 4.80x | —+— | — | — | 1 | 165.1 |
| tsvc_b1/s321 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 5.02x | —+— | — | — | 1 | 126.7 |
| tsvc_b1/s322 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 3.55x | —+— | — | — | 2 | 295.0 |
| tsvc_b1/s322 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 2.92x | —+— | — | — | 2 | 295.8 |
| tsvc_b1/s322 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 3.76x | —+— | — | — | 1 | 281.9 |
| tsvc_b1/s323 | bare_llm_v3 | claude-fable-5-1 | 1 | parallel-not-faster | 0.80x | —+— | — | — | 1 | 128.9 |
| tsvc_b1/s323 | bare_llm_v3 | claude-fable-5-1 | 2 | parallel-not-faster | 0.76x | —+— | — | — | 1 | 339.8 |
| tsvc_b1/s323 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 2.68x | —+— | — | — | 1 | 152.0 |
| tsvc_b1/s331 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 4.37x | —+— | — | — | 1 | 24.4 |
| tsvc_b1/s331 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 4.75x | —+— | — | — | 1 | 39.2 |
| tsvc_b1/s331 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 4.59x | —+— | — | — | 1 | 25.9 |
| tsvc_b1/s331 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 4.54x | —+— | — | — | 1 | 25.7 |
| tsvc_b1/s331 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 4.55x | —+— | — | — | 1 | 25.7 |
| tsvc_b1/s341 | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.38x | —+— | — | — | 1 | 35.9 |
| tsvc_b1/s341 | bare_llm_v3 | claude-fable-5-1 | 2 | FASTER | 2.32x | —+— | — | — | 1 | 53.7 |
| tsvc_b1/s341 | bare_llm_v3 | claude-fable-5-1 | 3 | FASTER | 2.38x | —+— | — | — | 1 | 57.1 |
| tsvc_b1/s341 | bare_llm_v3 | claude-fable-5-1 | 4 | FASTER | 2.36x | —+— | — | — | 1 | 57.4 |
| tsvc_b1/s341 | bare_llm_v3 | claude-fable-5-1 | 5 | FASTER | 2.39x | —+— | — | — | 1 | 41.2 |
| tsvc_b1/vpvtv | bare_llm_v3 | claude-fable-5-1 | 1 | FASTER | 2.90x | —+— | — | — | 1 | 39.1 |
