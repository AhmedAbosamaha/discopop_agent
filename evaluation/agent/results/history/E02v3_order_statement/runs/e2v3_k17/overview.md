# Agent experiment run `e2v3_k17`

- status: finished (created 2026-09-29T05:04:47, finished 2026-09-29T07:56:30)
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
| bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 1 | 9 | 0 | 0 | 0 | 0 | 0 | 83 | 10 |
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 138 | 10 |
| no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 147 | 20 |
| twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 105 | 10 |
| twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 60 | 10 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 1.02 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 0.97 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 1.00 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 1.00 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.97 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 0.98 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 0.97 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 1.04 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 1.01 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 0.97 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 1.00 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 0.99 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 0.99 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.06x | —+— | — | — | 1 | 69.2 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | 3.48x | —+— | — | — | 1 | 81.6 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 4.17x | —+— | — | — | 1 | 107.5 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.36x | —+— | — | — | 1 | 123.5 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 4.14x | —+— | — | — | 1 | 48.8 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | —+— | — | — | 1 | 10.3 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 4.52x | —+— | — | — | 1 | 41.0 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | 4.08x | —+— | — | — | 1 | 88.6 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 3.62x | —+— | — | — | 1 | 113.9 |
| tsvc_b1/k17 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 3.95x | —+— | — | — | 1 | 85.2 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 1.02x | 1+0 | 1 | 1 | 1 | 137.9 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-speed-not-measurable | 0.97x | 1+0 | 1 | 1 | 1 | 137.2 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-speed-not-measurable | 0.99x | 1+0 | 1 | 1 | 1 | 64.5 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 56.9 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-speed-not-measurable | 0.99x | 1+0 | 1 | 1 | 1 | 145.9 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 0.99x | 1+0 | 1 | 1 | 1 | 87.8 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | parallel-speed-not-measurable | 0.99x | 1+0 | 1 | 1 | 1 | 146.4 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-speed-not-measurable | 0.99x | 1+0 | 1 | 1 | 1 | 232.1 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 68.1 |
| tsvc_b1/k17 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-speed-not-measurable | 0.99x | 1+0 | 1 | 1 | 1 | 157.4 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.97x | 1+0 | 0 | 1 | 2 | 229.7 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-speed-not-measurable | 0.99x | 1+0 | 0 | 1 | 2 | 186.4 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-speed-not-measurable | 0.98x | 1+0 | 0 | 1 | 2 | 117.7 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 0.98x | 1+0 | 0 | 1 | 2 | 108.5 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-speed-not-measurable | 0.98x | 1+0 | 0 | 1 | 2 | 168.2 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 0.98x | 1+0 | 0 | 1 | 2 | 235.9 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | parallel-speed-not-measurable | 0.98x | 1+0 | 0 | 1 | 2 | 89.6 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-speed-not-measurable | 0.98x | 1+0 | 0 | 1 | 2 | 72.5 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | parallel-speed-not-measurable | 0.98x | 1+0 | 0 | 1 | 2 | 263.1 |
| tsvc_b1/k17 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-speed-not-measurable | 0.98x | 1+0 | 0 | 1 | 2 | 125.9 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.97x | —+— | — | — | 1 | 203.2 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 1 | 262.4 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-speed-not-measurable | 1.04x | —+— | — | — | 1 | 124.7 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 1.01x | —+— | — | — | 1 | 44.9 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 1 | 82.1 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 0.97x | —+— | — | — | 1 | 102.2 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 1 | 75.4 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 57.5 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 1 | 210.6 |
| tsvc_b1/k17 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 1 | 108.3 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 0.99x | —+— | — | — | 1 | 47.8 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | 1.00x | —+— | — | — | 1 | 99.6 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 0.27x | —+— | — | — | 1 | 56.1 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 0.99x | —+— | — | — | 1 | 82.2 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 0.99x | —+— | — | — | 1 | 58.1 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.00x | —+— | — | — | 1 | 45.7 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 0.99x | —+— | — | — | 1 | 253.7 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | 0.99x | —+— | — | — | 1 | 35.2 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 0.99x | —+— | — | — | 1 | 62.2 |
| tsvc_b1/k17 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 0.98x | —+— | — | — | 1 | 93.1 |
