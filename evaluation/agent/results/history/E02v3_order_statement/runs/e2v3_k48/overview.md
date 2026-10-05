# Agent experiment run `e2v3_k48`

- status: finished (created 2026-09-29T12:05:24, finished 2026-09-29T13:56:39)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `f45776d701e8be37a56f1b3d35e637ef344978d2` (uncommitted diff sha256 `None`)
- harness: `f45776d701e8be37a56f1b3d35e637ef344978d2` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 1 | 0 | 0 | 0 | 0 | 7 | 0 | 2 | 0 | 0 | 0 | 60 | 10 |
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 85 | 10 |
| no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 69 | 10 |
| twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 105 | 10 |
| twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 8 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 93 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.70x | —+— | — | — | 1 | 31.2 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | VERIFY_FAILED | — | —+— | — | — | 1 | 39.5 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.79x | —+— | — | — | 1 | 85.4 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | 4.75x | —+— | — | — | 1 | 84.6 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | 5.44x | —+— | — | — | 1 | 78.8 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | 4.35x | —+— | — | — | 1 | 57.7 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | 5.05x | —+— | — | — | 1 | 84.0 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | 3.66x | —+— | — | — | 1 | 53.2 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | VERIFY_FAILED | — | —+— | — | — | 1 | 31.0 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | 4.67x | —+— | — | — | 1 | 62.5 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.99x | 2+0 | 1 | 0 | 1 | 76.5 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.97x | 2+0 | 1 | 0 | 1 | 87.7 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.07x | 2+0 | 1 | 0 | 1 | 208.9 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.01x | 2+0 | 1 | 0 | 1 | 184.1 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.04x | 2+0 | 1 | 0 | 1 | 65.5 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.75x | 2+0 | 1 | 0 | 1 | 81.4 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 4.10x | 2+0 | 1 | 0 | 1 | 52.0 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 4.04x | 2+0 | 1 | 0 | 1 | 132.5 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.68x | 2+0 | 1 | 0 | 1 | 57.6 |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 4.12x | 2+0 | 1 | 0 | 1 | 221.9 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.95x | 2+0 | 1 | 0 | 1 | 164.6 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 4.00x | 2+0 | 1 | 0 | 1 | 69.5 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.88x | 2+0 | 1 | 0 | 1 | 57.5 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.01x | 2+0 | 1 | 0 | 1 | 157.2 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.29x | 2+0 | 1 | 0 | 1 | 97.7 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.21x | 2+0 | 1 | 0 | 1 | 67.7 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.87x | 2+0 | 1 | 0 | 1 | 59.4 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 3.69x | 2+0 | 1 | 0 | 1 | 58.2 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.90x | 2+0 | 1 | 0 | 1 | 64.0 |
| tsvc_b1/k48 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 4.11x | 2+0 | 1 | 0 | 1 | 208.5 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.03x | —+— | — | — | 1 | 154.8 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.59x | —+— | — | — | 1 | 95.4 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.07x | —+— | — | — | 1 | 193.4 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.04x | —+— | — | — | 1 | 70.8 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.98x | —+— | — | — | 1 | 96.9 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.04x | —+— | — | — | 1 | 60.6 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.82x | —+— | — | — | 1 | 113.6 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 3.94x | —+— | — | — | 1 | 136.8 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.66x | —+— | — | — | 1 | 75.8 |
| tsvc_b1/k48 | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.75x | —+— | — | — | 1 | 188.5 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | 0.99x | —+— | — | — | 1 | 136.6 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.99x | —+— | — | — | 1 | 81.8 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.99x | —+— | — | — | 1 | 127.7 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.01x | —+— | — | — | 1 | 92.2 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.68x | —+— | — | — | 1 | 58.7 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.05x | —+— | — | — | 1 | 31.8 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 4.11x | —+— | — | — | 1 | 93.1 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 4.01x | —+— | — | — | 1 | 127.1 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | 0.98x | —+— | — | — | 1 | 115.3 |
| tsvc_b1/k48 | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.87x | —+— | — | — | 1 | 79.9 |
