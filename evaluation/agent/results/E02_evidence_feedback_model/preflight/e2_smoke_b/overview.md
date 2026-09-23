# Agent experiment run `e2_smoke_b`

- status: finished (created 2026-09-23T15:41:13, finished 2026-09-23T16:19:52)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `b51fc73523dae45034bb477c655cf83be9cd4a1a` (uncommitted diff sha256 `None`)
- harness: `b51fc73523dae45034bb477c655cf83be9cd4a1a` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2.88x (n=1) |
| default | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.00x (n=1) |
| full_b1 | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.00x (n=1) |
| hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3.26x (n=1) |
| no_evidence | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3.24x (n=1) |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.00x (n=1) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2.88x (n=1) |
| R | default | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.00x (n=1) |
| R | full_b1 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.00x (n=1) |
| R | hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3.26x (n=1) |
| R | no_evidence | claude-haiku-4-5-20251001 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3.24x (n=1) |
| R | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1.00x (n=1) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s281 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | FASTER · 2.88x | 2.88x | 1 gained |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s281 | hotspot_only_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | FASTER · 3.26x | 3.26x | 1 gained |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | no-change · 1.00x | FASTER · 3.24x | 3.24x | 1 gained |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 316 | 1 |
| default | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 1 |
| discopop_gate | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| full_b1 | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 349 | 2 |
| hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 213 | 1 |
| no_evidence | claude-haiku-4-5-20251001 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 307 | 2 |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 163 | 1 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s281 | compiler_remarks_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.88x | 2+0 | 1 | 0 | 1 | 316.5 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 1 | 200.4 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.5 |
| tsvc/s281 | full_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 2 | 348.9 |
| tsvc/s281 | hotspot_only_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.26x | 2+0 | 1 | 0 | 1 | 213.1 |
| tsvc/s281 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.24x | 2+0 | 1 | 0 | 2 | 306.9 |
| tsvc/s281 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 163.1 |
