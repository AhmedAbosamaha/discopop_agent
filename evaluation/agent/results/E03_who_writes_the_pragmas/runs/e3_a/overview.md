# Agent experiment run `e3_a`

- status: finished (created 2026-10-10T04:27:42, finished 2026-10-10T05:14:29)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `8297abb28e0049561c6bc977e67a8780fc9f6768` (uncommitted diff sha256 `None`)
- harness: `8297abb28e0049561c6bc977e67a8780fc9f6768` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v5 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 435 | 10 |
| discopop_gate_v5 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 60 | 0 |
| llm_pragmas_v5 | claude-haiku-4-5-20251001 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 196 | 3 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s000 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 127.70x | 1+0 | 1 | 1 | 6 | 720.2 |
| tsvc_c2/s000 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.57x | 1+0 | 0 | 1 | 0 | 49.5 |
| tsvc_c2/s000 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.49x | 0+1 | 1 | 1 | 1 | 146.7 |
| tsvc_c2/vpvtv | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.59x | 1+0 | 0 | 1 | 3 | 435.1 |
| tsvc_c2/vpvtv | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.65x | 1+0 | 0 | 1 | 0 | 61.0 |
| tsvc_c2/vpvtv | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.63x | 0+1 | 1 | 1 | 1 | 212.4 |
| tsvc_c3/s313 | default_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.62x | 1+0 | 0 | 1 | 1 | 208.9 |
| tsvc_c3/s313 | discopop_gate_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.60x | 1+0 | 0 | 1 | 0 | 59.6 |
| tsvc_c3/s313 | llm_pragmas_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.63x | 1+0 | 0 | 1 | 1 | 196.0 |
