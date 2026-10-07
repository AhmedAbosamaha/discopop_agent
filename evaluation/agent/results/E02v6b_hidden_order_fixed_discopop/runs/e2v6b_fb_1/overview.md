# Agent experiment run `e2v6b_fb_1`

- status: finished (created 2026-10-07T03:30:45, finished 2026-10-07T11:11:42)
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
| full_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 17 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 133 | 35 |
| no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 7 | 3 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 886 | 152 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.93x | 2+0 | 1 | 0 | 1 | 152.0 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 4.10x | 2+0 | 1 | 0 | 1 | 100.4 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 4.15x | 2+0 | 1 | 0 | 1 | 100.1 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.62x | 2+0 | 1 | 0 | 1 | 76.4 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.01x | 2+0 | 1 | 0 | 1 | 74.5 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.28x | 2+0 | 1 | 0 | 1 | 83.4 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.97x | 2+0 | 1 | 0 | 1 | 95.3 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 3.77x | 2+0 | 1 | 0 | 1 | 139.0 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.90x | 2+0 | 1 | 0 | 1 | 126.7 |
| tsvc_c2/k19 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.75x | 2+0 | 1 | 0 | 1 | 285.7 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.02x | 2+0 | 1 | 0 | 1 | 189.4 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1485.2 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1298.5 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 4.05x | 2+0 | 1 | 0 | 3 | 408.4 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.01x | 0+0 | 0 | 0 | 12 | 1259.2 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.08x | 2+0 | 1 | 0 | 3 | 519.8 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1286.1 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 4.15x | 2+0 | 1 | 0 | 2 | 321.2 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.01x | 0+0 | 0 | 0 | 11 | 1096.6 |
| tsvc_c2/k19 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.96x | 2+0 | 1 | 0 | 7 | 914.3 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.16x | 2+0 | 1 | 0 | 1 | 139.9 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 3.16x | 2+0 | 1 | 0 | 1 | 103.3 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.50x | 2+0 | 1 | 0 | 5 | 689.5 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | parallel-not-faster | 0.33x | 2+0 | 1 | 0 | 6 | 651.9 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.98x | 2+0 | 1 | 0 | 2 | 194.7 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.99x | 1+0 | 1 | 0 | 2 | 187.2 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.15x | 2+0 | 1 | 0 | 1 | 113.5 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 2.80x | 2+0 | 1 | 0 | 1 | 111.2 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.23x | 2+0 | 1 | 0 | 2 | 276.3 |
| tsvc_c2/k23 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | parallel-not-faster | 0.97x | 1+0 | 1 | 0 | 4 | 361.7 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 999.1 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | parallel-not-faster | 0.99x | 1+0 | 1 | 0 | 6 | 610.1 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1060.2 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1110.4 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.21x | 2+0 | 1 | 0 | 6 | 702.0 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | parallel-not-faster | 0.73x | 1+0 | 1 | 0 | 5 | 434.1 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1175.8 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | parallel-not-faster | 0.78x | 1+0 | 1 | 0 | 4 | 515.1 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 9 | 857.5 |
| tsvc_c2/k23 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.16x | 2+0 | 1 | 0 | 6 | 678.8 |
