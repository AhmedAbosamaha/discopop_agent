# Agent experiment run `e2b1_b_1`

- status: finished (created 2026-09-28T01:30:01, finished 2026-09-28T10:00:06)
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
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 25 | 18 | 2 | 0 | 0 | 1 | 0 | 0 | 4 | 0 | 0 | 0 | 45 | 25 |
| full_b1_nospeed | claude-haiku-4-5-20251001 | 25 | 12 | 10 | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 256 | 41 |
| no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 25 | 19 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 110 | 25 |
| twin_full_nospeed | claude-haiku-4-5-20251001 | 25 | 10 | 5 | 0 | 0 | 0 | 5 | 3 | 2 | 0 | 0 | 0 | 182 | 28 |
| twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 25 | 16 | 3 | 0 | 0 | 0 | 4 | 0 | 2 | 0 | 0 | 0 | 102 | 28 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.47x | —+— | — | — | 1 | 41.5 |
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.48x | —+— | — | — | 1 | 22.9 |
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.25x | —+— | — | — | 1 | 38.5 |
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 2.88x | —+— | — | — | 1 | 30.3 |
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.66x | —+— | — | — | 1 | 34.3 |
| tsvc_b1/s152 | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 617.3 |
| tsvc_b1/s152 | full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.03x | 2+0 | 2 | 1 | 3 | 370.6 |
| tsvc_b1/s152 | full_b1_nospeed | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 645.3 |
| tsvc_b1/s152 | full_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.36x | 2+0 | 1 | 1 | 2 | 288.0 |
| tsvc_b1/s152 | full_b1_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.52x | 1+0 | 1 | 1 | 3 | 397.7 |
| tsvc_b1/s152 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.31x | 1+0 | 1 | 1 | 1 | 70.0 |
| tsvc_b1/s152 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.44x | 1+0 | 1 | 1 | 1 | 39.2 |
| tsvc_b1/s152 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.46x | 1+0 | 1 | 1 | 1 | 59.8 |
| tsvc_b1/s152 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.58x | 1+0 | 1 | 1 | 1 | 37.0 |
| tsvc_b1/s152 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.28x | 1+0 | 1 | 1 | 1 | 71.6 |
| tsvc_b1/s152 | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 2.97x | —+— | — | — | 2 | 266.1 |
| tsvc_b1/s152 | twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.44x | —+— | — | — | 1 | 194.9 |
| tsvc_b1/s152 | twin_full_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.44x | —+— | — | — | 1 | 99.7 |
| tsvc_b1/s152 | twin_full_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 2.74x | —+— | — | — | 2 | 478.9 |
| tsvc_b1/s152 | twin_full_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | — | —+— | — | — | 2 | 340.4 |
| tsvc_b1/s152 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 2.37x | —+— | — | — | 2 | 122.4 |
| tsvc_b1/s152 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.57x | —+— | — | — | 2 | 182.3 |
| tsvc_b1/s152 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.03x | —+— | — | — | 2 | 259.8 |
| tsvc_b1/s152 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.06x | —+— | — | — | 1 | 50.6 |
| tsvc_b1/s152 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.63x | —+— | — | — | 1 | 41.6 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.58x | —+— | — | — | 1 | 41.2 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 32.7 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.58x | —+— | — | — | 1 | 60.6 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 17.0 |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | —+— | — | — | 1 | 20.0 |
| tsvc_b1/s171 | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.88x | 1+0 | 1 | 1 | 3 | 256.9 |
| tsvc_b1/s171 | full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.70x | 1+0 | 1 | 1 | 1 | 133.9 |
| tsvc_b1/s171 | full_b1_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.15x | 1+0 | 1 | 1 | 2 | 324.2 |
| tsvc_b1/s171 | full_b1_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.84x | 1+0 | 1 | 1 | 1 | 144.3 |
| tsvc_b1/s171 | full_b1_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | — | 1+0 | 1 | 1 | 2 | 283.3 |
| tsvc_b1/s171 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.37x | 1+0 | 1 | 1 | 1 | 147.3 |
| tsvc_b1/s171 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.70x | 1+0 | 1 | 1 | 1 | 105.7 |
| tsvc_b1/s171 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.32x | 1+0 | 1 | 1 | 1 | 91.8 |
| tsvc_b1/s171 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.40x | 1+0 | 1 | 1 | 1 | 102.2 |
| tsvc_b1/s171 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.73x | 1+0 | 1 | 1 | 1 | 147.0 |
| tsvc_b1/s171 | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | — | —+— | — | — | 1 | 154.9 |
| tsvc_b1/s171 | twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | — | —+— | — | — | 1 | 129.9 |
| tsvc_b1/s171 | twin_full_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.19x | —+— | — | — | 1 | 259.2 |
| tsvc_b1/s171 | twin_full_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.66x | —+— | — | — | 1 | 228.7 |
| tsvc_b1/s171 | twin_full_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.14x | —+— | — | — | 1 | 177.0 |
| tsvc_b1/s171 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.73x | —+— | — | — | 1 | 87.7 |
| tsvc_b1/s171 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.52x | —+— | — | — | 1 | 71.4 |
| tsvc_b1/s171 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.09x | —+— | — | — | 1 | 85.2 |
| tsvc_b1/s171 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.35x | —+— | — | — | 1 | 142.5 |
| tsvc_b1/s171 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | 6.24x | —+— | — | — | 1 | 102.2 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 1.32x | —+— | — | — | 1 | 193.4 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 148.5 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 281.1 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.17x | —+— | — | — | 1 | 184.0 |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.23x | —+— | — | — | 1 | 222.8 |
| tsvc_b1/s277 | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.86x | 3+0 | 1 | 1 | 1 | 201.9 |
| tsvc_b1/s277 | full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 5.36x | 2+0 | 1 | 1 | 1 | 255.6 |
| tsvc_b1/s277 | full_b1_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 8.93x | 1+0 | 1 | 1 | 1 | 152.8 |
| tsvc_b1/s277 | full_b1_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.03x | 3+0 | 1 | 1 | 1 | 195.3 |
| tsvc_b1/s277 | full_b1_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 4.50x | 2+0 | 1 | 1 | 1 | 196.6 |
| tsvc_b1/s277 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 8.67x | 1+0 | 1 | 1 | 1 | 182.3 |
| tsvc_b1/s277 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 8.41x | 1+0 | 1 | 1 | 1 | 44.0 |
| tsvc_b1/s277 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.17x | 2+0 | 1 | 1 | 1 | 155.3 |
| tsvc_b1/s277 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 8.17x | 1+0 | 1 | 1 | 1 | 190.8 |
| tsvc_b1/s277 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.72x | 2+0 | 1 | 1 | 1 | 266.2 |
| tsvc_b1/s277 | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 8.21x | —+— | — | — | 1 | 142.3 |
| tsvc_b1/s277 | twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 8.87x | —+— | — | — | 1 | 161.2 |
| tsvc_b1/s277 | twin_full_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.71x | —+— | — | — | 1 | 290.9 |
| tsvc_b1/s277 | twin_full_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 5.57x | —+— | — | — | 1 | 219.7 |
| tsvc_b1/s277 | twin_full_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.09x | —+— | — | — | 1 | 171.1 |
| tsvc_b1/s277 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 7.22x | —+— | — | — | 1 | 137.7 |
| tsvc_b1/s277 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 156.2 |
| tsvc_b1/s277 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 8.48x | —+— | — | — | 1 | 231.3 |
| tsvc_b1/s277 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.78x | —+— | — | — | 1 | 191.6 |
| tsvc_b1/s277 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 2.40x | —+— | — | — | 1 | 101.3 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 2.67x | —+— | — | — | 1 | 45.1 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 2.57x | —+— | — | — | 1 | 70.2 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 1.91x | —+— | — | — | 1 | 86.6 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 2.70x | —+— | — | — | 1 | 153.0 |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 1.83x | —+— | — | — | 1 | 68.7 |
| tsvc_b1/s481 | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 2.90x | 1+0 | 1 | 2 | 2 | 354.4 |
| tsvc_b1/s481 | full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.21x | 1+0 | 1 | 2 | 1 | 104.1 |
| tsvc_b1/s481 | full_b1_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.61x | 1+0 | 1 | 2 | 2 | 245.9 |
| tsvc_b1/s481 | full_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 2.68x | 2+0 | 1 | 2 | 3 | 358.3 |
| tsvc_b1/s481 | full_b1_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.10x | 1+0 | 1 | 2 | 1 | 155.1 |
| tsvc_b1/s481 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.01x | 2+0 | 1 | 2 | 1 | 109.5 |
| tsvc_b1/s481 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.25x | 2+0 | 1 | 2 | 1 | 72.3 |
| tsvc_b1/s481 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.12x | 2+0 | 1 | 2 | 1 | 138.8 |
| tsvc_b1/s481 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.91x | 2+0 | 1 | 2 | 1 | 56.5 |
| tsvc_b1/s481 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.80x | 2+0 | 1 | 2 | 1 | 78.4 |
| tsvc_b1/s481 | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 222.0 |
| tsvc_b1/s481 | twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.20x | —+— | — | — | 1 | 67.0 |
| tsvc_b1/s481 | twin_full_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 2.67x | —+— | — | — | 1 | 182.3 |
| tsvc_b1/s481 | twin_full_nospeed | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 176.3 |
| tsvc_b1/s481 | twin_full_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.39x | —+— | — | — | 1 | 165.9 |
| tsvc_b1/s481 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.58x | —+— | — | — | 1 | 116.9 |
| tsvc_b1/s481 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | 4.17x | —+— | — | — | 1 | 159.9 |
| tsvc_b1/s481 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 2.65x | —+— | — | — | 1 | 147.3 |
| tsvc_b1/s481 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 54.1 |
| tsvc_b1/s481 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.95x | —+— | — | — | 1 | 23.9 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.66x | —+— | — | — | 1 | 40.3 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.63x | —+— | — | — | 1 | 31.1 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.58x | —+— | — | — | 1 | 31.0 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.59x | —+— | — | — | 1 | 65.5 |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.66x | —+— | — | — | 1 | 66.0 |
| tsvc_b1/vas | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 2.08x | 2+0 | 1 | 1 | 1 | 195.4 |
| tsvc_b1/vas | full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.17x | 1+0 | 1 | 1 | 1 | 275.6 |
| tsvc_b1/vas | full_b1_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 1.11x | 1+0 | 1 | 1 | 1 | 182.7 |
| tsvc_b1/vas | full_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 2.05x | 2+0 | 1 | 1 | 1 | 141.1 |
| tsvc_b1/vas | full_b1_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.63x | 2+0 | 1 | 1 | 2 | 379.7 |
| tsvc_b1/vas | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.20x | 2+0 | 1 | 1 | 1 | 138.9 |
| tsvc_b1/vas | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.55x | 2+0 | 1 | 1 | 1 | 166.2 |
| tsvc_b1/vas | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.80x | 2+0 | 1 | 1 | 1 | 123.8 |
| tsvc_b1/vas | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.02x | 1+0 | 1 | 1 | 1 | 112.5 |
| tsvc_b1/vas | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 1.63x | 2+0 | 1 | 1 | 1 | 137.7 |
| tsvc_b1/vas | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 1.00x | —+— | — | — | 1 | 289.3 |
| tsvc_b1/vas | twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 1.62x | —+— | — | — | 1 | 279.9 |
| tsvc_b1/vas | twin_full_nospeed | claude-haiku-4-5-20251001 | 3 | SCAFFOLD_MODIFIED | — | —+— | — | — | 1 | 214.3 |
| tsvc_b1/vas | twin_full_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 1.50x | —+— | — | — | 1 | 160.9 |
| tsvc_b1/vas | twin_full_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.02x | —+— | — | — | 1 | 144.9 |
| tsvc_b1/vas | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | FASTER | 3.59x | —+— | — | — | 1 | 91.6 |
| tsvc_b1/vas | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 3.67x | —+— | — | — | 1 | 97.7 |
| tsvc_b1/vas | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 3 | FASTER | 3.57x | —+— | — | — | 1 | 94.0 |
| tsvc_b1/vas | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 4 | FASTER | 3.77x | —+— | — | — | 1 | 77.4 |
| tsvc_b1/vas | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 5 | FASTER | 3.47x | —+— | — | — | 1 | 112.3 |
