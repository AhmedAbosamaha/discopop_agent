# Agent experiment run `e2c_ab_2`

- status: finished (created 2026-09-25T05:15:28, finished 2026-09-25T19:29:57)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `3f296eacdeacea41bd3e9104ca0c2f7cfd4c0e20` (uncommitted diff sha256 `None`)
- harness: `3f296eacdeacea41bd3e9104ca0c2f7cfd4c0e20` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1 | claude-haiku-4-5-20251001 | 25 | 7 | 1 | 0 | 0 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 486 | 34 |
| no_evidence | claude-haiku-4-5-20251001 | 25 | 12 | 3 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 310 | 26 |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 25 | 10 | 3 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 385 | 31 |
| twin_dp | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 5 | 20 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| twin_full | claude-haiku-4-5-20251001 | 25 | 4 | 6 | 0 | 2 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 166 | 27 |
| twin_no_evidence | claude-haiku-4-5-20251001 | 25 | 8 | 6 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 129 | 25 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s212 | full_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 248.3 |
| tsvc/s212 | full_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.29x | 1+0 | 1 | 0 | 2 | 345.5 |
| tsvc/s212 | full_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.05x | 2+0 | 1 | 0 | 2 | 366.4 |
| tsvc/s212 | full_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.18x | 2+0 | 1 | 0 | 1 | 228.8 |
| tsvc/s212 | full_b1 | claude-haiku-4-5-20251001 | 5 | no-change | 1.03x | 0+0 | 0 | 0 | 1 | 409.1 |
| tsvc/s212 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.42x | 2+0 | 1 | 0 | 1 | 158.0 |
| tsvc/s212 | no_evidence | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 1 | 206.9 |
| tsvc/s212 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.25x | 1+0 | 1 | 0 | 1 | 194.9 |
| tsvc/s212 | no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 1.24x | 1+0 | 1 | 0 | 1 | 167.5 |
| tsvc/s212 | no_evidence | claude-haiku-4-5-20251001 | 5 | FASTER | 2.51x | 2+0 | 1 | 0 | 1 | 237.4 |
| tsvc/s212 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 2 | 371.5 |
| tsvc/s212 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.66x | 2+0 | 1 | 0 | 1 | 171.3 |
| tsvc/s212 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 1 | 302.4 |
| tsvc/s212 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 349.4 |
| tsvc/s212 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.22x | 2+0 | 1 | 0 | 1 | 169.4 |
| tsvc/s212 | twin_dp | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | —+— | — | — | 0 | 1.7 |
| tsvc/s212 | twin_dp | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | —+— | — | — | 0 | 1.8 |
| tsvc/s212 | twin_dp | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | —+— | — | — | 0 | 1.7 |
| tsvc/s212 | twin_dp | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | —+— | — | — | 0 | 1.7 |
| tsvc/s212 | twin_dp | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | —+— | — | — | 0 | 1.7 |
| tsvc/s212 | twin_full | claude-haiku-4-5-20251001 | 1 | FASTER | 1.64x | —+— | — | — | 1 | 157.1 |
| tsvc/s212 | twin_full | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.24x | —+— | — | — | 1 | 109.1 |
| tsvc/s212 | twin_full | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.27x | —+— | — | — | 1 | 140.0 |
| tsvc/s212 | twin_full | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.37x | —+— | — | — | 1 | 88.9 |
| tsvc/s212 | twin_full | claude-haiku-4-5-20251001 | 5 | FASTER | 1.19x | —+— | — | — | 1 | 162.7 |
| tsvc/s212 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.27x | —+— | — | — | 1 | 79.3 |
| tsvc/s212 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.36x | —+— | — | — | 1 | 95.1 |
| tsvc/s212 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.65x | —+— | — | — | 1 | 113.4 |
| tsvc/s212 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 1.17x | —+— | — | — | 1 | 68.2 |
| tsvc/s212 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.14x | —+— | — | — | 1 | 34.6 |
| tsvc/s241 | full_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 606.7 |
| tsvc/s241 | full_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.30x | 1+0 | 1 | 1 | 2 | 894.5 |
| tsvc/s241 | full_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 1 | 2 | 863.3 |
| tsvc/s241 | full_b1 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 595.5 |
| tsvc/s241 | full_b1 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 576.7 |
| tsvc/s241 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 631.4 |
| tsvc/s241 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 1.50x | 3+0 | 1 | 1 | 1 | 593.1 |
| tsvc/s241 | no_evidence | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 460.0 |
| tsvc/s241 | no_evidence | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 757.8 |
| tsvc/s241 | no_evidence | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 469.9 |
| tsvc/s241 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 391.5 |
| tsvc/s241 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.11x | 0+0 | 0 | 1 | 1 | 804.1 |
| tsvc/s241 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 1.07x | 0+0 | 0 | 1 | 1 | 542.3 |
| tsvc/s241 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | no-change | 1.04x | 0+0 | 0 | 1 | 1 | 642.5 |
| tsvc/s241 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 631.8 |
| tsvc/s241 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.65x | —+— | — | — | 0 | 1.8 |
| tsvc/s241 | twin_dp | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.89x | —+— | — | — | 0 | 1.7 |
| tsvc/s241 | twin_dp | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.81x | —+— | — | — | 0 | 1.7 |
| tsvc/s241 | twin_dp | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.63x | —+— | — | — | 0 | 1.6 |
| tsvc/s241 | twin_dp | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.78x | —+— | — | — | 0 | 1.8 |
| tsvc/s241 | twin_full | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.87x | —+— | — | — | 1 | 250.1 |
| tsvc/s241 | twin_full | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.31x | —+— | — | — | 1 | 90.6 |
| tsvc/s241 | twin_full | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.37x | —+— | — | — | 1 | 358.7 |
| tsvc/s241 | twin_full | claude-haiku-4-5-20251001 | 4 | BROKEN | 0.45x | —+— | — | — | 1 | 149.5 |
| tsvc/s241 | twin_full | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.29x | —+— | — | — | 1 | 207.3 |
| tsvc/s241 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.69x | —+— | — | — | 1 | 204.1 |
| tsvc/s241 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.95x | —+— | — | — | 1 | 164.2 |
| tsvc/s241 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.41x | —+— | — | — | 1 | 144.1 |
| tsvc/s241 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | BROKEN | 1.10x | —+— | — | — | 1 | 63.5 |
| tsvc/s241 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.91x | —+— | — | — | 1 | 135.1 |
| tsvc/s243 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.05x | 2+0 | 1 | 1 | 1 | 505.9 |
| tsvc/s243 | full_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 611.1 |
| tsvc/s243 | full_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 1 | 1 | 747.2 |
| tsvc/s243 | full_b1 | claude-haiku-4-5-20251001 | 4 | no-change | 0.94x | 0+0 | 0 | 1 | 1 | 846.3 |
| tsvc/s243 | full_b1 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.06x | 1+0 | 1 | 1 | 1 | 460.2 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 643.5 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.03x | 1+0 | 1 | 1 | 1 | 508.4 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.09x | 2+0 | 1 | 1 | 1 | 593.7 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 731.6 |
| tsvc/s243 | no_evidence | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 581.9 |
| tsvc/s243 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.06x | 2+0 | 1 | 1 | 1 | 576.1 |
| tsvc/s243 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.10x | 0+0 | 0 | 1 | 1 | 508.1 |
| tsvc/s243 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 1 | 2 | 638.8 |
| tsvc/s243 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.01x | 2+0 | 1 | 1 | 1 | 515.2 |
| tsvc/s243 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.02x | 1+0 | 1 | 1 | 1 | 451.4 |
| tsvc/s243 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.78x | —+— | — | — | 0 | 1.7 |
| tsvc/s243 | twin_dp | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.83x | —+— | — | — | 0 | 1.6 |
| tsvc/s243 | twin_dp | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.67x | —+— | — | — | 0 | 1.7 |
| tsvc/s243 | twin_dp | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.73x | —+— | — | — | 0 | 1.7 |
| tsvc/s243 | twin_dp | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.76x | —+— | — | — | 0 | 1.6 |
| tsvc/s243 | twin_full | claude-haiku-4-5-20251001 | 1 | changed-not-parallel | 1.04x | —+— | — | — | 1 | 154.1 |
| tsvc/s243 | twin_full | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.44x | —+— | — | — | 1 | 291.9 |
| tsvc/s243 | twin_full | claude-haiku-4-5-20251001 | 3 | FASTER | 1.97x | —+— | — | — | 1 | 316.5 |
| tsvc/s243 | twin_full | claude-haiku-4-5-20251001 | 4 | FASTER | 1.88x | —+— | — | — | 1 | 128.5 |
| tsvc/s243 | twin_full | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.81x | —+— | — | — | 1 | 225.0 |
| tsvc/s243 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | BROKEN | 0.70x | —+— | — | — | 1 | 191.7 |
| tsvc/s243 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.67x | —+— | — | — | 1 | 180.8 |
| tsvc/s243 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 1.25x | —+— | — | — | 1 | 108.8 |
| tsvc/s243 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | BROKEN | 0.64x | —+— | — | — | 1 | 222.0 |
| tsvc/s243 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | FASTER | 2.08x | —+— | — | — | 1 | 83.4 |
| tsvc/s244 | full_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 2 | 537.1 |
| tsvc/s244 | full_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 406.7 |
| tsvc/s244 | full_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 352.9 |
| tsvc/s244 | full_b1 | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 1 | 1 | 510.8 |
| tsvc/s244 | full_b1 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 940.6 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 302.3 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 4.10x | 1+0 | 1 | 1 | 1 | 355.6 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 700.2 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 1.57x | 1+0 | 1 | 1 | 1 | 304.1 |
| tsvc/s244 | no_evidence | claude-haiku-4-5-20251001 | 5 | FASTER | 3.61x | 1+0 | 1 | 1 | 1 | 309.7 |
| tsvc/s244 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.20x | 1+0 | 1 | 1 | 1 | 365.8 |
| tsvc/s244 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 1 | 2 | 561.7 |
| tsvc/s244 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.18x | 2+0 | 1 | 1 | 1 | 364.9 |
| tsvc/s244 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.00x | 1+0 | 1 | 1 | 1 | 384.8 |
| tsvc/s244 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.02x | 1+0 | 1 | 1 | 2 | 494.6 |
| tsvc/s244 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.14x | —+— | — | — | 0 | 1.7 |
| tsvc/s244 | twin_dp | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.85x | —+— | — | — | 0 | 1.7 |
| tsvc/s244 | twin_dp | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.97x | —+— | — | — | 0 | 1.8 |
| tsvc/s244 | twin_dp | claude-haiku-4-5-20251001 | 4 | BROKEN | 4.03x | —+— | — | — | 0 | 1.7 |
| tsvc/s244 | twin_dp | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.97x | —+— | — | — | 0 | 1.7 |
| tsvc/s244 | twin_full | claude-haiku-4-5-20251001 | 1 | changed-not-parallel | 0.63x | —+— | — | — | 1 | 217.7 |
| tsvc/s244 | twin_full | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.27x | —+— | — | — | 1 | 165.6 |
| tsvc/s244 | twin_full | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.33x | —+— | — | — | 1 | 229.9 |
| tsvc/s244 | twin_full | claude-haiku-4-5-20251001 | 4 | BROKEN | 0.44x | —+— | — | — | 1 | 262.2 |
| tsvc/s244 | twin_full | claude-haiku-4-5-20251001 | 5 | BROKEN | 2.45x | —+— | — | — | 1 | 174.7 |
| tsvc/s244 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 1.89x | —+— | — | — | 1 | 247.9 |
| tsvc/s244 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | BROKEN | 1.12x | —+— | — | — | 1 | 86.2 |
| tsvc/s244 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 4.17x | —+— | — | — | 1 | 130.6 |
| tsvc/s244 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 4.18x | —+— | — | — | 1 | 331.8 |
| tsvc/s244 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.04x | —+— | — | — | 1 | 128.7 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 485.5 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 418.1 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.62x | 1+0 | 1 | 1 | 1 | 170.7 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.63x | 1+0 | 1 | 1 | 1 | 211.7 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 270.1 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 2.02x | 2+0 | 1 | 1 | 1 | 211.4 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.97x | 1+0 | 1 | 1 | 1 | 247.8 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 3.62x | 1+0 | 1 | 1 | 1 | 170.1 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 3.62x | 1+0 | 1 | 1 | 1 | 138.0 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 5 | FASTER | 2.02x | 2+0 | 1 | 1 | 1 | 188.9 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.02x | 2+0 | 1 | 1 | 1 | 263.5 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.63x | 1+0 | 1 | 1 | 1 | 135.1 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 368.5 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.00x | 1+0 | 1 | 1 | 1 | 217.9 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.03x | 2+0 | 1 | 1 | 1 | 209.6 |
| tsvc/s252 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.77x | —+— | — | — | 0 | 1.8 |
| tsvc/s252 | twin_dp | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.69x | —+— | — | — | 0 | 1.7 |
| tsvc/s252 | twin_dp | claude-haiku-4-5-20251001 | 3 | BROKEN | 4.13x | —+— | — | — | 0 | 1.8 |
| tsvc/s252 | twin_dp | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.83x | —+— | — | — | 0 | 1.8 |
| tsvc/s252 | twin_dp | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.87x | —+— | — | — | 0 | 1.7 |
| tsvc/s252 | twin_full | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.99x | —+— | — | — | 2 | 210.2 |
| tsvc/s252 | twin_full | claude-haiku-4-5-20251001 | 2 | BROKEN | 0.99x | —+— | — | — | 2 | 223.7 |
| tsvc/s252 | twin_full | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.71x | —+— | — | — | 1 | 119.5 |
| tsvc/s252 | twin_full | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.95x | —+— | — | — | 1 | 154.3 |
| tsvc/s252 | twin_full | claude-haiku-4-5-20251001 | 5 | BROKEN | 4.01x | —+— | — | — | 1 | 116.8 |
| tsvc/s252 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | BROKEN | 1.94x | —+— | — | — | 1 | 152.6 |
| tsvc/s252 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | BROKEN | 0.96x | —+— | — | — | 1 | 78.5 |
| tsvc/s252 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.98x | —+— | — | — | 1 | 40.1 |
| tsvc/s252 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | BROKEN | 0.96x | —+— | — | — | 1 | 130.7 |
| tsvc/s252 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | BROKEN | 2.10x | —+— | — | — | 1 | 78.4 |
