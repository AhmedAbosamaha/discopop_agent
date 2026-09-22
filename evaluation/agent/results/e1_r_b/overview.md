# Agent experiment run `e1_r_b`

- status: finished (created 2026-09-21T15:10:54, finished 2026-09-22T04:34:36)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `00d4594f1093d7610728a79463079acac522af26` (uncommitted diff sha256 `None`)
- harness: `00d4594f1093d7610728a79463079acac522af26` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 65 | 30 | 5 | 0 | 0 | 0 | 0 | 30 | 0 | 0 | 0 | 0 | 1.37x (n=60) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | default | claude-haiku-4-5-20251001 | 13 | 65 | 30 | 5 | 0 | 0 | 0 | 0 | 30 | 0 | 0 | 0 | 0 | 1.37x (n=60) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| polybench/floyd-warshall | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 5.12x | 5.12x | 3 gained, 2 neither |
| polybench/seidel-2d | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | parallel-speed-not-measurable,parallel-speed-not-measurable,parallel-speed-not-measurable,parallel-speed-not-measurable,parallel-speed-not-measurable · — | — | 5 gained-not-faster |
| rodinia-3.1/hotspot | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 2.35x | 2.35x | 3 gained, 2 neither |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.80x | 3.80x | 5 gained |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 2.29x | 2.29x | 4 gained, 1 neither |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.76x | 3.76x | 5 gained |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.34x | 2.34x | 5 gained |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.30x | 3.30x | 5 gained |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 65 | 30 | 0 | 5 | 0 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 206 | 118 |
| discopop_gate | claude-haiku-4-5-20251001 | 65 | 0 | 0 | 0 | 0 | 65 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | 0 |

### Kernels too short to time (T0.1) — ratios are not speedups

| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |
|---|---|---|---:|---|---:|
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 1 | LARGE | 0.08 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 2 | LARGE | 0.05 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 3 | LARGE | 0.15 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 4 | LARGE | 0.15 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 5 | LARGE | 0.10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/floyd-warshall | default | claude-haiku-4-5-20251001 | 1 | FASTER | 5.93x | 1+0 | 1 | 3 | 1 | 189.8 |
| polybench/floyd-warshall | default | claude-haiku-4-5-20251001 | 2 | no-change | 0.98x | 0+0 | 0 | 3 | 1 | 823.2 |
| polybench/floyd-warshall | default | claude-haiku-4-5-20251001 | 3 | FASTER | 5.12x | 1+0 | 1 | 3 | 1 | 195.9 |
| polybench/floyd-warshall | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 3 | 3 | 961.9 |
| polybench/floyd-warshall | default | claude-haiku-4-5-20251001 | 5 | FASTER | 10.28x | 1+0 | 1 | 3 | 1 | 152.9 |
| polybench/floyd-warshall | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 3 | 0 | 18.8 |
| polybench/floyd-warshall | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 18.7 |
| polybench/floyd-warshall | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 18.7 |
| polybench/floyd-warshall | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 3 | 0 | 18.7 |
| polybench/floyd-warshall | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 3 | 0 | 18.4 |
| polybench/seidel-2d | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 6 | 958.4 |
| polybench/seidel-2d | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 2372.7 |
| polybench/seidel-2d | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1376.8 |
| polybench/seidel-2d | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 2013.3 |
| polybench/seidel-2d | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 8 | 1342.1 |
| polybench/seidel-2d | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.5 |
| polybench/seidel-2d | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.5 |
| polybench/seidel-2d | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.6 |
| polybench/seidel-2d | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.5 |
| polybench/seidel-2d | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.5 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 1 | parallel-speed-not-measurable | 0.08x | 1+0 | 1 | 0 | 1 | 89.1 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 2 | parallel-speed-not-measurable | 0.05x | 1+0 | 1 | 0 | 1 | 101.4 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 3 | parallel-speed-not-measurable | 0.15x | 1+0 | 1 | 0 | 1 | 89.4 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 4 | parallel-speed-not-measurable | 0.15x | 1+0 | 1 | 0 | 1 | 80.5 |
| polybench/trisolv | default | claude-haiku-4-5-20251001 | 5 | parallel-speed-not-measurable | 0.10x | 1+0 | 1 | 0 | 1 | 83.6 |
| polybench/trisolv | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 1.9 |
| polybench/trisolv | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 1.8 |
| polybench/trisolv | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 1.8 |
| polybench/trisolv | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 1.9 |
| polybench/trisolv | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 1.9 |
| rodinia-3.1/hotspot | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.09x | 0+0 | 0 | 6 | 2 | 891.3 |
| rodinia-3.1/hotspot | default | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 6 | 1 | 742.7 |
| rodinia-3.1/hotspot | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 6 | 1 | 786.3 |
| rodinia-3.1/hotspot | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.04x | 0+0 | 0 | 6 | 1 | 1372.0 |
| rodinia-3.1/hotspot | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.09x | 0+0 | 0 | 6 | 1 | 683.0 |
| rodinia-3.1/hotspot | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 6 | 0 | 550.0 |
| rodinia-3.1/hotspot | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 6 | 0 | 560.6 |
| rodinia-3.1/hotspot | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 6 | 0 | 553.4 |
| rodinia-3.1/hotspot | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.05x | 0+0 | 0 | 6 | 0 | 557.1 |
| rodinia-3.1/hotspot | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 6 | 0 | 528.3 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 4.15x | 1+0 | 1 | 1 | 1 | 191.6 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 4.29x | 1+0 | 1 | 1 | 1 | 231.2 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.35x | 2+0 | 1 | 1 | 1 | 180.6 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 469.9 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 792.4 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 39.4 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 39.3 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 39.8 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 39.7 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 39.7 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.83x | 1+0 | 1 | 2 | 1 | 117.1 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.37x | 1+0 | 1 | 2 | 1 | 206.4 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.80x | 1+0 | 1 | 2 | 1 | 145.2 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 4.66x | 1+0 | 1 | 2 | 1 | 116.8 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 3.69x | 1+0 | 1 | 2 | 1 | 768.1 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 2 | 0 | 32.6 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 2 | 0 | 31.9 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 2 | 0 | 32.8 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 2 | 0 | 33.0 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 33.1 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.43x | 1+0 | 1 | 1 | 1 | 114.2 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.06x | 1+0 | 1 | 1 | 1 | 128.8 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.30x | 1+0 | 1 | 1 | 1 | 158.9 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 2 | 765.8 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.29x | 1+0 | 1 | 1 | 1 | 92.7 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 31.3 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 31.6 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 31.7 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 31.2 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 31.7 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 2 | 241.8 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 276.0 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 1 | 208.4 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 425.5 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 240.4 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.7 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.94x | 1+0 | 1 | 2 | 1 | 162.5 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.03x | 1+0 | 1 | 2 | 1 | 1287.9 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.68x | 1+0 | 1 | 2 | 1 | 120.8 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.97x | 1+0 | 1 | 2 | 1 | 108.1 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 3.76x | 1+0 | 1 | 2 | 1 | 108.6 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 32.7 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.98x | 0+0 | 0 | 2 | 0 | 32.7 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 2 | 0 | 33.1 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 31.9 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 2 | 0 | 32.8 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.74x | 1+0 | 1 | 1 | 1 | 107.4 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.45x | 1+0 | 1 | 1 | 1 | 1326.2 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.27x | 1+0 | 1 | 1 | 1 | 1300.6 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 2.34x | 1+0 | 1 | 1 | 1 | 110.3 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.40x | 1+0 | 1 | 1 | 1 | 90.8 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 40.2 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.03x | 0+0 | 0 | 1 | 0 | 40.0 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 39.9 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 40.2 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.04x | 0+0 | 0 | 1 | 0 | 39.9 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.38x | 1+0 | 1 | 1 | 1 | 73.3 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.19x | 1+0 | 1 | 1 | 1 | 135.6 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.30x | 1+0 | 1 | 1 | 1 | 76.1 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.50x | 1+0 | 1 | 1 | 1 | 126.2 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 3.11x | 1+0 | 1 | 1 | 1 | 115.1 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 23.5 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 23.7 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 23.4 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 23.7 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 23.7 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 2 | 458.7 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 2 | 1 | 250.6 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 2 | 2 | 2320.1 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 1392.3 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 2 | 2 | 685.6 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 29.4 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.97x | 0+0 | 0 | 2 | 0 | 28.9 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 29.3 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 2 | 0 | 29.4 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 29.4 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 118.9 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 826.2 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 164.7 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 166.3 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 276.9 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 30.6 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 30.6 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 30.7 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 30.6 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 30.6 |
