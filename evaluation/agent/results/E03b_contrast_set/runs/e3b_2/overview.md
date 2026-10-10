# Agent experiment run `e3b_2`

- status: finished (created 2026-10-10T13:14:41, finished 2026-10-10T15:12:11)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `cb921121f56cdae31ede62d3a6a3aaf64ef1ebfc` (uncommitted diff sha256 `None`)
- harness: `cb921121f56cdae31ede62d3a6a3aaf64ef1ebfc` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v5 | claude-haiku-4-5-20251001 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 325 | 28 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 10 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 158 | 13 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c4/s3113 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.23x | 1+0 | 1 | 0 | 5 | 437.8 |
| tsvc_c4/s3113 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.41x | 1+0 | 1 | 0 | 2 | 279.1 |
| tsvc_c4/s3113 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 6.73x | 1+0 | 1 | 0 | 3 | 189.9 |
| tsvc_c4/s3113 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.40x | 1+0 | 1 | 0 | 6 | 583.9 |
| tsvc_c4/s3113 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.82x | 1+0 | 1 | 0 | 3 | 345.5 |
| tsvc_c4/s3113 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.8 |
| tsvc_c4/s3113 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 5.9 |
| tsvc_c4/s3113 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.8 |
| tsvc_c4/s3113 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.8 |
| tsvc_c4/s3113 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 5.8 |
| tsvc_c4/s3113 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 9.02x | 0+1 | 1 | 0 | 1 | 144.5 |
| tsvc_c4/s3113 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 8.70x | 0+1 | 1 | 0 | 4 | 362.2 |
| tsvc_c4/s3113 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 7.37x | 0+1 | 1 | 0 | 1 | 146.8 |
| tsvc_c4/s3113 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 8.42x | 0+1 | 1 | 0 | 1 | 174.7 |
| tsvc_c4/s3113 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 8.74x | 0+1 | 1 | 0 | 1 | 187.9 |
| tsvc_c4/s319 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.18x | 1+0 | 1 | 0 | 2 | 346.9 |
| tsvc_c4/s319 | default_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.23x | 1+0 | 1 | 0 | 2 | 265.4 |
| tsvc_c4/s319 | default_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.16x | 1+0 | 1 | 0 | 2 | 379.2 |
| tsvc_c4/s319 | default_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.06x | 2+0 | 1 | 0 | 1 | 216.6 |
| tsvc_c4/s319 | default_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.22x | 1+0 | 1 | 0 | 2 | 303.7 |
| tsvc_c4/s319 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.9 |
| tsvc_c4/s319 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.2 |
| tsvc_c4/s319 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.9 |
| tsvc_c4/s319 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 7.9 |
| tsvc_c4/s319 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 8.2 |
| tsvc_c4/s319 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.07x | 0+1 | 1 | 0 | 1 | 148.4 |
| tsvc_c4/s319 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.10x | 0+1 | 1 | 0 | 1 | 152.3 |
| tsvc_c4/s319 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.11x | 0+1 | 1 | 0 | 1 | 143.1 |
| tsvc_c4/s319 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.10x | 0+1 | 1 | 0 | 1 | 162.9 |
| tsvc_c4/s319 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.19x | 0+1 | 1 | 0 | 1 | 188.2 |
