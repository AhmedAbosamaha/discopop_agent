# Agent experiment run `e1c_r_4`

- status: finished (created 2026-09-24T18:33:46, finished 2026-09-24T22:24:03)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `33673d7d0695b9ed0201deccd99efb0e2cf8eda9` (uncommitted diff sha256 `None`)
- harness: `33673d7d0695b9ed0201deccd99efb0e2cf8eda9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 20 | 12 | 0 | 0 | 0 | 6 | 0 | 0 | 1 | 1 | 0 | 0 | 2.58x (n=18) |
| default | claude-haiku-4-5-20251001 | 20 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 1.23x (n=20) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm | claude-haiku-4-5-20251001 | 4 | 20 | 12 | 0 | 0 | 0 | 6 | 0 | 0 | 1 | 1 | 0 | 0 | 2.58x (n=18) |
| R | default | claude-haiku-4-5-20251001 | 4 | 20 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 1.23x (n=20) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.52x | 2.52x | 5 gained |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.61x | 2.61x | 5 gained |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.84x | 2.84x | 5 gained |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.87x | 2.87x | 5 gained |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,VERIFY_FAILED,parallel-not-faster,parallel-not-faster · 2.28x | 2.28x | 2 gained, 2 worse, 1 invalid |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.43x | 0.43x | 4 worse, 1 unsafe |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |

**Speed ratios withheld for 2 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 20 | 12 | 6 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 81 | 20 |
| default | claude-haiku-4-5-20251001 | 20 | 10 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 172 | 21 |
| discopop_gate | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 29 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.50x | —+— | — | — | 1 | 57.3 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.73x | —+— | — | — | 1 | 75.2 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 2.52x | —+— | — | — | 1 | 87.0 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 2.40x | —+— | — | — | 1 | 72.0 |
| tsvc/s292 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 2.63x | —+— | — | — | 1 | 73.6 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.63x | 1+0 | 1 | 1 | 1 | 162.8 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.47x | 1+0 | 1 | 1 | 1 | 210.3 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.61x | 1+0 | 1 | 1 | 1 | 165.0 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 2.59x | 1+0 | 1 | 1 | 1 | 136.5 |
| tsvc/s292 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.67x | 1+0 | 1 | 1 | 1 | 139.0 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 38.4 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 38.5 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 38.6 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 1 | 0 | 38.8 |
| tsvc/s292 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 1 | 0 | 38.7 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.16x | —+— | — | — | 1 | 26.1 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.84x | —+— | — | — | 1 | 42.8 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 2.84x | —+— | — | — | 1 | 43.9 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 2.87x | —+— | — | — | 1 | 32.9 |
| tsvc/s293 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 2.81x | —+— | — | — | 1 | 38.7 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.87x | 1+0 | 1 | 1 | 1 | 130.4 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.02x | 1+0 | 1 | 1 | 1 | 114.1 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.46x | 1+0 | 1 | 1 | 1 | 136.7 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 2.92x | 1+0 | 1 | 1 | 1 | 132.9 |
| tsvc/s293 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.87x | 1+0 | 1 | 1 | 1 | 141.8 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 23.9 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.03x | 0+0 | 0 | 1 | 0 | 23.7 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 23.6 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.97x | 0+0 | 0 | 1 | 0 | 23.6 |
| tsvc/s293 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 1 | 0 | 23.7 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 4.48x | —+— | — | — | 1 | 98.4 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.08x | —+— | — | — | 1 | 154.7 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 4.48x | —+— | — | — | 1 | 92.6 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.08x | —+— | — | — | 1 | 102.7 |
| tsvc/s331 | bare_llm | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 101.4 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 179.0 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 2 | 1 | 179.6 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 2 | 1 | 211.7 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 2 | 1 | 260.4 |
| tsvc/s331 | default | claude-haiku-4-5-20251001 | 5 | no-change | 0.98x | 0+0 | 0 | 2 | 2 | 694.5 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 28.9 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 28.2 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 2 | 0 | 28.1 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 28.1 |
| tsvc/s331 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 28.0 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.21x | —+— | — | — | 1 | 91.2 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.43x | —+— | — | — | 1 | 108.8 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.43x | —+— | — | — | 1 | 84.3 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 0.43x | —+— | — | — | 1 | 113.2 |
| tsvc/s341 | bare_llm | claude-haiku-4-5-20251001 | 5 | BROKEN | — | —+— | — | — | 1 | 77.1 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 2 | 1 | 227.0 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 274.5 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 347.4 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.12x | 0+0 | 0 | 2 | 1 | 144.3 |
| tsvc/s341 | default | claude-haiku-4-5-20251001 | 5 | no-change | 0.96x | 0+0 | 0 | 2 | 1 | 216.5 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 2 | 0 | 29.8 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.04x | 0+0 | 0 | 2 | 0 | 29.9 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 30.2 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 2 | 0 | 30.2 |
| tsvc/s341 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.96x | 0+0 | 0 | 2 | 0 | 29.7 |
