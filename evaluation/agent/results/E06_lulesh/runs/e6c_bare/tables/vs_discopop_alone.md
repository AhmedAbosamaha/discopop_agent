| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-fable-5-1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | — |
| bare_llm_v4 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | — |
| bare_llm_v4 | claude-opus-5-5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | — |
| bare_llm_v4 | claude-sonnet-5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | — |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| llnl_c1/lulesh | bare_llm_v4 | claude-fable-5-1 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.02x | — | 5 no-baseline |
| llnl_c1/lulesh | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED · 1.95x | — | 5 no-baseline |
| llnl_c1/lulesh | bare_llm_v4 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.16x | — | 5 no-baseline |
| llnl_c1/lulesh | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED,VERIFY_FAILED · 1.99x | — | 5 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
