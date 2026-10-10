# Agent experiment run `e2v6_agent_2`

- status: finished (created 2026-10-05T15:15:21, finished 2026-10-05T18:59:09)
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
| full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 16 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 190 | 33 |
| no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 333 | 68 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 369.8 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.96x | 2+0 | 1 | 0 | 2 | 270.1 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 289.7 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 0.97x | 0+0 | 0 | 0 | 3 | 388.2 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.80x | 2+0 | 1 | 0 | 3 | 573.3 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.75x | 2+0 | 1 | 0 | 2 | 162.5 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.00x | 2+0 | 1 | 0 | 2 | 238.4 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.92x | 2+0 | 1 | 0 | 1 | 215.6 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.94x | 2+0 | 1 | 0 | 1 | 165.2 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.06x | 0+0 | 0 | 0 | 3 | 470.9 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 260.1 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 184.1 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 165.1 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 348.8 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 234.4 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 205.3 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 227.8 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 162.0 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 243.1 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 323.7 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.35x | 1+0 | 1 | 0 | 1 | 109.3 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.37x | 1+0 | 1 | 0 | 1 | 254.5 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.38x | 1+0 | 1 | 0 | 1 | 165.0 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.31x | 1+0 | 1 | 0 | 1 | 140.6 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.37x | 1+0 | 1 | 0 | 1 | 112.2 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.39x | 1+0 | 1 | 0 | 1 | 147.1 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.22x | 1+0 | 1 | 0 | 1 | 143.2 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.37x | 1+0 | 1 | 0 | 1 | 148.3 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.38x | 1+0 | 1 | 0 | 1 | 213.8 |
| tsvc_c2/k31 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.35x | 1+0 | 1 | 0 | 1 | 114.6 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 368.7 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 565.3 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.03x | 0+0 | 0 | 0 | 4 | 362.0 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 4 | 627.7 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 432.4 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 277.0 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 352.8 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 382.6 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 456.0 |
| tsvc_c2/k31 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 341.5 |
