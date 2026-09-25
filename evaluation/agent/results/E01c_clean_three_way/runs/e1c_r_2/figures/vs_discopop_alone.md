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
