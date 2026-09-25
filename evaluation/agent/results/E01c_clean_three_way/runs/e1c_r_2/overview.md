# Agent experiment run `e1c_r_2`

- status: finished (created 2026-09-24T18:33:43, finished 2026-09-25T00:30:24)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `33673d7d0695b9ed0201deccd99efb0e2cf8eda9` (uncommitted diff sha256 `None`)
- harness: `33673d7d0695b9ed0201deccd99efb0e2cf8eda9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 25 | 12 | 3 | 0 | 0 | 5 | 0 | 1 | 3 | 1 | 0 | 0 | 1.30x (n=21) |
| default | claude-haiku-4-5-20251001 | 25 | 13 | 1 | 0 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 1.13x (n=25) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm | claude-haiku-4-5-20251001 | 5 | 25 | 12 | 3 | 0 | 0 | 5 | 0 | 1 | 3 | 1 | 0 | 0 | 1.30x (n=21) |
| R | default | claude-haiku-4-5-20251001 | 5 | 25 | 13 | 1 | 0 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 1.13x (n=25) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 1.32x | 1.32x | 5 gained |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 1.27x | 1.27x | 3 gained, 2 neither |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,no-change,parallel-not-faster,parallel-not-faster · 1.00x | 1.00x | 1 gained-not-faster, 1 worse, 1 neither, 2 unsafe |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 1.24x | 1.24x | 4 gained, 1 neither |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.36x | 0.36x | 1 gained-not-faster, 4 worse |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,parallel-not-faster · 1.06x | 1.06x | 2 gained, 1 gained-not-faster, 2 neither |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,FASTER,FASTER,FASTER · 3.52x | 3.52x | 4 gained, 1 unsafe |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,VERIFY_FAILED,parallel-not-faster · 2.04x | 2.04x | 3 gained, 1 gained-not-faster, 1 invalid |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 2.80x | 2.80x | 4 gained, 1 neither |

**Speed ratios withheld for 1 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 25 | 12 | 8 | 0 | 0 | 1 | 3 | 0 | 1 | 0 | 0 | 0 | 107 | 25 |
| default | claude-haiku-4-5-20251001 | 25 | 13 | 1 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 510 | 30 |
| discopop_gate | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 54 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 1.28x | —+— | — | — | 1 | 164.2 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.19x | —+— | — | — | 1 | 93.6 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 1.32x | —+— | — | — | 1 | 108.4 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 1.30x | —+— | — | — | 1 | 95.9 |
| tsvc/s212 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 3.09x | —+— | — | — | 1 | 82.4 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.10x | 2+0 | 1 | 1 | 1 | 397.9 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.27x | 1+0 | 1 | 1 | 1 | 318.8 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 509.9 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 1.28x | 1+0 | 1 | 1 | 1 | 499.0 |
| tsvc/s212 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 1 | 1 | 502.3 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 49.4 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 50.6 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 50.3 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 50.6 |
| tsvc/s212 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 50.6 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.05x | —+— | — | — | 1 | 88.6 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 2.35x | —+— | — | — | 1 | 163.7 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.31x | —+— | — | — | 1 | 137.6 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 4 | BROKEN | 2.42x | —+— | — | — | 1 | 109.5 |
| tsvc/s241 | bare_llm | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | —+— | — | — | 1 | 13.3 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 3 | 934.3 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.48x | 3+0 | 1 | 1 | 1 | 697.4 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.44x | 3+0 | 1 | 1 | 1 | 673.1 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 1.24x | 2+0 | 1 | 1 | 1 | 578.4 |
| tsvc/s241 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 1.23x | 3+0 | 1 | 1 | 2 | 681.8 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 121.4 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 126.2 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 126.5 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 1 | 0 | 122.6 |
| tsvc/s241 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.07x | 0+0 | 0 | 1 | 0 | 123.0 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.36x | —+— | — | — | 1 | 106.7 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.35x | —+— | — | — | 1 | 62.9 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 1.07x | —+— | — | — | 1 | 94.4 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.46x | —+— | — | — | 1 | 191.2 |
| tsvc/s243 | bare_llm | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.36x | —+— | — | — | 1 | 83.5 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.06x | 1+0 | 1 | 1 | 1 | 556.0 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.34x | 2+0 | 1 | 1 | 1 | 592.4 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 644.8 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.07x | 0+0 | 0 | 1 | 1 | 293.2 |
| tsvc/s243 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 1.13x | 1+0 | 1 | 1 | 1 | 524.6 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 128.1 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.07x | 0+0 | 0 | 1 | 0 | 132.5 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 129.3 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 128.5 |
| tsvc/s243 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 128.6 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.00x | —+— | — | — | 1 | 229.0 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 0.26x | —+— | — | — | 1 | 188.8 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 4.03x | —+— | — | — | 1 | 220.2 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 4.18x | —+— | — | — | 1 | 147.6 |
| tsvc/s244 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 1.36x | —+— | — | — | 1 | 295.2 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 1 | 1 | 293.5 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.05x | 0+0 | 0 | 1 | 2 | 684.8 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 290.3 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 1 | 2 | 672.6 |
| tsvc/s244 | default | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 1 | 1 | 513.7 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 53.8 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.06x | 0+0 | 0 | 1 | 0 | 54.4 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 53.7 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 53.8 |
| tsvc/s244 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 53.3 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.61x | —+— | — | — | 1 | 80.3 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 2 | VERIFY_FAILED | — | —+— | — | — | 1 | 103.5 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.97x | —+— | — | — | 1 | 82.2 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 2.06x | —+— | — | — | 1 | 109.8 |
| tsvc/s252 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 2.03x | —+— | — | — | 1 | 61.9 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.58x | 1+0 | 1 | 1 | 1 | 177.7 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 2 | no-change | 0.98x | 0+0 | 0 | 1 | 1 | 228.3 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.63x | 1+0 | 1 | 1 | 1 | 168.3 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 2.06x | 2+0 | 1 | 1 | 1 | 278.0 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.80x | 1+0 | 1 | 1 | 1 | 228.3 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 38.4 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 40.9 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 38.5 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 38.5 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 38.4 |
