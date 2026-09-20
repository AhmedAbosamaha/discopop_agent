| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | claude-haiku-4-5-20251001 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13.68x (n=3) |
| speed_gate_large | claude-haiku-4-5-20251001 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13.21x (n=3) |
| speed_gate_small | claude-haiku-4-5-20251001 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 4.72x (n=3) |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| polybench/lu | full | claude-haiku-4-5-20251001 | parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.21x | FASTER,FASTER,FASTER · 2.90x | 13.68x | 3 better |
| polybench/lu | speed_gate_large | claude-haiku-4-5-20251001 | parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.21x | FASTER,FASTER,FASTER · 2.80x | 13.21x | 3 better |
| polybench/lu | speed_gate_small | claude-haiku-4-5-20251001 | parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.21x | no-change,no-change,no-change · 1.00x | 4.72x | 3 lost |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — both parallel and correct; the agent's program is >= 1.1x slower than DiscoPoP alone's; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
