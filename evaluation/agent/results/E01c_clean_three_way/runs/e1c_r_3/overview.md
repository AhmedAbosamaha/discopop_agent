# Agent experiment run `e1c_r_3`

- status: finished (created 2026-09-24T18:33:44, finished 2026-09-24T21:39:32)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `33673d7d0695b9ed0201deccd99efb0e2cf8eda9` (uncommitted diff sha256 `None`)
- harness: `33673d7d0695b9ed0201deccd99efb0e2cf8eda9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

The sequential original is the reference both are measured against, not the comparison.

| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 20 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 0 | 0 | 3.35x (n=15) |
| default | claude-haiku-4-5-20251001 | 20 | 16 | 3 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2.76x (n=20) |

| Class | Arm | Model | Benchmarks | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | bare_llm | claude-haiku-4-5-20251001 | 4 | 20 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 0 | 0 | 3.35x (n=15) |
| R | default | claude-haiku-4-5-20251001 | 4 | 20 | 16 | 3 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2.76x (n=20) |

Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified parallel program in any of three profile draws; A = it does in the majority; D = R, and a true recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control.

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 3.50x | 3.50x | 4 gained, 1 invalid |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.44x | 3.44x | 5 gained |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 2.58x | 2.58x | 4 gained, 1 invalid |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 3.37x | 3.37x | 5 gained |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | BROKEN,BROKEN,FASTER,FASTER,VERIFY_FAILED · 3.02x | 3.02x | 2 gained, 2 unsafe, 1 invalid |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,no-change,parallel-not-faster,parallel-not-faster,parallel-not-faster · 1.04x | 1.04x | 1 gained, 3 gained-not-faster, 1 neither |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.70x | 2.70x | 5 gained |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | no-change,no-change,no-change,no-change,no-change · 1.00x | FASTER,FASTER,FASTER,FASTER,FASTER · 2.71x | 2.71x | 5 gained |

**Speed ratios withheld for 3 trial(s):** the DiscoPoP-alone trial was timed on another host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio.

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm | claude-haiku-4-5-20251001 | 20 | 15 | 0 | 0 | 0 | 0 | 2 | 0 | 3 | 0 | 0 | 0 | 51 | 20 |
| default | claude-haiku-4-5-20251001 | 20 | 16 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 21 |
| discopop_gate | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 3.44x | —+— | — | — | 1 | 53.6 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 3.35x | —+— | — | — | 1 | 28.5 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 3.67x | —+— | — | — | 1 | 68.4 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 3.56x | —+— | — | — | 1 | 46.5 |
| tsvc/s254 | bare_llm | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 34.4 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.34x | 1+0 | 1 | 2 | 1 | 134.8 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 3.44x | 1+0 | 1 | 2 | 1 | 149.2 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.49x | 1+0 | 1 | 2 | 1 | 148.4 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 3.41x | 1+0 | 1 | 2 | 1 | 424.0 |
| tsvc/s254 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 3.54x | 1+0 | 1 | 2 | 1 | 179.1 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 0.97x | 0+0 | 0 | 2 | 0 | 31.6 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 0.98x | 0+0 | 0 | 2 | 0 | 32.3 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 2 | 0 | 32.0 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 32.4 |
| tsvc/s254 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 32.1 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 1.58x | —+— | — | — | 1 | 93.9 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.64x | —+— | — | — | 1 | 52.6 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 3.35x | —+— | — | — | 1 | 46.8 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 2.52x | —+— | — | — | 1 | 52.2 |
| tsvc/s255 | bare_llm | claude-haiku-4-5-20251001 | 5 | VERIFY_FAILED | — | —+— | — | — | 1 | 48.2 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 3.42x | 1+0 | 1 | 1 | 1 | 191.7 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.44x | 1+0 | 1 | 1 | 1 | 164.4 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.39x | 1+0 | 1 | 1 | 1 | 135.2 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 2.76x | 1+0 | 1 | 1 | 1 | 154.4 |
| tsvc/s255 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 3.37x | 1+0 | 1 | 1 | 1 | 117.3 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 31.3 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 32.0 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 1 | 0 | 31.2 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 31.9 |
| tsvc/s255 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.03x | 0+0 | 0 | 1 | 0 | 31.6 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.38x | —+— | — | — | 1 | 163.0 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 2 | BROKEN | 0.31x | —+— | — | — | 1 | 156.8 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 3 | BROKEN | 3.30x | —+— | — | — | 1 | 33.3 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 4 | VERIFY_FAILED | — | —+— | — | — | 1 | 95.1 |
| tsvc/s281 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 3.66x | —+— | — | — | 1 | 181.3 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 1.04x | 1+0 | 1 | 0 | 1 | 287.9 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.09x | 1+0 | 1 | 0 | 1 | 211.5 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 3.36x | 2+0 | 1 | 0 | 2 | 210.5 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 4 | parallel-not-faster | 1.04x | 1+0 | 1 | 0 | 1 | 212.6 |
| tsvc/s281 | default | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 1 | 210.4 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.2 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.4 |
| tsvc/s281 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.3 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 1 | FASTER | 2.69x | —+— | — | — | 1 | 35.3 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 2 | FASTER | 2.58x | —+— | — | — | 1 | 46.2 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 3 | FASTER | 2.70x | —+— | — | — | 1 | 49.5 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 4 | FASTER | 3.40x | —+— | — | — | 1 | 53.5 |
| tsvc/s291 | bare_llm | claude-haiku-4-5-20251001 | 5 | FASTER | 3.47x | —+— | — | — | 1 | 34.2 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 1 | FASTER | 2.75x | 1+0 | 1 | 2 | 1 | 189.9 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 2 | FASTER | 2.76x | 1+0 | 1 | 2 | 1 | 208.8 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 3 | FASTER | 2.65x | 1+0 | 1 | 2 | 1 | 156.2 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 4 | FASTER | 2.66x | 1+0 | 1 | 2 | 1 | 215.9 |
| tsvc/s291 | default | claude-haiku-4-5-20251001 | 5 | FASTER | 2.71x | 1+0 | 1 | 2 | 1 | 364.2 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 2 | 0 | 33.4 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 34.0 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 32.4 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 2 | 0 | 32.4 |
| tsvc/s291 | discopop_gate | claude-haiku-4-5-20251001 | 5 | no-change | 1.03x | 0+0 | 0 | 2 | 0 | 32.4 |
