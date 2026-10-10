# E3b — descriptive read-outs (fixed in the pre-registration of 10 Oct 2026)

140 trials in five runs; no trial with a failed model call. Outcomes are the harness's; the race check (`checks/e3b_race_check`) finds every changed program of the agent's two setups clean and one of Haiku alone's racy.

## Per loop

Outcomes (FASTER · parallel, not faster · no change · BROKEN); the speed-ups of the FASTER trials (best of 6 and 12 threads, against the original), their median; model calls and cost per trial.

| loop | setup | outcomes | speed-ups of the FASTER trials | median | calls | $ |
|---|---|---|---|---:|---:|---:|
| `s314` | DiscoPoP alone | 0 · 0 · 5 · 0 | — | — | 0.0 | 0.00 |
| `s314` | DiscoPoP writes | 5 · 0 · 0 · 0 | 1.86 2.17 3.32 8.31 10.97 | 3.32× | 4.0 | 0.68 |
| `s314` | the model writes | 5 · 0 · 0 · 0 | 8.02 8.65 8.73 9.10 9.30 | 8.73× | 1.0 | 0.09 |
| `s314` | Haiku alone | 5 · 0 · 0 · 0 | 8.29 9.21 9.58 9.93 10.04 | 9.58× | 1.0 | 0.09 |
| `s316` | DiscoPoP alone | 0 · 0 · 5 · 0 | — | — | 0.0 | 0.00 |
| `s316` | DiscoPoP writes | 3 · 0 · 2 · 0 | 1.33 3.77 8.02 | 3.77× | 9.2 | 1.43 |
| `s316` | the model writes | 5 · 0 · 0 · 0 | 7.32 8.27 8.78 8.97 9.04 | 8.78× | 1.6 | 0.19 |
| `s316` | Haiku alone | 4 · 0 · 0 · 1 | 7.17 8.89 9.03 9.05 | 8.96× | 1.0 | 0.05 |
| `s3113` | DiscoPoP alone | 0 · 0 · 5 · 0 | — | — | 0.0 | 0.00 |
| `s3113` | DiscoPoP writes | 5 · 0 · 0 · 0 | 1.82 3.23 3.40 3.41 6.73 | 3.40× | 3.8 | 0.51 |
| `s3113` | the model writes | 5 · 0 · 0 · 0 | 7.37 8.42 8.70 8.74 9.02 | 8.70× | 1.6 | 0.20 |
| `s3113` | Haiku alone | 5 · 0 · 0 · 0 | 3.13 8.45 8.90 8.93 8.96 | 8.90× | 1.0 | 0.08 |
| `s315` | DiscoPoP alone | 0 · 0 · 5 · 0 | — | — | 0.0 | 0.00 |
| `s315` | DiscoPoP writes | 2 · 0 · 3 · 0 | 1.73 11.57 | 6.65× | 7.4 | 1.34 |
| `s315` | the model writes | 5 · 0 · 0 · 0 | 1.68 10.62 11.05 11.26 13.53 | 11.05× | 1.8 | 0.19 |
| `s315` | Haiku alone | 5 · 0 · 0 · 0 | 4.31 9.05 9.28 10.31 11.14 | 9.28× | 1.0 | 0.09 |
| `s318` | DiscoPoP alone | 0 · 0 · 5 · 0 | — | — | 0.0 | 0.00 |
| `s318` | DiscoPoP writes | 4 · 1 · 0 · 0 | 1.10 1.20 2.38 3.16 | 1.79× | 6.4 | 0.97 |
| `s318` | the model writes | 5 · 0 · 0 · 0 | 5.55 6.53 17.32 19.67 20.31 | 17.32× | 1.8 | 0.22 |
| `s318` | Haiku alone | 4 · 0 · 0 · 1 | 4.50 5.25 5.29 6.64 | 5.27× | 1.0 | 0.12 |
| `s319` | DiscoPoP alone | 0 · 0 · 5 · 0 | — | — | 0.0 | 0.00 |
| `s319` | DiscoPoP writes | 5 · 0 · 0 · 0 | 1.23 3.06 4.16 4.18 4.22 | 4.16× | 1.8 | 0.20 |
| `s319` | the model writes | 5 · 0 · 0 · 0 | 4.07 4.10 4.10 4.11 4.19 | 4.10× | 1.0 | 0.06 |
| `s319` | Haiku alone | 5 · 0 · 0 · 0 | 3.80 3.91 4.05 4.05 4.15 | 4.05× | 1.0 | 0.04 |
| `s311` (control) | DiscoPoP alone | 5 · 0 · 0 · 0 | 8.35 8.45 8.54 8.70 8.76 | 8.54× | 0.0 | 0.00 |
| `s311` (control) | DiscoPoP writes | 5 · 0 · 0 · 0 | 8.06 8.19 8.52 8.55 8.75 | 8.52× | 3.2 | 0.78 |
| `s311` (control) | the model writes | 5 · 0 · 0 · 0 | 5.50 8.47 8.54 8.60 8.74 | 8.54× | 1.6 | 0.26 |
| `s311` (control) | Haiku alone | 5 · 0 · 0 · 0 | 5.53 7.33 8.48 8.56 8.62 | 8.48× | 1.0 | 0.03 |

