# Agent experiment run `e2v6_pilot`

- status: finished (created 2026-10-05T14:42:52, finished 2026-10-05T15:09:24)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `cf52d13abf250db3f4b8d2870eba528bec086346` (uncommitted diff sha256 `None`)
- harness: `cf52d13abf250db3f4b8d2870eba528bec086346` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 165 | 7 |
| no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 226 | 12 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.42x | 1+0 | 1 | 0 | 1 | 227.2 |
| tsvc_c2/k19 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.44x | 1+0 | 1 | 0 | 1 | 72.7 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.98x | 0+0 | 0 | 0 | 3 | 247.9 |
| tsvc_c2/k19 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.07x | 0+0 | 0 | 0 | 3 | 184.0 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.01x | 0+0 | 0 | 0 | 4 | 480.0 |
| tsvc_c2/k27 | full_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | FASTER | 1.88x | 2+0 | 1 | 0 | 1 | 102.7 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 1.02x | 0+0 | 0 | 0 | 3 | 491.0 |
| tsvc_c2/k27 | no_evidence_b1_nospeed_v4 | claude-haiku-4-5-20251001 | 2 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 204.3 |
