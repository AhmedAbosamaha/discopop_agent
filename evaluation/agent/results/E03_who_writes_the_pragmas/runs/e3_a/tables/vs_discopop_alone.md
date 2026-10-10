| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v5 | claude-haiku-4-5-20251001 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | — |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | — |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | default_v5 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | — |
| A | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | — |
| A | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/s000 | default_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 127.70x | — | 1 no-baseline |
| tsvc_c2/s000 | discopop_gate_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.57x | — | 1 no-baseline |
| tsvc_c2/s000 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.49x | — | 1 no-baseline |
| tsvc_c2/vpvtv | default_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.59x | — | 1 no-baseline |
| tsvc_c2/vpvtv | discopop_gate_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.65x | — | 1 no-baseline |
| tsvc_c2/vpvtv | llm_pragmas_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.63x | — | 1 no-baseline |
| tsvc_c3/s313 | default_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 4.62x | — | 1 no-baseline |
| tsvc_c3/s313 | discopop_gate_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 4.60x | — | 1 no-baseline |
| tsvc_c3/s313 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | — · — | FASTER · 4.63x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
