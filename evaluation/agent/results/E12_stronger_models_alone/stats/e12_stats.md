# E12 — the Haiku agent with evidence against stronger models alone

Per loop: successes (race-free verified parallel program covering the hot loop) · of them FASTER · unsafe (BROKEN, racy, not compiling) · trials with a verdict; harness edits apart. p: Fisher's exact, one-sided, the agent against the row (more successes / more FASTER successes / fewer unsafe).

| arm | `k19` | `k48` | `s424` | `s161` |
|---|---|---|---|---|
| Haiku agent + evidence (v3) | 10/10 (10 faster) · 0 unsafe | 10/10 (10 faster) · 0 unsafe | 1/10 (0 faster) · 0 unsafe | 10/10 (10 faster) · 0 unsafe |
| Opus 5.5 alone | 3/5 (0 faster) · 2 unsafe<br>p: success 0.0952 · faster 0.000333 · unsafe 0.0952 | 3/5 (0 faster) · 2 unsafe<br>p: success 0.0952 · faster 0.000333 · unsafe 0.0952 | 5/5 (0 faster) · 0 unsafe<br>p: success 1 · faster 1 · unsafe 1 | 5/5 (5 faster) · 0 unsafe<br>p: success 1 · faster 1 · unsafe 1 |
| Fable 5.1 alone | 3/3 (0 faster) · 0 unsafe · 2 harness edit(s)<br>p: success 1 · faster 0.0035 · unsafe 1 | 1/4 (0 faster) · 3 unsafe · 1 harness edit(s)<br>p: success 0.011 · faster 0.000999 · unsafe 0.011 | 5/5 (0 faster) · 0 unsafe<br>p: success 1 · faster 1 · unsafe 1 | 5/5 (5 faster) · 0 unsafe<br>p: success 1 · faster 1 · unsafe 1 |
| Sonnet 5 alone | 0/10 (0 faster) · 10 unsafe<br>p: success 5.41e-06 · faster 5.41e-06 · unsafe 5.41e-06 | — | — | — |
| Haiku alone (new CLI) | 0/5 (0 faster) · 5 unsafe<br>p: success 0.000333 · faster 0.000333 · unsafe 0.000333 | 1/5 (1 faster) · 4 unsafe<br>p: success 0.00366 · faster 0.00366 · unsafe 0.00366 | 0/5 (0 faster) · 5 unsafe<br>p: success 0.667 · faster 1 · unsafe 0.000333 | 2/5 (2 faster) · 3 unsafe<br>p: success 0.022 · faster 0.022 · unsafe 0.022 |
| Haiku alone (old CLI) | 0/10 (0 faster) · 10 unsafe<br>p: success 5.41e-06 · faster 5.41e-06 · unsafe 5.41e-06 | 1/10 (1 faster) · 9 unsafe<br>p: success 5.95e-05 · faster 5.95e-05 · unsafe 5.95e-05 | 0/10 (0 faster) · 9 unsafe<br>p: success 0.5 · faster 1 · unsafe 5.95e-05 | 4/10 (4 faster) · 6 unsafe<br>p: success 0.00542 · faster 0.00542 · unsafe 0.00542 |

Runs: Haiku agent + evidence (v3) — e12_agent_v3, e2v3_k19, e2v3_k48; Opus 5.5 alone — e12_opus_b1, e12_opus_v3; Fable 5.1 alone — e12_fable_b1, e12_fable_v3; Sonnet 5 alone — e2v3s_k19; Haiku alone (new CLI) — e12_haiku_b1, e12_haiku_v3; Haiku alone (old CLI) — e2b1_bare_m3_a, e2v3_k19, e2v3_k48.
