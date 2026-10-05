| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-sonnet-5 | 105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 105 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm_v4 | claude-sonnet-5 | 18 | 90 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 90 | — |
| A | bare_llm_v4 | claude-sonnet-5 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | — |
| D | bare_llm_v4 | claude-sonnet-5 | 4 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/s000 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER · 3.53x | — | 1 no-baseline |
| tsvc_c2/s112 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 1.46x | — | 5 no-baseline |
| tsvc_c2/s121 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 1.38x | — | 5 no-baseline |
| tsvc_c2/s1213 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.09x | — | 5 no-baseline |
| tsvc_c2/s127 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.93x | — | 5 no-baseline |
| tsvc_c2/s211 | bare_llm_v4 | claude-sonnet-5 | — · — | BROKEN,FASTER,FASTER,FASTER,FASTER · 2.34x | — | 5 no-baseline |
| tsvc_c2/s212 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.32x | — | 5 no-baseline |
| tsvc_c2/s241 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 1.74x | — | 5 no-baseline |
| tsvc_c2/s243 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.39x | — | 5 no-baseline |
| tsvc_c2/s244 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 5.36x | — | 5 no-baseline |
| tsvc_c2/s252 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.59x | — | 5 no-baseline |
| tsvc_c2/s254 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.50x | — | 5 no-baseline |
| tsvc_c2/s255 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.28x | — | 5 no-baseline |
| tsvc_c2/s281 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 4.01x | — | 5 no-baseline |
| tsvc_c2/s291 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.40x | — | 5 no-baseline |
| tsvc_c2/s292 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.91x | — | 5 no-baseline |
| tsvc_c2/s293 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.83x | — | 5 no-baseline |
| tsvc_c2/s3112 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER · 3.25x | — | 3 no-baseline |
| tsvc_c2/s313 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER · 4.63x | — | 1 no-baseline |
| tsvc_c2/s321 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,parallel-not-faster,parallel-not-faster · 1.01x | — | 3 no-baseline |
| tsvc_c2/s322 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,no-change,parallel-not-faster · 1.02x | — | 3 no-baseline |
| tsvc_c2/s323 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,parallel-not-faster,parallel-not-faster · 1.06x | — | 3 no-baseline |
| tsvc_c2/s331 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 4.47x | — | 5 no-baseline |
| tsvc_c2/s341 | bare_llm_v4 | claude-sonnet-5 | — · — | BROKEN,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 1.61x | — | 5 no-baseline |
| tsvc_c2/vpvtv | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER · 3.64x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