## Totals

| setup | trials | FASTER | model calls | cost |
|---|---:|---:|---:|---:|
| DiscoPoP alone | 35 | 5 | 0 | $0.00 |
| DiscoPoP writes | 35 | 29 | 179 | $29.59 |
| the model writes | 35 | 35 | 52 | $6.03 |
| Haiku alone | 35 | 33 | 35 | $2.49 |

All setups together: $38.11.

## The directives in the final programs

By setup and loop: the forms the final program carries (number of trials). Where DiscoPoP writes, every directive is DiscoPoP's; where the model writes, the model's except where noted in the trial records (`pragmas_discopop`).

| loop | DiscoPoP writes | the model writes | Haiku alone |
|---|---|---|---|
| `s314` | reduction(max) (3); parallel for (2) | reduction(max) (5) | reduction(max) (5) |
| `s316` | parallel for (3); no directive (2) | reduction(min) (5) | reduction(min) (5) |
| `s3113` | reduction(max) (4); parallel for (1) | reduction(max) (5) | reduction(max) (5) |
| `s315` | no directive (3); parallel for (2) | critical + for inside a region + parallel region (2); reduction(max) (2); parallel for (1) | reduction(max) (3); critical + parallel for (1); critical + for inside a region + parallel region (1) |
| `s318` | parallel for (4); reduction(max) (1) | critical + for inside a region + parallel region (2); reduction(max) + reduction(min) (1); parallel for + parallel region (1); reduction(max) (1) | reduction(max) (5) |
| `s319` | reduction(+) (3); parallel for (1); parallel for + reduction(+) (1) | reduction(+) (5) | reduction(+) (5) |
| `s311` | reduction(+) (5) | reduction(+) (5) | reduction(+) (5) |

## The directives DiscoPoP itself wrote on the model's rewrites (the setup in which DiscoPoP writes)

Every candidate carrying a directive of DiscoPoP's that the gate judged, by loop and form — while the model's budget lasted (a rewrite judged as it would ship) and at the end. A candidate with two forms is counted under each.

| loop | DiscoPoP's directive | the gate | candidates |
|---|---|---|---:|
| `s311` | `reduction(+:…)` | passed | 13 |
| `s3113` | `parallel for` | passed | 5 |
| `s3113` | `reduction(max:…)` | passed | 8 |
| `s314` | `parallel for` | passed | 5 |
| `s314` | `reduction(max:…)` | passed | 6 |
| `s315` | `parallel for` | passed | 5 |
| `s316` | `a task construct` | refused: correctness | 1 |
| `s316` | `lastprivate` | refused: correctness | 1 |
| `s316` | `parallel for` | passed | 10 |
| `s316` | `reduction(max:…)` | refused: correctness | 9 |
| `s318` | `parallel for` | passed | 10 |
| `s318` | `reduction(max:…)` | passed | 2 |
| `s319` | `parallel for` | passed | 9 |
| `s319` | `reduction(+:…)` | passed | 12 |

## The gate's verdicts on every candidate, by stage

**DiscoPoP writes** — 278 candidates recorded
- phase A, passed: 144
- phase A, refused: compile: 21
- phase A, refused: correctness: 14
- phase A-D40, passed: 50
- phase A-D40, refused: correctness: 11
- phase A-tier1, passed: 5
- phase B, passed: 33

**the model writes** — 61 candidates recorded
- phase A, passed: 35
- phase A, refused: clause: 2
- phase A, refused: compile: 2
- phase A, refused: correctness: 6
- phase A, refused: performance: 2
- phase A, refused: tsan: 5
- phase A-D40, passed: 2
- phase A-tier1, passed: 2
- phase B, passed: 2
- phase B, refused: clause: 3

