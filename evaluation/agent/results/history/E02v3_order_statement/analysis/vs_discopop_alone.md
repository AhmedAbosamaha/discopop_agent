| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | 40 | 5 | 2 | 0 | 0 | 2 | 0 | 0 | 25 | 6 | 0 | 0 | 2.46x (n=9) |
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 40 | 35 | 2 | 0 | 0 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 1.71x (n=40) |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,VERIFY_FAILED · — | — | 9 unsafe, 1 invalid |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 1.43x | 1.43x | 10 gained |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED,VERIFY_FAILED,parallel-not-faster · 2.47x | 2.47x | 4 gained, 1 worse, 3 unsafe, 2 invalid |
| tsvc_b1/s1213 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,no-change · 2.54x | 2.54x | 9 gained, 1 neither |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,VERIFY_FAILED,parallel-not-faster,parallel-not-faster,parallel-not-faster · 1.05x | 1.05x | 2 gained-not-faster, 1 worse, 6 unsafe, 1 invalid |
| tsvc_b1/s211 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 1.10x | 1.10x | 6 gained, 2 gained-not-faster, 2 worse |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,BROKEN,FASTER,VERIFY_FAILED,VERIFY_FAILED · 3.79x | 3.79x | 1 gained, 7 unsafe, 2 invalid |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 4.02x | 4.02x | 10 gained |

**Speed ratios withheld for 7 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
