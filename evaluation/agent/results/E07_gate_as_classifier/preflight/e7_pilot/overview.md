# Agent experiment run `e7_pilot`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 36 | 10 | 16 | 0 | 0 | 0 | 8 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | e7 | none | 26 | parallel-not-faster | 0.45x | —+— | — | — | 0 | — |
| tsvc_c2/k19 | e7 | none | 31 | BROKEN | 0.14x | —+— | — | — | 0 | — |
| tsvc_c2/k23 | e7 | none | 35 | parallel-not-faster | 0.77x | —+— | — | — | 0 | — |
| tsvc_c2/k23 | e7 | none | 57 | FASTER | 1.43x | —+— | — | — | 0 | — |
| tsvc_c2/k27 | e7 | none | 1 | FASTER | 1.13x | —+— | — | — | 0 | — |
| tsvc_c2/k27 | e7 | none | 51 | FASTER | 1.21x | —+— | — | — | 0 | — |
| tsvc_c2/k27 | e7 | none | 69 | BROKEN | 0.94x | —+— | — | — | 0 | — |
| tsvc_c2/k27 | e7 | none | 73 | FASTER | 1.25x | —+— | — | — | 0 | — |
| tsvc_c2/k31 | e7 | none | 44 | parallel-not-faster | 1.08x | —+— | — | — | 0 | — |
| tsvc_c2/k31 | e7 | none | 53 | BROKEN | 0.73x | —+— | — | — | 0 | — |
| tsvc_c2/k48 | e7 | none | 4 | FASTER | 1.29x | —+— | — | — | 0 | — |
| tsvc_c2/k48 | e7 | none | 6 | FASTER | 1.38x | —+— | — | — | 0 | — |
| tsvc_c2/k48 | e7 | none | 7 | FASTER | 4.07x | —+— | — | — | 0 | — |
| tsvc_c2/k53 | e7 | none | 145 | BROKEN | 4.82x | —+— | — | — | 0 | — |
| tsvc_c2/k53 | e7 | none | 17 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| tsvc_c2/s112 | e7 | none | 2 | FASTER | 1.47x | —+— | — | — | 0 | — |
| tsvc_c2/s112 | e7 | none | 21 | parallel-not-faster | 0.43x | —+— | — | — | 0 | — |
| tsvc_c2/s112 | e7 | none | 23 | parallel-not-faster | 0.15x | —+— | — | — | 0 | — |
| tsvc_c2/s112 | e7 | none | 5 | FASTER | 1.48x | —+— | — | — | 0 | — |
| tsvc_c2/s121 | e7 | none | 3 | parallel-not-faster | 0.66x | —+— | — | — | 0 | — |
| tsvc_c2/s121 | e7 | none | 9 | parallel-not-faster | 0.54x | —+— | — | — | 0 | — |
| tsvc_c2/s1213 | e7 | none | 1 | parallel-not-faster | 0.70x | —+— | — | — | 0 | — |
| tsvc_c2/s161 | e7 | none | 20 | parallel-not-faster | 0.60x | —+— | — | — | 0 | — |
| tsvc_c2/s211 | e7 | none | 16 | parallel-not-faster | 0.79x | —+— | — | — | 0 | — |
| tsvc_c2/s212 | e7 | none | 23 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| tsvc_c2/s241 | e7 | none | 44 | parallel-not-faster | 0.39x | —+— | — | — | 0 | — |
| tsvc_c2/s241 | e7 | none | 47 | parallel-not-faster | 1.02x | —+— | — | — | 0 | — |
| tsvc_c2/s281 | e7 | none | 7 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| tsvc_c2/s322 | e7 | none | 34 | BROKEN | 1.20x | —+— | — | — | 0 | — |
| tsvc_c2/s322 | e7 | none | 37 | BROKEN | 1.75x | —+— | — | — | 0 | — |
| tsvc_c2/s323 | e7 | none | 29 | BROKEN | 0.57x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | e7 | none | 18 | BROKEN | 0.97x | —+— | — | — | 0 | — |
| tsvc_c2/s341 | e7 | none | 22 | parallel-not-faster | 0.65x | —+— | — | — | 0 | — |
| tsvc_c3/s241 | e7 | none | 50 | VERIFY_FAILED | — | —+— | — | — | 0 | — |
| tsvc_c3/s331 | e7 | none | 15 | parallel-not-faster | 0.88x | —+— | — | — | 0 | — |
| tsvc_c3/s331 | e7 | none | 3 | FASTER | 1.14x | —+— | — | — | 0 | — |
