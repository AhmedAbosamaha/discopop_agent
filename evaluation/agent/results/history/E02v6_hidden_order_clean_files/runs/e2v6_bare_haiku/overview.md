# Agent experiment run `e2v6_bare_haiku`

- status: finished (created 2026-10-06T04:41:56, finished 2026-10-06T07:09:38)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `4adf76ec2aa5419aa268da8a8f895a55f39507bd` (uncommitted diff sha256 `None`)
- harness: `4adf76ec2aa5419aa268da8a8f895a55f39507bd` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 70 | 4 | 0 | 0 | 0 | 0 | 61 | 0 | 5 | 0 | 0 | 0 | 83 | 70 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.62x | —+— | — | — | 1 | 76.8 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | BROKEN | 5.12x | —+— | — | — | 1 | 88.6 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 99.3 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 5.09x | —+— | — | — | 1 | 71.6 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | BROKEN | 5.07x | —+— | — | — | 1 | 59.2 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 5.09x | —+— | — | — | 1 | 54.1 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | BROKEN | 4.18x | —+— | — | — | 1 | 83.8 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | BROKEN | 4.69x | —+— | — | — | 1 | 75.3 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | BROKEN | 4.84x | —+— | — | — | 1 | 76.1 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | BROKEN | 5.17x | —+— | — | — | 1 | 95.5 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.31x | —+— | — | — | 1 | 37.1 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | BROKEN | 4.08x | —+— | — | — | 1 | 36.0 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 4.18x | —+— | — | — | 1 | 46.0 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 4.08x | —+— | — | — | 1 | 34.3 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | BROKEN | 4.17x | —+— | — | — | 1 | 35.7 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 4.29x | —+— | — | — | 1 | 46.5 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | BROKEN | 4.21x | —+— | — | — | 1 | 58.9 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | BROKEN | 4.12x | —+— | — | — | 1 | 38.6 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | BROKEN | 4.28x | —+— | — | — | 1 | 44.3 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | BROKEN | 4.20x | —+— | — | — | 1 | 36.7 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 5.57x | —+— | — | — | 1 | 80.7 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | BROKEN | 5.49x | —+— | — | — | 1 | 52.6 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 5.64x | —+— | — | — | 1 | 73.3 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 5.66x | —+— | — | — | 1 | 86.6 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | BROKEN | 5.52x | —+— | — | — | 1 | 106.5 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 5.59x | —+— | — | — | 1 | 84.0 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | BROKEN | 5.57x | —+— | — | — | 1 | 94.7 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | BROKEN | 5.72x | —+— | — | — | 1 | 89.9 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | BROKEN | 5.36x | —+— | — | — | 1 | 60.1 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | BROKEN | 5.57x | —+— | — | — | 1 | 57.7 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.82x | —+— | — | — | 1 | 149.0 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | VERIFY_FAILED | — | —+— | — | — | 1 | 168.5 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.04x | —+— | — | — | 1 | 167.3 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.05x | —+— | — | — | 1 | 71.3 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.85x | —+— | — | — | 1 | 255.4 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.96x | —+— | — | — | 1 | 93.0 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | BROKEN | 3.80x | —+— | — | — | 1 | 361.1 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | BROKEN | 4.06x | —+— | — | — | 1 | 436.2 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | BROKEN | 3.89x | —+— | — | — | 1 | 175.5 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | BROKEN | 2.91x | —+— | — | — | 1 | 97.6 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 5.03x | —+— | — | — | 1 | 76.3 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | BROKEN | 5.18x | —+— | — | — | 1 | 78.2 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 4.91x | —+— | — | — | 1 | 66.0 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 5.10x | —+— | — | — | 1 | 63.5 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.10x | —+— | — | — | 1 | 103.4 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 5.17x | —+— | — | — | 1 | 82.6 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.87x | —+— | — | — | 1 | 87.4 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | BROKEN | 5.05x | —+— | — | — | 1 | 50.7 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | BROKEN | 4.99x | —+— | — | — | 1 | 96.3 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | BROKEN | 5.09x | —+— | — | — | 1 | 98.5 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 8.00x | —+— | — | — | 1 | 76.4 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | BROKEN | 7.53x | —+— | — | — | 1 | 60.6 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 8.26x | —+— | — | — | 1 | 92.3 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | BROKEN | 7.70x | —+— | — | — | 1 | 60.1 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | BROKEN | 14.97x | —+— | — | — | 1 | 71.2 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | BROKEN | 7.22x | —+— | — | — | 1 | 89.4 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | BROKEN | 16.87x | —+— | — | — | 1 | 40.7 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | BROKEN | 16.54x | —+— | — | — | 1 | 86.2 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | BROKEN | 9.01x | —+— | — | — | 1 | 71.1 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | BROKEN | 8.79x | —+— | — | — | 1 | 52.4 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.27x | —+— | — | — | 1 | 148.7 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.16x | —+— | — | — | 1 | 109.1 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.24x | —+— | — | — | 1 | 105.9 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 167.0 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 236.3 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.66x | —+— | — | — | 1 | 128.5 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | VERIFY_FAILED | — | —+— | — | — | 1 | 103.2 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | BROKEN | 2.17x | —+— | — | — | 1 | 91.3 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | BROKEN | 1.77x | —+— | — | — | 1 | 161.0 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.15x | —+— | — | — | 1 | 183.4 |
