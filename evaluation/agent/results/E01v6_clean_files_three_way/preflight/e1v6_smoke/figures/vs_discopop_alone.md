| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-fable-5-1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | — |
| bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | — |
| bare_llm_v4 | claude-opus-5-5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | — |
| bare_llm_v4 | claude-sonnet-5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | — |
| default_v4 | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | — |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | — |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm_v4 | claude-fable-5-1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| R | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| R | bare_llm_v4 | claude-opus-5-5 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| R | bare_llm_v4 | claude-sonnet-5 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| R | default_v4 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| R | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| A | bare_llm_v4 | claude-fable-5-1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| A | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| A | bare_llm_v4 | claude-opus-5-5 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| A | bare_llm_v4 | claude-sonnet-5 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| A | default_v4 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |
| A | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | — |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_c2/s000 | bare_llm_v4 | claude-fable-5-1 | — · — | FASTER · 3.44x | — | 1 no-baseline |
| tsvc_c2/s000 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.43x | — | 1 no-baseline |
| tsvc_c2/s000 | bare_llm_v4 | claude-opus-5-5 | — · — | FASTER · 3.48x | — | 1 no-baseline |
| tsvc_c2/s000 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER · 3.44x | — | 1 no-baseline |
| tsvc_c2/s000 | default_v4 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.52x | — | 1 no-baseline |
| tsvc_c2/s000 | discopop_gate_v4 | claude-haiku-4-5-20251001 | — · — | FASTER · 3.46x | — | 1 no-baseline |
| tsvc_c2/s211 | bare_llm_v4 | claude-fable-5-1 | — · — | FASTER · 2.18x | — | 1 no-baseline |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | — · — | FASTER · 1.97x | — | 1 no-baseline |
| tsvc_c2/s211 | bare_llm_v4 | claude-opus-5-5 | — · — | FASTER · 2.17x | — | 1 no-baseline |
| tsvc_c2/s211 | bare_llm_v4 | claude-sonnet-5 | — · — | FASTER · 2.40x | — | 1 no-baseline |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | — · — | FASTER · 1.37x | — | 1 no-baseline |
| tsvc_c2/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | — · — | no-change · 1.00x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
