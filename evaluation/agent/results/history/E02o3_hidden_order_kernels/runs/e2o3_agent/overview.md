# Agent experiment run `e2o3_agent`

- status: finished (created 2026-10-03T09:45:53, finished 2026-10-03T19:58:25)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `7789d91e26b387529837aa0c18f339e0911c9407` (uncommitted diff sha256 `None`)
- harness: `7789d91e26b387529837aa0c18f339e0911c9407` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 30 | 29 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 177 | 52 |
| no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 30 | 0 | 2 | 0 | 0 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 229 | 90 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.45x | 1+0 | 1 | 0 | 1 | 97.9 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.44x | 1+0 | 1 | 0 | 1 | 74.3 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.46x | 1+0 | 1 | 0 | 2 | 275.1 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.41x | 1+0 | 1 | 0 | 2 | 155.9 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.48x | 1+0 | 1 | 0 | 2 | 213.4 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.47x | 1+0 | 1 | 0 | 1 | 102.5 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 222.8 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.48x | 1+0 | 1 | 0 | 2 | 165.3 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.46x | 1+0 | 1 | 0 | 3 | 206.1 |
| tsvc_b1/k23 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.42x | 1+0 | 1 | 0 | 1 | 72.8 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 264.7 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 226.1 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 301.6 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.80x | 1+0 | 1 | 0 | 3 | 290.0 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 225.0 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 188.4 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 224.6 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 237.6 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 306.3 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 214.1 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.13x | 1+0 | 1 | 0 | 2 | 315.5 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.34x | 1+0 | 1 | 0 | 1 | 96.8 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.13x | 1+0 | 1 | 0 | 2 | 286.3 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.12x | 1+0 | 1 | 0 | 3 | 487.2 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.17x | 1+0 | 1 | 0 | 1 | 124.8 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.14x | 1+0 | 1 | 0 | 1 | 214.9 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.35x | 1+0 | 1 | 0 | 1 | 76.8 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.34x | 1+0 | 1 | 0 | 1 | 98.4 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.33x | 1+0 | 1 | 0 | 3 | 437.3 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.35x | 1+0 | 1 | 0 | 3 | 453.3 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 331.4 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 366.3 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.84x | 1+0 | 1 | 0 | 3 | 309.0 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 343.9 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 371.0 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 231.4 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 248.7 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 267.6 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 373.2 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 244.3 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.26x | 1+0 | 1 | 0 | 1 | 228.8 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.27x | 1+0 | 1 | 0 | 2 | 251.2 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.34x | 1+0 | 1 | 0 | 1 | 189.3 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | FASTER | 1.29x | 1+0 | 1 | 0 | 1 | 148.4 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | FASTER | 1.28x | 1+0 | 1 | 0 | 1 | 103.9 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.34x | 1+0 | 1 | 0 | 1 | 124.1 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.27x | 1+0 | 1 | 0 | 4 | 449.4 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | FASTER | 1.27x | 1+0 | 1 | 0 | 1 | 130.2 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.33x | 1+0 | 1 | 0 | 1 | 71.7 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.27x | 1+0 | 1 | 0 | 3 | 257.0 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 159.5 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 162.1 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 178.4 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 183.4 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 129.6 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 118.2 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 142.6 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 197.4 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 160.2 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 159.8 |
