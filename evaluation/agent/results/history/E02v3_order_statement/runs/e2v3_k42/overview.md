# Agent experiment run `e2v3_k42`

- status: finished (created 2026-09-29T05:04:54, finished 2026-09-29T07:21:06)
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
| bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 1 | 0 | 0 | 8 | 0 | 1 | 0 | 0 | 0 | 76 | 10 |
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 64 | 10 |
| no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 64 | 10 |
| twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 52 | 10 |
| twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 60 | 10 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 3.53 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 1.05 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 1.08 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 1.01 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 0.98 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 1.01 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 0.99 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 1.01 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 0.99 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 1.01 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 1.01 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 1.02 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | EXTRALARGE | 1.01 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | EXTRALARGE | 0.98 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | EXTRALARGE | 1.00 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | EXTRALARGE | 1.01 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.19x | —+— | — | — | 1 | 76.2 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | 4.92x | —+— | — | — | 1 | 181.0 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.45x | —+— | — | — | 1 | 76.5 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.82x | —+— | — | — | 1 | 59.2 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.47x | —+— | — | — | 1 | 41.3 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 3.53x | —+— | — | — | 1 | 111.0 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | VERIFY_FAILED | — | —+— | — | — | 1 | 47.6 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | 4.18x | —+— | — | — | 1 | 43.2 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 4.36x | —+— | — | — | 1 | 98.7 |
| tsvc_b1/k42 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 3.94x | —+— | — | — | 1 | 81.4 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 58.6 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 160.5 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-speed-not-measurable | 1.05x | 1+0 | 1 | 1 | 1 | 44.2 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 1.08x | 1+0 | 1 | 1 | 1 | 68.9 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 190.5 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 1.01x | 1+0 | 1 | 1 | 1 | 58.2 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | parallel-speed-not-measurable | 0.98x | 1+0 | 1 | 1 | 1 | 79.2 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 53.5 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 51.3 |
| tsvc_b1/k42 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 88.0 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 43.3 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 107.4 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 61.6 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 1.01x | 1+0 | 1 | 1 | 1 | 44.5 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 181.9 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 0.99x | 1+0 | 1 | 1 | 1 | 32.5 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 66.6 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 44.0 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 71.1 |
| tsvc_b1/k42 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-speed-not-measurable | 1.00x | 1+0 | 1 | 1 | 1 | 103.4 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 111.5 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-speed-not-measurable | 1.01x | —+— | — | — | 1 | 65.6 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 42.3 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 46.9 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 31.1 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 0.99x | —+— | — | — | 1 | 57.0 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | parallel-speed-not-measurable | 1.01x | —+— | — | — | 1 | 104.7 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 35.8 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | parallel-speed-not-measurable | 1.01x | —+— | — | — | 1 | 56.9 |
| tsvc_b1/k42 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-speed-not-measurable | 1.02x | —+— | — | — | 1 | 39.0 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 44.5 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 83.1 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 75.0 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 58.6 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-speed-not-measurable | 1.01x | —+— | — | — | 1 | 70.3 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 63.8 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 30.5 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | parallel-speed-not-measurable | 0.98x | —+— | — | — | 1 | 54.9 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | parallel-speed-not-measurable | 1.00x | —+— | — | — | 1 | 41.8 |
| tsvc_b1/k42 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | parallel-speed-not-measurable | 1.01x | —+— | — | — | 1 | 61.2 |
