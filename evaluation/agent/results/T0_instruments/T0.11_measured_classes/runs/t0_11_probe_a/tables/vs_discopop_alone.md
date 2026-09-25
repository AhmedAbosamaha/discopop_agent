| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_capability | none | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | — |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s353 | discopop_capability | none | — · — | FASTER · 3.15x | — | 1 no-baseline |
| tsvc/s4112 | discopop_capability | none | — · — | FASTER · 3.73x | — | 1 no-baseline |
| tsvc/s4113 | discopop_capability | none | — · — | FASTER · 3.66x | — | 1 no-baseline |
| tsvc/s4114 | discopop_capability | none | — · — | FASTER · 2.91x | — | 1 no-baseline |
| tsvc/s4115 | discopop_capability | none | — · — | FASTER · 3.65x | — | 1 no-baseline |
| tsvc/s4117 | discopop_capability | none | — · — | FASTER · 3.53x | — | 1 no-baseline |
| tsvc/s4121 | discopop_capability | none | — · — | FASTER · 3.59x | — | 1 no-baseline |
| tsvc/s491 | discopop_capability | none | — · — | FASTER · 2.97x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
