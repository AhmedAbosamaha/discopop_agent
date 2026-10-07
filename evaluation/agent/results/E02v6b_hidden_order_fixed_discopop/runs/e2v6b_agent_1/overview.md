# Agent experiment run `e2v6b_agent_1`

- status: finished (created 2026-10-07T03:31:14, finished 2026-10-07T06:52:41)
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
| full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 19 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 229 | 42 |
| no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 3 | 1 | 0 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 270 | 63 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.12x | 2+0 | 1 | 0 | 1 | 180.0 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 4.16x | 2+0 | 1 | 0 | 1 | 129.3 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.46x | 2+0 | 1 | 0 | 1 | 148.0 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.15x | 2+0 | 1 | 0 | 1 | 109.6 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.05x | 2+0 | 1 | 0 | 1 | 61.8 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.19x | 2+0 | 1 | 0 | 1 | 70.4 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 4.09x | 2+0 | 1 | 0 | 1 | 158.3 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 4.05x | 2+0 | 1 | 0 | 1 | 217.9 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.17x | 2+0 | 1 | 0 | 1 | 55.4 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.70x | 2+0 | 1 | 0 | 2 | 197.4 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.09x | 0+0 | 0 | 0 | 3 | 242.5 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 335.9 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 357.4 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 195.2 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.08x | 0+0 | 0 | 0 | 4 | 223.9 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 339.8 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 180.4 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 295.3 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 202.5 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 269.3 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.28x | 2+0 | 1 | 0 | 3 | 422.0 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.29x | 2+0 | 1 | 0 | 3 | 459.8 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.27x | 2+0 | 1 | 0 | 2 | 277.7 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.20x | 2+0 | 1 | 0 | 3 | 338.2 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.20x | 2+0 | 1 | 0 | 4 | 464.5 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.30x | 2+0 | 1 | 0 | 2 | 239.9 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.27x | 2+0 | 1 | 0 | 3 | 288.7 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 3.30x | 2+0 | 1 | 0 | 4 | 442.5 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 4 | 403.0 |
| tsvc_c2/k23 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.66x | 2+0 | 1 | 0 | 3 | 354.4 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 265.8 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 226.1 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.28x | 2+0 | 1 | 0 | 3 | 246.3 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 351.5 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.27x | 2+0 | 1 | 0 | 3 | 286.5 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.23x | 2+0 | 1 | 0 | 2 | 295.9 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 318.2 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.62x | 1+0 | 1 | 0 | 4 | 270.8 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 260.7 |
| tsvc_c2/k23 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 366.9 |
