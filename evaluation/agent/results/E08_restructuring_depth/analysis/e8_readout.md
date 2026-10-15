# E8 — restructuring depth: the read-out as pre-registered

Registered in THESIS_EXPERIMENTS §6 on 14 Oct 2026 before any counted trial ("Plan, E8 pre-registration"; the agent with Fix 106, "Agent, Fix 106" and "Plan, E8's second smoke"). One test, one-sided as registered, a member of the campaign's family: the bound is p × 54.

## The test

| test | hypothesis | p (one-sided) | family bound | verdict | detail |
|---|---|---:|---:|---|---|
| H8 | race-free verified FASTER more often at depth 1 than at depth 0 on the depth set (CMH stratified by loop) | 0.9048 | 1.0000 | not established | depth 1 8 of 15, depth 0 9 of 15; 1 informative loop(s); the normal approximation does not hold (Mantel-Fleiss) — read the exact p; Mantel-Haenszel odds ratio 0.375 (95 % 0.0222–6.35); exact conditional p 0.9167; unusable programs: depth 1 0 of 15, depth 0 0 of 15 |

## The depth set, per loop and arm

| loop | arm | race-free FASTER | FASTER | unusable | outcomes | speed-up 6 / 12 (median) | calls (median) | cost $ (sum) | full profiles (median) | agent s (median) |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| `s2251` | `default_v5` | 4 of 5 | 4 | 0 | FASTER 4, parallel-not-faster 1 | 2.35 / 2.34 | 3.00 | 1.65 | 2.00 | 411.10 |
| `s2251` | `depth1_v5` | 3 of 5 | 3 | 0 | FASTER 3, no-change 2 | 2.35 / 2.36 | 3.00 | 2.44 | 2.00 | 614.40 |
| `s2251` | `depth2_v5` | 2 of 5 | 2 | 0 | FASTER 2, no-change 3 | 1.01 / 1.01 | 6.00 | 5.35 | 3.00 | 901.60 |
| `s221` | `default_v5` | 0 of 5 | 0 | 0 | no-change 5 | 1.00 / 1.00 | 10.00 | 12.31 | 8.00 | 1326.50 |
| `s221` | `depth1_v5` | 0 of 5 | 0 | 0 | no-change 5 | 1.00 / 1.00 | 4.00 | 4.95 | 2.00 | 635.50 |
| `s221` | `depth2_v5` | 0 of 5 | 0 | 0 | no-change 5 | 1.00 / 1.00 | 7.00 | 9.28 | 4.00 | 938.20 |
| `s257` | `default_v5` | 5 of 5 | 5 | 0 | FASTER 5 | 4.51 / 2.21 | 1.00 | 0.91 | 1.00 | 169.10 |
| `s257` | `depth1_v5` | 5 of 5 | 5 | 0 | FASTER 5 | 4.69 / 2.89 | 4.00 | 3.72 | 2.00 | 506.50 |
| `s257` | `depth2_v5` | 5 of 5 | 5 | 0 | FASTER 5 | 4.50 / 2.43 | 8.00 | 6.78 | 3.00 | 727.10 |

## Each trial of the depth set: what each level did, what Settle kept, what shipped

Model calls and rewrites kept in Phase A per level (`{depth: n}`); Settle: changes kept by Fix 106's `[keep]`, changes dropped, repairs of the finished-program check; candidate Fix 107's signature; Fix 108: rewrites it sent back (a crash at the timing size before the last level) and whether its residual signature shows.

