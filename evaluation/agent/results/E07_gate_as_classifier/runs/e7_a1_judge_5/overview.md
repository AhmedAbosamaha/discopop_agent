# Agent experiment run `e7_a1_judge_5`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 14 | 5 | 5 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s244 | e7 | none | 10 | FASTER | 3.03x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 40 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 41 | FASTER | 5.47x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 42 | BROKEN | 5.32x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 43 | parallel-not-faster | 0.88x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 44 | FASTER | 6.75x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 45 | FASTER | 5.59x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 46 | FASTER | 6.19x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 47 | parallel-not-faster | 0.88x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 48 | BROKEN | 5.13x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 49 | BROKEN | 1122.07x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 50 | parallel-not-faster | 0.88x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 51 | parallel-not-faster | 0.88x | —+— | — | — | 0 | — |
| tsvc_c2/s331 | e7 | none | 52 | BROKEN | 5.11x | —+— | — | — | 0 | — |
