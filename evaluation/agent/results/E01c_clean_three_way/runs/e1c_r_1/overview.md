# Agent experiment run `e1c_r_1`

- status: finished (created 2026-09-24T18:33:40, finished 2026-09-25T00:40:20)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `33673d7d0695b9ed0201deccd99efb0e2cf8eda9` (uncommitted diff sha256 `None`)
- harness: `33673d7d0695b9ed0201deccd99efb0e2cf8eda9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 25 | 5 | 0 | 0 | 0 | 6 | 0 | 1 | 10 | 3 | 0 | 0 | 0.88x (n=12) |
| default | claude-haiku-4-5-20251001 | 25 | 12 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 1.00x (n=25) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm | claude-haiku-4-5-20251001 | 5 | 25 | 5 | 0 | 0 | 0 | 6 | 0 | 1 | 10 | 3 | 0 | 0 | 0.88x (n=12) |
| R | default | claude-haiku-4-5-20251001 | 5 | 25 | 12 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 1.00x (n=25) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.70x | 0.70x | 4 worse, 1 unsafe |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,parallel-not-faster,parallel-not-faster · 0.69x | 0.69x | 2 worse, 3 unsafe |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,VERIFY_FAILED,VERIFY_FAILED · — | — | 3 unsafe, 2 invalid |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 3.72x | 3.72x | 4 gained, 1 neither |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.83x | 3.83x | 5 gained |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,FASTER,VERIFY_FAILED · 1.56x | 1.56x | 1 gained, 3 unsafe, 1 invalid |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 1.10x | 1.10x | 3 gained, 2 neither |

**Speed ratios withheld for 3 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 25 | 5 | 6 | 0 | 0 | 1 | 10 | 0 | 3 | 0 | 0 | 0 | 120 | 25 |
| default | claude-haiku-4-5-20251001 | 25 | 12 | 0 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 440 | 54 |
| discopop_gate | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.76x | —+— | — | — | 1 | 127.3 |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.63x | —+— | — | — | 1 | 76.7 |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.77x | —+— | — | — | 1 | 159.4 |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 4 | BROKEN | 3.46x | —+— | — | — | 1 | 86.2 |
| tsvc/s112 | bare_llm | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.59x | —+— | — | — | 1 | 215.0 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 1 | 2 | 274.7 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 1 | 1 | 390.0 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.05x | 0+0 | 0 | 1 | 2 | 440.5 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 4 | no-change | 0.96x | 0+0 | 0 | 1 | 3 | 547.0 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 1 | 3 | 663.3 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 31.2 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 31.3 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 31.4 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 1 | 0 | 31.3 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.97x | 0+0 | 0 | 1 | 0 | 30.8 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.63x | —+— | — | — | 1 | 98.6 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 3.50x | —+— | — | — | 1 | 51.7 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.42x | —+— | — | — | 1 | 38.4 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.76x | —+— | — | — | 1 | 120.5 |
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 5 | BROKEN | 3.55x | —+— | — | — | 1 | 58.8 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.33x | 2+0 | 1 | 1 | 1 | 241.4 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.39x | 2+0 | 1 | 1 | 1 | 380.0 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 288.9 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.05x | 0+0 | 0 | 1 | 1 | 235.0 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 324.5 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 30.9 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 30.5 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 30.6 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 31.0 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 31.3 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 152.4 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 0.83x | —+— | — | — | 1 | 156.6 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 0.78x | —+— | — | — | 1 | 311.1 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 4 | BROKEN | 0.80x | —+— | — | — | 1 | 97.7 |
| tsvc/s1213 | bare_llm | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 211.9 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 6 | 1209.5 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.57x | 2+0 | 1 | 0 | 5 | 1486.2 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 781.8 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 2.54x | 2+0 | 1 | 0 | 5 | 1093.5 |
| tsvc/s1213 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 905.9 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s1213 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.2 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.67x | —+— | — | — | 1 | 28.8 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 3.82x | —+— | — | — | 1 | 46.1 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 3.72x | —+— | — | — | 1 | 39.3 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 3.98x | —+— | — | — | 1 | 42.0 |
| tsvc/s127 | bare_llm | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | —+— | — | — | 1 | 38.0 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.11x | 1+0 | 1 | 1 | 1 | 155.2 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.83x | 1+0 | 1 | 1 | 1 | 150.9 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.67x | 1+0 | 1 | 1 | 1 | 151.4 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.92x | 1+0 | 1 | 1 | 1 | 143.4 |
| tsvc/s127 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 3.98x | 1+0 | 1 | 1 | 1 | 136.7 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 38.6 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 38.5 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 38.6 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 1 | 0 | 39.0 |
| tsvc/s127 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 40.0 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 2.56x | —+— | — | — | 1 | 147.2 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 1.25x | —+— | — | — | 1 | 143.6 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 2.92x | —+— | — | — | 1 | 155.0 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 212.5 |
| tsvc/s211 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 1.56x | —+— | — | — | 1 | 185.6 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 758.2 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.10x | 1+0 | 1 | 0 | 2 | 672.1 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.14x | 1+0 | 1 | 0 | 2 | 521.9 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 892.7 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.12x | 3+0 | 1 | 0 | 2 | 442.8 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 7.7 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.7 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.1 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.2 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.0 |
