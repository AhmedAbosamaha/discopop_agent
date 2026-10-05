# Agent experiment run `e1c_a`

- status: finished (created 2026-09-25T13:38:53, finished 2026-09-25T14:33:10)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `a812b232d2c1f65829873b8d53242729f2c4b011` (uncommitted diff sha256 `None`)
- harness: `a812b232d2c1f65829873b8d53242729f2c4b011` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 3 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1.02x (n=2) |
| default | claude-haiku-4-5-20251001 | 3 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00x (n=2) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | bare_llm | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1.02x (n=2) |
| A | default | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00x (n=2) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s000 | bare_llm | claude-haiku-4-5-20251001 | FASTER · 3.60x | FASTER · 3.50x | 0.97x | 1 equal |
| tsvc/s000 | default | claude-haiku-4-5-20251001 | FASTER · 3.60x | FASTER · 3.62x | 1.01x | 1 equal |
| tsvc/s313 | bare_llm | claude-haiku-4-5-20251001 | FASTER · 4.68x | FASTER · 4.98x | 1.06x | 1 equal |
| tsvc/s313 | default | claude-haiku-4-5-20251001 | FASTER · 4.68x | SCAFFOLD_MODIFIED · — | — | 1 invalid |
| tsvc/vpvtv | bare_llm | claude-haiku-4-5-20251001 | FASTER · 3.67x | VERIFY_FAILED · — | — | 1 invalid |
| tsvc/vpvtv | default | claude-haiku-4-5-20251001 | FASTER · 3.67x | FASTER · 3.65x | 0.99x | 1 equal |

**Speed ratios withheld for 1 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 46 | 3 |
| default | claude-haiku-4-5-20251001 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 357 | 3 |
| discopop_gate | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 59 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s000 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.50x | —+— | — | — | 1 | 45.5 |
| tsvc/s000 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.62x | 1+0 | 0 | 2 | 1 | 356.9 |
| tsvc/s000 | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 3.60x | 1+0 | 0 | 2 | 0 | 48.9 |
| tsvc/s313 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 4.98x | —+— | — | — | 1 | 72.3 |
| tsvc/s313 | default | claude-haiku-4-5-20251001 | 1 | SCAFFOLD_MODIFIED | 4.70x | 1+0 | 1 | 2 | 1 | 346.2 |
| tsvc/s313 | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 4.68x | 1+0 | 0 | 2 | 0 | 59.3 |
| tsvc/vpvtv | bare_llm | claude-haiku-4-5-20251001 | 1 | VERIFY_FAILED | — | —+— | — | — | 1 | 22.0 |
| tsvc/vpvtv | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.65x | 1+0 | 0 | 1 | 1 | 401.5 |
| tsvc/vpvtv | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 3.67x | 1+0 | 0 | 1 | 0 | 59.7 |
