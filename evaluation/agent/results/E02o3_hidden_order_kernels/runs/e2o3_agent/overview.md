# Agent experiment run `e2o3_agent`

- status: finished (created 2026-10-03T09:45:53, finished 2026-10-03T10:49:50)
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
| full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 30 | 9 | 0 | 0 | 0 | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 33 | 78 |
| no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 30 | 0 | 1 | 0 | 0 | 29 | 0 | 0 | 0 | 0 | 0 | 0 | 33 | 90 |

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
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 182.3 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 224.6 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 237.6 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 306.3 |
| tsvc_b1/k23 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 214.1 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 33.1 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 33.0 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 32.9 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 32.8 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 32.8 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 32.7 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 33.6 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 0.97x | 0+0 | 0 | 0 | 3 | 33.0 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 32.3 |
| tsvc_b1/k31 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 32.9 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.03x | 0+0 | 0 | 0 | 3 | 32.8 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 33.3 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 33.0 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 32.7 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 32.7 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 33.2 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 32.8 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 33.0 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 33.0 |
| tsvc_b1/k31 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 33.1 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 32.5 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 32.9 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 32.7 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 33.0 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 32.6 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 32.9 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 32.8 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 32.2 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 32.8 |
| tsvc_b1/k36 | full_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 32.6 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 33.5 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 10 | no-change | 0.97x | 0+0 | 0 | 0 | 3 | 32.1 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 32.9 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 3 | no-change | 1.03x | 0+0 | 0 | 0 | 3 | 33.4 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 33.8 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 32.7 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 6 | no-change | 0.97x | 0+0 | 0 | 0 | 3 | 33.3 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 7 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 32.9 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 8 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 33.1 |
| tsvc_b1/k36 | no_evidence_b1_nospeed_v3 | claude-haiku-4-5-20251001 | 9 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 33.2 |
