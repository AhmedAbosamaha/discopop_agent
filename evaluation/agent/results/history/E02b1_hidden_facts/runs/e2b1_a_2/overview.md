# Agent experiment run `e2b1_a_2`

- status: finished (created 2026-09-28T01:29:57, finished 2026-09-29T02:17:00)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `7f76a31050f720f76507ebd200d0969c4db8ad5b` (uncommitted diff sha256 `None`)
- harness: `7f76a31050f720f76507ebd200d0969c4db8ad5b` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed | claude-haiku-4-5-20251001 | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 756 | 24 |
| no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 10 | 1 | 7 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 641 | 28 |
| twin_full_nospeed | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 136 | 10 |
| twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 10 | 2 | 0 | 0 | 0 | 0 | 7 | 0 | 1 | 0 | 0 | 0 | 278 | 17 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.84x | 1+0 | 1 | 1 | 2 | 1129.2 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.87x | 1+0 | 1 | 1 | 3 | 943.0 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.04x | 2+0 | 2 | 1 | 2 | 484.4 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.89x | 1+0 | 1 | 1 | 2 | 452.2 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.03x | 2+0 | 2 | 1 | 2 | 569.4 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.86x | 1+0 | 1 | 1 | 2 | 502.6 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 6 | parallel-not-faster | 0.84x | 1+0 | 1 | 1 | 3 | 1212.8 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.81x | 1+0 | 1 | 1 | 3 | 1541.7 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 8 | parallel-not-faster | 1.00x | 1+0 | 1 | 1 | 3 | 993.4 |
| rodinia_b1/bfs | full_b1_nospeed | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.88x | 1+0 | 1 | 1 | 2 | 548.2 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.93x | 1+0 | 1 | 1 | 1 | 794.2 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 1.08x | 3+0 | 1 | 1 | 1 | 211.7 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.06x | 2+0 | 1 | 1 | 4 | 874.3 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 347.2 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.07x | 2+0 | 2 | 1 | 2 | 334.3 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 1.00x | 2+0 | 1 | 1 | 1 | 186.8 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 6 | FASTER | 1.10x | 1+0 | 2 | 1 | 5 | 1569.5 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 1.04x | 1+0 | 1 | 1 | 5 | 1931.1 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | — | 1+0 | 1 | 1 | 4 | 979.9 |
| rodinia_b1/bfs | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 1.09x | 1+0 | 0 | 1 | 3 | 488.5 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 1 | 163.7 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 10 | BROKEN | — | —+— | — | — | 1 | 132.4 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 2 | BROKEN | — | —+— | — | — | 1 | 129.1 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | — | —+— | — | — | 1 | 132.4 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 4 | BROKEN | — | —+— | — | — | 1 | 143.8 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | — | —+— | — | — | 1 | 120.0 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 6 | BROKEN | — | —+— | — | — | 1 | 138.9 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 7 | BROKEN | — | —+— | — | — | 1 | 191.1 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | — | —+— | — | — | 1 | 150.0 |
| rodinia_b1/bfs | twin_full_nospeed | claude-haiku-4-5-20251001 | 9 | BROKEN | — | —+— | — | — | 1 | 134.0 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 1 | 224.8 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 10 | BROKEN | — | —+— | — | — | 3 | 346.1 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 2 | FASTER | 9.66x | —+— | — | — | 2 | 244.2 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 3 | BROKEN | — | —+— | — | — | 2 | 361.8 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 2 | 280.9 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 5 | BROKEN | — | —+— | — | — | 1 | 145.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 6 | BROKEN | — | —+— | — | — | 1 | 274.4 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 7 | BROKEN | — | —+— | — | — | 1 | 163.1 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 8 | BROKEN | — | —+— | — | — | 2 | 320.6 |
| rodinia_b1/bfs | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 9 | FASTER | 5.80x | —+— | — | — | 2 | 294.8 |
