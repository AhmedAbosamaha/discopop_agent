| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v5 | claude-haiku-4-5-20251001 | 35 | 24 | 1 | 0 | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 1.86x (n=35) |
| bare_llm_v4 | claude-haiku-4-5-20251001 | 35 | 28 | 0 | 0 | 3 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 7.17x (n=33) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | default_v5 | claude-haiku-4-5-20251001 | 6 | 30 | 24 | 1 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 2.72x (n=30) |
| R | bare_llm_v4 | claude-haiku-4-5-20251001 | 6 | 30 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 8.67x (n=28) |
| A | default_v5 | claude-haiku-4-5-20251001 | 1 | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.00x (n=5) |
| A | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | 5 | 0 | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.99x (n=5) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c4/s314 | default_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.32x | 3.32x | 5 gained |
| tsvc_c4/s316 | default_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,no-change,no-change · 1.33x | 1.33x | 3 gained, 2 neither |
| tsvc_c4/s3113 | default_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.40x | 3.40x | 5 gained |
| tsvc_c4/s319 | default_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 4.16x | 4.16x | 5 gained |
| tsvc_c4/s311 | default_v5 | claude-haiku-4-5-20251001 | FASTER,FASTER,FASTER,FASTER,FASTER · 8.54x | FASTER,FASTER,FASTER,FASTER,FASTER · 8.52x | 1.00x | 5 equal |
| tsvc_c4/s315 | default_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc_c4/s318 | default_v5 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 1.20x | 1.20x | 4 gained, 1 gained-not-faster |
| tsvc_c4/s311 | bare_llm_v4 | claude-haiku-4-5-20251001 | FASTER,FASTER,FASTER,FASTER,FASTER · 8.54x | FASTER,FASTER,FASTER,FASTER,FASTER · 8.48x | 0.99x | 3 equal, 2 worse |
| tsvc_c4/s3113 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 8.90x | 8.90x | 5 gained |
| tsvc_c4/s314 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 9.58x | 9.58x | 5 gained |
| tsvc_c4/s315 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 9.28x | 9.28x | 5 gained |
| tsvc_c4/s316 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,FASTER,FASTER,FASTER · 8.96x | 8.96x | 4 gained, 1 unsafe |
| tsvc_c4/s318 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,FASTER,FASTER,FASTER,FASTER · 5.27x | 5.27x | 4 gained, 1 unsafe |
| tsvc_c4/s319 | bare_llm_v4 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 4.05x | 4.05x | 5 gained |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
