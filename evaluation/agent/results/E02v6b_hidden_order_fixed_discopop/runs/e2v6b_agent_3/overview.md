# Agent experiment run `e2v6b_agent_3`

- status: finished (created 2026-10-07T11:13:01, finished 2026-10-07T16:12:33)
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
| full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 30 | 20 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 155 | 56 |
| no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 30 | 19 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 188 | 62 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.94x | 2+0 | 1 | 0 | 1 | 62.3 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.77x | 2+0 | 1 | 0 | 1 | 118.8 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.16x | 2+0 | 1 | 0 | 1 | 72.7 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.81x | 2+0 | 1 | 0 | 1 | 148.9 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.85x | 2+0 | 1 | 0 | 1 | 56.8 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.04x | 2+0 | 1 | 0 | 1 | 86.8 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.95x | 2+0 | 1 | 0 | 1 | 91.5 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 3.08x | 2+0 | 1 | 0 | 1 | 153.2 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 4.09x | 2+0 | 1 | 0 | 1 | 156.9 |
| tsvc_c2/k48 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.85x | 2+0 | 1 | 0 | 1 | 112.3 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.97x | 2+0 | 1 | 0 | 1 | 62.3 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 4.06x | 2+0 | 1 | 0 | 1 | 98.9 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.84x | 2+0 | 1 | 0 | 1 | 217.7 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.17x | 2+0 | 1 | 0 | 1 | 120.5 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.13x | 2+0 | 1 | 0 | 1 | 74.4 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.14x | 2+0 | 1 | 0 | 1 | 97.1 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 4.02x | 2+0 | 1 | 0 | 1 | 86.5 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 4.17x | 2+0 | 1 | 0 | 1 | 56.7 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 4.12x | 2+0 | 1 | 0 | 1 | 108.2 |
| tsvc_c2/k48 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 4.13x | 2+0 | 1 | 0 | 3 | 177.5 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 571.9 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 472.9 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 873.3 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 5 | 597.5 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 372.4 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 426.4 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 217.0 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 608.1 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 481.2 |
| tsvc_c2/k53 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 0.99x | 0+0 | 0 | 0 | 4 | 768.9 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.04x | 0+0 | 0 | 0 | 3 | 270.3 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 394.3 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 243.5 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 245.1 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 193.3 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 190.9 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.04x | 0+0 | 0 | 0 | 3 | 294.1 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 184.5 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 170.9 |
| tsvc_c2/k53 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 258.2 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.87x | 2+0 | 1 | 0 | 1 | 160.3 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.16x | 2+0 | 1 | 0 | 1 | 123.6 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.24x | 2+0 | 1 | 0 | 1 | 118.7 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.12x | 2+0 | 1 | 0 | 1 | 104.5 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.17x | 2+0 | 1 | 0 | 1 | 188.1 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 1.85x | 2+0 | 1 | 0 | 1 | 117.7 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.14x | 2+0 | 1 | 0 | 1 | 156.1 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.03x | 2+0 | 1 | 0 | 2 | 161.3 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.13x | 2+0 | 1 | 0 | 1 | 132.7 |
| tsvc_c2/s161 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.14x | 2+0 | 1 | 0 | 1 | 116.4 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.19x | 2+0 | 1 | 0 | 2 | 267.2 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.10x | 2+0 | 1 | 0 | 1 | 115.0 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.15x | 2+0 | 1 | 0 | 3 | 208.9 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 346.0 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.19x | 2+0 | 1 | 0 | 1 | 108.8 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.24x | 2+0 | 1 | 0 | 1 | 121.7 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 2.21x | 2+0 | 1 | 0 | 2 | 223.7 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.19x | 2+0 | 1 | 0 | 2 | 195.9 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 2.06x | 2+0 | 1 | 0 | 1 | 93.5 |
| tsvc_c2/s161 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.15x | 2+0 | 1 | 0 | 3 | 413.2 |
