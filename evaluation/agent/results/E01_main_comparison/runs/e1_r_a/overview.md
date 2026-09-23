# Agent experiment run `e1_r_a`

- status: finished (created 2026-09-21T15:10:46, finished 2026-09-22T10:26:10)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `00d4594f1093d7610728a79463079acac522af26` (uncommitted diff sha256 `None`)
- harness: `00d4594f1093d7610728a79463079acac522af26` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 65 | 17 | 4 | 0 | 0 | 0 | 0 | 42 | 0 | 2 | 0 | 0 | 1.00x (n=62) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | default | claude-haiku-4-5-20251001 | 13 | 65 | 17 | 4 | 0 | 0 | 0 | 0 | 42 | 0 | 2 | 0 | 0 | 1.00x (n=62) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| burkardt/md | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| npb/is | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | AGENT_TIMEOUT,AGENT_TIMEOUT,no-change,no-change,no-change · 1.00x | 1.00x | 3 neither, 2 invalid |
| polybench/bicg | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,parallel-speed-not-measurable · 1.00x | 1.00x | 1 gained-not-faster, 4 neither |
| polybench/doitgen | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,parallel-not-faster · 1.00x | 1.00x | 1 gained-not-faster, 4 neither |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 4.26x | 4.26x | 5 gained |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,parallel-not-faster · 1.00x | 1.00x | 1 gained, 1 gained-not-faster, 3 neither |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 1.36x | 1.36x | 3 gained, 2 neither |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,parallel-not-faster · 1.17x | 1.17x | 3 gained, 1 gained-not-faster, 1 neither |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |

**Speed ratios withheld for 2 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 65 | 17 | 3 | 1 | 0 | 42 | 0 | 0 | 0 | 0 | 2 | 0 | 492 | 151 |
| discopop_gate | claude-haiku-4-5-20251001 | 65 | 0 | 0 | 0 | 0 | 65 | 0 | 0 | 0 | 0 | 0 | 0 | 14 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/bicg | default | claude-haiku-4-5-20251001 | 3 | LARGE | 0.71 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| burkardt/md | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 4 | 7 | 1980.6 |
| burkardt/md | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 4 | 5 | 1670.0 |
| burkardt/md | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 4 | 11 | 2335.9 |
| burkardt/md | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 4 | 10 | 2393.9 |
| burkardt/md | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 4 | 10 | 2203.9 |
| burkardt/md | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 708.3 |
| burkardt/md | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 708.5 |
| burkardt/md | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 708.6 |
| burkardt/md | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 709.1 |
| burkardt/md | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 708.6 |
| npb/is | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 1216.7 |
| npb/is | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 7 | 5012.4 |
| npb/is | default | claude-haiku-4-5-20251001 | 3 | AGENT_TIMEOUT | — | —+— | — | 1 | 3 | 5400.0 |
| npb/is | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 3 | 1077.4 |
| npb/is | default | claude-haiku-4-5-20251001 | 5 | AGENT_TIMEOUT | — | —+— | — | 1 | 7 | 5400.0 |
| npb/is | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 110.9 |
| npb/is | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 110.9 |
| npb/is | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 111.0 |
| npb/is | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 110.6 |
| npb/is | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 110.9 |
| polybench/bicg | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 88.3 |
| polybench/bicg | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 121.4 |
| polybench/bicg | default | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 0.71x | 1+0 | 1 | 2 | 1 | 102.2 |
| polybench/bicg | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 158.6 |
| polybench/bicg | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 151.3 |
| polybench/bicg | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.5 |
| polybench/bicg | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.5 |
| polybench/bicg | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.5 |
| polybench/bicg | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.4 |
| polybench/bicg | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.3 |
| polybench/doitgen | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 4 | 3 | 478.3 |
| polybench/doitgen | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 4 | 2 | 523.6 |
| polybench/doitgen | default | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.01x | 1+0 | 1 | 4 | 1 | 379.3 |
| polybench/doitgen | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 4 | 1 | 413.8 |
| polybench/doitgen | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 4 | 3 | 627.7 |
| polybench/doitgen | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 4 | 0 | 166.1 |
| polybench/doitgen | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 4 | 0 | 167.1 |
| polybench/doitgen | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 166.6 |
| polybench/doitgen | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 4 | 0 | 167.1 |
| polybench/doitgen | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 4 | 0 | 166.2 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 1 | no-change | 0.96x | 0+0 | 0 | 1 | 3 | 462.9 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.76x | 2+0 | 1 | 1 | 2 | 1018.1 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 368.6 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 4 | no-change | 0.95x | 0+0 | 0 | 1 | 2 | 950.3 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.04x | 0+0 | 0 | 1 | 1 | 210.2 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 1 | 0 | 31.3 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.05x | 0+0 | 0 | 1 | 0 | 31.6 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.06x | 0+0 | 0 | 1 | 0 | 31.4 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.04x | 0+0 | 0 | 1 | 0 | 31.1 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 31.6 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 1 | 174.5 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 850.1 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 188.1 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 0 | 1 | 296.2 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 1 | 172.7 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 4.5 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 480.2 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.15x | 2+0 | 1 | 0 | 1 | 1428.9 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 2 | 500.3 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 683.3 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 3.50x | 1+0 | 1 | 0 | 2 | 675.6 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.80x | 1+0 | 1 | 1 | 1 | 94.9 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 4.87x | 1+0 | 1 | 1 | 1 | 96.2 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 4.27x | 1+0 | 1 | 1 | 1 | 104.6 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 4.18x | 1+0 | 1 | 1 | 1 | 87.9 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 4.26x | 1+0 | 1 | 1 | 1 | 101.1 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 39.4 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 39.8 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 39.2 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 39.5 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 39.4 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 1 | 491.6 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.07x | 1+0 | 1 | 0 | 2 | 506.4 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 507.7 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 450.8 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 1.10x | 1+0 | 1 | 0 | 1 | 949.7 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 7.4 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.39x | 1+0 | 1 | 0 | 1 | 275.8 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.10x | 2+0 | 1 | 0 | 1 | 249.6 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.36x | 1+0 | 1 | 0 | 1 | 213.9 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 228.2 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 356.5 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.23x | 2+0 | 1 | 1 | 4 | 723.8 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 737.9 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 1 | 5 | 900.4 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 1115.6 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 1 | 1 | 353.3 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 122.1 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.97x | 0+0 | 0 | 1 | 0 | 123.9 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 123.9 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 124.5 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 124.2 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.68x | 3+0 | 1 | 0 | 1 | 442.0 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.08x | 1+0 | 1 | 0 | 1 | 1092.3 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.17x | 1+0 | 1 | 0 | 1 | 338.1 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 1.24x | 1+0 | 1 | 0 | 3 | 1019.8 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 1461.7 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.8 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.7 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.7 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.95x | 0+0 | 0 | 0 | 0 | 13.8 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.8 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 524.6 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 2 | 497.2 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 2 | 568.0 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 446.0 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 4.39x | 1+0 | 1 | 0 | 2 | 313.5 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.0 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 6.9 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.9 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.8 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.9 |
