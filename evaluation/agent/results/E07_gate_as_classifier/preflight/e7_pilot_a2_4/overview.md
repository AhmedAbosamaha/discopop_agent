# Agent experiment run `e7_pilot_a2_4`

- status: None (created None, finished None)
- host: `None`, compilers `None` / `None`
- agent: `None` (uncommitted diff sha256 `None`)
- harness: `None` on `None`
- verify size `None`, threads None, repeats None

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e7 | none | 9 | 6 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | e7 | none | 1 | FASTER | 1.98x | —+— | — | — | 0 | — |
| polybench/3mm | e7 | none | 1 | FASTER | 1.50x | —+— | — | — | 0 | — |
| polybench/atax | e7 | none | 1 | BROKEN | 0.92x | —+— | — | — | 0 | — |
| polybench/fdtd-apml | e7 | none | 1 | FASTER | 4.57x | —+— | — | — | 0 | — |
| polybench/gramschmidt | e7 | none | 1 | FASTER | 7.65x | —+— | — | — | 0 | — |
| polybench/seidel-2d | e7 | none | 1 | BROKEN | 7.08x | —+— | — | — | 0 | — |
| tsvc_c3/s152 | e7 | none | 1 | FASTER | 3.34x | —+— | — | — | 0 | — |
| tsvc_c3/s481 | e7 | none | 1 | BROKEN | 4.82x | —+— | — | — | 0 | — |
| tsvc_c3/vpvtv | e7 | none | 2 | FASTER | 3.70x | —+— | — | — | 0 | — |
