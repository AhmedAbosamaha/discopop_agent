| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 40 | 30 | 1 | 0 | 0 | 1 | 0 | 8 | 0 | 0 | 0 | 0 | 1.67x (n=40) |
| bare_llm_nospeed_v3 | claude-opus-5-5 | 10 | 0 | 5 | 0 | 0 | 2 | 0 | 0 | 3 | 0 | 0 | 0 | 0.96x (n=7) |
| bare_llm_nospeed | claude-opus-5-5 | 10 | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 1.24x (n=10) |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 1.43x | 1.43x | 10 gained |
| tsvc_b1/k48 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 4.02x | 4.02x | 10 gained |
| tsvc_b1/s161 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER,FASTER · 2.15x | 2.15x | 10 gained |
| tsvc_b1/s424 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change,no-change,no-change,no-change,parallel-not-faster,parallel-not-faster · 1.00x | 1.00x | 1 gained-not-faster, 1 worse, 8 neither |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-opus-5-5 | no-change,no-change,no-change · 1.00x | BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.97x | 0.97x | 3 gained-not-faster, 1 worse, 1 unsafe |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-opus-5-5 | no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.94x | 0.94x | 2 gained-not-faster, 1 worse, 2 unsafe |
| tsvc_b1/s161 | bare_llm_nospeed | claude-opus-5-5 | no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.49x | 3.49x | 5 gained |
| tsvc_b1/s424 | bare_llm_nospeed | claude-opus-5-5 | no-change,no-change,no-change · 1.00x | parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.30x | 0.30x | 5 worse |

**Speed ratios withheld for 3 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
