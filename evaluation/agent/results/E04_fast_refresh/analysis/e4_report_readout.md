# E4 step 2 — the model's report and the deletion review on the saved rewrites (`e4_report_a`)

Built by `e4_report_readout.py` from the run's records. F: the decision after the fast refresh; X: after the fast refresh with the model's report (or with the deletion); P: after the full re-profile of this pass. Decisions are the agent's own, speed aside, as in step 1.

**116 of the 116 rewrites selected for the report and 21 of the 21 selected for the deletion are read out.** Model calls counted: 136 (116 for the report, 20 for the deletion); calls that failed and were asked again or are still open: 0. Commit `501a738c9`, the DiscoPoP pass `b22cb05f336e`; 2026-10-12T22:04:02Z to 2026-10-12T23:16:46Z.

Cost of the counted calls: $8.53 in all; per call $0.007 to $0.158, median $0.061. Seconds per call: 7.3 to 199.8, median 78.9.

## 0 This pass against step 1's record of the same rewrites

134 rewrites: the decision after the fast refresh is step 1's in 134, the decision after the full re-profile in 134.


Answers that left the profile as the fast refresh made it (no row placed, nothing removed): 29; the decision judged again on that same profile differs from the first judgement in 0 — the checks' own variation, not the model's doing.

## 1 The report on the rewrites whose decision differs after the fast refresh

| after the fast refresh alone (F against P) | rewrites | repaired: X equals P | still kept only after the full re-profile | kept only with the report | kept after both, other directives | X differs from F | X equals P, `shared` clauses aside |
|---|---:|---:|---:|---:|---:|---:|---:|
| kept only after the full re-profile | 22 | 20 | 2 | 0 | 0 | 20 | 20 |
| kept only after the fast refresh | 2 | 2 | 0 | 0 | 0 | 2 | 2 |
| kept after both, other directives | 34 | 6 | 1 | 0 | 27 | 9 | 30 |
| **all** | 58 | 28 | 3 | 0 | 27 | 31 | 52 |

**Of the 22 wins the fast refresh loses, 20 are kept again with the full profile's directives.** By loop (kept again of lost): `s293` 0 of 1, `s3113` 4 of 4, `s314` 3 of 3, `s316` 9 of 9, `s318` 1 of 1, `s319` 3 of 3, `s331` 0 of 1.

- not kept again: `e1v6_r_4` `s293` repeat 5, rewrite 0 — the reply: 4 claimed, 3 resolved, 1 outside the gap (correctly skipped), 0 unplaceable, 1 loop(s) declared independent; claims [[5, 'RAW', 'a', 6, 6], [5, 'WAR', 'a', 6, 6], [5, 'RAW', 'a', 6, 8], [5, 'WAW', 'a', 8, 8]]; after it: no_pattern/None
- not kept again: `e1v6_r_4` `s331` repeat 1, rewrite 3 — the reply: 2 claimed, 2 resolved, 0 outside the gap (correctly skipped), 0 unplaceable, 1 loop(s) declared independent; claims [[7, 'RAW', 'j', 16, 17], [9, 'RAW', 'j_local', 12, 11]]; after it: exposed/pattern_broken
- kept after both before, a win lost with the report: `e3b_1` `s316` repeat 2, rewrite 10 — P [((11, 21), ('#pragma omp parallel for firstprivate(num_chunks) shared(chunk_mins)',))]; F [((11, 21), ('#pragma omp parallel for firstprivate(num_chunks)',))]; with the report no_pattern/None; claims [[16, 'RAW', 'chunk_mins', 18, 17], [24, 'RAW', 'x', 26, 25], [24, 'WAW', 'x', 26, 26]]; loops the reply declared independent [6, 11]

## 2 The report on the rewrites whose decision is the same after the fast refresh

| after the fast refresh alone (F equals P) | rewrites | intact: X equals P | broken: a win lost | broken: kept only with the report | broken: other directives | broken, `shared` clauses aside |
|---|---:|---:|---:|---:|---:|---:|
| reverted after both | 14 | 14 | 0 | 0 | 0 | 0 |
| kept after both, the same directives | 44 | 33 | 4 | 0 | 7 | 11 |
| **all** | 58 | 47 | 4 | 0 | 7 | 11 |

