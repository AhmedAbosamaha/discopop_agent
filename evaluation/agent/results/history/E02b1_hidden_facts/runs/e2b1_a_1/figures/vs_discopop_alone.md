| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| full_b1_nospeed | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| twin_full_nospeed | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |
| twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | — |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_b1/s151 | bare_llm_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,VERIFY_FAILED,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.15x | — | 10 no-baseline |
| tsvc_b1/s151 | full_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.48x | — | 10 no-baseline |
| tsvc_b1/s151 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 1.09x | — | 10 no-baseline |
| tsvc_b1/s151 | twin_full_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,SCAFFOLD_MODIFIED,changed-not-parallel,changed-not-parallel,changed-not-parallel,changed-not-parallel,parallel-not-faster · 1.00x | — | 10 no-baseline |
| tsvc_b1/s151 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,FASTER,FASTER,FASTER,changed-not-parallel,changed-not-parallel,changed-not-parallel,changed-not-parallel,parallel-not-faster,parallel-not-faster · 1.00x | — | 10 no-baseline |
| tsvc_b1/s161 | bare_llm_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,FASTER,FASTER,FASTER,parallel-not-faster · 1.74x | — | 10 no-baseline |
| tsvc_b1/s161 | full_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,no-change,no-change,no-change,no-change · 2.16x | — | 10 no-baseline |
| tsvc_b1/s161 | no_evidence_b1_nospeed | claude-haiku-4-5-20251001 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,no-change,no-change,no-change,parallel-not-faster · 1.52x | — | 10 no-baseline |
| tsvc_b1/s161 | twin_full_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,FASTER,VERIFY_FAILED,VERIFY_FAILED · 2.28x | — | 10 no-baseline |
| tsvc_b1/s161 | twin_no_evidence_nospeed | claude-haiku-4-5-20251001 | — · — | BROKEN,BROKEN,BROKEN,FASTER,FASTER,FASTER,FASTER,FASTER,changed-not-parallel,changed-not-parallel · 1.52x | — | 10 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
