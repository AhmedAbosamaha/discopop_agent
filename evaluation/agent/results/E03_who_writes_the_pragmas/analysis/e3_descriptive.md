# E3 — descriptive read-outs (fixed in the pre-registration of 9 Oct 2026)

315 trials in nine runs; no trial with a failed model call. Outcomes are the harness's; every changed program of the two setups is race-clean (`checks/e3_race_check`), so FASTER here is race-free FASTER.

## Per loop

FASTER · parallel but not faster · no change; the median speed-up of the FASTER trials (best of 6 and 12 threads, against the original); model calls and cost per trial; kept pragmas by author (DiscoPoP + the model).

| class | loop | DiscoPoP writes: outcomes | speed-up | calls | $ | pragmas | the model writes: outcomes | speed-up | calls | $ | pragmas |
|---|---|---|---:|---:|---:|---|---|---:|---:|---:|---|
| R | `s112` | 5 · 0 · 0 | 1.39× | 3.2 | 0.46 | 10 + 0 | 4 · 1 · 0 | 1.30× | 3.6 | 0.61 | 0 + 20 |
| R | `s121` | 5 · 0 · 0 | 1.44× | 3.4 | 0.50 | 10 + 0 | 5 · 0 · 0 | 1.38× | 8.4 | 1.23 | 0 + 18 |
| R | `s1213` | 5 · 0 · 0 | 2.52× | 1.4 | 0.29 | 10 + 0 | 5 · 0 · 0 | 2.62× | 2.8 | 0.44 | 2 + 10 |
| R | `s127` | 5 · 0 · 0 | 3.89× | 1.0 | 0.04 | 5 + 0 | 5 · 0 · 0 | 3.75× | 1.0 | 0.06 | 0 + 5 |
| R | `s211` | 4 · 1 · 0 | 1.14× | 2.0 | 0.31 | 6 + 0 | 5 · 0 · 0 | 2.00× | 3.8 | 0.58 | 3 + 11 |
| R | `s212` | 5 · 0 · 0 | 1.72× | 2.4 | 0.36 | 12 + 0 | 5 · 0 · 0 | 2.29× | 3.6 | 0.67 | 1 + 13 |
| R | `s241` | 4 · 1 · 0 | 1.32× | 5.0 | 0.79 | 13 + 0 | 3 · 0 · 2 | 1.44× | 3.6 | 0.53 | 0 + 9 |
| R | `s243` | 5 · 0 · 0 | 1.37× | 2.2 | 0.35 | 8 + 0 | 4 · 1 · 0 | 1.31× | 3.0 | 0.44 | 1 + 6 |
| R | `s244` | 3 · 0 · 2 | 3.70× | 9.6 | 2.66 | 6 + 0 | 4 · 0 · 1 | 4.36× | 6.8 | 1.86 | 1 + 4 |
| R | `s252` | 3 · 2 · 0 | 3.41× | 2.2 | 0.26 | 5 + 0 | 5 · 0 · 0 | 3.62× | 1.0 | 0.07 | 0 + 5 |
| R | `s254` | 5 · 0 · 0 | 3.40× | 1.0 | 0.05 | 5 + 0 | 5 · 0 · 0 | 3.17× | 1.2 | 0.08 | 0 + 5 |
| R | `s255` | 5 · 0 · 0 | 2.48× | 1.6 | 0.19 | 5 + 0 | 5 · 0 · 0 | 2.68× | 1.0 | 0.07 | 0 + 5 |
| R | `s281` | 5 · 0 · 0 | 3.27× | 3.0 | 0.43 | 10 + 0 | 5 · 0 · 0 | 2.78× | 1.8 | 0.28 | 0 + 10 |
| R | `s291` | 5 · 0 · 0 | 3.49× | 1.0 | 0.04 | 5 + 0 | 5 · 0 · 0 | 3.48× | 1.2 | 0.06 | 0 + 5 |
| R | `s292` | 5 · 0 · 0 | 2.97× | 1.0 | 0.05 | 5 + 0 | 5 · 0 · 0 | 2.91× | 1.0 | 0.05 | 0 + 5 |
| R | `s293` | 5 · 0 · 0 | 2.89× | 1.0 | 0.06 | 5 + 0 | 5 · 0 · 0 | 2.90× | 1.0 | 0.07 | 0 + 5 |
| R | `s331` | 1 · 1 · 3 | 1.22× | 11.2 | 1.85 | 2 + 0 | 5 · 0 · 0 | 4.42× | 1.6 | 0.13 | 0 + 11 |
| R | `s341` | 1 · 0 · 4 | 2.19× | 11.8 | 1.66 | 1 + 0 | 1 · 0 · 4 | 2.20× | 12.4 | 1.93 | 0 + 1 |
| D | `s321` | 0 · 0 · 3 | — | 12.3 | 2.70 | 0 + 0 | 0 · 0 · 3 | — | 12.3 | 4.59 | 0 + 0 |
| D | `s322` | 0 · 0 · 3 | — | 11.0 | 2.61 | 0 + 0 | 0 · 0 · 3 | — | 12.7 | 4.16 | 0 + 0 |
| D | `s323` | 0 · 0 · 3 | — | 10.7 | 2.63 | 0 + 0 | 0 · 0 · 3 | — | 13.7 | 3.54 | 0 + 0 |
| D | `s3112` | 0 · 0 · 3 | — | 11.0 | 2.23 | 0 + 0 | 0 · 0 · 3 | — | 11.0 | 2.53 | 0 + 0 |
| A | `s000` | 1 · 0 · 0 | 127.70× | 6.0 | 1.44 | 1 + 0 | 1 · 0 · 0 | 3.49× | 1.0 | 0.07 | 0 + 1 |
| A | `vpvtv` | 1 · 0 · 0 | 3.59× | 3.0 | 0.68 | 1 + 0 | 1 · 0 · 0 | 3.63× | 1.0 | 0.11 | 0 + 1 |
| A | `s313` | 1 · 0 · 0 | 4.62× | 1.0 | 0.10 | 1 + 0 | 1 · 0 · 0 | 4.63× | 1.0 | 0.10 | 1 + 0 |

