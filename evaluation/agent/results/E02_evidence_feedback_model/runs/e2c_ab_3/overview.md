# Agent experiment run `e2c_ab_3`

- status: finished (created 2026-09-25T05:15:30, finished 2026-09-25T11:48:26)
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
| full_b1 | claude-haiku-4-5-20251001 | 20 | 18 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 186 | 23 |
| no_evidence | claude-haiku-4-5-20251001 | 20 | 16 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 173 | 23 |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 20 | 17 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 153 | 26 |
| twin_dp | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 5 | 15 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| twin_full | claude-haiku-4-5-20251001 | 20 | 2 | 0 | 0 | 0 | 0 | 18 | 0 | 0 | 0 | 0 | 0 | 94 | 21 |
| twin_no_evidence | claude-haiku-4-5-20251001 | 20 | 1 | 1 | 0 | 0 | 0 | 18 | 0 | 0 | 0 | 0 | 0 | 60 | 20 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s254 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.54x | 1+0 | 1 | 2 | 1 | 205.2 |
| tsvc/s254 | full_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.51x | 1+0 | 1 | 2 | 1 | 128.3 |
| tsvc/s254 | full_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.49x | 2+0 | 1 | 2 | 1 | 221.0 |
| tsvc/s254 | full_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.52x | 1+0 | 1 | 2 | 1 | 194.6 |
| tsvc/s254 | full_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.45x | 1+0 | 1 | 2 | 1 | 203.7 |
| tsvc/s254 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.42x | 1+0 | 1 | 2 | 1 | 104.5 |
| tsvc/s254 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 3.57x | 1+0 | 1 | 2 | 1 | 105.3 |
| tsvc/s254 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 3.30x | 1+0 | 1 | 2 | 1 | 177.7 |
| tsvc/s254 | no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 3.48x | 1+0 | 1 | 2 | 1 | 133.5 |
| tsvc/s254 | no_evidence | claude-haiku-4-5-20251001 | 5 | FASTER | 3.58x | 1+0 | 1 | 2 | 1 | 107.3 |
| tsvc/s254 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.69x | 1+0 | 1 | 2 | 1 | 169.6 |
| tsvc/s254 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.66x | 1+0 | 1 | 2 | 1 | 103.4 |
| tsvc/s254 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.42x | 1+0 | 1 | 2 | 1 | 136.9 |
| tsvc/s254 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.41x | 1+0 | 1 | 2 | 1 | 171.4 |
| tsvc/s254 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.29x | 1+0 | 1 | 2 | 1 | 112.2 |
| tsvc/s254 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.07x | —+— | — | — | 0 | 1.9 |
| tsvc/s254 | twin_dp | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.38x | —+— | — | — | 0 | 1.8 |
| tsvc/s254 | twin_dp | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.32x | —+— | — | — | 0 | 2.1 |
| tsvc/s254 | twin_dp | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.40x | —+— | — | — | 0 | 1.9 |
| tsvc/s254 | twin_dp | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.35x | —+— | — | — | 0 | 2.0 |
| tsvc/s254 | twin_full | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.46x | —+— | — | — | 1 | 290.0 |
| tsvc/s254 | twin_full | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.63x | —+— | — | — | 1 | 80.2 |
| tsvc/s254 | twin_full | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.57x | —+— | — | — | 1 | 120.5 |
| tsvc/s254 | twin_full | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.60x | —+— | — | — | 1 | 89.2 |
| tsvc/s254 | twin_full | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.52x | —+— | — | — | 1 | 131.1 |
| tsvc/s254 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.08x | —+— | — | — | 1 | 108.5 |
| tsvc/s254 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.26x | —+— | — | — | 1 | 58.4 |
| tsvc/s254 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.39x | —+— | — | — | 1 | 113.4 |
| tsvc/s254 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.44x | —+— | — | — | 1 | 58.9 |
| tsvc/s254 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.42x | —+— | — | — | 1 | 50.5 |
| tsvc/s255 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.73x | 1+0 | 1 | 1 | 1 | 160.7 |
| tsvc/s255 | full_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.77x | 1+0 | 1 | 1 | 1 | 136.9 |
| tsvc/s255 | full_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.47x | 1+0 | 1 | 1 | 1 | 193.4 |
| tsvc/s255 | full_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.33x | 1+0 | 1 | 1 | 1 | 137.9 |
| tsvc/s255 | full_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.57x | 1+0 | 1 | 1 | 1 | 171.8 |
| tsvc/s255 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.67x | 1+0 | 1 | 1 | 1 | 124.4 |
| tsvc/s255 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 2.61x | 1+0 | 1 | 1 | 1 | 118.8 |
| tsvc/s255 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 2.52x | 1+0 | 1 | 1 | 1 | 206.7 |
| tsvc/s255 | no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 2.35x | 1+0 | 1 | 1 | 1 | 105.5 |
| tsvc/s255 | no_evidence | claude-haiku-4-5-20251001 | 5 | FASTER | 1.43x | 2+0 | 1 | 1 | 1 | 168.4 |
| tsvc/s255 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.55x | 1+0 | 1 | 1 | 1 | 127.5 |
| tsvc/s255 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.53x | 1+0 | 1 | 1 | 1 | 175.5 |
| tsvc/s255 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.17x | 1+0 | 1 | 1 | 1 | 174.9 |
| tsvc/s255 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.50x | 1+0 | 1 | 1 | 1 | 129.6 |
| tsvc/s255 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.77x | 1+0 | 1 | 1 | 1 | 132.3 |
| tsvc/s255 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.31x | —+— | — | — | 0 | 2.0 |
| tsvc/s255 | twin_dp | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.54x | —+— | — | — | 0 | 1.9 |
| tsvc/s255 | twin_dp | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.40x | —+— | — | — | 0 | 1.9 |
| tsvc/s255 | twin_dp | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.14x | —+— | — | — | 0 | 2.0 |
| tsvc/s255 | twin_dp | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.44x | —+— | — | — | 0 | 2.0 |
| tsvc/s255 | twin_full | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.23x | —+— | — | — | 1 | 41.5 |
| tsvc/s255 | twin_full | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.43x | —+— | — | — | 1 | 74.8 |
| tsvc/s255 | twin_full | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.21x | —+— | — | — | 1 | 92.6 |
| tsvc/s255 | twin_full | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.63x | —+— | — | — | 1 | 82.0 |
| tsvc/s255 | twin_full | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.37x | —+— | — | — | 2 | 119.2 |
| tsvc/s255 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.54x | —+— | — | — | 1 | 34.7 |
| tsvc/s255 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.29x | —+— | — | — | 1 | 62.8 |
| tsvc/s255 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.40x | —+— | — | — | 1 | 55.4 |
| tsvc/s255 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.48x | —+— | — | — | 1 | 61.4 |
| tsvc/s255 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.47x | —+— | — | — | 1 | 54.3 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.16x | 1+0 | 1 | 0 | 2 | 523.8 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 598.1 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.63x | 2+0 | 1 | 0 | 1 | 253.2 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.23x | 2+0 | 1 | 0 | 3 | 454.5 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 1 | 178.8 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.07x | 1+0 | 1 | 0 | 1 | 227.6 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.04x | 1+0 | 1 | 0 | 1 | 375.7 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 2 | 222.1 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 3.25x | 2+0 | 1 | 0 | 2 | 372.4 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.07x | 1+0 | 1 | 0 | 2 | 278.8 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.73x | 2+0 | 1 | 0 | 2 | 225.7 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.07x | 1+0 | 1 | 0 | 2 | 446.6 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.38x | 2+0 | 1 | 0 | 2 | 513.5 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 2 | 393.3 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 390.4 |
| tsvc/s281 | twin_dp | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | —+— | — | — | 0 | 2.1 |
| tsvc/s281 | twin_dp | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | —+— | — | — | 0 | 2.0 |
| tsvc/s281 | twin_dp | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | —+— | — | — | 0 | 1.9 |
| tsvc/s281 | twin_dp | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | —+— | — | — | 0 | 2.1 |
| tsvc/s281 | twin_dp | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | —+— | — | — | 0 | 2.0 |
| tsvc/s281 | twin_full | claude-haiku-4-5-20251001 | 1 | FASTER | 3.23x | —+— | — | — | 1 | 133.3 |
| tsvc/s281 | twin_full | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.15x | —+— | — | — | 1 | 80.9 |
| tsvc/s281 | twin_full | claude-haiku-4-5-20251001 | 3 | BROKEN | 1.55x | —+— | — | — | 1 | 97.7 |
| tsvc/s281 | twin_full | claude-haiku-4-5-20251001 | 4 | FASTER | 3.18x | —+— | — | — | 1 | 220.8 |
| tsvc/s281 | twin_full | claude-haiku-4-5-20251001 | 5 | BROKEN | 0.64x | —+— | — | — | 1 | 108.2 |
| tsvc/s281 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.26x | —+— | — | — | 1 | 237.6 |
| tsvc/s281 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 3.28x | —+— | — | — | 1 | 96.8 |
| tsvc/s281 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.08x | —+— | — | — | 1 | 78.3 |
| tsvc/s281 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | BROKEN | 1.94x | —+— | — | — | 1 | 85.7 |
| tsvc/s281 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.06x | —+— | — | — | 1 | 171.6 |
| tsvc/s291 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.61x | 1+0 | 1 | 1 | 1 | 128.1 |
| tsvc/s291 | full_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.37x | 1+0 | 1 | 1 | 1 | 130.5 |
| tsvc/s291 | full_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.59x | 1+0 | 1 | 1 | 1 | 159.9 |
| tsvc/s291 | full_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.56x | 1+0 | 1 | 1 | 1 | 196.3 |
| tsvc/s291 | full_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.41x | 1+0 | 1 | 1 | 1 | 125.2 |
| tsvc/s291 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.68x | 1+0 | 1 | 1 | 1 | 230.3 |
| tsvc/s291 | no_evidence | claude-haiku-4-5-20251001 | 2 | FASTER | 3.50x | 1+0 | 1 | 1 | 1 | 102.7 |
| tsvc/s291 | no_evidence | claude-haiku-4-5-20251001 | 3 | FASTER | 2.65x | 1+0 | 1 | 1 | 1 | 165.8 |
| tsvc/s291 | no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 3.42x | 1+0 | 1 | 1 | 1 | 185.0 |
| tsvc/s291 | no_evidence | claude-haiku-4-5-20251001 | 5 | FASTER | 3.40x | 1+0 | 1 | 1 | 1 | 177.4 |
| tsvc/s291 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.00x | 1+0 | 1 | 1 | 1 | 104.3 |
| tsvc/s291 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.70x | 1+0 | 1 | 1 | 1 | 120.2 |
| tsvc/s291 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.76x | 1+0 | 1 | 1 | 1 | 182.5 |
| tsvc/s291 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.79x | 1+0 | 1 | 1 | 1 | 110.2 |
| tsvc/s291 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.71x | 1+0 | 1 | 1 | 1 | 122.0 |
| tsvc/s291 | twin_dp | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.50x | —+— | — | — | 0 | 1.9 |
| tsvc/s291 | twin_dp | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.59x | —+— | — | — | 0 | 1.9 |
| tsvc/s291 | twin_dp | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.22x | —+— | — | — | 0 | 2.0 |
| tsvc/s291 | twin_dp | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.17x | —+— | — | — | 0 | 1.8 |
| tsvc/s291 | twin_dp | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.17x | —+— | — | — | 0 | 1.9 |
| tsvc/s291 | twin_full | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.47x | —+— | — | — | 1 | 96.2 |
| tsvc/s291 | twin_full | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.67x | —+— | — | — | 1 | 95.5 |
| tsvc/s291 | twin_full | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.58x | —+— | — | — | 1 | 56.1 |
| tsvc/s291 | twin_full | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.62x | —+— | — | — | 1 | 66.9 |
| tsvc/s291 | twin_full | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.29x | —+— | — | — | 1 | 76.8 |
| tsvc/s291 | twin_no_evidence | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.74x | —+— | — | — | 1 | 31.9 |
| tsvc/s291 | twin_no_evidence | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.40x | —+— | — | — | 1 | 33.4 |
| tsvc/s291 | twin_no_evidence | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.45x | —+— | — | — | 1 | 38.2 |
| tsvc/s291 | twin_no_evidence | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.61x | —+— | — | — | 1 | 30.2 |
| tsvc/s291 | twin_no_evidence | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.48x | —+— | — | — | 1 | 97.7 |
