# E4 step 2 — the dry pass (`e4_report_dry`), no model

Built by `e4_report_dry_readout.py` from the run's records. Every request was built as the agent builds it and recorded; none was sent.

**599 rewrites** (599 in step 1); commit `ad4cacf4e`, the DiscoPoP pass `b22cb05f336e`; 2026-10-12T20:47:20Z to 2026-10-12T21:03:38Z; profiles before a rewrite that failed: 0; fast refreshes that reported themselves unusable: 0.

## 1 The report requests

| rewrites of | rewrites | a request would be sent | none (the rewrite left no new line) |
|---|---:|---:|---:|
| the pragma experiment, the 18 loops | 227 | 227 | 0 |
| the pragma experiment, the recurrence loops | 52 | 52 | 0 |
| the contrast set | 144 | 144 | 0 |
| the main comparison, the 18 loops | 176 | 176 | 0 |
| **all** | 599 | 599 | 0 |

The request: 972 to 2528 characters, median 1235; the instructions with it: 1279 characters (`e298f72f252656c1`). Loops named per request: 2 to 6, median 3; requests that name no loop: 0.

## 2 Where the deletion review has anything to ask

The agent's review asks only about Do-All blockers that DiscoPoP recorded from STATIC analysis and whose loop holds a rewritten line.

| rewrites of | rewrites | with any Do-All blocker recorded | with one of static origin | a request would be sent |
|---|---:|---:|---:|---:|
| the pragma experiment, the 18 loops | 227 | 92 | 8 | 1 |
| the pragma experiment, the recurrence loops | 52 | 25 | 17 | 3 |
| the contrast set | 144 | 80 | 27 | 16 |
| the main comparison, the 18 loops | 176 | 58 | 6 | 1 |
| **all** | 599 | 255 | 58 | 21 |

Blockers recorded after the fast refresh, by origin, summed over the rewrites: DYNAMIC_ANALYSIS 242, STATIC_ANALYSIS 224.

Blockers asked about per request: 1 to 6, median 1, 43 in all; by loop: `s252` 1, `s3112` 2, `s3113` 3, `s314` 2, `s315` 9, `s319` 2, `s323` 1, `s331` 1.

Step 1's decision on the rewrites the review would ask about: reverted after both 16, kept after both, the same directives 5.

What the review said (no answer was given, so nothing is removed): 'no static Do-All blockers in the rewritten lines' 550; 'reviewed N static blocker(s) — none discharged' 49.

## 3 The fast refresh a second time

The verdict and the decision after the fast refresh here against step 1's record of the same rewrite — the fast refresh's own repeatability (step 1's control compared two full re-profiles).

599 rewrites in both; the same status in 599, the same status and directives in 599, the same decision (kept with the same directives, or reverted) in 599.

