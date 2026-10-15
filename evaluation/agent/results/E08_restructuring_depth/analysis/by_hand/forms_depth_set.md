# E8 — the form each changed program of the depth set reached (read by hand, 15 Oct 2026)

Registered descriptive read-out (§6, 14 Oct, "Plan, E8 pre-registration"): on the depth set the form the shipped program
reached — the original, step 1 or the final form (step 2) — read program by program against the references
(`evaluation/agent/reference_solutions/tsvc_c5/<loop>.step1.c` and `<loop>.c`). Each program is the trial's `final/`
file; the speed-ups are the harness's at 6 / 12 threads (`trial.json` → `verify.par`). `s221` changed no program in any
arm (15 no-change), so it has no row.

## `s2251`

Step 1: the values `b[i] + c[i]` precomputed into a temporary by a parallel loop, the recurrence loop still sequential.
Final form: the second loop parallel too, each iteration taking its `s` from the temporary at `i - 1`.

| arm | rep | outcome | 6 / 12 threads | form reached |
|---|---:|---|---|---|
| `default_v5` | 1 | FASTER | 2.351 / 2.344 | final (both loops parallel, `s` from `b[i-1] + c[i-1]` precomputed) |
| `default_v5` | 2 | FASTER | 2.275 / 2.253 | final |
| `default_v5` | 3 | parallel-not-faster | 1.026 / 1.029 | final form's split, only the second loop parallel (the temporary filled sequentially) |
| `default_v5` | 4 | FASTER | 2.401 / 2.405 | final |
| `default_v5` | 5 | FASTER | 2.392 / 2.348 | final |
| `depth1_v5` | 1 | FASTER | 2.953 / 2.915 | final (no temporary: `a[i]` from `b[i-1] + c[i-1]` in one parallel loop, `b` in a second) |
| `depth1_v5` | 2 | FASTER | 2.575 / 2.763 | final, with the repetition loop rotated (the first pass peeled) |
| `depth1_v5` | 4 | FASTER | 2.346 / 2.357 | final |
| `depth2_v5` | 3 | FASTER | 1.292 / 1.287 | final, plus a copy of `b` per repetition (`memcpy` after `dummy()`) |
| `depth2_v5` | 4 | FASTER | 1.485 / 1.459 | final, plus a copy of `b` per repetition (`memcpy` before the loops) |

At depth 0 the model did both steps in one rewrite in 4 of 5 trials; no deeper level reached a form depth 0 did not.

## `s257`

Step 1: the inner loop over `j` parallel for each `i`, the recurrence on `a` kept in the `i` loop. Final form: the
recurrence on `a` split out into its own sequential loop, then the loop over `i` parallel.

| arm | rep | outcome | 6 / 12 threads | form reached |
|---|---:|---|---|---|
| `default_v5` | 1 | FASTER | 4.541 / 2.131 | step 1 |
| `default_v5` | 2 | FASTER | 3.134 / 2.072 | step 1 (two parallel inner loops through a stack temporary) |
| `default_v5` | 3 | FASTER | 4.419 / 2.484 | step 1 |
| `default_v5` | 4 | FASTER | 4.508 / 2.205 | step 1 |
| `default_v5` | 5 | FASTER | 4.582 / 2.355 | step 1 |
| `depth1_v5` | 1 | FASTER | 4.542 / 2.283 | step 1 |
| `depth1_v5` | 2 | FASTER | 4.101 / 2.892 | step 1, plus a parallel loop over `i` writing `aa` from a saved temporary (no split of the recurrence) |
| `depth1_v5` | 3 | FASTER | 4.691 / 2.112 | step 1 |
| `depth1_v5` | 4 | FASTER | 4.932 / 3.758 | step 1, plus a parallel copy loop over `i` (no split of the recurrence) |
| `depth1_v5` | 5 | FASTER | 7.547 / 7.464 | **final** — made at depth 1 (D40 6.72×) |
| `depth2_v5` | 1 | FASTER | 4.463 / 2.108 | step 1 |
| `depth2_v5` | 2 | FASTER | 4.302 / 2.321 | step 1 |
| `depth2_v5` | 3 | FASTER | 6.455 / 7.335 | **final**, plus a copy of `aa` per repetition — made at depth 2 (D40 4.88×) |
| `depth2_v5` | 4 | FASTER | 7.567 / 6.883 | **final** — made at depth 2 (D40 5.96×) |
| `depth2_v5` | 5 | FASTER | 4.499 / 2.433 | step 1 |

The final form: 0 of 5 at depth 0, 1 of 5 at depth 1, 2 of 5 at depth 2, each by the last level's rewrite
(`agent_patches/accepted.json`: the outer loop's pattern first appears in that level's exposed patterns).
