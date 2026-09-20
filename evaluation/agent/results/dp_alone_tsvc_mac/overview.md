# Agent experiment run `dp_alone_tsvc_mac`

- status: finished (created 2026-09-19T19:49:29, finished 2026-09-19T20:07:38)
- host: `ahmeds-MacBook-Pro.local`, compilers `/usr/local/Cellar/llvm@19/19.1.7/bin/clang` / `/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`
- agent: `6eefbdf04627f666d34f4b17c560e432e17db232` (uncommitted diff sha256 `None`)
- harness: `13af1efe815fbfbf2d20e9be8bb90d20339ad603` on `agent-experiments`
- verify size `SMALL`, threads [4], repeats 1

Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's values differ from the original's (relative error > 1e-09) or move between repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ 1.1× at some thread count.

## Summary

| Arm | Model | Trials | FASTER | parallel-not-faster | parallel-speed-not-measurable | changed-not-parallel | no-change | BROKEN | SCAFFOLD_MODIFIED | VERIFY_FAILED | AGENT_ERROR | AGENT_TIMEOUT | PROFILE_ERROR | Median agent s | LLM calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discopop_gate | none | 25 | 0 | 3 | 0 | 0 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 17 | 0 |

## Trials

| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | Rewrites | Baseline | LLM calls | Agent s |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|
| tsvc/s000 | discopop_gate | none | 1 | parallel-not-faster | 0.07x | 1+0 | 0 | 2 | 0 | 29.1 |
| tsvc/s112 | discopop_gate | none | 1 | no-change | 1.02x | 0+0 | 0 | 1 | 0 | 16.4 |
| tsvc/s121 | discopop_gate | none | 1 | no-change | 1.11x | 0+0 | 0 | 1 | 0 | 16.5 |
| tsvc/s1213 | discopop_gate | none | 1 | no-change | 0.99x | 0+0 | 0 | 0 | 0 | 13.8 |
| tsvc/s127 | discopop_gate | none | 1 | no-change | 0.81x | 0+0 | 0 | 1 | 0 | 16.6 |
| tsvc/s211 | discopop_gate | none | 1 | no-change | 1.18x | 0+0 | 0 | 0 | 0 | 13.8 |
| tsvc/s212 | discopop_gate | none | 1 | no-change | 1.21x | 0+0 | 0 | 1 | 0 | 17.2 |
| tsvc/s241 | discopop_gate | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 16.7 |
| tsvc/s243 | discopop_gate | none | 1 | no-change | 1.79x | 0+0 | 0 | 1 | 0 | 16.7 |
| tsvc/s244 | discopop_gate | none | 1 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 16.6 |
| tsvc/s252 | discopop_gate | none | 1 | no-change | 0.95x | 0+0 | 0 | 1 | 0 | 16.3 |
| tsvc/s254 | discopop_gate | none | 1 | no-change | 1.45x | 0+0 | 0 | 1 | 0 | 16.5 |
| tsvc/s255 | discopop_gate | none | 1 | no-change | 1.40x | 0+0 | 0 | 1 | 0 | 16.7 |
| tsvc/s281 | discopop_gate | none | 1 | no-change | 1.07x | 0+0 | 0 | 0 | 0 | 13.5 |
| tsvc/s291 | discopop_gate | none | 1 | no-change | 1.60x | 0+0 | 0 | 2 | 0 | 19.9 |
| tsvc/s292 | discopop_gate | none | 1 | no-change | 1.91x | 0+0 | 0 | 1 | 0 | 18.2 |
| tsvc/s293 | discopop_gate | none | 1 | no-change | 1.04x | 0+0 | 0 | 1 | 0 | 20.1 |
| tsvc/s3112 | discopop_gate | none | 1 | no-change | 1.00x | 0+0 | 0 | 1 | 0 | 19.3 |
| tsvc/s313 | discopop_gate | none | 1 | parallel-not-faster | 0.19x | 1+0 | 0 | 2 | 0 | 25.1 |
| tsvc/s321 | discopop_gate | none | 1 | no-change | 0.96x | 0+0 | 0 | 0 | 0 | 15.1 |
| tsvc/s322 | discopop_gate | none | 1 | no-change | 1.09x | 0+0 | 0 | 0 | 0 | 15.8 |
| tsvc/s323 | discopop_gate | none | 1 | no-change | 0.98x | 0+0 | 0 | 1 | 0 | 37.0 |
| tsvc/s331 | discopop_gate | none | 1 | no-change | 0.98x | 0+0 | 0 | 2 | 0 | 28.9 |
| tsvc/s341 | discopop_gate | none | 1 | no-change | 0.99x | 0+0 | 0 | 2 | 0 | 25.1 |
| tsvc/vpvtv | discopop_gate | none | 1 | parallel-not-faster | 0.10x | 1+0 | 0 | 1 | 0 | 31.4 |
