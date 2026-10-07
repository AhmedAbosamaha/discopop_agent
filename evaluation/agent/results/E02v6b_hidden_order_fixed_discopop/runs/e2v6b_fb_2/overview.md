# Agent experiment run `e2v6b_fb_2`

- status: finished (created 2026-10-07T03:30:55, finished 2026-10-07T16:02:16)
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
| full_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 18 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 221 | 46 |
| no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 20 | 3 | 1 | 0 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 1457 | 201 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 4.23x | 3+0 | 1 | 0 | 1 | 222.9 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 4.11x | 3+0 | 1 | 0 | 5 | 631.1 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 1.07x | 1+0 | 1 | 0 | 4 | 767.5 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.87x | 3+0 | 1 | 0 | 1 | 144.8 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.03x | 3+0 | 1 | 0 | 1 | 145.2 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.79x | 3+0 | 1 | 0 | 6 | 838.9 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.73x | 3+0 | 1 | 0 | 5 | 878.6 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 3.75x | 3+0 | 1 | 0 | 2 | 265.2 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | parallel-not-faster | 1.05x | 1+0 | 1 | 0 | 6 | 861.9 |
| tsvc_c2/k27 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.32x | 3+0 | 1 | 0 | 1 | 249.2 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1899.0 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1602.0 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 10 | 1458.2 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.01x | 0+0 | 0 | 0 | 10 | 1998.2 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1479.8 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 10 | 1746.8 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1455.3 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.02x | 0+0 | 0 | 0 | 10 | 1230.4 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1494.1 |
| tsvc_c2/k27 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1433.3 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.12x | 2+0 | 1 | 0 | 1 | 218.3 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | FASTER | 2.98x | 2+0 | 1 | 0 | 1 | 63.1 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.35x | 2+0 | 1 | 0 | 1 | 175.7 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.00x | 2+0 | 1 | 0 | 1 | 164.0 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.06x | 2+0 | 1 | 0 | 1 | 206.9 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.12x | 2+0 | 1 | 0 | 1 | 115.2 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 3.00x | 2+0 | 1 | 0 | 3 | 341.3 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | FASTER | 3.08x | 2+0 | 1 | 0 | 3 | 343.9 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | FASTER | 3.11x | 2+0 | 1 | 0 | 1 | 106.0 |
| tsvc_c2/k31 | full_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 3.11x | 2+0 | 1 | 0 | 1 | 166.8 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.00x | 2+0 | 1 | 0 | 7 | 674.4 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 10 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1761.4 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | parallel-not-faster | 0.64x | 1+0 | 1 | 0 | 8 | 880.4 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 3 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1586.0 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | no-change | 1.00x | 0+0 | 0 | 0 | 12 | 1562.3 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 5 | no-change | 1.01x | 0+0 | 0 | 0 | 11 | 1098.3 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 6 | FASTER | 1.48x | 2+0 | 1 | 0 | 7 | 815.1 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 11 | 1324.5 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 8 | no-change | 0.99x | 0+0 | 0 | 0 | 11 | 1302.1 |
| tsvc_c2/k31 | no_evidence_nospeed_v4 | claude-haiku-4-5-20251001 | 9 | FASTER | 2.80x | 2+0 | 1 | 0 | 9 | 1430.2 |
