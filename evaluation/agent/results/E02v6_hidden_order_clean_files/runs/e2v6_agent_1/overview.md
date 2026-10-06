# Agent experiment run `e2v6_agent_1`

- status: finished (created 2026-10-05T15:15:12, finished 2026-10-05T18:24:37)
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
| full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 19 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 165 | 30 |
| no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 0 | 1 | 0 | 0 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 296 | 63 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.37x | 1+0 | 1 | 0 | 1 | 178.8 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.43x | 1+0 | 1 | 0 | 1 | 60.5 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.43x | 1+0 | 1 | 0 | 1 | 61.4 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.46x | 1+0 | 1 | 0 | 1 | 119.0 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.31x | 1+0 | 1 | 0 | 1 | 213.4 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.32x | 1+0 | 1 | 0 | 1 | 127.4 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.54x | 1+0 | 1 | 0 | 1 | 138.2 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.51x | 1+0 | 1 | 0 | 1 | 250.5 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.53x | 1+0 | 1 | 0 | 2 | 358.7 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.50x | 1+0 | 1 | 0 | 1 | 151.9 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 463.9 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 224.6 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 205.2 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 299.1 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 201.1 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 298.5 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 373.8 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 153.6 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.02x | 0+0 | 0 | 0 | 4 | 394.5 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 305.5 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.47x | 1+0 | 1 | 0 | 1 | 86.0 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.38x | 1+0 | 1 | 0 | 2 | 222.1 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.37x | 1+0 | 1 | 0 | 1 | 59.4 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 302.0 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.40x | 1+0 | 1 | 0 | 1 | 116.6 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.39x | 1+0 | 1 | 0 | 3 | 239.1 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.46x | 1+0 | 1 | 0 | 2 | 392.2 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.44x | 1+0 | 1 | 0 | 1 | 101.0 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.37x | 1+0 | 1 | 0 | 2 | 252.4 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.41x | 1+0 | 1 | 0 | 3 | 357.8 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 270.1 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 204.4 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 304.4 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 293.4 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 337.6 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.65x | 1+0 | 1 | 0 | 4 | 405.4 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 298.2 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 253.6 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 252.3 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 275.3 |
