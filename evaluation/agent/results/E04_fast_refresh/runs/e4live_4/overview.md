# Agent experiment run `e4live_4`

- status: finished (created 2026-10-18T23:16:04, finished 2026-10-19T03:56:01)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `7bb69f79a558a5cb8041b35aaadbac39dad56839` (uncommitted diff sha256 `None`)
- harness: `7bb69f79a558a5cb8041b35aaadbac39dad56839` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fast_recon_v5 | claude-haiku-4-5-20251001 | 30 | 28 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 349 | 88 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s254 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.40x | 1+0 | 1 | 0 | 1 | 179.7 |
| tsvc_c2/s254 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.44x | 1+0 | 1 | 0 | 3 | 480.8 |
| tsvc_c2/s254 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.77x | 1+0 | 1 | 0 | 1 | 196.5 |
| tsvc_c2/s254 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.39x | 1+0 | 1 | 0 | 1 | 162.8 |
| tsvc_c2/s254 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.62x | 1+0 | 1 | 0 | 1 | 199.4 |
| tsvc_c2/s255 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 2.60x | 1+0 | 1 | 0 | 1 | 169.9 |
| tsvc_c2/s255 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 2.62x | 1+0 | 1 | 0 | 1 | 187.0 |
| tsvc_c2/s255 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 2.64x | 1+0 | 1 | 0 | 1 | 167.2 |
| tsvc_c2/s255 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 2.60x | 1+0 | 1 | 0 | 3 | 610.7 |
| tsvc_c2/s255 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 2.59x | 1+0 | 1 | 0 | 1 | 179.7 |
| tsvc_c2/s281 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 2 | 602.5 |
| tsvc_c2/s281 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.40x | 2+0 | 1 | 0 | 2 | 378.3 |
| tsvc_c2/s281 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.46x | 2+0 | 1 | 0 | 4 | 533.4 |
| tsvc_c2/s281 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.58x | 2+0 | 1 | 0 | 6 | 946.0 |
| tsvc_c2/s281 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 4.73x | 1+0 | 1 | 0 | 4 | 697.2 |
| tsvc_c2/s291 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.45x | 1+0 | 1 | 0 | 1 | 182.1 |
| tsvc_c2/s291 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 3.47x | 1+0 | 1 | 0 | 1 | 134.1 |
| tsvc_c2/s291 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 3.84x | 1+0 | 1 | 0 | 1 | 147.1 |
| tsvc_c2/s291 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 3.44x | 1+0 | 1 | 0 | 1 | 228.1 |
| tsvc_c2/s291 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 3.45x | 1+0 | 1 | 0 | 1 | 194.0 |
| tsvc_c4/s311 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 8.90x | 1+0 | 1 | 1 | 7 | 894.5 |
| tsvc_c4/s311 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 9.67x | 1+0 | 0 | 1 | 3 | 320.5 |
| tsvc_c4/s311 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 8.85x | 1+0 | 0 | 1 | 2 | 282.4 |
| tsvc_c4/s311 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 8.49x | 1+0 | 1 | 1 | 3 | 475.3 |
| tsvc_c4/s311 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | FASTER | 8.78x | 1+0 | 0 | 1 | 4 | 546.6 |
| tsvc_c4/s315 | fast_recon_v5 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.73x | 1+0 | 1 | 0 | 2 | 547.1 |
| tsvc_c4/s315 | fast_recon_v5 | claude-haiku-4-5-20251001 | 2 | FASTER | 12.50x | 1+0 | 1 | 0 | 4 | 629.7 |
| tsvc_c4/s315 | fast_recon_v5 | claude-haiku-4-5-20251001 | 3 | FASTER | 10.23x | 1+0 | 1 | 0 | 8 | 1500.1 |
| tsvc_c4/s315 | fast_recon_v5 | claude-haiku-4-5-20251001 | 4 | FASTER | 4.29x | 1+0 | 1 | 0 | 8 | 1341.2 |
| tsvc_c4/s315 | fast_recon_v5 | claude-haiku-4-5-20251001 | 5 | no-change | 1.00x | 0+0 | 0 | 0 | 10 | 1606.5 |