**Broken: 11 of 58.** For the 541 such rewrites of step 1: each loop's broken share times its number of them gives 101.9; the exact one-sided 95 % bound on the broken share is 29.4 %, that is 159 rewrites (the draw is by loop, the bound is not: an indication). Not registered, added while the run was going: the same bound from below is 11.0 %, that is 60 rewrites.

- broken: `e1v6_r_2` `s212` repeat 4, rewrite 2 — F and P: [((14, 17), ('#pragma omp parallel for shared(a_copy)',))]; with the report: no_usable_pragma/None None; claims [[10, 'RAW', 'a', 15, 12], [10, 'RAW', 'b', 16, 16]]
- broken: `e1v6_r_2` `s212` repeat 5, rewrite 3 — F and P: [((12, 15), ('#pragma omp parallel for shared(a_old)',))]; with the report: no_usable_pragma/None None; claims [[9, 'RAW', 'a', 13, 10], [9, 'RAW', 'b', 14, 14], [9, 'WAR', 'a', 10, 13], [9, 'WAR', 'b', 14, 14], [9, 'WAW', 'a_old', 10, 10], [9, 'WAW', 'b', 14, 14]]
- broken: `e1v6_r_2` `s252` repeat 3, rewrite 1 — F and P: [((9, 11), ('#pragma omp parallel for shared(s_temp)',)), ((14, 16), ('#pragma omp parallel for shared(s_temp)',))]; with the report: exposed/safe_deferred [((14, 16), ('#pragma omp parallel for shared(s_temp)',))]; claims [[7, 'WAW', 's_temp', 10, 10], [7, 'WAW', 'a', 13, 13], [7, 'WAW', 'a', 15, 15], [7, 'WAR', 's_temp', 10, 13], [7, 'WAR', 's_temp', 10, 15], [7, 'WAR', 'a', 13, 17], [7, 'WAR', 'a', 15, 17]]
- broken: `e1v6_r_3` `s281` repeat 3, rewrite 7 — F and P: [((8, 12), ('#pragma omp parallel for private(x)',)), ((14, 18), ('#pragma omp parallel for private(x)',))]; with the report: exposed/safe_deferred [((14, 18), ('#pragma omp parallel for private(x)',))]; claims [[6, 'RAW', 'a', 10, 15], [6, 'RAW', 'a', 16, 9], [6, 'RAW', 'b', 11, 9], [6, 'RAW', 'b', 17, 15]]
- broken: `e3_r_1` `s121` repeat 3, rewrite 3 — F and P: [((9, 11), ('#pragma omp parallel for shared(temp)',)), ((12, 14), ('#pragma omp parallel for shared(temp)',))]; with the report: exposed/safe_deferred [((9, 11), ('#pragma omp parallel for firstprivate(temp)',)), ((12, 14), ('#pragma omp parallel for shared(temp)',))]; claims [[8, 'RAW', 'a', 13, 10], [8, 'WAR', 'a', 13, 10], [8, 'WAW', 'a', 13, 13], [8, 'WAR', 'temp', 10, 13], [8, 'WAW', 'temp', 10, 10]]
- broken: `e3_r_2` `s243` repeat 5, rewrite 6 — F and P: [((11, 13), ('#pragma omp parallel for shared(a_old)',)), ((16, 19), ('#pragma omp parallel for',)), ((22, 24), ('#pragma omp parallel for shared(a_old)',))]; with the report: exposed/safe_deferred [((11, 13), ('#pragma omp parallel for firstprivate(a_old)',)), ((16, 19), ('#pragma omp parallel for',)), ((22, 24), ('#pragma omp parallel for firstprivate(a_old)',))]; claims [[9, 'RAW', 'a', 23, 12], [9, 'RAW', 'b', 18, 17], [9, 'WAW', 'a_old', 12, 12], [9, 'WAR', 'a_old', 23, 12]]
- broken: `e3_r_2` `s244` repeat 2, rewrite 6 — F and P: [((8, 10), ('#pragma omp parallel for shared(a_saved)',))]; with the report: exposed/safe_deferred [((8, 10), ('#pragma omp parallel for firstprivate(a_saved)',))]; claims [[7, 'RAW', 'a', 12, 9], [7, 'RAW', 'a', 14, 9], [7, 'RAW', 'b', 13, 12], [7, 'RAW', 'b', 13, 14], [7, 'RAW', 'a_saved', 9, 14], [7, 'WAR', 'a', 12, 9], [7, 'WAR', 'a', 14, 9], [7, 'WAR', 'b', 13, 12], [7, 'WAR', 'b', 13, 14], [7, 'WAR', 'a_saved', 9, 14], [7, 'WAW', 'a', 12, 12], [7, 'WAW', 'a', 14, 14], [7, 'WAW', 'b', 13, 13], [7, 'WAW', 'a_saved', 9, 9], [11, 'WAW', 'a', 14, 12]]
- broken: `e3_r_2` `s241` repeat 4, rewrite 1 — F and P: [((11, 14), ('#pragma omp parallel for shared(a_old)',))]; with the report: no_pattern/None None; claims [[7, 'RAW', 'a', 12, 9], [7, 'RAW', 'b', 13, 12]]
- broken: `e3_r_4` `s341` repeat 4, rewrite 5 — F and P: [((21, 23), ('#pragma omp parallel for firstprivate(count) shared(indices)',))]; with the report: exposed/safe_deferred [((21, 23), ('#pragma omp parallel for firstprivate(count,indices)',))]; claims [[13, 'RAW', 'count', 15, 15], [13, 'WAR', 'count', 15, 15], [13, 'WAW', 'count', 15, 15], [9, 'RAW', 'indices', 15, 22], [9, 'WAR', 'indices', 22, 15], [9, 'WAW', 'indices', 15, 15], [9, 'WAR', 'a', 25, 22]]
- broken: `e3b_1` `s314` repeat 3, rewrite 7 — F and P: [((15, 26), ('#pragma omp parallel for firstprivate(num_chunks) shared(chunk_max)',))]; with the report: no_pattern/None None; claims [[13, 'WAR', 'chunk_max', 20, 31], [21, 'RAW', 'chunk_max', 23, 22], [30, 'RAW', 'x', 32, 31]]
- broken: `e3b_2` `s3113` repeat 4, rewrite 1 — F and P: [((9, 11), ('#pragma omp parallel for shared(abs_vals)',))]; with the report: exposed/safe_deferred [((9, 11), ('#pragma omp parallel for firstprivate(abs_vals)',))]; claims [[8, 'WAR', 'abs_vals', 10, 12], [8, 'WAR', 'abs_vals', 10, 14], [8, 'WAW', 'abs_vals', 10, 10], [8, 'WAW', 'max', 12, 12], [8, 'WAW', 'max', 14, 14], [8, 'WAR', 'max', 12, 14], [8, 'WAR', 'max', 14, 14], [13, 'RAW', 'max', 14, 14], [13, 'WAW', 'max', 14, 14], [13, 'WAR', 'max', 14, 14]]

