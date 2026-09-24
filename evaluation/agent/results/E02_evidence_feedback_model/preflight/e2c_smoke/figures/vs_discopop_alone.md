| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | — |
| compiler_remarks_b1 | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1.00x (n=2) |
| default | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1.00x (n=2) |
| full_b1 | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2.26x (n=2) |
| hotspot_only_b1 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.33x (n=2) |
| no_evidence | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2.01x (n=2) |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.28x (n=2) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | — |
| R | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1.00x (n=2) |
| R | default | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1.00x (n=2) |
| R | full_b1 | claude-haiku-4-5-20251001 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2.26x (n=2) |
| R | hotspot_only_b1 | claude-haiku-4-5-20251001 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.33x (n=2) |
| R | no_evidence | claude-haiku-4-5-20251001 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2.01x (n=2) |
| R | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.28x (n=2) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | no-change · 1.00x | BROKEN · — | — | 1 unsafe |
| tsvc/s121 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s121 | full_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | FASTER · 1.50x | 1.50x | 1 gained |
| tsvc/s121 | hotspot_only_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | FASTER · 1.66x | 1.66x | 1 gained |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s121 | no_evidence_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | FASTER · 1.56x | 1.56x | 1 gained |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | no-change · 1.00x | BROKEN · — | — | 1 unsafe |
| tsvc/s281 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | FASTER · 3.02x | 3.02x | 1 gained |
| tsvc/s281 | hotspot_only_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | no-change · 1.00x | FASTER · 3.02x | 3.02x | 1 gained |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
