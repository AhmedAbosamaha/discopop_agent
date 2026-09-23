# Agent experiment run `e2_ab_b`

- status: running (created 2026-09-23T17:21:53, finished None)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `8a845b335bb9464c9f65920ba84bd6b63f2813f9` (uncommitted diff sha256 `None`)
- harness: `8a845b335bb9464c9f65920ba84bd6b63f2813f9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 5 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 3.50x (n=5) |
| full_b1 | claude-haiku-4-5-20251001 | 5 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 4.07x (n=5) |
| no_evidence | claude-haiku-4-5-20251001 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 1.00x (n=5) |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | 1 | 1 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 1.00x (n=5) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | default | claude-haiku-4-5-20251001 | 1 | 5 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 3.50x (n=5) |
| R | full_b1 | claude-haiku-4-5-20251001 | 1 | 5 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 4.07x (n=5) |
| R | no_evidence | claude-haiku-4-5-20251001 | 1 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 1.00x (n=5) |
| R | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | 5 | 1 | 1 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 1.00x (n=5) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s252 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 3.50x | 3.50x | 4 gained, 1 neither |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,no-change · 4.07x | 4.07x | 4 gained, 1 neither |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,no-change,no-change,no-change · 1.00x | 1.00x | 2 gained, 3 neither |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,no-change,no-change,parallel-not-faster · 1.00x | 1.00x | 1 gained, 1 gained-not-faster, 3 neither |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 5 | 4 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 194 | 5 |
| discopop_gate | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 36 | 0 |
| full_b1 | claude-haiku-4-5-20251001 | 5 | 4 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 179 | 6 |
| no_evidence | claude-haiku-4-5-20251001 | 5 | 2 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 241 | 5 |
| no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | 1 | 1 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 202 | 5 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 4.07x | 1+0 | 1 | 1 | 1 | 194.3 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.50x | 1+0 | 1 | 1 | 1 | 188.8 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.15x | 2+0 | 1 | 1 | 1 | 208.5 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 1 | 1 | 259.8 |
| tsvc/s252 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 4.09x | 1+0 | 1 | 1 | 1 | 167.0 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 1 | 0 | 39.6 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 40.0 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 40.1 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 39.9 |
| tsvc/s252 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 39.6 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.24x | 1+0 | 1 | 1 | 1 | 173.8 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 2 | 994.0 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.63x | 1+0 | 1 | 1 | 1 | 179.1 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.05x | 1+0 | 1 | 1 | 1 | 142.7 |
| tsvc/s252 | full_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.07x | 1+0 | 1 | 1 | 1 | 203.2 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 1 | FASTER | 3.79x | 1+0 | 1 | 1 | 1 | 152.6 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 240.8 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 1 | 1 | 926.8 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 4 | FASTER | 2.11x | 2+0 | 1 | 1 | 1 | 791.7 |
| tsvc/s252 | no_evidence | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 1 | 1 | 180.9 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.03x | 1+0 | 1 | 1 | 1 | 799.4 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 1 | 1 | 202.2 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 3 | no-change | 0.98x | 0+0 | 0 | 1 | 1 | 160.3 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 1 | 1 | 776.0 |
| tsvc/s252 | no_evidence_b1 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.12x | 1+0 | 1 | 1 | 1 | 140.9 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 2 | 0 | 32.1 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.04x | 0+0 | 0 | 2 | 0 | 32.8 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 32.4 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 2 | 0 | 32.2 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 32.3 |
