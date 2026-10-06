# Agent experiment run `e2v6_bare_sonnet`

- status: finished (created 2026-10-06T01:16:14, finished 2026-10-06T05:43:08)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `4adf76ec2aa5419aa268da8a8f895a55f39507bd` (uncommitted diff sha256 `None`)
- harness: `4adf76ec2aa5419aa268da8a8f895a55f39507bd` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v4 | claude-sonnet-5 | 35 | 7 | 0 | 0 | 1 | 0 | 27 | 0 | 0 | 0 | 0 | 0 | 190 | 35 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-sonnet-5 | 1 | BROKEN | 4.88x | —+— | — | — | 1 | 138.5 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-sonnet-5 | 2 | changed-not-parallel | 1.00x | —+— | — | — | 1 | 261.6 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-sonnet-5 | 3 | BROKEN | 5.00x | —+— | — | — | 1 | 223.4 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-sonnet-5 | 4 | BROKEN | 5.21x | —+— | — | — | 1 | 315.9 |
| tsvc_c2/k19 | bare_llm_nospeed_v4 | claude-sonnet-5 | 5 | BROKEN | 5.16x | —+— | — | — | 1 | 304.0 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-sonnet-5 | 1 | BROKEN | 4.18x | —+— | — | — | 1 | 19.4 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-sonnet-5 | 2 | BROKEN | 4.27x | —+— | — | — | 1 | 190.1 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-sonnet-5 | 3 | BROKEN | 4.30x | —+— | — | — | 1 | 21.9 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-sonnet-5 | 4 | BROKEN | 4.22x | —+— | — | — | 1 | 30.6 |
| tsvc_c2/k23 | bare_llm_nospeed_v4 | claude-sonnet-5 | 5 | BROKEN | 4.11x | —+— | — | — | 1 | 25.0 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-sonnet-5 | 1 | BROKEN | 5.65x | —+— | — | — | 1 | 228.7 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-sonnet-5 | 2 | BROKEN | 5.39x | —+— | — | — | 1 | 260.1 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-sonnet-5 | 3 | BROKEN | 5.10x | —+— | — | — | 1 | 163.2 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-sonnet-5 | 4 | BROKEN | 5.41x | —+— | — | — | 1 | 947.8 |
| tsvc_c2/k27 | bare_llm_nospeed_v4 | claude-sonnet-5 | 5 | BROKEN | 5.50x | —+— | — | — | 1 | 414.0 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-sonnet-5 | 1 | FASTER | 3.02x | —+— | — | — | 1 | 799.3 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-sonnet-5 | 2 | FASTER | 3.08x | —+— | — | — | 1 | 694.2 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-sonnet-5 | 3 | BROKEN | 0.79x | —+— | — | — | 1 | 542.9 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-sonnet-5 | 4 | BROKEN | 1.56x | —+— | — | — | 1 | 505.8 |
| tsvc_c2/k31 | bare_llm_nospeed_v4 | claude-sonnet-5 | 5 | BROKEN | 1.89x | —+— | — | — | 1 | 275.6 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-sonnet-5 | 1 | BROKEN | 5.01x | —+— | — | — | 1 | 192.6 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-sonnet-5 | 2 | BROKEN | 4.63x | —+— | — | — | 1 | 176.9 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-sonnet-5 | 3 | BROKEN | 5.08x | —+— | — | — | 1 | 327.4 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-sonnet-5 | 4 | BROKEN | 4.73x | —+— | — | — | 1 | 134.3 |
| tsvc_c2/k48 | bare_llm_nospeed_v4 | claude-sonnet-5 | 5 | BROKEN | 4.30x | —+— | — | — | 1 | 142.1 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-sonnet-5 | 1 | BROKEN | 5.62x | —+— | — | — | 1 | 189.4 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-sonnet-5 | 2 | BROKEN | 5.78x | —+— | — | — | 1 | 162.7 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-sonnet-5 | 3 | BROKEN | 5.78x | —+— | — | — | 1 | 147.8 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-sonnet-5 | 4 | BROKEN | 8.89x | —+— | — | — | 1 | 265.5 |
| tsvc_c2/k53 | bare_llm_nospeed_v4 | claude-sonnet-5 | 5 | BROKEN | 9.06x | —+— | — | — | 1 | 243.0 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-sonnet-5 | 1 | FASTER | 3.84x | —+— | — | — | 1 | 115.4 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-sonnet-5 | 2 | FASTER | 1.33x | —+— | — | — | 1 | 153.7 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-sonnet-5 | 3 | FASTER | 3.77x | —+— | — | — | 1 | 128.1 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-sonnet-5 | 4 | FASTER | 3.80x | —+— | — | — | 1 | 147.8 |
| tsvc_c2/s161 | bare_llm_nospeed_v4 | claude-sonnet-5 | 5 | FASTER | 2.21x | —+— | — | — | 1 | 99.3 |
