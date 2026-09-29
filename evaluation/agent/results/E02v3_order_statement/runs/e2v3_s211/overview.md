# Agent experiment run `e2v3_s211`

- status: finished (created 2026-09-29T05:04:51, finished 2026-09-29T07:43:17)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `dc97e27e6651adb79012c2c861fe050676bda539` (uncommitted diff sha256 `None`)
- harness: `dc97e27e6651adb79012c2c861fe050676bda539` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 3 | 0 | 0 | 0 | 6 | 0 | 1 | 0 | 0 | 0 | 172 | 10 |
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 6 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 122 | 12 |
| no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 7 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 164 | 17 |
| twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 1 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 0 | 0 | 120 | 10 |
| twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 3 | 1 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 122 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.01x | —+— | — | — | 1 | 195.0 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | 2.97x | —+— | — | — | 1 | 173.2 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | — | —+— | — | — | 1 | 219.1 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 170.9 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 1.40x | —+— | — | — | 1 | 85.6 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.35x | —+— | — | — | 1 | 254.9 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 2.71x | —+— | — | — | 1 | 286.2 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 1.05x | —+— | — | — | 1 | 147.7 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 0.91x | —+— | — | — | 1 | 78.9 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 1.07x | —+— | — | — | 1 | 94.7 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 1 | 87.9 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.14x | 1+0 | 1 | 0 | 1 | 98.0 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.10x | 1+0 | 1 | 0 | 1 | 73.2 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.35x | 2+0 | 1 | 0 | 1 | 113.8 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 1 | 119.3 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.92x | 2+0 | 1 | 0 | 1 | 158.3 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.32x | 2+0 | 1 | 0 | 2 | 140.5 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.28x | 2+0 | 1 | 0 | 1 | 125.1 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.10x | 1+0 | 1 | 0 | 2 | 235.0 |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.80x | 3+0 | 1 | 0 | 1 | 277.6 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 2 | 158.0 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.15x | 1+0 | 1 | 0 | 3 | 315.4 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.15x | 1+0 | 1 | 0 | 1 | 143.8 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.82x | 2+0 | 1 | 0 | 1 | 145.9 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.13x | 1+0 | 1 | 0 | 3 | 197.6 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.28x | 2+0 | 1 | 0 | 2 | 368.2 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | parallel-not-faster | 0.35x | 2+0 | 1 | 0 | 1 | 171.0 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.36x | 2+0 | 1 | 0 | 1 | 131.9 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.10x | 1+0 | 1 | 0 | 2 | 347.8 |
| tsvc_b1/s211 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.16x | 1+0 | 1 | 0 | 1 | 146.4 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 1.87x | —+— | — | — | 1 | 239.1 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | 1.55x | —+— | — | — | 1 | 136.0 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.88x | —+— | — | — | 1 | 158.1 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.87x | —+— | — | — | 1 | 91.4 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 2.91x | —+— | — | — | 1 | 73.3 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.79x | —+— | — | — | 1 | 122.3 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 2.86x | —+— | — | — | 1 | 110.6 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | SCAFFOLD_MODIFIED | 1.18x | —+— | — | — | 1 | 117.4 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 2.92x | —+— | — | — | 1 | 99.7 |
| tsvc_b1/s211 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 3.02x | —+— | — | — | 1 | 198.2 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.34x | —+— | — | — | 1 | 60.1 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | 2.99x | —+— | — | — | 1 | 82.1 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.99x | —+— | — | — | 1 | 114.7 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.91x | —+— | — | — | 1 | 128.4 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.03x | —+— | — | — | 1 | 153.7 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.03x | —+— | — | — | 1 | 208.0 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 2.90x | —+— | — | — | 1 | 111.5 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | 0.35x | —+— | — | — | 1 | 106.3 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | parallel-not-faster | 0.71x | —+— | — | — | 1 | 225.6 |
| tsvc_b1/s211 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 2.30x | —+— | — | — | 1 | 253.2 |
