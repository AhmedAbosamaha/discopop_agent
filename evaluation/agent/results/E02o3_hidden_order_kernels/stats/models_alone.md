# E2-O3 — the Haiku agent against every model alone on the ORDER-3 kernels

Per loop: successes (race-free verified parallel program covering the hot loop) · of them FASTER · unsafe (wrong output, a crash, racy, not compiling) · trials with a verdict; harness edits apart. "did not finish": the output verified exact, the timed run exceeded 30 minutes — correct but far too slow, not unsafe (§6, 4 Oct). p: Fisher's exact, one-sided, the agent against the row (more successes / more FASTER successes / fewer unsafe).

| arm | `k23` | `k31` | `k36` |
|---|---|---|---|
| Haiku agent + evidence (v3) | 9/10 (9 faster) · 0 unsafe | 10/10 (10 faster) · 0 unsafe | 10/10 (10 faster) · 0 unsafe |
| Haiku agent, no evidence | 0/10 (0 faster) · 0 unsafe<br>p: success 5.95e-05 · faster 5.95e-05 · unsafe 1 | 0/10 (0 faster) · 0 unsafe<br>p: success 5.41e-06 · faster 5.41e-06 · unsafe 1 | 0/10 (0 faster) · 0 unsafe<br>p: success 5.41e-06 · faster 5.41e-06 · unsafe 1 |
| Haiku alone | 0/10 (0 faster) · 10 unsafe<br>p: success 5.95e-05 · faster 5.95e-05 · unsafe 5.41e-06 | 0/10 (0 faster) · 10 unsafe<br>p: success 5.41e-06 · faster 5.41e-06 · unsafe 5.41e-06 | 0/10 (0 faster) · 10 unsafe<br>p: success 5.41e-06 · faster 5.41e-06 · unsafe 5.41e-06 |
| Sonnet 5 alone | 0/5 (0 faster) · 5 unsafe<br>p: success 0.002 · faster 0.002 · unsafe 0.000333 | 2/5 (2 faster) · 3 unsafe<br>p: success 0.022 · faster 0.022 · unsafe 0.022 | 0/5 (0 faster) · 5 unsafe<br>p: success 0.000333 · faster 0.000333 · unsafe 0.000333 |
| Opus 5.5 alone | 0/5 (0 faster) · 5 unsafe<br>p: success 0.002 · faster 0.002 · unsafe 0.000333 | 5/5 (1 faster) · 0 unsafe<br>p: success 1 · faster 0.00366 · unsafe 1 | 3/5 (1 faster) · 2 unsafe<br>p: success 0.0952 · faster 0.00366 · unsafe 0.0952 |
| Fable 5.1 alone | 0/5 (0 faster) · 5 unsafe<br>p: success 0.002 · faster 0.002 · unsafe 0.000333 | 4/5 (4 faster) · 1 unsafe<br>p: success 0.333 · faster 0.333 · unsafe 0.333 | 2/5 (1 faster) · 3 unsafe<br>p: success 0.022 · faster 0.00366 · unsafe 0.022 |

Runs: Haiku agent + evidence (v3) — e2o3_agent; Haiku agent, no evidence — e2o3_agent; Haiku alone — e2o3_bare_haiku; Sonnet 5 alone — e2o3_bare_sonnet; Opus 5.5 alone — e2o3_bare_opus; Fable 5.1 alone — e2o3_bare_fable.
