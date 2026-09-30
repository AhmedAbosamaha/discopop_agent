# Agent experiment run `e2v3s_k19`

- status: finished (created 2026-09-29T17:07:26, finished 2026-09-30T01:00:22)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `b507acc13a68839b5820e8f1dffd2d56699ee980` (uncommitted diff sha256 `None`)
- harness: `b507acc13a68839b5820e8f1dffd2d56699ee980` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_nospeed_v3 | claude-sonnet-5 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 252 | 10 |
| full_b1_nospeed_v3 | claude-sonnet-5 | 10 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 244 | 11 |
| no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 10 | 0 | 1 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 1343 | 30 |
| twin_full_nospeed_v3 | claude-sonnet-5 | 10 | 8 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 280 | 10 |
| twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 514 | 10 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 1 | BROKEN | 4.73x | —+— | — | — | 1 | 317.7 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 10 | BROKEN | 4.55x | —+— | — | — | 1 | 240.6 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 2 | BROKEN | 4.60x | —+— | — | — | 1 | 287.2 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 3 | BROKEN | 4.50x | —+— | — | — | 1 | 143.7 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 4 | BROKEN | 4.43x | —+— | — | — | 1 | 169.1 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 5 | BROKEN | 4.55x | —+— | — | — | 1 | 455.3 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 6 | BROKEN | 4.63x | —+— | — | — | 1 | 264.0 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 7 | BROKEN | 4.64x | —+— | — | — | 1 | 354.8 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 8 | BROKEN | 4.71x | —+— | — | — | 1 | 121.9 |
| tsvc_b1/k19 | bare_llm_nospeed_v3 | claude-sonnet-5 | 9 | BROKEN | 4.65x | —+— | — | — | 1 | 199.4 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 1 | FASTER | 1.42x | 1+0 | 1 | 0 | 1 | 162.0 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 10 | FASTER | 1.38x | 1+0 | 1 | 0 | 1 | 220.3 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 2 | FASTER | 1.44x | 1+0 | 1 | 0 | 1 | 223.3 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 3 | FASTER | 1.33x | 1+0 | 1 | 0 | 1 | 220.0 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 4 | FASTER | 1.45x | 1+0 | 1 | 0 | 1 | 264.7 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 5 | FASTER | 1.51x | 1+0 | 1 | 0 | 1 | 427.8 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 6 | FASTER | 1.42x | 1+0 | 1 | 0 | 2 | 652.4 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 7 | FASTER | 1.38x | 1+0 | 1 | 0 | 1 | 289.5 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 8 | FASTER | 1.41x | 1+0 | 1 | 0 | 1 | 129.4 |
| tsvc_b1/k19 | full_b1_nospeed_v3 | claude-sonnet-5 | 9 | parallel-not-faster | 0.83x | 1+0 | 1 | 0 | 1 | 590.7 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 1 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 1495.0 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 10 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 1380.6 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 2 | no-change | 1.04x | 0+0 | 0 | 0 | 3 | 1249.2 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 3 | no-change | 1.04x | 0+0 | 0 | 0 | 3 | 657.1 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 4 | parallel-not-faster | 0.92x | 1+0 | 1 | 0 | 3 | 1305.0 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 5 | no-change | 1.03x | 0+0 | 0 | 0 | 3 | 1255.5 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 6 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 897.4 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 7 | no-change | 1.00x | 0+0 | 0 | 0 | 3 | 1446.3 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 8 | no-change | 0.99x | 0+0 | 0 | 0 | 3 | 1512.6 |
| tsvc_b1/k19 | no_evidence_b1_nospeed_v3 | claude-sonnet-5 | 9 | no-change | 1.01x | 0+0 | 0 | 0 | 3 | 1382.1 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 1 | FASTER | 1.22x | —+— | — | — | 1 | 216.8 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 10 | changed-not-parallel | 0.80x | —+— | — | — | 1 | 329.3 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 2 | FASTER | 1.41x | —+— | — | — | 1 | 288.3 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 3 | FASTER | 1.36x | —+— | — | — | 1 | 503.2 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 4 | FASTER | 1.32x | —+— | — | — | 1 | 136.6 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 5 | BROKEN | 1.36x | —+— | — | — | 1 | 415.1 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 6 | FASTER | 1.27x | —+— | — | — | 1 | 142.6 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 7 | FASTER | 1.39x | —+— | — | — | 1 | 168.7 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 8 | FASTER | 1.43x | —+— | — | — | 1 | 279.3 |
| tsvc_b1/k19 | twin_full_nospeed_v3 | claude-sonnet-5 | 9 | FASTER | 1.38x | —+— | — | — | 1 | 280.6 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 1 | BROKEN | 3.38x | —+— | — | — | 1 | 638.3 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 10 | BROKEN | 3.65x | —+— | — | — | 1 | 310.2 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 2 | BROKEN | 2.16x | —+— | — | — | 1 | 481.2 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 3 | BROKEN | 3.45x | —+— | — | — | 1 | 496.3 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 4 | BROKEN | 3.54x | —+— | — | — | 1 | 650.4 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 5 | BROKEN | 3.02x | —+— | — | — | 1 | 530.8 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 6 | BROKEN | 3.58x | —+— | — | — | 1 | 279.9 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 7 | BROKEN | 3.57x | —+— | — | — | 1 | 541.1 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 8 | BROKEN | 3.92x | —+— | — | — | 1 | 427.5 |
| tsvc_b1/k19 | twin_no_evidence_nospeed_v3 | claude-sonnet-5 | 9 | BROKEN | 3.74x | —+— | — | — | 1 | 654.6 |
