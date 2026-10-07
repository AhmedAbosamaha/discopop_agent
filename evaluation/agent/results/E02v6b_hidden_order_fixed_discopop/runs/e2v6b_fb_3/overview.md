# Agent experiment run `e2v6b_fb_3`

- status: finished (created 2026-10-07T03:31:04, finished 2026-10-07T12:15:16)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `27ac32333e8f80d886874b1d5086f5faffec5158` (uncommitted diff sha256 `None`)
- harness: `27ac32333e8f80d886874b1d5086f5faffec5158` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_nospeed_v4 | claude-haiku-4-5-20251001 | 30 | 19 | 7 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 134 | 107 |
| no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 30 | 20 | 4 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 209 | 115 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.03x | 2+0 | 1 | 0 | 1 | 111.1 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 4.07x | 2+0 | 1 | 0 | 1 | 73.8 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.14x | 2+0 | 1 | 0 | 1 | 112.3 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.04x | 2+0 | 1 | 0 | 1 | 63.8 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.68x | 2+0 | 1 | 0 | 1 | 68.0 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.05x | 2+0 | 1 | 0 | 1 | 141.2 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.72x | 2+0 | 1 | 0 | 1 | 130.9 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 4.00x | 2+0 | 1 | 0 | 1 | 60.2 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 4.07x | 2+0 | 1 | 0 | 1 | 104.8 |
| tsvc_c2/k48 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.70x | 2+0 | 1 | 0 | 1 | 83.2 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.16x | 2+0 | 1 | 0 | 1 | 47.0 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.60x | 2+0 | 1 | 0 | 1 | 91.2 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.68x | 2+0 | 1 | 0 | 1 | 112.9 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.95x | 2+0 | 1 | 0 | 1 | 54.8 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.08x | 2+0 | 1 | 0 | 1 | 153.7 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.07x | 2+0 | 1 | 0 | 1 | 65.8 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.75x | 2+0 | 1 | 0 | 1 | 53.5 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 4.11x | 2+0 | 1 | 0 | 1 | 125.6 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.55x | 2+0 | 1 | 0 | 1 | 132.1 |
| tsvc_c2/k48 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.51x | 2+0 | 1 | 0 | 1 | 57.3 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.98x | 2+0 | 1 | 0 | 10 | 1388.6 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.98x | 2+0 | 1 | 0 | 10 | 1304.1 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.78x | 2+0 | 1 | 0 | 7 | 665.3 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.95x | 1+0 | 1 | 0 | 4 | 483.2 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1572.4 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1297.8 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1558.6 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.98x | 2+0 | 1 | 0 | 3 | 233.4 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1632.6 |
| tsvc_c2/k53 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.98x | 2+0 | 1 | 0 | 6 | 588.4 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | parallel-not-faster | 0.96x | 1+0 | 1 | 0 | 4 | 346.1 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1418.9 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1184.5 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 984.0 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1172.8 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.92x | 2+0 | 1 | 0 | 4 | 426.4 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | parallel-not-faster | 0.85x | 1+0 | 1 | 0 | 4 | 360.2 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.86x | 1+0 | 1 | 0 | 10 | 835.6 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 973.0 |
| tsvc_c2/k53 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1011.8 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.29x | 2+0 | 1 | 0 | 1 | 120.3 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.29x | 2+0 | 1 | 0 | 1 | 64.0 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.30x | 2+0 | 1 | 0 | 1 | 121.6 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.15x | 2+0 | 1 | 0 | 1 | 116.0 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.22x | 2+0 | 1 | 0 | 1 | 136.9 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.18x | 2+0 | 1 | 0 | 1 | 116.7 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.22x | 2+0 | 1 | 0 | 1 | 149.8 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.18x | 2+0 | 1 | 0 | 1 | 156.3 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | parallel-not-faster | 0.28x | 2+0 | 1 | 0 | 2 | 150.7 |
| tsvc_c2/s161 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.23x | 2+0 | 1 | 0 | 1 | 130.5 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.22x | 2+0 | 1 | 0 | 2 | 190.1 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.22x | 2+0 | 1 | 0 | 3 | 468.9 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.17x | 2+0 | 1 | 0 | 2 | 186.8 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.22x | 2+0 | 1 | 0 | 1 | 107.3 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.23x | 2+0 | 1 | 0 | 2 | 236.5 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.19x | 2+0 | 1 | 0 | 3 | 317.4 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.18x | 2+0 | 1 | 0 | 2 | 183.5 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.25x | 2+0 | 1 | 0 | 1 | 153.2 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 1.45x | 3+0 | 1 | 0 | 1 | 231.7 |
| tsvc_c2/s161 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.23x | 2+0 | 1 | 0 | 2 | 228.2 |