| loop | arm | rep | calls per level | rewrites kept per level | pragmas applied | Fix 106 kept | dropped | repairs | Fix 107 | Fix 108 sent back | Fix 108 residual | outcome | speed-up 6 / 12 | race |
|---|---|---:|---|---|---:|---:|---:|---:|---|---:|---|---|---|---|
| `s221` | `default_v5` | 1 | {0: 12} | {} | 0 | 0 | 0 | 0 | no | 0 | no | no-change | 0.998 / 1.004 | clean |
| `s221` | `default_v5` | 2 | {0: 10} | {} | 0 | 0 | 0 | 0 | no | 0 | no | no-change | 0.966 / 0.997 | clean |
| `s221` | `default_v5` | 3 | {0: 11} | {} | 0 | 0 | 0 | 0 | no | 0 | no | no-change | 1.005 / 1.008 | clean |
| `s221` | `default_v5` | 4 | {0: 10} | {} | 0 | 0 | 0 | 0 | no | 0 | no | no-change | 0.988 / 0.988 | clean |
| `s221` | `default_v5` | 5 | {0: 9} | {} | 0 | 0 | 0 | 0 | no | 0 | no | no-change | 0.996 / 0.996 | clean |
| `s221` | `depth1_v5` | 1 | {0: 1, 1: 7} | {0: 1, 1: 1} | 2 | 0 | 4 | 2 | no | 0 | no | no-change | 1.001 / 0.999 | clean |
| `s221` | `depth1_v5` | 2 | {0: 1, 1: 3} | {0: 1, 1: 1} | 1 | 0 | 3 | 1 | no | 0 | no | no-change | 0.994 / 0.989 | clean |
| `s221` | `depth1_v5` | 3 | {0: 1, 1: 7} | {0: 1, 1: 1} | 2 | 0 | 4 | 2 | no | 0 | no | no-change | 0.983 / 0.981 | clean |
| `s221` | `depth1_v5` | 4 | {0: 1, 1: 3} | {0: 1, 1: 1} | 2 | 0 | 4 | 2 | no | 0 | no | no-change | 0.997 / 0.999 | clean |
| `s221` | `depth1_v5` | 5 | {0: 1, 1: 3} | {0: 1, 1: 1} | 2 | 0 | 4 | 2 | no | 0 | no | no-change | 1.0 / 0.999 | clean |
| `s221` | `depth2_v5` | 1 | {0: 1, 1: 3, 2: 2} | {0: 1, 1: 1, 2: 1} | 2 | 0 | 5 | 2 | no | 0 | no | no-change | 0.993 / 1.006 | clean |
| `s221` | `depth2_v5` | 2 | {0: 1, 1: 3, 2: 8} | {0: 1, 1: 1, 2: 2} | 3 | 4 | 7 | 3 | no | 0 | no | no-change | 0.997 / 0.992 | clean |
| `s221` | `depth2_v5` | 3 | {0: 1, 1: 8, 2: 5} | {0: 1, 1: 1, 2: 2} | 3 | 3 | 7 | 3 | no | 0 | no | no-change | 0.99 / 1.0 | clean |
| `s221` | `depth2_v5` | 4 | {0: 1, 1: 2, 2: 3} | {0: 1, 1: 1, 2: 1} | 1 | 0 | 4 | 1 | no | 0 | no | no-change | 0.997 / 0.994 | clean |
| `s221` | `depth2_v5` | 5 | {0: 1, 1: 4, 2: 2} | {0: 1, 1: 1, 2: 1} | 1 | 0 | 4 | 1 | no | 0 | no | no-change | 1.001 / 0.999 | clean |
| `s2251` | `default_v5` | 1 | {0: 3} | {0: 1} | 2 | 0 | 0 | 0 | no | 0 | no | FASTER | 2.351 / 2.344 | clean |
| `s2251` | `default_v5` | 2 | {0: 3} | {0: 1} | 2 | 0 | 0 | 0 | no | 0 | no | FASTER | 2.275 / 2.253 | clean |
| `s2251` | `default_v5` | 3 | {0: 2} | {0: 1} | 1 | 0 | 0 | 0 | no | 0 | no | parallel-not-faster | 1.026 / 1.029 | clean |
| `s2251` | `default_v5` | 4 | {0: 3} | {0: 1} | 2 | 0 | 0 | 0 | no | 0 | no | FASTER | 2.401 / 2.405 | clean |
| `s2251` | `default_v5` | 5 | {0: 3} | {0: 1} | 2 | 0 | 0 | 0 | no | 0 | no | FASTER | 2.392 / 2.348 | clean |
| `s2251` | `depth1_v5` | 1 | {0: 1, 1: 1} | {0: 1, 1: 1} | 2 | 1 | 0 | 0 | no | 0 | no | FASTER | 2.953 / 2.915 | clean |
| `s2251` | `depth1_v5` | 2 | {0: 1, 1: 4} | {0: 1, 1: 2} | 2 | 0 | 0 | 0 | no | 0 | no | FASTER | 2.575 / 2.763 | clean |
| `s2251` | `depth1_v5` | 3 | {0: 3, 1: 1} | {0: 1, 1: 1} | 3 | 3 | 5 | 3 | no | 1 | no | no-change | 1.002 / 1.0 | clean |
| `s2251` | `depth1_v5` | 4 | {0: 2, 1: 1} | {0: 1, 1: 1} | 2 | 0 | 0 | 0 | no | 0 | no | FASTER | 2.346 / 2.357 | clean |
| `s2251` | `depth1_v5` | 5 | {0: 2, 1: 1} | {0: 1, 1: 1} | 3 | 3 | 5 | 3 | no | 0 | no | no-change | 1.003 / 0.999 | clean |
| `s2251` | `depth2_v5` | 1 | {0: 2, 1: 1, 2: 3} | {0: 1, 1: 1, 2: 1} | 2 | 4 | 5 | 2 | no | 0 | no | no-change | 0.999 / 1.002 | clean |
| `s2251` | `depth2_v5` | 2 | {0: 3, 1: 1, 2: 2} | {0: 1, 1: 1, 2: 1} | 4 | 7 | 7 | 4 | no | 1 | no | no-change | 1.008 / 1.008 | clean |
| `s2251` | `depth2_v5` | 3 | {0: 2, 1: 2, 2: 2} | {0: 1, 1: 1, 2: 1} | 2 | 0 | 0 | 0 | no | 0 | no | FASTER | 1.292 / 1.287 | clean |
| `s2251` | `depth2_v5` | 4 | {0: 1, 1: 1, 2: 3} | {0: 1, 1: 1, 2: 1} | 2 | 2 | 0 | 0 | no | 0 | no | FASTER | 1.485 / 1.459 | clean |
| `s2251` | `depth2_v5` | 5 | {0: 2, 1: 3, 2: 3} | {0: 1, 1: 1, 2: 1} | 2 | 1 | 5 | 2 | no | 0 | no | no-change | 1.001 / 1.001 | clean |
| `s257` | `default_v5` | 1 | {0: 1} | {0: 1} | 1 | 0 | 0 | 0 | no | 0 | no | FASTER | 4.541 / 2.131 | clean |
| `s257` | `default_v5` | 2 | {0: 2} | {0: 1} | 2 | 0 | 0 | 0 | no | 0 | no | FASTER | 3.134 / 2.072 | clean |
| `s257` | `default_v5` | 3 | {0: 2} | {0: 1} | 1 | 0 | 0 | 0 | no | 0 | no | FASTER | 4.419 / 2.484 | clean |
| `s257` | `default_v5` | 4 | {0: 1} | {0: 1} | 1 | 0 | 0 | 0 | no | 0 | no | FASTER | 4.508 / 2.205 | clean |
| `s257` | `default_v5` | 5 | {0: 1} | {0: 1} | 1 | 0 | 0 | 0 | no | 0 | no | FASTER | 4.582 / 2.355 | clean |
| `s257` | `depth1_v5` | 1 | {0: 1, 1: 3} | {0: 1, 1: 1} | 1 | 1 | 0 | 0 | no | 0 | no | FASTER | 4.542 / 2.283 | clean |
| `s257` | `depth1_v5` | 2 | {0: 1, 1: 3} | {0: 1, 1: 1} | 2 | 1 | 0 | 0 | no | 0 | yes | FASTER | 4.101 / 2.892 | clean |
| `s257` | `depth1_v5` | 3 | {0: 1, 1: 2} | {0: 1, 1: 1} | 1 | 1 | 0 | 0 | no | 0 | no | FASTER | 4.691 / 2.112 | clean |
| `s257` | `depth1_v5` | 4 | {0: 1, 1: 3} | {0: 1, 1: 1} | 3 | 1 | 0 | 0 | no | 0 | no | FASTER | 4.932 / 3.758 | clean |
| `s257` | `depth1_v5` | 5 | {0: 3, 1: 1} | {0: 1, 1: 1} | 1 | 1 | 0 | 0 | no | 0 | no | FASTER | 7.547 / 7.464 | clean |
| `s257` | `depth2_v5` | 1 | {0: 1, 1: 4, 2: 3} | {0: 1, 1: 1, 2: 1} | 1 | 0 | 0 | 0 | no | 0 | no | FASTER | 4.463 / 2.108 | clean |
| `s257` | `depth2_v5` | 2 | {0: 1, 1: 6, 2: 2} | {0: 1, 1: 1, 2: 1} | 1 | 0 | 0 | 0 | no | 0 | no | FASTER | 4.302 / 2.321 | clean |
| `s257` | `depth2_v5` | 3 | {0: 1, 1: 3, 2: 2} | {0: 1, 1: 1, 2: 1} | 2 | 2 | 0 | 0 | no | 0 | no | FASTER | 6.455 / 7.335 | clean |
| `s257` | `depth2_v5` | 4 | {0: 2, 1: 3, 2: 3} | {0: 1, 1: 1, 2: 1} | 1 | 2 | 0 | 0 | no | 0 | no | FASTER | 7.567 / 6.883 | clean |
| `s257` | `depth2_v5` | 5 | {0: 1, 1: 2, 2: 1} | {0: 1, 1: 1, 2: 1} | 1 | 0 | 0 | 0 | no | 0 | no | FASTER | 4.499 / 2.433 | clean |

