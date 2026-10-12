# E4 step 2 — the saved replies placed again (`e4_report_a_placement`), no model

Built by `e4_report_placement_readout.py`. The replies recorded by `e4_report_a` are placed again without a model: as the agent places them (a control, which should give `e4_report_a`'s decisions again) and with one rule changed — a claimed dependence is left out where both of its lines lie inside a loop the same reply declares independent. **The rule is a what-if chosen after the result was seen; it is not the agent as built.**

Commit `87179936b`, the DiscoPoP pass `b22cb05f336e`; 2026-10-12T23:24:41Z to 2026-10-12T23:43:28Z; model calls: 0.

|  | as recorded (`e4_report_a`, the model's calls) | placed again as built (the control) | placed again with the rule (the what-if) |
|---|---:|---:|---:|
| rewrites read out | 116 | 116 | 116 |
| rows placed in the dependence file | 347 | 347 | 272 |
| claims left out by the rule (in how many replies) | 0 (0) | 0 (0) | 114 (61) |
| of the rewrites that differ after the fast refresh: repaired | 28 of 58 | 28 of 58 | 21 of 58 |
| — of the wins the fast refresh loses: kept again with the full profile's directives | 20 of 22 | 20 of 22 | 17 of 22 |
| — of the keeps the full profile does not make: still kept | 0 of 2 | 0 of 2 | 1 of 2 |
| — kept after both before, a win lost with the report | 1 | 1 | 0 |
| of the rewrites that agree after the fast refresh: broken | 11 of 58 | 11 of 58 | 7 of 58 |
| — a win lost | 4 | 4 | 0 |
| — kept with other directives | 7 | 7 | 7 |
| broken among the 541, each loop's share times its number | 101.9 | 101.9 | 62.4 |
| — wins lost among the 541, the same way | 38.5 | 38.5 | 0.0 |
| keeps the full profile does not make, produced by the report | 0 | 0 | 0 |

## The control

116 rewrites in all three. Placed again as built, the decision with the report is `e4_report_a`'s in 116; the decision after the fast refresh in 116, after the full re-profile in 116.


## What the rule changes, rewrite by rewrite

The decision with the rule differs from the decision placed again as built in 16 of 116 rewrites.

| drawn as | as built, against the full re-profile | with the rule, against the full re-profile | rewrites |
|---|---:|---:|---:|
| same | kept only after the full re-profile | kept after both, the same directives | 3 |
| differs | kept after both, the same directives | kept after both, other directives | 3 |
| differs | kept after both, the same directives | kept only after the full re-profile | 3 |
| differs | kept after both, other directives | kept after both, other directives | 2 |
| same | kept after both, other directives | kept after both, the same directives | 1 |
| same | kept after both, other directives | kept after both, other directives | 1 |
| same | kept only after the full re-profile | kept after both, other directives | 1 |
| differs | kept only after the full re-profile | kept after both, other directives | 1 |
| differs | reverted after both | kept only with the report | 1 |

- `e1v6_r_2` `s212` repeat 3, rewrite 0 (differs): the full re-profile [((8, 10), ('#pragma omp parallel for shared(a_next)',)), ((12, 15), ('#pragma omp parallel for shared(a_next)',))]; as built [((8, 10), ('#pragma omp parallel for',))]; with the rule [((8, 10), ('#pragma omp parallel for',)), ((12, 15), ('#pragma omp parallel for',))]; left out [[5, 'RAW', 'b', 14, 14], [5, 'WAW', 'a', 13, 13], [5, 'WAW', 'b', 14, 14]]
- `e1v6_r_2` `s212` repeat 4, rewrite 2 (same): the full re-profile [((14, 17), ('#pragma omp parallel for shared(a_copy)',))]; as built None; with the rule [((14, 17), ('#pragma omp parallel for shared(a_copy)',))]; left out [[10, 'RAW', 'b', 16, 16]]
- `e1v6_r_2` `s212` repeat 5, rewrite 3 (same): the full re-profile [((12, 15), ('#pragma omp parallel for shared(a_old)',))]; as built None; with the rule [((12, 15), ('#pragma omp parallel for shared(a_old)',))]; left out [[9, 'RAW', 'b', 14, 14], [9, 'WAR', 'b', 14, 14], [9, 'WAW', 'b', 14, 14]]
- `e1v6_r_2` `s241` repeat 1, rewrite 2 (differs): the full re-profile [((7, 9), ('#pragma omp parallel for shared(a_old)',)), ((10, 13), ('#pragma omp parallel for shared(a_old)',))]; as built [((7, 9), ('#pragma omp parallel for',))]; with the rule [((7, 9), ('#pragma omp parallel for',)), ((10, 13), ('#pragma omp parallel for',))]; left out [[5, 'RAW', 'b', 12, 11], [5, 'WAR', 'b', 12, 11], [5, 'WAW', 'a', 11, 11], [5, 'WAW', 'b', 12, 12]]
- `e1v6_r_3` `s281` repeat 3, rewrite 7 (same): the full re-profile [((8, 12), ('#pragma omp parallel for private(x)',)), ((14, 18), ('#pragma omp parallel for private(x)',))]; as built [((14, 18), ('#pragma omp parallel for private(x)',))]; with the rule [((8, 12), ('#pragma omp parallel for private(x)',)), ((14, 18), ('#pragma omp parallel for private(x)',))]; left out [[6, 'RAW', 'b', 11, 9], [6, 'RAW', 'b', 17, 15]]
- `e3_r_2` `s243` repeat 5, rewrite 6 (same): the full re-profile [((11, 13), ('#pragma omp parallel for shared(a_old)',)), ((16, 19), ('#pragma omp parallel for',)), ((22, 24), ('#pragma omp parallel for shared(a_old)',))]; as built [((11, 13), ('#pragma omp parallel for firstprivate(a_old)',)), ((16, 19), ('#pragma omp parallel for',)), ((22, 24), ('#pragma omp parallel for firstprivate(a_old)',))]; with the rule [((11, 13), ('#pragma omp parallel for shared(a_old)',)), ((16, 19), ('#pragma omp parallel for',)), ((22, 24), ('#pragma omp parallel for firstprivate(a_old)',))]; left out [[9, 'RAW', 'b', 18, 17], [9, 'WAW', 'a_old', 12, 12]]
- `e3_r_2` `s241` repeat 4, rewrite 1 (same): the full re-profile [((11, 14), ('#pragma omp parallel for shared(a_old)',))]; as built None; with the rule [((11, 14), ('#pragma omp parallel for shared(a_old)',))]; left out [[7, 'RAW', 'b', 13, 12]]
- `e3b_1` `s314` repeat 3, rewrite 5 (differs): the full re-profile [((12, 14), ('#pragma omp parallel for shared(temp)',))]; as built [((12, 14), ('#pragma omp parallel for shared(temp)',))]; with the rule [((12, 14), ('#pragma omp parallel for shared(temp)',)), ((23, 25), ('#pragma omp parallel for firstprivate(n) shared(next,temp)',))]; left out [[18, 'RAW', 'temp', 24, 24]]
- `e3b_1` `s314` repeat 3, rewrite 7 (same): the full re-profile [((15, 26), ('#pragma omp parallel for firstprivate(num_chunks) shared(chunk_max)',))]; as built None; with the rule [((15, 26), ('#pragma omp parallel for firstprivate(chunk_max,num_chunks)',))]; left out [[21, 'RAW', 'chunk_max', 23, 22]]
- `e3b_1` `s316` repeat 2, rewrite 10 (differs): the full re-profile [((11, 21), ('#pragma omp parallel for firstprivate(num_chunks) shared(chunk_mins)',))]; as built None; with the rule [((11, 21), ('#pragma omp parallel for firstprivate(num_chunks)',))]; left out [[16, 'RAW', 'chunk_mins', 18, 17], [24, 'RAW', 'x', 26, 25], [24, 'WAW', 'x', 26, 26]]
- `e3b_1` `s316` repeat 3, rewrite 1 (differs): the full re-profile [((9, 11), ('#pragma omp parallel for reduction(min:x)',))]; as built [((9, 11), ('#pragma omp parallel for reduction(min:x)',))]; with the rule None; left out [[9, 'RAW', 'x', 10, 10]]
- `e3b_1` `s316` repeat 4, rewrite 6 (differs): the full re-profile [((10, 12), ('#pragma omp parallel for shared(temp)',))]; as built [((10, 12), ('#pragma omp parallel for shared(temp)',))]; with the rule [((10, 12), ('#pragma omp parallel for shared(temp)',)), ((15, 17), ('#pragma omp parallel for firstprivate(stride) shared(temp)',))]; left out [[14, 'RAW', 'temp', 16, 16], [14, 'WAW', 'temp', 16, 16]]
- `e3b_1` `s316` repeat 4, rewrite 8 (differs): the full re-profile None; as built None; with the rule [((11, 17), ('#pragma omp parallel for firstprivate(stride) shared(temp)',))]; left out [[10, 'RAW', 'temp', 13, 15], [10, 'RAW', 'temp', 15, 15], [10, 'WAW', 'temp', 13, 15], [10, 'WAW', 'temp', 15, 15], [9, 'RAW', 'temp', 13, 15], [9, 'RAW', 'temp', 15, 15], [9, 'WAW', 'temp', 13, 13], [9, 'WAW', 'temp', 13, 15], [9, 'WAW', 'temp', 15, 15], [9, 'WAR', 'temp', 15, 13], [9, 'WAR', 'temp', 15, 15]]
- `e3b_1` `s316` repeat 4, rewrite 11 (differs): the full re-profile [((9, 11), ('#pragma omp parallel for reduction(min:x)',))]; as built [((9, 11), ('#pragma omp parallel for reduction(min:x)',))]; with the rule None; left out [[9, 'RAW', 'x', 10, 10]]
- `e3b_2` `s319` repeat 1, rewrite 2 (differs): the full re-profile [((8, 12), ('#pragma omp parallel for reduction(+:sum)',))]; as built [((8, 12), ('#pragma omp parallel for reduction(+:sum)',))]; with the rule None; left out [[8, 'RAW', 'sum', 11, 11]]
- `e3b_2` `s319` repeat 2, rewrite 1 (differs): the full re-profile [((9, 14), ('#pragma omp parallel for shared(partial)',)), ((16, 18), ('#pragma omp parallel for shared(partial) reduction(+:sum)',))]; as built [((9, 14), ('#pragma omp parallel for shared(partial)',)), ((16, 18), ('#pragma omp parallel for shared(partial) reduction(+:sum)',))]; with the rule [((9, 14), ('#pragma omp parallel for shared(partial)',))]; left out [[16, 'RAW', 'sum', 17, 17]]

## Still broken with the rule

- `e1v6_r_2` `s252` repeat 3, rewrite 1: the full re-profile [((9, 11), ('#pragma omp parallel for shared(s_temp)',)), ((14, 16), ('#pragma omp parallel for shared(s_temp)',))]; with the rule [((14, 16), ('#pragma omp parallel for shared(s_temp)',))]; left out [[7, 'WAW', 's_temp', 10, 10], [7, 'WAW', 'a', 15, 15]]; claims placed [[7, 'WAW', 'a', 13, 13], [7, 'WAR', 's_temp', 10, 13], [7, 'WAR', 's_temp', 10, 15], [7, 'WAR', 'a', 13, 17], [7, 'WAR', 'a', 15, 17]]; loops the reply declared independent [9, 14]
- `e3_r_1` `s121` repeat 3, rewrite 3: the full re-profile [((9, 11), ('#pragma omp parallel for shared(temp)',)), ((12, 14), ('#pragma omp parallel for shared(temp)',))]; with the rule [((9, 11), ('#pragma omp parallel for firstprivate(temp)',)), ((12, 14), ('#pragma omp parallel for shared(temp)',))]; left out [[8, 'WAW', 'a', 13, 13], [8, 'WAW', 'temp', 10, 10]]; claims placed [[8, 'RAW', 'a', 13, 10], [8, 'WAR', 'a', 13, 10], [8, 'WAR', 'temp', 10, 13]]; loops the reply declared independent [9, 12]
- `e3_r_2` `s243` repeat 5, rewrite 6: the full re-profile [((11, 13), ('#pragma omp parallel for shared(a_old)',)), ((16, 19), ('#pragma omp parallel for',)), ((22, 24), ('#pragma omp parallel for shared(a_old)',))]; with the rule [((11, 13), ('#pragma omp parallel for shared(a_old)',)), ((16, 19), ('#pragma omp parallel for',)), ((22, 24), ('#pragma omp parallel for firstprivate(a_old)',))]; left out [[9, 'RAW', 'b', 18, 17], [9, 'WAW', 'a_old', 12, 12]]; claims placed [[9, 'RAW', 'a', 23, 12], [9, 'WAR', 'a_old', 23, 12]]; loops the reply declared independent [11, 16, 22]
- `e3_r_2` `s244` repeat 2, rewrite 6: the full re-profile [((8, 10), ('#pragma omp parallel for shared(a_saved)',))]; with the rule [((8, 10), ('#pragma omp parallel for firstprivate(a_saved)',))]; left out [[7, 'WAW', 'a_saved', 9, 9]]; claims placed [[7, 'RAW', 'a', 12, 9], [7, 'RAW', 'a', 14, 9], [7, 'RAW', 'b', 13, 12], [7, 'RAW', 'b', 13, 14], [7, 'RAW', 'a_saved', 9, 14], [7, 'WAR', 'a', 12, 9], [7, 'WAR', 'a', 14, 9], [7, 'WAR', 'b', 13, 12], [7, 'WAR', 'b', 13, 14], [7, 'WAR', 'a_saved', 9, 14], [7, 'WAW', 'a', 12, 12], [7, 'WAW', 'a', 14, 14], [7, 'WAW', 'b', 13, 13], [11, 'WAW', 'a', 14, 12]]; loops the reply declared independent [8]
- `e3_r_4` `s341` repeat 4, rewrite 5: the full re-profile [((21, 23), ('#pragma omp parallel for firstprivate(count) shared(indices)',))]; with the rule [((21, 23), ('#pragma omp parallel for firstprivate(count,indices)',))]; left out []; claims placed [[13, 'RAW', 'count', 15, 15], [13, 'WAR', 'count', 15, 15], [13, 'WAW', 'count', 15, 15], [9, 'RAW', 'indices', 15, 22], [9, 'WAR', 'indices', 22, 15], [9, 'WAW', 'indices', 15, 15], [9, 'WAR', 'a', 25, 22]]; loops the reply declared independent [21]
- `e3b_1` `s314` repeat 3, rewrite 7: the full re-profile [((15, 26), ('#pragma omp parallel for firstprivate(num_chunks) shared(chunk_max)',))]; with the rule [((15, 26), ('#pragma omp parallel for firstprivate(chunk_max,num_chunks)',))]; left out [[21, 'RAW', 'chunk_max', 23, 22]]; claims placed [[13, 'WAR', 'chunk_max', 20, 31], [30, 'RAW', 'x', 32, 31]]; loops the reply declared independent [15]
- `e3b_2` `s3113` repeat 4, rewrite 1: the full re-profile [((9, 11), ('#pragma omp parallel for shared(abs_vals)',))]; with the rule [((9, 11), ('#pragma omp parallel for firstprivate(abs_vals)',))]; left out [[8, 'WAW', 'abs_vals', 10, 10]]; claims placed [[8, 'WAR', 'abs_vals', 10, 12], [8, 'WAR', 'abs_vals', 10, 14], [8, 'WAW', 'max', 12, 12], [8, 'WAW', 'max', 14, 14], [8, 'WAR', 'max', 12, 14], [8, 'WAR', 'max', 14, 14], [13, 'RAW', 'max', 14, 14], [13, 'WAW', 'max', 14, 14], [13, 'WAR', 'max', 14, 14]]; loops the reply declared independent [9]

