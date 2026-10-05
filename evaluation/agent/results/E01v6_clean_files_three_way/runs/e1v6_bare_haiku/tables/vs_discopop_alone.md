| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-haiku-4-5-20251001 | 105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 105 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm_v4 | claude-haiku-4-5-20251001 | 18 | 90 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 90 | — |
| A | bare_llm_v4 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | — |
| D | bare_llm_v4 | claude-haiku-4-5-20251001 | 4 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/s000 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | VERIFY_FAILED · — | — | 1 no-baseline |
| tsvc_c2/s112 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,VERIFY_FAILED,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.65x | — | 5 no-baseline |
| tsvc_c2/s121 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.67x | — | 5 no-baseline |
| tsvc_c2/s1213 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,FASTER,FASTER,VERIFY_FAILED · 2.57x | — | 5 no-baseline |
| tsvc_c2/s127 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.89x | — | 5 no-baseline |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,VERIFY_FAILED,parallel-not-faster · 1.10x | — | 5 no-baseline |
| tsvc_c2/s212 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,FASTER · 1.73x | — | 5 no-baseline |
| tsvc_c2/s241 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,VERIFY_FAILED,VERIFY_FAILED,parallel-not-faster · 1.20x | — | 5 no-baseline |
| tsvc_c2/s243 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,VERIFY_FAILED,VERIFY_FAILED,parallel-not-faster · 1.39x | — | 5 no-baseline |
| tsvc_c2/s244 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED · — | — | 5 no-baseline |
| tsvc_c2/s252 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,VERIFY_FAILED,parallel-not-faster · 2.92x | — | 5 no-baseline |
| tsvc_c2/s254 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 3.43x | — | 5 no-baseline |
| tsvc_c2/s255 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,VERIFY_FAILED,VERIFY_FAILED · 2.55x | — | 5 no-baseline |
| tsvc_c2/s281 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,FASTER,FASTER,FASTER · 3.21x | — | 5 no-baseline |
| tsvc_c2/s291 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 3.48x | — | 5 no-baseline |
| tsvc_c2/s292 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED · 2.93x | — | 5 no-baseline |
| tsvc_c2/s293 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.89x | — | 5 no-baseline |
| tsvc_c2/s3112 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,VERIFY_FAILED,VERIFY_FAILED · — | — | 3 no-baseline |
| tsvc_c2/s313 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER · 4.65x | — | 1 no-baseline |
| tsvc_c2/s321 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,VERIFY_FAILED,changed-not-parallel · 1.00x | — | 3 no-baseline |
| tsvc_c2/s322 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN · — | — | 3 no-baseline |
| tsvc_c2/s323 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN · — | — | 3 no-baseline |
| tsvc_c2/s331 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 4.70x | — | 5 no-baseline |
| tsvc_c2/s341 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,VERIFY_FAILED,parallel-not-faster,parallel-not-faster · 0.39x | — | 5 no-baseline |
| tsvc_c2/vpvtv | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.62x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
