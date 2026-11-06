# Agent experiment run `e11b_bare`

- status: finished (created 2026-11-06T09:03:49, finished 2026-11-06T10:47:15)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `4077730ec8ad0a34af7f2967ed17be29ffe5ec5d` (uncommitted diff sha256 `None`)
- harness: `4077730ec8ad0a34af7f2967ed17be29ffe5ec5d` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-sonnet-4-5-20250929 | 35 | 8 | 0 | 0 | 0 | 0 | 27 | 0 | 0 | 0 | 0 | 0 | 131 | 35 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | BROKEN | 2.38x | —+— | — | — | 1 | 142.0 |
| tsvc_c2/k19 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | BROKEN | 4.28x | —+— | — | — | 1 | 111.9 |
| tsvc_c2/k19 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | BROKEN | 4.12x | —+— | — | — | 1 | 114.5 |
| tsvc_c2/k19 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | FASTER | 1.18x | —+— | — | — | 1 | 247.2 |
| tsvc_c2/k19 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | BROKEN | 4.97x | —+— | — | — | 1 | 127.8 |
| tsvc_c2/k23 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | BROKEN | 4.07x | —+— | — | — | 1 | 41.6 |
| tsvc_c2/k23 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | BROKEN | 4.11x | —+— | — | — | 1 | 45.8 |
| tsvc_c2/k23 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | BROKEN | 4.24x | —+— | — | — | 1 | 47.7 |
| tsvc_c2/k23 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | BROKEN | 4.30x | —+— | — | — | 1 | 45.1 |
| tsvc_c2/k23 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | BROKEN | 4.34x | —+— | — | — | 1 | 65.5 |
| tsvc_c2/k27 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | BROKEN | 3.31x | —+— | — | — | 1 | 161.3 |
| tsvc_c2/k27 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | BROKEN | 2.83x | —+— | — | — | 1 | 158.5 |
| tsvc_c2/k27 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | BROKEN | 2.87x | —+— | — | — | 1 | 167.9 |
| tsvc_c2/k27 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | BROKEN | 2.83x | —+— | — | — | 1 | 132.9 |
| tsvc_c2/k27 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | BROKEN | 4.21x | —+— | — | — | 1 | 130.6 |
| tsvc_c2/k31 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | BROKEN | 2.32x | —+— | — | — | 1 | 156.3 |
| tsvc_c2/k31 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | BROKEN | 0.21x | —+— | — | — | 1 | 266.6 |
| tsvc_c2/k31 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | BROKEN | 3.26x | —+— | — | — | 1 | 112.3 |
| tsvc_c2/k31 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | BROKEN | 3.35x | —+— | — | — | 1 | 75.1 |
| tsvc_c2/k31 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | BROKEN | 3.04x | —+— | — | — | 1 | 350.5 |
| tsvc_c2/k48 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | FASTER | 2.38x | —+— | — | — | 1 | 170.5 |
| tsvc_c2/k48 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | FASTER | 2.38x | —+— | — | — | 1 | 202.0 |
| tsvc_c2/k48 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | FASTER | 2.38x | —+— | — | — | 1 | 194.1 |
| tsvc_c2/k48 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | FASTER | 2.36x | —+— | — | — | 1 | 119.5 |
| tsvc_c2/k48 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | FASTER | 2.40x | —+— | — | — | 1 | 215.4 |
| tsvc_c2/k53 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | BROKEN | 8.83x | —+— | — | — | 1 | 176.6 |
| tsvc_c2/k53 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | BROKEN | 9.69x | —+— | — | — | 1 | 125.7 |
| tsvc_c2/k53 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | BROKEN | 22.99x | —+— | — | — | 1 | 91.4 |
| tsvc_c2/k53 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | BROKEN | 19.21x | —+— | — | — | 1 | 100.4 |
| tsvc_c2/k53 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | BROKEN | 8.47x | —+— | — | — | 1 | 213.8 |
| tsvc_c2/s161 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 1 | BROKEN | 2.42x | —+— | — | — | 1 | 66.5 |
| tsvc_c2/s161 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 2 | FASTER | 2.10x | —+— | — | — | 1 | 184.5 |
| tsvc_c2/s161 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 3 | BROKEN | 0.32x | —+— | — | — | 1 | 107.5 |
| tsvc_c2/s161 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 4 | FASTER | 2.40x | —+— | — | — | 1 | 232.8 |
| tsvc_c2/s161 | bare_llm_v4 | claude-sonnet-4-5-20250929 | 5 | BROKEN | 2.39x | —+— | — | — | 1 | 67.9 |
