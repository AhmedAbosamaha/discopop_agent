# Agent experiment run `e2v6_fb_1`

- status: finished (created 2026-10-05T18:26:43, finished 2026-10-06T04:40:39)
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
| full_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 18 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 146 | 39 |
| no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 6 | 0 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 988 | 189 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.54x | 1+0 | 1 | 0 | 1 | 88.1 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.42x | 1+0 | 1 | 0 | 1 | 96.6 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.52x | 1+0 | 1 | 0 | 1 | 73.2 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.37x | 1+0 | 1 | 0 | 1 | 210.0 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.53x | 1+0 | 1 | 0 | 1 | 44.6 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.52x | 1+0 | 1 | 0 | 1 | 222.4 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.51x | 1+0 | 1 | 0 | 1 | 67.1 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.52x | 1+0 | 1 | 0 | 1 | 168.8 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.50x | 1+0 | 1 | 0 | 4 | 576.6 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.44x | 1+0 | 1 | 0 | 1 | 95.5 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1011.1 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 965.1 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1094.5 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.51x | 1+0 | 1 | 0 | 11 | 1091.2 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1249.9 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 11 | 1260.4 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 959.0 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.02x | 0+0 | 0 | 0 | 10 | 871.6 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1050.4 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 5.04x | 1+0 | 1 | 0 | 10 | 1191.2 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.36x | 1+0 | 1 | 0 | 1 | 86.6 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | BROKEN | — | 1+0 | 1 | 0 | 3 | 416.2 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.46x | 1+0 | 1 | 0 | 1 | 111.9 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.44x | 1+0 | 1 | 0 | 2 | 184.7 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.40x | 1+0 | 1 | 0 | 1 | 122.2 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.40x | 1+0 | 1 | 0 | 1 | 84.0 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.25x | 1+0 | 1 | 0 | 2 | 198.3 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.38x | 1+0 | 1 | 0 | 2 | 207.4 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1020.9 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.39x | 1+0 | 1 | 0 | 2 | 177.4 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1086.3 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.44x | 1+0 | 1 | 0 | 1 | 76.1 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 787.4 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.46x | 1+0 | 1 | 0 | 5 | 399.9 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.46x | 1+0 | 1 | 0 | 10 | 707.7 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 10 | 814.4 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 908.2 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.44x | 1+0 | 1 | 0 | 3 | 411.8 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1130.6 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 1132.3 |
