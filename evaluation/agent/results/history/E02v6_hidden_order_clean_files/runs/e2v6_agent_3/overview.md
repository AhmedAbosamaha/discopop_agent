# Agent experiment run `e2v6_agent_3`

- status: finished (created 2026-10-05T15:15:30, finished 2026-10-05T19:27:11)
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
| full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 30 | 20 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 155 | 61 |
| no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 30 | 18 | 1 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 170 | 56 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.75x | 2+0 | 1 | 0 | 1 | 118.5 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.62x | 2+0 | 1 | 0 | 1 | 78.8 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.66x | 2+0 | 1 | 0 | 1 | 82.9 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.04x | 2+0 | 1 | 0 | 1 | 75.1 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.94x | 2+0 | 1 | 0 | 1 | 184.2 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.72x | 2+0 | 1 | 0 | 1 | 59.4 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 4.04x | 2+0 | 1 | 0 | 1 | 99.2 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 3.84x | 2+0 | 1 | 0 | 1 | 54.6 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.67x | 2+0 | 1 | 0 | 1 | 57.1 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 4.03x | 2+0 | 1 | 0 | 1 | 87.7 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.67x | 2+0 | 1 | 0 | 1 | 103.7 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.81x | 2+0 | 1 | 0 | 1 | 95.5 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.77x | 2+0 | 1 | 0 | 1 | 176.8 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.81x | 2+0 | 1 | 0 | 1 | 56.0 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.82x | 2+0 | 1 | 0 | 1 | 211.7 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.77x | 2+0 | 1 | 0 | 1 | 89.6 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.75x | 2+0 | 1 | 0 | 1 | 89.8 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 4.08x | 2+0 | 1 | 0 | 1 | 80.5 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.70x | 2+0 | 1 | 0 | 1 | 120.6 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.66x | 2+0 | 1 | 0 | 1 | 155.0 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 527.8 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 633.5 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 364.5 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 817.5 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 505.0 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 665.7 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 589.5 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 503.7 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 600.3 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 435.8 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 281.3 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 187.0 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 277.7 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 257.9 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 236.5 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 183.5 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 166.7 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 190.6 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 215.5 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 400.1 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.17x | 2+0 | 1 | 0 | 1 | 237.1 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.23x | 2+0 | 1 | 0 | 1 | 58.8 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.21x | 2+0 | 1 | 0 | 1 | 162.4 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.04x | 2+0 | 1 | 0 | 1 | 125.2 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.12x | 2+0 | 1 | 0 | 1 | 116.7 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.17x | 2+0 | 1 | 0 | 1 | 158.5 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.98x | 2+0 | 1 | 0 | 1 | 194.8 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.18x | 2+0 | 1 | 0 | 1 | 122.7 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.14x | 2+0 | 1 | 0 | 1 | 151.2 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 1.88x | 2+0 | 1 | 0 | 1 | 119.4 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 4 | 364.6 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 1.16x | 2+0 | 1 | 0 | 2 | 251.4 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.85x | 2+0 | 1 | 0 | 1 | 71.7 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.08x | 2+0 | 1 | 0 | 1 | 153.7 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.15x | 2+0 | 1 | 0 | 1 | 195.8 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.24x | 2+0 | 1 | 0 | 1 | 134.6 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.20x | 2+0 | 1 | 0 | 1 | 136.5 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.66x | 4+0 | 1 | 0 | 2 | 149.5 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.17x | 2+0 | 1 | 0 | 1 | 161.7 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.23x | 2+0 | 1 | 0 | 1 | 173.0 |
