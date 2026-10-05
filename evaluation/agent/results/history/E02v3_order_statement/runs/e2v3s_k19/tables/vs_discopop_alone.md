| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-sonnet-5 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | — |
| full_b1_nospeed_v3 | claude-sonnet-5 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | — |
| no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | — |
| twin_full_nospeed_v3 | claude-sonnet-5 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | — |
| twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | — |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 10 no-baseline |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,parallel-not-faster · 1.41x | — | 10 no-baseline |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | — · — | no-change,no-change,no-change,no-change,no-change,no-change,no-change,no-change,no-change,parallel-not-faster · 1.00x | — | 10 no-baseline |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | — · — | BROKEN,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,changed-not-parallel · 1.36x | — | 10 no-baseline |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | — · — | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN · — | — | 10 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
