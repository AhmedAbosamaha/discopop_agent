# Agent experiment run `e2_ab_a`

- status: running (created 2026-09-23T17:21:52, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `8a845b335bb9464c9f65920ba84bd6b63f2813f9` (uncommitted diff sha256 `None`)
- harness: `8a845b335bb9464c9f65920ba84bd6b63f2813f9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 9 | 3 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 1.00x (n=9) |
| full_b1 | claude-haiku-4-5-20251001 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 1.00x (n=5) |
| no_evidence | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 1.00x (n=5) |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 1.00x (n=5) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | default | claude-haiku-4-5-20251001 | 2 | 9 | 3 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 1.00x (n=9) |
| R | full_b1 | claude-haiku-4-5-20251001 | 1 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 1.00x (n=5) |
| R | no_evidence | claude-haiku-4-5-20251001 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 1.00x (n=5) |
| R | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 1.00x (n=5) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s112 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 1 gained, 4 neither |
| tsvc/s112 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | no-change,no-change,no-change,no-change,no-change · 1.00x | 1.00x | 5 neither |
| tsvc/s112 | no_evidence_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change · 1.22x | 1.22x | 2 gained, 2 neither |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 9 | 3 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 328 | 10 |
| discopop_gate | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |
| full_b1 | claude-haiku-4-5-20251001 | 5 | 2 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 281 | 5 |
| no_evidence | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 157 | 5 |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | 2 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 227 | 5 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 1 | 895.9 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 1.43x | 2+0 | 1 | 0 | 1 | 271.6 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 3 | no-change | 1.03x | 0+0 | 0 | 0 | 2 | 348.0 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 165.0 |
| tsvc/s112 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.03x | 0+0 | 0 | 0 | 1 | 201.3 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc/s112 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.04x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s112 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.54x | 2+0 | 1 | 0 | 1 | 281.3 |
| tsvc/s112 | full_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 1 | 326.3 |
| tsvc/s112 | full_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 0.97x | 0+0 | 0 | 0 | 1 | 326.1 |
| tsvc/s112 | full_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.56x | 2+0 | 1 | 0 | 1 | 228.5 |
| tsvc/s112 | full_b1 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 1 | 232.1 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 134.7 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 2 | no-change | 1.04x | 0+0 | 0 | 0 | 1 | 142.7 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 1 | 156.6 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 4 | no-change | 1.03x | 0+0 | 0 | 0 | 1 | 974.5 |
| tsvc/s112 | no_evidence | claude-haiku-4-5-20251001 | 5 | no-change | 1.08x | 0+0 | 0 | 0 | 1 | 333.2 |
| tsvc/s112 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.53x | 2+0 | 1 | 0 | 1 | 227.1 |
| tsvc/s112 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.58x | 2+0 | 1 | 0 | 1 | 248.3 |
| tsvc/s112 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 1.03x | 0+0 | 0 | 0 | 1 | 161.5 |
| tsvc/s112 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 1 | 66.9 |
| tsvc/s112 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 1 | 389.3 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 1.44x | 2+0 | 1 | 0 | 1 | 328.5 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 328.1 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 1.51x | 2+0 | 1 | 0 | 1 | 296.3 |
| tsvc/s121 | default | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 1 | 368.2 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 4.7 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 4.8 |
| tsvc/s121 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 0.98x | 0+0 | 0 | 0 | 0 | 4.8 |
