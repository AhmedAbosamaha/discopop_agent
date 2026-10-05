# Agent experiment run `e2b1v3_bfs`

- status: finished (created 2026-09-29T17:08:17, finished 2026-09-30T05:54:22)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `b507acc13a68839b5820e8f1dffd2d56699ee980` (uncommitted diff sha256 `None`)
- harness: `b507acc13a68839b5820e8f1dffd2d56699ee980` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 151 | 10 |
| twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | 2 | 1 | 0 | 2 | 0 | 4 | 0 | 1 | 0 | 0 | 0 | 294 | 18 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 1 | 238.0 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | BROKEN | — | —+— | — | — | 1 | 110.0 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | — | —+— | — | — | 1 | 107.2 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | BROKEN | — | —+— | — | — | 1 | 161.8 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | — | —+— | — | — | 1 | 210.6 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | BROKEN | — | —+— | — | — | 1 | 219.0 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | BROKEN | — | —+— | — | — | 1 | 118.3 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | — | —+— | — | — | 1 | 212.2 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | BROKEN | — | —+— | — | — | 1 | 119.6 |
| rodinia_b1/bfs | twin_full_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | BROKEN | — | —+— | — | — | 1 | 139.8 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | BROKEN | — | —+— | — | — | 1 | 155.7 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.86x | —+— | — | — | 2 | 330.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | BROKEN | — | —+— | — | — | 2 | 292.9 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.20x | —+— | — | — | 2 | 311.1 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | BROKEN | — | —+— | — | — | 2 | 321.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 2 | 280.8 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | changed-not-parallel | 0.98x | —+— | — | — | 1 | 179.3 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | BROKEN | — | —+— | — | — | 2 | 312.9 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.05x | —+— | — | — | 2 | 234.9 |
| rodinia_b1/bfs | twin_no_evidence_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | changed-not-parallel | 0.04x | —+— | — | — | 2 | 294.1 |
