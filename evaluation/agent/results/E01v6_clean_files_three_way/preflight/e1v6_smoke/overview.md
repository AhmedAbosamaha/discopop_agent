# Agent experiment run `e1v6_smoke`

- status: finished (created 2026-10-05T00:06:05, finished 2026-10-05T00:45:20)
- host: `rms14562`, compilers `/usr/bin/clang-20` / `/usr/bin/clang++-20`
- agent: `611c8b24c6f46d024349e3caf1aeb74c501859bb` (uncommitted diff sha256 `None`)
- harness: `611c8b24c6f46d024349e3caf1aeb74c501859bb` on `agentic_DiscoPop`
- verify size `per_kernel`, threads [6, 12], repeats 5

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Main comparison: DiscoPoP alone vs DiscoPoP + agent

**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks (no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the sequential original alone do not show what the agent adds.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v4 | claude-fable-5-1 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 43 | 2 |
| bare_llm_v4 | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 182 | 2 |
| bare_llm_v4 | claude-opus-5-5 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 2 |
| bare_llm_v4 | claude-sonnet-5 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 42 | 2 |
| default_v4 | claude-haiku-4-5-20251001 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 538 | 10 |
| discopop_gate_v4 | claude-haiku-4-5-20251001 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 28 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc_c2/s000 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 3.44x | —+— | — | — | 1 | 32.7 |
| tsvc_c2/s000 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.43x | —+— | — | — | 1 | 31.5 |
| tsvc_c2/s000 | bare_llm_v4 | claude-opus-5-5 | 1 | FASTER | 3.48x | —+— | — | — | 1 | 16.9 |
| tsvc_c2/s000 | bare_llm_v4 | claude-sonnet-5 | 1 | FASTER | 3.44x | —+— | — | — | 1 | 14.2 |
| tsvc_c2/s000 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.52x | 1+0 | 0 | 1 | 7 | 812.6 |
| tsvc_c2/s000 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 3.46x | 1+0 | 0 | 1 | 0 | 49.1 |
| tsvc_c2/s211 | bare_llm_v4 | claude-fable-5-1 | 1 | FASTER | 2.18x | —+— | — | — | 1 | 54.0 |
| tsvc_c2/s211 | bare_llm_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.97x | —+— | — | — | 1 | 332.5 |
| tsvc_c2/s211 | bare_llm_v4 | claude-opus-5-5 | 1 | FASTER | 2.17x | —+— | — | — | 1 | 29.2 |
| tsvc_c2/s211 | bare_llm_v4 | claude-sonnet-5 | 1 | FASTER | 2.40x | —+— | — | — | 1 | 69.0 |
| tsvc_c2/s211 | default_v4 | claude-haiku-4-5-20251001 | 1 | FASTER | 1.37x | 2+0 | 1 | 0 | 3 | 264.4 |
| tsvc_c2/s211 | discopop_gate_v4 | claude-haiku-4-5-20251001 | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 7.6 |
