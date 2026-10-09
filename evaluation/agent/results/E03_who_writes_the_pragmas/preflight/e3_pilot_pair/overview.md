# Agent experiment run `e3_pilot_pair`

- status: finished (created 2026-10-09T15:29:21, finished 2026-10-09T16:09:30)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `88a5c6bf741741de7d1cada0c3a784137248c728` (uncommitted diff sha256 `None`)
- harness: `88a5c6bf741741de7d1cada0c3a784137248c728` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v5 | claude-haiku-4-5-20251001 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 192 | 8 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 177 | 4 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s1213 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.61x | 2+0 | 1 | 0 | 2 | 274.8 |
| tsvc_c2/s1213 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.80x | 3+0 | 1 | 0 | 4 | 568.6 |
| tsvc_c2/s1213 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.9 |
| tsvc_c2/s1213 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 6.6 |
| tsvc_c2/s1213 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.55x | 0+2 | 1 | 0 | 1 | 233.4 |
| tsvc_c2/s1213 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.56x | 0+2 | 1 | 0 | 1 | 250.2 |
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.50x | 1+0 | 1 | 0 | 1 | 108.1 |
| tsvc_c2/s254 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.45x | 1+0 | 1 | 0 | 1 | 109.0 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c2/s254 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 4.9 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.50x | 0+1 | 1 | 0 | 1 | 120.1 |
| tsvc_c2/s254 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.76x | 0+1 | 1 | 0 | 1 | 105.7 |
