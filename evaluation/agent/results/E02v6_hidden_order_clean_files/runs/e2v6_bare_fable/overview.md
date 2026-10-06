# Agent experiment run `e2v6_bare_fable`

- status: finished (created 2026-10-05T15:15:39, finished 2026-10-06T01:15:40)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `1258cd677fa14c0ff235f7da1cc5bbca41548378` (uncommitted diff sha256 `None`)
- harness: `1258cd677fa14c0ff235f7da1cc5bbca41548378` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v4 | claude-fable-5-1 | 35 | 10 | 17 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 120 | 35 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-fable-5-1 | 1 | parallel-not-faster | 0.28x | —+— | — | — | 1 | 112.8 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-fable-5-1 | 2 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 116.4 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-fable-5-1 | 3 | parallel-not-faster | 1.00x | —+— | — | — | 1 | 72.6 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-fable-5-1 | 4 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 99.4 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-fable-5-1 | 5 | BROKEN | — | —+— | — | — | 1 | 123.6 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-fable-5-1 | 1 | BROKEN | 4.29x | —+— | — | — | 1 | 19.6 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-fable-5-1 | 2 | BROKEN | 4.13x | —+— | — | — | 1 | 32.3 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-fable-5-1 | 3 | BROKEN | 4.22x | —+— | — | — | 1 | 20.7 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-fable-5-1 | 4 | BROKEN | 4.24x | —+— | — | — | 1 | 34.9 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-fable-5-1 | 5 | BROKEN | 4.24x | —+— | — | — | 1 | 20.5 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-fable-5-1 | 1 | BROKEN | — | —+— | — | — | 1 | 119.7 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-fable-5-1 | 2 | BROKEN | — | —+— | — | — | 1 | 125.0 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-fable-5-1 | 3 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 114.4 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-fable-5-1 | 4 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 159.3 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-fable-5-1 | 5 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 107.6 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-fable-5-1 | 1 | FASTER | 2.29x | —+— | — | — | 1 | 142.6 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-fable-5-1 | 2 | FASTER | 3.17x | —+— | — | — | 1 | 175.2 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-fable-5-1 | 3 | FASTER | 2.27x | —+— | — | — | 1 | 141.1 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-fable-5-1 | 4 | FASTER | 2.30x | —+— | — | — | 1 | 125.6 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-fable-5-1 | 5 | FASTER | 3.06x | —+— | — | — | 1 | 210.3 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-fable-5-1 | 1 | parallel-not-faster | 0.31x | —+— | — | — | 1 | 129.6 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-fable-5-1 | 2 | parallel-not-faster | 0.49x | —+— | — | — | 1 | 149.7 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-fable-5-1 | 3 | parallel-not-faster | 0.01x | —+— | — | — | 1 | 193.0 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-fable-5-1 | 4 | parallel-not-faster | 0.94x | —+— | — | — | 1 | 219.1 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-fable-5-1 | 5 | parallel-not-faster | 0.93x | —+— | — | — | 1 | 138.8 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-fable-5-1 | 1 | parallel-not-faster | 0.90x | —+— | — | — | 1 | 128.2 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-fable-5-1 | 2 | parallel-not-faster | 0.03x | —+— | — | — | 1 | 147.8 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-fable-5-1 | 3 | parallel-not-faster | 0.98x | —+— | — | — | 1 | 182.3 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-fable-5-1 | 4 | parallel-not-faster | 0.03x | —+— | — | — | 1 | 113.6 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-fable-5-1 | 5 | parallel-not-faster | 0.92x | —+— | — | — | 1 | 139.2 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-fable-5-1 | 1 | FASTER | 2.16x | —+— | — | — | 1 | 45.9 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-fable-5-1 | 2 | FASTER | 2.02x | —+— | — | — | 1 | 40.1 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-fable-5-1 | 3 | FASTER | 2.17x | —+— | — | — | 1 | 50.3 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-fable-5-1 | 4 | FASTER | 2.24x | —+— | — | — | 1 | 59.0 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-fable-5-1 | 5 | FASTER | 2.18x | —+— | — | — | 1 | 33.6 |