## The speed question at depth 0 (the depth set): the judge's verdicts per trial

- `s221` rep 1: {'not_faster': 4, 'pattern_broken': 1}; exposure {'exposed': 5, 'no_pattern': 3}; outcome no-change
- `s221` rep 2: {'not_faster': 6}; exposure {'exposed': 6, 'no_pattern': 1}; outcome no-change
- `s221` rep 3: {'not_faster': 5}; exposure {'exposed': 5, 'no_pattern': 1}; outcome no-change
- `s221` rep 4: {'not_faster': 7, 'pattern_broken': 1}; exposure {'exposed': 8}; outcome no-change
- `s221` rep 5: {'not_faster': 8}; exposure {'exposed': 8}; outcome no-change
- `s2251` rep 1: {'not_faster': 1, 'ok': 1}; exposure {'exposed': 2}; outcome FASTER
- `s2251` rep 2: {'not_faster': 1, 'ok': 1}; exposure {'exposed': 2}; outcome FASTER
- `s2251` rep 3: {'ok': 1}; exposure {'exposed': 1}; outcome parallel-not-faster
- `s2251` rep 4: {'not_faster': 1, 'ok': 1}; exposure {'exposed': 2}; outcome FASTER
- `s2251` rep 5: {'not_faster': 1, 'ok': 1}; exposure {'exposed': 2}; outcome FASTER
- `s257` rep 1: {'ok': 1}; exposure {'exposed': 1}; outcome FASTER
- `s257` rep 2: {'ok': 1}; exposure {'exposed': 1}; outcome FASTER
- `s257` rep 3: {'ok': 1}; exposure {'exposed': 1}; outcome FASTER
- `s257` rep 4: {'ok': 1}; exposure {'exposed': 1}; outcome FASTER
- `s257` rep 5: {'ok': 1}; exposure {'exposed': 1}; outcome FASTER

