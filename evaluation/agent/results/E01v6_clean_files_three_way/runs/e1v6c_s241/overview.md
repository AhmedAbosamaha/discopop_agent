# Agent experiment run `e1v6c_s241`

- status: finished (created 2026-10-08T17:11:30, finished 2026-10-08T18:36:35)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `f9e7744df83491d22042d1de961cd5b8a74cf45f` (uncommitted diff sha256 `None`)
- harness: `f9e7744df83491d22042d1de961cd5b8a74cf45f` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v4 | claude-haiku-4-5-20251001 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 785 | 30 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c3/s241 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.40x | 3+0 | 1 | 0 | 8 | 827.2 |
| tsvc_c3/s241 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.45x | 3+0 | 1 | 0 | 12 | 1480.0 |
| tsvc_c3/s241 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.41x | 3+0 | 1 | 0 | 3 | 784.8 |
| tsvc_c3/s241 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.36x | 3+0 | 1 | 0 | 4 | 718.4 |
| tsvc_c3/s241 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.39x | 3+0 | 1 | 0 | 3 | 609.0 |
| tsvc_c3/s241 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.1 |
| tsvc_c3/s241 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 13.0 |
| tsvc_c3/s241 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 13.0 |
| tsvc_c3/s241 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 0 | 13.0 |
| tsvc_c3/s241 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 13.0 |
