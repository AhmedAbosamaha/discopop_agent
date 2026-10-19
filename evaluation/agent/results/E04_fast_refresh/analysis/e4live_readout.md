# E4 step 4 — the fast refresh's live trials: the read-out as pre-registered

Registered in THESIS_EXPERIMENTS §6 on 18 Oct 2026 before any trial ("Plan, E4 step 4 pre-registration"). `fast_recon_v5` (the fast refresh and the model's report) beside `default_v5` (the full re-profile; E3's and E3b's corrected cells). No test, as registered.

## The 18 loops

| loop | full re-profile (E3/E3b) race-free FASTER | fast refresh + report | unusable full / fast | outcomes, fast | speed-up 6 / 12, fast (median) | fast refreshes (sum) | reports answered (sum) |
|---|---:|---:|---|---|---:|---:|---:|
| `s112` | 5 of 5 | 4 of 5 | 0 / 0 | FASTER 4, no-change 1 | 1.31 / 1.40 | 13 | 13 |
| `s121` | 5 of 5 | 4 of 5 | 0 / 0 | FASTER 4, no-change 1 | 1.43 / 1.50 | 11 | 11 |
| `s1213` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 2.78 / 2.64 | 5 | 5 |
| `s127` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 3.84 / 3.95 | 5 | 5 |
| `s211` | 4 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 1.15 / 1.24 | 5 | 5 |
| `s212` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 1.84 / 1.80 | 20 | 20 |
| `s243` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 1.90 / 1.88 | 9 | 9 |
| `s244` | 3 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 4.18 / 4.10 | 15 | 15 |
| `s252` | 3 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 2.65 / 2.60 | 8 | 8 |
| `s254` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 3.44 / 3.40 | 6 | 6 |
| `s255` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 1.45 / 2.60 | 6 | 6 |
| `s281` | 5 of 5 | 4 of 5 | 0 / 0 | FASTER 4, no-change 1 | 2.54 / 3.46 | 9 | 9 |
| `s291` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 3.45 / 3.45 | 5 | 5 |
| `s292` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 1.70 / 2.95 | 5 | 5 |
| `s293` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 2.78 / 2.87 | 5 | 5 |
| `s241` | 4 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 1.10 / 1.10 | 11 | 11 |
| `s331` | 1 of 5 | 1 of 5 | 0 / 0 | FASTER 1, no-change 3, parallel-not-faster 1 | 1.00 / 1.00 | 39 | 39 |
| `s341` | 0 of 5 | 0 of 5 | 0 / 0 | no-change 5 | 0.99 / 0.99 | 43 | 43 |

| setup | trials | race-free FASTER | unusable | rewrite calls (median) | all calls, usage log (median) | cost $ (sum) | full profiles (median) | agent s (median) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `default_v5` (E3/E3b) | 90 | 75 of 90 | 0 | 2.00 | 2.00 | 52.08 | 1.00 | 284.50 |
| `fast_recon_v5` | 90 | 78 of 90 | 0 | 2.00 | 3.00 | 61.89 | 0.00 | 365.65 |

## The contrast set and its control (`s311`)

| loop | full re-profile (E3/E3b) race-free FASTER | fast refresh + report | unusable full / fast | outcomes, fast | speed-up 6 / 12, fast (median) | fast refreshes (sum) | reports answered (sum) |
|---|---:|---:|---|---|---:|---:|---:|
| `s314` | 5 of 5 | 4 of 5 | 0 / 0 | FASTER 4, no-change 1 | 5.96 / 9.89 | 28 | 28 |
| `s316` | 4 of 5 | 4 of 5 | 0 / 0 | FASTER 4, no-change 1 | 1.73 / 3.37 | 21 | 21 |
| `s3113` | 5 of 5 | 3 of 5 | 0 / 0 | FASTER 3, no-change 2 | 1.74 / 3.35 | 34 | 34 |
| `s315` | 2 of 5 | 4 of 5 | 0 / 0 | FASTER 4, no-change 1 | 2.21 / 4.29 | 28 | 28 |
| `s318` | 4 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 2.25 / 2.21 | 16 | 16 |
| `s319` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 3.94 / 4.02 | 11 | 11 |
| `s311` | 5 of 5 | 5 of 5 | 0 / 0 | FASTER 5 | 5.68 / 8.85 | 8 | 8 |

| setup | trials | race-free FASTER | unusable | rewrite calls (median) | all calls, usage log (median) | cost $ (sum) | full profiles (median) | agent s (median) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `default_v5` (E3/E3b) | 35 | 30 of 35 | 0 | 4.00 | 4.00 | 25.94 | 3.00 | 379.20 |
| `fast_recon_v5` | 35 | 30 of 35 | 0 | 4.00 | 7.00 | 41.22 | 0.00 | 771.10 |

## The refresh and the report in the trials

- refreshes after a kept rewrite, by kind (the agent's own `[refresh]` lines): fast 366
- trials with at least one fast refresh: 125 of 125; with a fallback to the full re-profile: 0
- reports answered and placed: 366 in 125 trials; report calls that failed: 0; reports that broke the explorer: 0
- the agent's warnings that the model called a loop independent where static analysis records a dependence: 749 (the agent prints at most three per report); the whole count, from the audit `llm_recon.json` (one per loop, variable and dependence type): 1739 in 257 of 366 reports, in 111 trials; loops the model declared independent: 398
- profiling seconds a refresh saved, estimated (step 1's medians, 1.75 s against 1.54 s): 366 fast refreshes × 0.21 s = 76.9 s, against 86318 s of agent time in these trials

## Rewrites kept and reverted, with the agent's recorded reasons (R2)

After a rewrite that passed the quality gate and its refresh: did DiscoPoP find a usable pattern in the changed lines (the exposure verdict), and for a pattern found, D40's judgement of its pragmas — `ok` kept, `not_faster` reverted, `pattern_broken` reverted because a pragma failed the safety gate. Sums over the trials, from their records.

| set | setup | trials | rewrites kept | reverts | pattern found | no pattern | no usable pragma | other | D40 ok | D40 not faster | D40 pragma failed the safety gate | D40 other |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| The 18 loops | `default_v5` (E3/E3b) | 90 | 80 | 147 | 176 | 51 | 0 | 0 | 80 | 76 | 20 | 0 |
| The 18 loops | `fast_recon_v5` | 90 | 79 | 139 | 192 | 25 | 3 | 0 | 81 | 88 | 23 | 0 |
| The contrast set and its control | `default_v5` (E3/E3b) | 35 | 28 | 90 | 45 | 72 | 4 | 0 | 31 | 12 | 2 | 0 |
| The contrast set and its control | `fast_recon_v5` | 35 | 27 | 116 | 83 | 46 | 17 | 0 | 30 | 14 | 39 | 0 |

## Every unusable program

- none

## Trials without a verdict (left out of every rate)

- none

## To be read by hand (registered): loops that moved by 2 or more race-free FASTER

- `tsvc_c2/s244`: full 3 of 5, fast 5 of 5
- `tsvc_c2/s252`: full 3 of 5, fast 5 of 5
- `tsvc_c4/s3113`: full 5 of 5, fast 3 of 5
- `tsvc_c4/s315`: full 2 of 5, fast 4 of 5
