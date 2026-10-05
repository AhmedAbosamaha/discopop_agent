# Agent experiment run `e2o3_bare_haiku`

- status: finished (created 2026-10-03T10:14:05, finished 2026-10-03T18:57:50)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `7789d91e26b387529837aa0c18f339e0911c9407` (uncommitted diff sha256 `None`)
- harness: `7789d91e26b387529837aa0c18f339e0911c9407` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 30 | 0 | 0 | 0 | 0 | 0 | 28 | 0 | 2 | 0 | 0 | 0 | 37 | 30 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.23x | —+— | — | — | 1 | 36.5 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | 4.29x | —+— | — | — | 1 | 22.9 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 4.16x | —+— | — | — | 1 | 22.9 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 4.30x | —+— | — | — | 1 | 33.7 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 4.28x | —+— | — | — | 1 | 32.0 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 4.35x | —+— | — | — | 1 | 18.7 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 4.30x | —+— | — | — | 1 | 23.7 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | 4.29x | —+— | — | — | 1 | 37.7 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 4.31x | —+— | — | — | 1 | 16.6 |
| tsvc_b1/k23 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 4.25x | —+— | — | — | 1 | 29.1 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.33x | —+— | — | — | 1 | 90.8 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | VERIFY_FAILED | — | —+— | — | — | 1 | 115.4 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 4.17x | —+— | — | — | 1 | 116.7 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.24x | —+— | — | — | 1 | 70.2 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.90x | —+— | — | — | 1 | 97.7 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.85x | —+— | — | — | 1 | 128.8 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 4.07x | —+— | — | — | 1 | 90.1 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | 4.16x | —+— | — | — | 1 | 63.5 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 4.09x | —+— | — | — | 1 | 76.5 |
| tsvc_b1/k31 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 0.20x | —+— | — | — | 1 | 129.2 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.21x | —+— | — | — | 1 | 25.9 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | 4.01x | —+— | — | — | 1 | 40.8 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | 4.24x | —+— | — | — | 1 | 31.8 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | VERIFY_FAILED | — | —+— | — | — | 1 | 26.9 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 4.14x | —+— | — | — | 1 | 44.3 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 4.20x | —+— | — | — | 1 | 26.0 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 4.04x | —+— | — | — | 1 | 60.1 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | 4.06x | —+— | — | — | 1 | 26.3 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 4.09x | —+— | — | — | 1 | 31.4 |
| tsvc_b1/k36 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 4.17x | —+— | — | — | 1 | 44.9 |