## Depth 2 against depth 1 on the depth set ("a third adds little") — no test

| loop | depth 1 race-free FASTER | depth 2 race-free FASTER | depth 1 unusable | depth 2 unusable |
|---|---:|---:|---:|---:|
| `s2251` | 3 of 5 | 2 of 5 | 0 | 0 |
| `s221` | 0 of 5 | 0 of 5 | 0 | 0 |
| `s257` | 5 of 5 | 5 of 5 | 0 | 0 |

## The 18 loops — depth 1 and 2 beside E3's depth 0 (no test)

| loop | depth 0 (E3) race-free FASTER | depth 1 | depth 2 | unusable 0 / 1 / 2 |
|---|---:|---:|---:|---|
| `tsvc_c2/s112` | 5 of 5 | 1 of 3 | 1 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s121` | 5 of 5 | 0 of 3 | 1 of 3 | 0 / 1 / 0 |
| `tsvc_c2/s1213` | 5 of 5 | 3 of 3 | 1 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s127` | 5 of 5 | 3 of 3 | 1 of 3 | 0 / 0 / 1 |
| `tsvc_c2/s211` | 4 of 5 | 1 of 3 | 2 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s212` | 5 of 5 | 3 of 3 | 1 of 3 | 0 / 0 / 0 |
| `tsvc_c3/s241` | 4 of 5 | 1 of 3 | 0 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s243` | 5 of 5 | 1 of 3 | 2 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s244` | 3 of 5 | 2 of 3 | 3 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s252` | 3 of 5 | 3 of 3 | 3 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s254` | 5 of 5 | 3 of 3 | 2 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s255` | 5 of 5 | 3 of 3 | 3 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s281` | 5 of 5 | 1 of 3 | 2 of 3 | 0 / 1 / 0 |
| `tsvc_c2/s291` | 5 of 5 | 3 of 3 | 1 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s292` | 5 of 5 | 3 of 3 | 2 of 3 | 0 / 0 / 0 |
| `tsvc_c2/s293` | 5 of 5 | 3 of 3 | 3 of 3 | 0 / 0 / 0 |
| `tsvc_c3/s331` | 1 of 5 | 0 of 3 | 0 of 3 | 0 / 0 / 0 |
| `tsvc_c4/s341` | 0 of 5 | 0 of 3 | 0 of 3 | 0 / 0 / 0 |

