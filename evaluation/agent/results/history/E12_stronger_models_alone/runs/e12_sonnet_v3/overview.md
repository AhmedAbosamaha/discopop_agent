# Agent experiment run `e12_sonnet_v3`

- status: finished (created 2026-10-03T04:35:08, finished 2026-10-03T05:18:32)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `ab0e7f4759b982c26184c0efa24f19e97ea795f9` (uncommitted diff sha256 `None`)
- harness: `ab0e7f4759b982c26184c0efa24f19e97ea795f9` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-sonnet-5 | 15 | 10 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 119 | 15 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-sonnet-5 | 1 | BROKEN | 4.32x | —+— | — | — | 1 | 204.1 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-sonnet-5 | 2 | BROKEN | 4.96x | —+— | — | — | 1 | 253.9 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-sonnet-5 | 3 | BROKEN | 4.34x | —+— | — | — | 1 | 158.0 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-sonnet-5 | 4 | BROKEN | 3.88x | —+— | — | — | 1 | 228.4 |
| tsvc_b1/k48 | bare_llm_nospeed_v3 | claude-sonnet-5 | 5 | BROKEN | 5.01x | —+— | — | — | 1 | 234.0 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-sonnet-5 | 1 | FASTER | 2.56x | —+— | — | — | 1 | 103.3 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-sonnet-5 | 2 | FASTER | 2.03x | —+— | — | — | 1 | 101.5 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-sonnet-5 | 3 | FASTER | 2.53x | —+— | — | — | 1 | 99.6 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-sonnet-5 | 4 | FASTER | 1.86x | —+— | — | — | 1 | 82.4 |
| tsvc_b1/s1213 | bare_llm_nospeed_v3 | claude-sonnet-5 | 5 | FASTER | 1.76x | —+— | — | — | 1 | 86.7 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-sonnet-5 | 1 | FASTER | 2.06x | —+— | — | — | 1 | 74.7 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-sonnet-5 | 2 | FASTER | 1.84x | —+— | — | — | 1 | 114.9 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-sonnet-5 | 3 | FASTER | 2.44x | —+— | — | — | 1 | 119.4 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-sonnet-5 | 4 | FASTER | 1.54x | —+— | — | — | 1 | 167.9 |
| tsvc_b1/s211 | bare_llm_nospeed_v3 | claude-sonnet-5 | 5 | FASTER | 2.37x | —+— | — | — | 1 | 169.8 |
