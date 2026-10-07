# Agent experiment run `e1v6c_s281`

- status: finished (created 2026-10-07T12:17:28, finished 2026-10-07T12:51:05)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `27ac32333e8f80d886874b1d5086f5faffec5158` (uncommitted diff sha256 `None`)
- harness: `27ac32333e8f80d886874b1d5086f5faffec5158` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_v4 | claude-haiku-4-5-20251001 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 380 | 11 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.28x | 2+0 | 1 | 0 | 2 | 387.1 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.25x | 2+0 | 1 | 0 | 3 | 333.2 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.34x | 2+0 | 1 | 0 | 2 | 393.7 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.35x | 2+0 | 1 | 0 | 1 | 256.4 |
| tsvc_c2/s281 | default_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.30x | 2+0 | 1 | 0 | 3 | 379.5 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 6.7 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 10.6 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.97x | 0+0 | 0 | 0 | 0 | 9.0 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 0 | 7.7 |
| tsvc_c2/s281 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 0 | 6.8 |
