# Agent experiment run `e2v3_s1213`

- status: finished (created 2026-09-29T05:04:49, finished 2026-09-29T08:07:43)
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
| bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 4 | 1 | 0 | 0 | 0 | 3 | 0 | 2 | 0 | 0 | 0 | 158 | 10 |
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 9 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 155 | 14 |
| no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 8 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 216 | 17 |
| twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 6 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 148 | 10 |
| twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 3 | 2 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 174 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.72x | —+— | — | — | 1 | 107.1 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | VERIFY_FAILED | — | —+— | — | — | 1 | 99.2 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.57x | —+— | — | — | 1 | 127.0 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.27x | —+— | — | — | 1 | 185.2 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.53x | —+— | — | — | 1 | 298.1 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.07x | —+— | — | — | 1 | 105.7 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.46x | —+— | — | — | 1 | 224.5 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.47x | —+— | — | — | 1 | 130.1 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 0.14x | —+— | — | — | 1 | 257.3 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | VERIFY_FAILED | — | —+— | — | — | 1 | 412.7 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.48x | 2+0 | 1 | 0 | 3 | 149.3 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.54x | 2+0 | 1 | 0 | 1 | 103.8 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.67x | 2+0 | 1 | 0 | 1 | 110.2 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.33x | 2+0 | 1 | 0 | 1 | 178.8 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.53x | 2+0 | 1 | 0 | 1 | 85.1 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.76x | 2+0 | 1 | 0 | 1 | 418.4 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.57x | 2+0 | 1 | 0 | 1 | 160.6 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 730.8 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.48x | 2+0 | 1 | 0 | 1 | 109.9 |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.56x | 2+0 | 1 | 0 | 1 | 220.6 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 206.2 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.55x | 2+0 | 1 | 0 | 1 | 121.5 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.47x | 2+0 | 1 | 0 | 1 | 255.0 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.56x | 2+0 | 1 | 0 | 2 | 253.7 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.74x | 3+0 | 1 | 0 | 1 | 225.2 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.59x | 3+0 | 1 | 0 | 3 | 463.2 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.58x | 2+0 | 1 | 0 | 3 | 576.8 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.78x | 3+0 | 1 | 0 | 1 | 122.9 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.56x | 2+0 | 1 | 0 | 1 | 171.8 |
| tsvc_b1/s1213 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.48x | 2+0 | 1 | 0 | 1 | 173.7 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.53x | —+— | — | — | 1 | 138.1 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.50x | —+— | — | — | 1 | 223.6 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.57x | —+— | — | — | 1 | 153.5 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.57x | —+— | — | — | 1 | 66.8 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 2.57x | —+— | — | — | 1 | 64.6 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 1.76x | —+— | — | — | 1 | 181.0 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 1.78x | —+— | — | — | 1 | 166.4 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.45x | —+— | — | — | 1 | 142.7 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.25x | —+— | — | — | 1 | 142.0 |
| tsvc_b1/s1213 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.34x | —+— | — | — | 1 | 181.2 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 1.41x | —+— | — | — | 1 | 206.9 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.92x | —+— | — | — | 1 | 169.8 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.76x | —+— | — | — | 1 | 177.4 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 0.36x | —+— | — | — | 1 | 142.7 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.99x | —+— | — | — | 1 | 177.9 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 2.59x | —+— | — | — | 1 | 49.0 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.56x | —+— | — | — | 1 | 266.4 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.55x | —+— | — | — | 1 | 169.2 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 2.48x | —+— | — | — | 1 | 40.9 |
| tsvc_b1/s1213 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 1.77x | —+— | — | — | 1 | 214.1 |