By kind (not registered): kept after both, other directives: 7 of 58 — by loop 63.4 of the 541, between 31 and 116 by the two one-sided 95 % bounds; kept only after the full re-profile: 4 of 58 — by loop 38.5 of the 541, between 13 and 82 by the two one-sided 95 % bounds.

**The balance of wins** (rewrites the full profile keeps and the other does not; not registered): after the fast refresh alone 22 of the 599; with the report, 2 of those stay lost, 1 more among the rewrites that differed only in their directives, and 4 of the 58 drawn from the 541 that agreed — by loop 38.5 of the 541.

**What stands behind the broken ones** (a reading aid: the agent places a claimed dependence by its two lines and its variable; the loop the model named it for is not carried into the dependence file, so a dependence claimed for the loop around can block the loop inside): only dependences the model claimed for another loop, with both lines inside the kept loop 10; no placed dependence with both lines inside the kept loop 2 (a rewrite with several kept loops can count in more than one).

- `e1v6_r_2` `s212` repeat 4, rewrite 2: the loop of lines 14–17 (#pragma omp parallel for shared(a_copy)) — claimed for it: []; claimed for another loop, both lines inside it: [[10, 'RAW', 'b', 16, 16]]; loops the reply declared independent: [14]
- `e1v6_r_2` `s212` repeat 5, rewrite 3: the loop of lines 12–15 (#pragma omp parallel for shared(a_old)) — claimed for it: []; claimed for another loop, both lines inside it: [[9, 'RAW', 'b', 14, 14], [9, 'WAR', 'b', 14, 14], [9, 'WAW', 'b', 14, 14]]; loops the reply declared independent: [12]
- `e1v6_r_2` `s252` repeat 3, rewrite 1: the loop of lines 9–11 (#pragma omp parallel for shared(s_temp)) — claimed for it: []; claimed for another loop, both lines inside it: [[7, 'WAW', 's_temp', 10, 10]]; loops the reply declared independent: [9, 14]
- `e1v6_r_3` `s281` repeat 3, rewrite 7: the loop of lines 8–12 (#pragma omp parallel for private(x)) — claimed for it: []; claimed for another loop, both lines inside it: [[6, 'RAW', 'b', 11, 9]]; loops the reply declared independent: [8, 14]
- `e3_r_1` `s121` repeat 3, rewrite 3: the loop of lines 9–11 (#pragma omp parallel for shared(temp)) — claimed for it: []; claimed for another loop, both lines inside it: [[8, 'WAW', 'temp', 10, 10]]; loops the reply declared independent: [9, 12]
- `e3_r_2` `s243` repeat 5, rewrite 6: the loop of lines 11–13 (#pragma omp parallel for shared(a_old)) — claimed for it: []; claimed for another loop, both lines inside it: [[9, 'WAW', 'a_old', 12, 12]]; loops the reply declared independent: [11, 16, 22]
- `e3_r_2` `s243` repeat 5, rewrite 6: the loop of lines 22–24 (#pragma omp parallel for shared(a_old)) — claimed for it: []; claimed for another loop, both lines inside it: []; loops the reply declared independent: [11, 16, 22]
- `e3_r_2` `s244` repeat 2, rewrite 6: the loop of lines 8–10 (#pragma omp parallel for shared(a_saved)) — claimed for it: []; claimed for another loop, both lines inside it: [[7, 'WAW', 'a_saved', 9, 9]]; loops the reply declared independent: [8]
- `e3_r_2` `s241` repeat 4, rewrite 1: the loop of lines 11–14 (#pragma omp parallel for shared(a_old)) — claimed for it: []; claimed for another loop, both lines inside it: [[7, 'RAW', 'b', 13, 12]]; loops the reply declared independent: [11]
- `e3_r_4` `s341` repeat 4, rewrite 5: the loop of lines 21–23 (#pragma omp parallel for firstprivate(count) shared(indices)) — claimed for it: []; claimed for another loop, both lines inside it: []; loops the reply declared independent: [21]
- `e3b_1` `s314` repeat 3, rewrite 7: the loop of lines 15–26 (#pragma omp parallel for firstprivate(num_chunks) shared(chunk_max)) — claimed for it: []; claimed for another loop, both lines inside it: [[21, 'RAW', 'chunk_max', 23, 22]]; loops the reply declared independent: [15]
- `e3b_2` `s3113` repeat 4, rewrite 1: the loop of lines 9–11 (#pragma omp parallel for shared(abs_vals)) — claimed for it: []; claimed for another loop, both lines inside it: [[8, 'WAW', 'abs_vals', 10, 10]]; loops the reply declared independent: [9]

## 3 Keeps the full re-profile does not make

On the 116 rewrites the report was asked on: after the fast refresh alone 2; with the report 0, of which 0 the report produced (reverted after the fast refresh alone) and 0 were already so; 2 of the fast refresh's own are gone with the report.

- `e3b_1` `s316` repeat 4, rewrite 8: after the fast refresh [((11, 17), ('#pragma omp parallel for firstprivate(stride) shared(temp)',))]; with the report None; claims [[10, 'RAW', 'temp', 13, 15], [10, 'RAW', 'temp', 15, 15], [10, 'WAW', 'temp', 13, 15], [10, 'WAW', 'temp', 15, 15], [9, 'RAW', 'temp', 13, 15], [9, 'RAW', 'temp', 15, 15], [9, 'WAW', 'temp', 13, 13], [9, 'WAW', 'temp', 13, 15], [9, 'WAW', 'temp', 15, 15], [9, 'WAR', 'temp', 15, 13], [9, 'WAR', 'temp', 15, 15]]
- `e3b_4` `s318` repeat 4, rewrite 1: after the fast refresh [((17, 23), ('#pragma omp parallel for firstprivate(max)',))]; with the report None; claims [[7, 'RAW', 'a', 25, 8], [9, 'RAW', 'max', 13, 12], [17, 'RAW', 'index', 21, 20]]

## 4 What the replies held

116 replies: 0 empty, 0 from which the agent's parser read nothing; 456 dependences claimed, 347 placed as rows of the dependence file (in 104 replies); 142 loops declared independent, 86 of them loops on which static analysis records a dependence; the explorer failed after a merge in 0.

Claims not placed: on lines the rewrite did not touch (left out by design) 108; variable ‹name› is unknown to this build 1.

## 5 The deletion review on the rewrites where it has something to ask

21 rewrites, a request on 20; 41 blockers asked about: 16 called real, 19 called spurious, 6 not answered (kept as real).

What the review then did: 'reviewed N static blocker(s) — none discharged' 16; 'reviewed N static blocker(s), discharged N (N dependence line(s) removed, recorded in llm_deps.json)' 3; 'no static Do-All blockers in the rewritten lines' 1; 'reviewed N static blocker(s), N judged spurious, but none matched a dependence line — nothing changed' 1.

| after the fast refresh alone (F against P) | with the deletion (X against P) | X differs from F | rewrites |
|---|---:|---:|---:|
| reverted after both | reverted after both | no | 16 |
| kept after both, the same directives | kept after both, the same directives | no | 5 |

**Keeps the full re-profile does not make, produced by the deletion: 0 of 21.** Directives DiscoPoP offers after a deletion that it did not offer after the fast refresh alone: 0.

- called spurious: `e3b_3` `s315` repeat 2, rewrite 0 — [('RAW', 'x', '12-12')]; then: reviewed 1 static blocker(s), 1 judged spurious, but none matched a dependence line — nothing changed; decision with the deletion None, after the full re-profile None
- called spurious: `e3b_3` `s315` repeat 2, rewrite 6 — [('RAW', 'index', '18-24'), ('RAW', 'chksum', '18-24'), ('RAW', 'chksum', '18-24'), ('RAW', 'x', '18-24'), ('RAW', 'index', '18-24'), ('RAW', 'x', '18-24')]; then: reviewed 6 static blocker(s), discharged 6 (2 dependence line(s) removed, recorded in llm_deps.json); decision with the deletion None, after the full re-profile None
- called spurious: `e3b_3` `s315` repeat 4, rewrite 6 — [('RAW', 'x', '15-21'), ('RAW', 'x', '15-21'), ('RAW', 'index', '15-21'), ('RAW', 'index', '15-21'), ('RAW', 'chksum', '15-21'), ('RAW', 'chksum', '15-21')]; then: reviewed 6 static blocker(s), discharged 6 (1 dependence line(s) removed, recorded in llm_deps.json); decision with the deletion None, after the full re-profile None
- called spurious: `e3b_3` `s315` repeat 4, rewrite 8 — [('RAW', 'x', '13-19'), ('RAW', 'chksum', '13-19'), ('RAW', 'chksum', '13-19'), ('RAW', 'index', '13-19'), ('RAW', 'x', '13-19'), ('RAW', 'index', '13-19')]; then: reviewed 6 static blocker(s), discharged 6 (3 dependence line(s) removed, recorded in llm_deps.json); decision with the deletion None, after the full re-profile None

## 6 The two hypotheses, read as registered

**H7** (the report reduces the decisions that differ; refuted by no reduction or by an increase in keeps the full profile does not make): repaired 28 of 58 that differ (20 of the 22 lost wins kept again); broken 11 of 58 that agree (estimate for the 541: 101.9; 95 % bound 159); keeps the full profile does not make: 2 after the fast refresh alone, 0 with the report (0 produced by it).

**H7b** (deleting produces keeps the full profile does not make, adding does not; refuted if deletion produces no more than addition): the deletion produced 0 on 21 rewrites; the report produced 0 on 116.

