# Agent experiment run `e11b_r_repoomp`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| repoomp_release | none | 35 | 5 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 196 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | repoomp_release | none | 1 | parallel-not-faster | 0.99x | —+— | — | — | 3 | — |
| tsvc_c2/k19 | repoomp_release | none | 2 | parallel-not-faster | 1.00x | —+— | — | — | 12 | — |
| tsvc_c2/k19 | repoomp_release | none | 3 | parallel-not-faster | 1.01x | —+— | — | — | 4 | — |
| tsvc_c2/k19 | repoomp_release | none | 4 | parallel-not-faster | 1.00x | —+— | — | — | 6 | — |
| tsvc_c2/k19 | repoomp_release | none | 5 | parallel-not-faster | 1.00x | —+— | — | — | 1 | — |
| tsvc_c2/k23 | repoomp_release | none | 1 | parallel-not-faster | 1.00x | —+— | — | — | 12 | — |
| tsvc_c2/k23 | repoomp_release | none | 2 | parallel-not-faster | 1.04x | —+— | — | — | 12 | — |
| tsvc_c2/k23 | repoomp_release | none | 3 | parallel-not-faster | 1.00x | —+— | — | — | 12 | — |
| tsvc_c2/k23 | repoomp_release | none | 4 | parallel-not-faster | 1.01x | —+— | — | — | 12 | — |
| tsvc_c2/k23 | repoomp_release | none | 5 | parallel-not-faster | 1.00x | —+— | — | — | 12 | — |
| tsvc_c2/k27 | repoomp_release | none | 1 | parallel-not-faster | 1.01x | —+— | — | — | 1 | — |
| tsvc_c2/k27 | repoomp_release | none | 2 | parallel-not-faster | 1.03x | —+— | — | — | 3 | — |
| tsvc_c2/k27 | repoomp_release | none | 3 | parallel-not-faster | 1.01x | —+— | — | — | 12 | — |
| tsvc_c2/k27 | repoomp_release | none | 4 | parallel-not-faster | 1.00x | —+— | — | — | 4 | — |
| tsvc_c2/k27 | repoomp_release | none | 5 | parallel-not-faster | 1.00x | —+— | — | — | 1 | — |
| tsvc_c2/k31 | repoomp_release | none | 1 | parallel-not-faster | 1.00x | —+— | — | — | 12 | — |
| tsvc_c2/k31 | repoomp_release | none | 2 | parallel-not-faster | 1.08x | —+— | — | — | 12 | — |
| tsvc_c2/k31 | repoomp_release | none | 3 | parallel-not-faster | 1.04x | —+— | — | — | 12 | — |
| tsvc_c2/k31 | repoomp_release | none | 4 | parallel-not-faster | 1.01x | —+— | — | — | 12 | — |
| tsvc_c2/k31 | repoomp_release | none | 5 | parallel-not-faster | 1.00x | —+— | — | — | 12 | — |
| tsvc_c2/k48 | repoomp_release | none | 1 | parallel-not-faster | 1.01x | —+— | — | — | 2 | — |
| tsvc_c2/k48 | repoomp_release | none | 2 | parallel-not-faster | 1.02x | —+— | — | — | 7 | — |
| tsvc_c2/k48 | repoomp_release | none | 3 | parallel-not-faster | 1.08x | —+— | — | — | 4 | — |
| tsvc_c2/k48 | repoomp_release | none | 4 | parallel-not-faster | 1.00x | —+— | — | — | 1 | — |
| tsvc_c2/k48 | repoomp_release | none | 5 | parallel-not-faster | 1.00x | —+— | — | — | 1 | — |
| tsvc_c2/k53 | repoomp_release | none | 1 | parallel-not-faster | 1.00x | —+— | — | — | 2 | — |
| tsvc_c2/k53 | repoomp_release | none | 2 | parallel-not-faster | 1.00x | —+— | — | — | 1 | — |
| tsvc_c2/k53 | repoomp_release | none | 3 | parallel-not-faster | 1.00x | —+— | — | — | 3 | — |
| tsvc_c2/k53 | repoomp_release | none | 4 | parallel-not-faster | 1.00x | —+— | — | — | 1 | — |
| tsvc_c2/k53 | repoomp_release | none | 5 | parallel-not-faster | 1.00x | —+— | — | — | 0 | — |
| tsvc_c2/s161 | repoomp_release | none | 1 | FASTER | 4.02x | —+— | — | — | 1 | — |
| tsvc_c2/s161 | repoomp_release | none | 2 | FASTER | 3.96x | —+— | — | — | 2 | — |
| tsvc_c2/s161 | repoomp_release | none | 3 | FASTER | 3.83x | —+— | — | — | 2 | — |
| tsvc_c2/s161 | repoomp_release | none | 4 | FASTER | 4.00x | —+— | — | — | 1 | — |
| tsvc_c2/s161 | repoomp_release | none | 5 | FASTER | 3.77x | —+— | — | — | 1 | — |
