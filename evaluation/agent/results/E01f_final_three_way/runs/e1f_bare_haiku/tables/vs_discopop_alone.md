| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v3 | claude-haiku-4-5-20251001 | 105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 105 | — |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_b1/s000 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.17x | — | 1 no-baseline |
| tsvc_b1/s112 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,parallel-not-faster,parallel-not-faster · 0.41x | — | 5 no-baseline |
| tsvc_b1/s121 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.61x | — | 5 no-baseline |
| tsvc_b1/s1213 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,VERIFY_FAILED · — | — | 5 no-baseline |
| tsvc_b1/s127 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 4.33x | — | 5 no-baseline |
| tsvc_b1/s211 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,FASTER,VERIFY_FAILED,parallel-not-faster · 1.53x | — | 5 no-baseline |
| tsvc_b1/s212 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.29x | — | 5 no-baseline |
| tsvc_b1/s241 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 1.15x | — | 5 no-baseline |
| tsvc_b1/s243 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.40x | — | 5 no-baseline |
| tsvc_b1/s244 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,FASTER · 3.54x | — | 5 no-baseline |
| tsvc_b1/s252 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 2.81x | — | 5 no-baseline |
| tsvc_b1/s254 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 3.34x | — | 5 no-baseline |
| tsvc_b1/s255 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.54x | — | 5 no-baseline |
| tsvc_b1/s281 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,FASTER,FASTER,parallel-not-faster · 3.19x | — | 5 no-baseline |
| tsvc_b1/s291 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 3.42x | — | 5 no-baseline |
| tsvc_b1/s292 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.62x | — | 5 no-baseline |
| tsvc_b1/s293 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.57x | — | 5 no-baseline |
| tsvc_b1/s3112 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | no-change,parallel-not-faster,parallel-not-faster · 0.08x | — | 3 no-baseline |
| tsvc_b1/s313 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER · 4.96x | — | 1 no-baseline |
| tsvc_b1/s321 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,changed-not-parallel,changed-not-parallel · 1.00x | — | 3 no-baseline |
| tsvc_b1/s322 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,no-change · 1.00x | — | 3 no-baseline |
| tsvc_b1/s323 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | BROKEN,VERIFY_FAILED,VERIFY_FAILED · — | — | 3 no-baseline |
| tsvc_b1/s331 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 4.50x | — | 5 no-baseline |
| tsvc_b1/s341 | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.58x | — | 5 no-baseline |
| tsvc_b1/vpvtv | bare_llm_v3 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.41x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
