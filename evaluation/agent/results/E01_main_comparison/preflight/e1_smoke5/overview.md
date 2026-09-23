# Agent experiment run `e1_smoke5`

- status: finished (created 2026-09-21T14:12:20, finished 2026-09-21T15:00:32)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `721369dd5764446f0c4d13141b7f93215195d2ef` (uncommitted diff sha256 `None`)
- harness: `721369dd5764446f0c4d13141b7f93215195d2ef` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 4 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1.03x (n=4) |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| polybench/2mm | default | claude-haiku-4-5-20251001 | FASTER · 9.49x | FASTER · 10.62x | 1.12x | 1 better |
| polybench/bicg | default | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | no-change · 1.00x | parallel-not-faster · 1.06x | 1.06x | 1 gained-not-faster |
| tsvc/s321 | default | claude-haiku-4-5-20251001 | no-change · 1.00x | no-change · 1.00x | 1.00x | 1 neither |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default | claude-haiku-4-5-20251001 | 4 | 1 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 399 | 13 |
| discopop_gate | claude-haiku-4-5-20251001 | 4 | 1 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| polybench/2mm | default | claude-haiku-4-5-20251001 | 1 | FASTER | 10.62x | 1+0 | 1 | 6 | 1 | 410.4 |
| polybench/2mm | discopop_gate | claude-haiku-4-5-20251001 | 1 | FASTER | 9.49x | 2+0 | 0 | 6 | 0 | 330.5 |
| polybench/bicg | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 1 | 167.5 |
| polybench/bicg | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 3.7 |
| tsvc/s211 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.06x | 1+0 | 1 | 0 | 2 | 387.5 |
| tsvc/s211 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 7.6 |
| tsvc/s321 | default | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1216.6 |
| tsvc/s321 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.8 |