| arm | trials | race-free FASTER | unusable | calls (median) | cost $ (sum) | full profiles (median) | agent s (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `default_v5` (E3) | 90 | 75 of 90 | 0 | 2.00 | 52.08 | 1.00 | 284.50 |
| `depth1_v5` | 54 | 34 of 54 | 2 | 4.00 | 47.03 | 2.00 | 555.05 |
| `depth2_v5` | 54 | 28 of 54 | 1 | 5.00 | 51.09 | 3.00 | 709.45 |

## Every unusable program

- tsvc_c2/s127 depth2_v5 rep3: BROKEN
- tsvc_c2/s121 depth1_v5 rep2: BROKEN
- tsvc_c2/s281 depth1_v5 rep1: BROKEN

## Trials without a verdict (left out of every rate)

- none

## Fix 106, candidate Fix 107 and Fix 108 in E8's trials

- trials in which Fix 106 kept a rewrite (`[keep]`): 65 of 153 (133 rewrites)
- trials with candidate Fix 107's signature: 0 of 153; its pattern after a repair of the finished-program check, to be read by hand: `s221` depth1_v5 rep 1, `s221` depth1_v5 rep 2, `s221` depth1_v5 rep 3, `s221` depth1_v5 rep 4, `s221` depth1_v5 rep 5, `s221` depth2_v5 rep 1, `s221` depth2_v5 rep 2, `s221` depth2_v5 rep 3, `s221` depth2_v5 rep 4, `s221` depth2_v5 rep 5, `s2251` depth1_v5 rep 3, `s2251` depth1_v5 rep 5, `s2251` depth2_v5 rep 1, `s2251` depth2_v5 rep 2, `s2251` depth2_v5 rep 5, `s112` depth1_v5 rep 1, `s112` depth1_v5 rep 3, `s112` depth2_v5 rep 1, `s112` depth2_v5 rep 2, `s127` depth2_v5 rep 1, `s212` depth2_v5 rep 1, `s212` depth2_v5 rep 2, `s254` depth2_v5 rep 2, `s341` depth1_v5 rep 1, `s341` depth1_v5 rep 2, `s341` depth1_v5 rep 3, `s341` depth2_v5 rep 1, `s341` depth2_v5 rep 2, `s341` depth2_v5 rep 3, `s121` depth1_v5 rep 3, `s121` depth2_v5 rep 1, `s121` depth2_v5 rep 3, `s1213` depth2_v5 rep 1, `s1213` depth2_v5 rep 2, `s244` depth1_v5 rep 3, `s281` depth1_v5 rep 2, `s281` depth2_v5 rep 1, `s211` depth1_v5 rep 1, `s211` depth1_v5 rep 3, `s211` depth2_v5 rep 1, `s243` depth1_v5 rep 1, `s243` depth2_v5 rep 2, `s291` depth2_v5 rep 1, `s291` depth2_v5 rep 3, `s292` depth2_v5 rep 3, `s241` depth1_v5 rep 3, `s241` depth2_v5 rep 1, `s241` depth2_v5 rep 2, `s241` depth2_v5 rep 3, `s331` depth1_v5 rep 1, `s331` depth1_v5 rep 2, `s331` depth2_v5 rep 1, `s331` depth2_v5 rep 2, `s331` depth2_v5 rep 3
- trials in which Fix 108 sent a rewrite back (it crashed at the timing size before the last level): 12 of 153 (13 rewrites); models told of a crash at the timing size, at any level: 18 trials
- trials with Fix 108's residual signature (a failure named as the program before the rewrite's, a pragma dropped because the program before it crashed, the noise measurement crashing): 3 of 153: `s257` depth1_v5 rep 2, `s127` depth1_v5 rep 1, `s291` depth1_v5 rep 2
- trials in which Settle's orphan rule still dropped a rewrite: 54; a rewrite that no longer applied: 0

## Read by hand (registered)

The form the shipped program reached on the depth set — the original, step 1 or step 2 — is read program by program against the references (`e8_c5_refs`, `e8_c5_steps`): the changed programs are the trials above whose outcome is not `no-change`, each in its trial folder under `final/`.
