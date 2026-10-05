# Agent experiment run `e2b1_a_1`

- status: finished (created 2026-09-28T01:29:54, finished 2026-09-28T09:37:28)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `7f76a31050f720f76507ebd200d0969c4db8ad5b` (uncommitted diff sha256 `None`)
- harness: `7f76a31050f720f76507ebd200d0969c4db8ad5b` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 20 | 3 | 8 | 0 | 0 | 0 | 8 | 0 | 1 | 0 | 0 | 0 | 111 | 20 |
| full_b1_nospeed | claude-haiku-4-5-20251001 | 20 | 8 | 8 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 382 | 46 |
| no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 20 | 11 | 6 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 190 | 37 |
| twin_full_nospeed | claude-haiku-4-5-20251001 | 20 | 2 | 1 | 0 | 4 | 0 | 10 | 1 | 2 | 0 | 0 | 0 | 166 | 24 |
| twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 20 | 8 | 2 | 0 | 6 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 121 | 23 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.47x | —+— | — | — | 1 | 132.8 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.15x | —+— | — | — | 1 | 85.7 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.47x | —+— | — | — | 1 | 96.3 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.82x | —+— | — | — | 1 | 46.8 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.44x | —+— | — | — | 1 | 113.1 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 97.6 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 6 | parallel-not-faster | 0.15x | —+— | — | — | 1 | 175.3 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 7 | VERIFY_FAILED | — | —+— | — | — | 1 | 63.5 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 8 | parallel-not-faster | 0.38x | —+— | — | — | 1 | 157.8 |
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 97.9 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.40x | 2+0 | 1 | 0 | 3 | 577.3 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.80x | 1+0 | 1 | 0 | 1 | 79.5 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.43x | 2+0 | 1 | 0 | 3 | 536.6 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.35x | 2+0 | 1 | 0 | 3 | 497.3 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.15x | 1+0 | 1 | 0 | 3 | 355.4 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.46x | 2+0 | 1 | 0 | 2 | 332.5 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 6 | parallel-not-faster | 0.50x | 2+0 | 1 | 0 | 4 | 312.1 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.93x | 1+0 | 1 | 0 | 3 | 513.2 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 8 | FASTER | 1.41x | 2+0 | 1 | 0 | 1 | 191.1 |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | 9 | FASTER | 1.36x | 2+0 | 1 | 0 | 2 | 398.7 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.43x | 2+0 | 1 | 0 | 2 | 166.3 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.42x | 2+0 | 1 | 0 | 2 | 237.8 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 1.49x | 2+0 | 1 | 0 | 1 | 103.9 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 1.39x | 2+0 | 1 | 0 | 2 | 136.7 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 1.43x | 2+0 | 1 | 0 | 2 | 268.4 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.45x | 2+0 | 1 | 0 | 3 | 219.2 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 6 | FASTER | 1.45x | 2+0 | 1 | 0 | 1 | 69.0 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.14x | 1+0 | 1 | 0 | 2 | 178.4 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 8 | FASTER | 1.51x | 2+0 | 1 | 0 | 2 | 239.7 |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.79x | 1+0 | 1 | 0 | 2 | 114.0 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.14x | —+— | — | — | 2 | 324.8 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 10 | FASTER | 1.43x | —+— | — | — | 1 | 109.8 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | changed-not-parallel | 1.01x | —+— | — | — | 1 | 120.9 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 3 | SCAFFOLD_MODIFIED | — | —+— | — | — | 2 | 273.3 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 4 | changed-not-parallel | 1.02x | —+— | — | — | 1 | 169.9 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | — | —+— | — | — | 1 | 200.1 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 6 | changed-not-parallel | 1.00x | —+— | — | — | 1 | 184.6 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 7 | BROKEN | 0.51x | —+— | — | — | 2 | 284.6 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | 0.64x | —+— | — | — | 2 | 344.5 |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | 9 | changed-not-parallel | 0.97x | —+— | — | — | 1 | 111.3 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 1.44x | —+— | — | — | 1 | 131.7 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.45x | —+— | — | — | 2 | 161.7 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 1.50x | —+— | — | — | 1 | 71.9 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 3 | changed-not-parallel | 0.98x | —+— | — | — | 1 | 68.8 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 1.50x | —+— | — | — | 1 | 115.2 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 5 | changed-not-parallel | 1.01x | —+— | — | — | 1 | 43.3 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 6 | changed-not-parallel | 1.04x | —+— | — | — | 1 | 113.2 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 7 | BROKEN | 0.15x | —+— | — | — | 2 | 217.2 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 8 | parallel-not-faster | 0.80x | —+— | — | — | 2 | 160.7 |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 9 | changed-not-parallel | 1.02x | —+— | — | — | 1 | 90.5 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 0.66x | —+— | — | — | 1 | 174.1 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 10 | BROKEN | 0.44x | —+— | — | — | 1 | 150.4 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 1.75x | —+— | — | — | 1 | 108.3 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 1.73x | —+— | — | — | 1 | 215.7 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | BROKEN | 1.82x | —+— | — | — | 1 | 83.6 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | 2.16x | —+— | — | — | 1 | 241.7 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 6 | BROKEN | 1.90x | —+— | — | — | 1 | 76.4 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 7 | FASTER | 1.84x | —+— | — | — | 1 | 105.0 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | 0.65x | —+— | — | — | 1 | 160.5 |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.90x | —+— | — | — | 1 | 254.1 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 2.17x | 2+0 | 1 | 0 | 1 | 216.8 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 10 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 623.9 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 2.17x | 2+0 | 1 | 0 | 2 | 444.4 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 2.29x | 2+0 | 1 | 0 | 2 | 336.4 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 2.15x | 2+0 | 1 | 0 | 1 | 200.6 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 2.29x | 2+0 | 1 | 0 | 1 | 305.6 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 6 | FASTER | 2.40x | 2+0 | 1 | 0 | 2 | 364.6 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 460.6 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 471.7 |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 464.6 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 247.3 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 10 | FASTER | 2.20x | 2+0 | 1 | 0 | 1 | 75.2 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 1.42x | 2+0 | 1 | 0 | 3 | 357.1 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 1.62x | 2+0 | 1 | 0 | 1 | 65.7 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 1.71x | 2+0 | 1 | 0 | 1 | 148.2 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 1.78x | 2+0 | 1 | 0 | 1 | 168.0 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 6 | parallel-not-faster | 0.82x | 2+0 | 1 | 0 | 1 | 256.3 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 438.9 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 304.8 |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 9 | FASTER | 2.21x | 2+0 | 1 | 0 | 1 | 201.8 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.29x | —+— | — | — | 1 | 150.4 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 10 | VERIFY_FAILED | — | —+— | — | — | 1 | 114.6 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 2.28x | —+— | — | — | 1 | 161.5 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 334.5 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 4 | BROKEN | 1.55x | —+— | — | — | 1 | 383.6 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.53x | —+— | — | — | 1 | 112.5 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 6 | BROKEN | 1.96x | —+— | — | — | 1 | 113.8 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 7 | BROKEN | 1.06x | —+— | — | — | 1 | 155.4 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | 1.74x | —+— | — | — | 1 | 98.4 |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | 9 | BROKEN | 1.69x | —+— | — | — | 1 | 371.3 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 1.51x | —+— | — | — | 1 | 127.3 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 10 | FASTER | 1.76x | —+— | — | — | 1 | 179.8 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | 1.57x | —+— | — | — | 1 | 144.2 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 3 | changed-not-parallel | 1.00x | —+— | — | — | 1 | 109.0 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 1.50x | —+— | — | — | 1 | 99.5 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.55x | —+— | — | — | 1 | 256.9 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 6 | changed-not-parallel | 1.01x | —+— | — | — | 1 | 93.2 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 7 | FASTER | 1.60x | —+— | — | — | 1 | 130.7 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 8 | FASTER | 1.52x | —+— | — | — | 1 | 129.5 |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 9 | FASTER | 1.55x | —+— | — | — | 1 | 62.9 |
