# Agent experiment run `e2c_smoke`

- status: finished (created 2026-09-23T20:46:49, finished 2026-09-23T22:40:52)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `1be54f01ce194c490695549fcc562da17c9c72c1` (uncommitted diff sha256 `None`)
- harness: `1be54f01ce194c490695549fcc562da17c9c72c1` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

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

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 86 | 2 |
| compiler_remarks_b1 | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 588 | 4 |
| default | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 254 | 3 |
| discopop_gate | claude-haiku-4-5-20251001 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| full_b1 | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 276 | 2 |
| hotspot_only_b1 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 388 | 4 |
| no_evidence | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 241 | 2 |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 529 | 2 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s121 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 4.02x | —+— | — | — | 1 | 50.6 |
| tsvc/s121 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 1 | 750.3 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 1 | 189.8 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s121 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.50x | 2+0 | 1 | 0 | 1 | 243.8 |
| tsvc/s121 | hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.66x | 2+0 | 1 | 0 | 1 | 244.5 |
| tsvc/s121 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 0.97x | 0+0 | 0 | 0 | 1 | 171.4 |
| tsvc/s121 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.56x | 2+0 | 1 | 0 | 1 | 196.8 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 1 | BROKEN | 3.50x | —+— | — | — | 1 | 121.0 |
| tsvc/s281 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 425.1 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 318.3 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.02x | 2+0 | 1 | 0 | 1 | 309.2 |
| tsvc/s281 | hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 531.3 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.02x | 2+0 | 1 | 0 | 1 | 310.5 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 861.2 |
