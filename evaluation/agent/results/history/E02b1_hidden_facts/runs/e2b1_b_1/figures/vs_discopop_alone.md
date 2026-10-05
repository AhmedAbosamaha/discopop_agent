| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| full_b1_nospeed | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| twin_full_nospeed | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |
| twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | — |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_b1/s152 | bare_llm_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.47x | — | 5 no-baseline |
| tsvc_b1/s152 | full_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,no-change,no-change,parallel-not-faster · 1.00x | — | 5 no-baseline |
| tsvc_b1/s152 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.44x | — | 5 no-baseline |
| tsvc_b1/s152 | twin_full_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,FASTER,FASTER,FASTER · 3.20x | — | 5 no-baseline |
| tsvc_b1/s152 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 3.06x | — | 5 no-baseline |
| tsvc_b1/s171 | bare_llm_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,VERIFY_FAILED,VERIFY_FAILED,no-change · 3.58x | — | 5 no-baseline |
| tsvc_b1/s171 | full_b1_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.77x | — | 5 no-baseline |
| tsvc_b1/s171 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 3.37x | — | 5 no-baseline |
| tsvc_b1/s171 | twin_full_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,SCAFFOLD_MODIFIED,parallel-not-faster,parallel-not-faster · 0.40x | — | 5 no-baseline |
| tsvc_b1/s171 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,FASTER,FASTER,parallel-not-faster · 3.30x | — | 5 no-baseline |
| tsvc_b1/s277 | bare_llm_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,VERIFY_FAILED,VERIFY_FAILED,parallel-not-faster,parallel-not-faster · 0.23x | — | 5 no-baseline |
| tsvc_b1/s277 | full_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 4.50x | — | 5 no-baseline |
| tsvc_b1/s277 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 8.17x | — | 5 no-baseline |
| tsvc_b1/s277 | twin_full_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 5.57x | — | 5 no-baseline |
| tsvc_b1/s277 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,VERIFY_FAILED,parallel-not-faster · 4.81x | — | 5 no-baseline |
| tsvc_b1/s481 | bare_llm_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.57x | — | 5 no-baseline |
| tsvc_b1/s481 | full_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 2.90x | — | 5 no-baseline |
| tsvc_b1/s481 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.25x | — | 5 no-baseline |
| tsvc_b1/s481 | twin_full_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,FASTER,VERIFY_FAILED,VERIFY_FAILED · 2.67x | — | 5 no-baseline |
| tsvc_b1/s481 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,VERIFY_FAILED · 2.65x | — | 5 no-baseline |
| tsvc_b1/vas | bare_llm_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.63x | — | 5 no-baseline |
| tsvc_b1/vas | full_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 1.11x | — | 5 no-baseline |
| tsvc_b1/vas | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster · 1.63x | — | 5 no-baseline |
| tsvc_b1/vas | twin_full_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,SCAFFOLD_MODIFIED,SCAFFOLD_MODIFIED,parallel-not-faster · 1.50x | — | 5 no-baseline |
| tsvc_b1/vas | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.59x | — | 5 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