## Per class

| class | setup | trials | FASTER | parallel, not faster | no change | model calls | cost | per trial | per FASTER trial | kept rewrites | kept pragmas: DiscoPoP's | the model's |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R | DiscoPoP writes | 90 | 76 | 5 | 9 | 320 | $51.75 | $0.57 | $0.68 | 81 | 123 | 0 |
| R | the model writes | 90 | 81 | 2 | 7 | 294 | $45.80 | $0.51 | $0.57 | 83 | 8 | 148 |
| D | DiscoPoP writes | 12 | 0 | 0 | 12 | 135 | $30.53 | $2.54 | — | 0 | 0 | 0 |
| D | the model writes | 12 | 0 | 0 | 12 | 149 | $44.45 | $3.70 | — | 0 | 0 | 0 |
| A | DiscoPoP writes | 3 | 3 | 0 | 0 | 10 | $2.21 | $0.74 | $0.74 | 1 | 3 | 0 |
| A | the model writes | 3 | 3 | 0 | 0 | 3 | $0.28 | $0.09 | $0.09 | 2 | 1 | 2 |
| all | DiscoPoP writes | 105 | 79 | 5 | 21 | 465 | $84.49 | $0.80 | $1.07 | 82 | 126 | 0 |
| all | the model writes | 105 | 84 | 2 | 19 | 446 | $90.54 | $0.86 | $1.08 | 85 | 9 | 150 |

Both setups together: $175.03.

## The gate's verdicts on every candidate, by stage

