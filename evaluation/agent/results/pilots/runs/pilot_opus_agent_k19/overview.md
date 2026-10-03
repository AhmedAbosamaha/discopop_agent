# Agent experiment run `pilot_opus_agent_k19`

- status: finished (created 2026-10-03T18:26:35, finished 2026-10-03T20:07:18)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `8277854d41b94b393e17b452d3f291b3a1c8820a` (uncommitted diff sha256 `None`)
- harness: `8277854d41b94b393e17b452d3f291b3a1c8820a` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed_v3 | claude-opus-5-5 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 154 | 5 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 1 | BROKEN | — | 1+0 | 1 | 2 | 1 | 147.1 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 2 | BROKEN | — | 1+0 | 1 | 2 | 3 | 270.0 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-opus-5-5 | 3 | BROKEN | — | 1+0 | 1 | 2 | 1 | 153.5 |
