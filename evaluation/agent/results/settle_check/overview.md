# Agent experiment run `settle_check`

- status: running (created 2026-09-22T17:27:48, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `00d4594f1093d7610728a79463079acac522af26` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| settle_dropped_s112_rep3 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s1213_rep4 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s121_rep3 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s211_rep3 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s212_rep5 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s241_rep2 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s241_rep4 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s252_rep5 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s331_rep1 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| settle_dropped_s341_rep5 | none | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s112 | settle_dropped_s112_rep3 | none | 1 | parallel-not-faster | 0.14x | —+— | — | — | 0 | — |
| tsvc/s121 | settle_dropped_s121_rep3 | none | 1 | parallel-not-faster | 0.79x | —+— | — | — | 0 | — |
| tsvc/s1213 | settle_dropped_s1213_rep4 | none | 1 | parallel-not-faster | 0.35x | —+— | — | — | 0 | — |
| tsvc/s211 | settle_dropped_s211_rep3 | none | 1 | parallel-not-faster | 0.35x | —+— | — | — | 0 | — |
| tsvc/s212 | settle_dropped_s212_rep5 | none | 1 | parallel-not-faster | 0.37x | —+— | — | — | 0 | — |
| tsvc/s241 | settle_dropped_s241_rep2 | none | 1 | parallel-not-faster | 0.30x | —+— | — | — | 0 | — |
| tsvc/s241 | settle_dropped_s241_rep4 | none | 1 | parallel-not-faster | 0.90x | —+— | — | — | 0 | — |
| tsvc/s252 | settle_dropped_s252_rep5 | none | 1 | parallel-not-faster | 0.99x | —+— | — | — | 0 | — |
| tsvc/s331 | settle_dropped_s331_rep1 | none | 1 | parallel-not-faster | 0.94x | —+— | — | — | 0 | — |
| tsvc/s341 | settle_dropped_s341_rep5 | none | 1 | parallel-not-faster | 0.20x | —+— | — | — | 0 | — |
