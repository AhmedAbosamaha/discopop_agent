# E4 step 2 — the rewrites the model is asked about

Built by `e4_report_selection.py` from step 1's records and the dry pass; seed 20261012.

**The report: 116 rewrites** — the 58 whose decision differs after the fast refresh and 58 of the 541 whose decision is the same. **The deletion: 21 rewrites** (3 of them also among those the report is asked on). Model calls: 137.

| loop | rewrites | decision differs: all asked | decision the same | of those, drawn | deletion asked |
|---|---:|---:|---:|---:|---:|
| `s112` | 22 | 0 | 22 | 2 | 0 |
| `s121` | 19 | 0 | 19 | 2 | 0 |
| `s1213` | 11 | 0 | 11 | 2 | 0 |
| `s127` | 10 | 0 | 10 | 2 | 0 |
| `s211` | 15 | 3 | 12 | 2 | 0 |
| `s212` | 20 | 1 | 19 | 2 | 0 |
| `s241` | 34 | 8 | 26 | 2 | 0 |
| `s243` | 16 | 0 | 16 | 2 | 0 |
| `s244` | 39 | 6 | 33 | 3 | 0 |
| `s252` | 19 | 3 | 16 | 2 | 1 |
| `s254` | 10 | 0 | 10 | 1 | 0 |
| `s255` | 12 | 1 | 11 | 2 | 0 |
| `s281` | 15 | 0 | 15 | 2 | 0 |
| `s291` | 10 | 0 | 10 | 1 | 0 |
| `s292` | 10 | 0 | 10 | 1 | 0 |
| `s293` | 10 | 1 | 9 | 1 | 0 |
| `s311` | 8 | 1 | 7 | 1 | 0 |
| `s3112` | 20 | 0 | 20 | 2 | 2 |
| `s3113` | 16 | 4 | 12 | 2 | 3 |
| `s314` | 17 | 4 | 13 | 2 | 2 |
| `s315` | 30 | 0 | 30 | 3 | 9 |
| `s316` | 39 | 12 | 27 | 2 | 0 |
| `s318` | 26 | 4 | 22 | 2 | 0 |
| `s319` | 8 | 5 | 3 | 1 | 2 |
| `s321` | 13 | 0 | 13 | 2 | 0 |
| `s322` | 8 | 0 | 8 | 1 | 0 |
| `s323` | 11 | 0 | 11 | 2 | 1 |
| `s331` | 61 | 2 | 59 | 4 | 1 |
| `s341` | 70 | 3 | 67 | 5 | 0 |
| **all** | 599 | 58 | 541 | 58 | 21 |

By step 1's decision: differs: kept after both, other directives 34; differs: kept only after the fast refresh 2; differs: kept only after the full re-profile 22; same: kept after both, the same directives 44; same: reverted after both 14.

By part: e3_r 37 for the report and 1 for the deletion, e3_d 7 for the report and 3 for the deletion, e3b 43 for the report and 16 for the deletion, e1v6 29 for the report and 1 for the deletion.