Phase A = a rewrite the model proposed; A-D40 = a rewrite without a pragma judged as it would ship (DiscoPoP's pragma added, then the same checks); A-tier1 = DiscoPoP's own pragma for a loop it already finds parallel, sent through the safety checks before the model is asked; B = DiscoPoP's own pragma for a loop that carries none.

**class R, DiscoPoP writes** — 816 candidates recorded
- phase A, without a pragma, passed: 227
- phase A, without a pragma, refused: compile: 67
- phase A, without a pragma, refused: correctness: 26
- phase A-D40, without a pragma, passed: 353
- phase A-D40, without a pragma, refused: correctness: 3
- phase A-D40, without a pragma, refused: schedules: 3
- phase A-D40, without a pragma, refused: tsan: 10
- phase B, without a pragma, passed: 123
- phase B, without a pragma, refused: tsan: 4
- after phase A (rewrites without a pragma): d40: not_faster 94, d40: ok 81, d40: pattern_broken 16, exposure: exposed 191, exposure: no_pattern 36

**class R, the model writes** — 303 candidates recorded
- phase A, with the model's pragma, passed: 85
- phase A, with the model's pragma, refused: clause: 2
- phase A, with the model's pragma, refused: compile: 53
- phase A, with the model's pragma, refused: correctness: 18
- phase A, with the model's pragma, refused: dependences: 1
- phase A, with the model's pragma, refused: openmp_compile: 17
- phase A, with the model's pragma, refused: performance: 85
- phase A, with the model's pragma, refused: schedules: 4
- phase A, with the model's pragma, refused: tsan: 29
- phase B, without a pragma, passed: 9

**class D, DiscoPoP writes** — 179 candidates recorded
- phase A, without a pragma, passed: 52
- phase A, without a pragma, refused: compile: 27
- phase A, without a pragma, refused: correctness: 56
- phase A-D40, without a pragma, passed: 43
- phase A-D40, without a pragma, refused: correctness: 1
- after phase A (rewrites without a pragma): d40: not_faster 29, d40: pattern_broken 1, exposure: exposed 30, exposure: no_pattern 22

**class D, the model writes** — 149 candidates recorded
- phase A, with the model's pragma, refused: clause: 1
- phase A, with the model's pragma, refused: compile: 28
- phase A, with the model's pragma, refused: correctness: 65
- phase A, with the model's pragma, refused: openmp_compile: 13
- phase A, with the model's pragma, refused: performance: 12
- phase A, with the model's pragma, refused: schedules: 1
- phase A, with the model's pragma, refused: tsan: 24
- phase A, without a pragma, passed: 5
- after phase A (rewrites without a pragma): exposure: no_pattern 5

**class A, DiscoPoP writes** — 26 candidates recorded
- phase A, without a pragma, passed: 6
- phase A, without a pragma, refused: compile: 1
- phase A, without a pragma, refused: correctness: 3
- phase A-D40, without a pragma, passed: 11
- phase A-tier1, without a pragma, passed: 1
- phase B, without a pragma, passed: 4
- after phase A (rewrites without a pragma): d40: not_faster 1, d40: ok 3, d40: pattern_broken 1, exposure: exposed 5, exposure: no_pattern 1

**class A, the model writes** — 3 candidates recorded
- phase A, with the model's pragma, passed: 3

## Where the model may write and DiscoPoP added a pragma of its own

| loop | trial | DiscoPoP's | the model's | outcome |
|---|---|---:|---:|---|
| `s313` | rep1 | 1 | 0 | FASTER |
| `s1213` | rep1 | 1 | 2 | FASTER |
| `s1213` | rep3 | 1 | 2 | FASTER |
| `s211` | rep3 | 1 | 2 | FASTER |
| `s211` | rep4 | 1 | 2 | FASTER |
| `s211` | rep5 | 1 | 2 | FASTER |
| `s212` | rep2 | 1 | 1 | FASTER |
| `s243` | rep3 | 1 | 1 | FASTER |
| `s244` | rep1 | 1 | 1 | FASTER |

A pragma of DiscoPoP's that passed the checks in phase B and is not in the final program (dropped after the checks — the agent's log gives the reason): `s244` rep4 (1 passed, 0 in the final program).

## The floor: which program was shipped

The floor decides last (D32): the agent's program, or DiscoPoP's own — what the DiscoPoP-alone setup delivers — if that is faster. `original`: DiscoPoP alone keeps nothing on this loop, so there is nothing to fall back to.

| setup | agent | discopop | original | same |
|---|---:|---:|---:|---:|
| DiscoPoP writes | 1 | 2 | 102 | 0 |
| the model writes | 1 | 1 | 102 | 1 |

| class A loop | setup | shipped | kept rewrites | DiscoPoP's pragmas | the model's |
|---|---|---|---:|---:|---:|
| `s000` | DiscoPoP writes | agent | 1 | 1 | 0 |
| `s000` | the model writes | same | 1 | 0 | 1 |
| `s313` | DiscoPoP writes | discopop | 0 | 1 | 0 |
| `s313` | the model writes | discopop | 0 | 1 | 0 |
| `vpvtv` | DiscoPoP writes | discopop | 0 | 1 | 0 |
| `vpvtv` | the model writes | agent | 1 | 0 | 1 |
