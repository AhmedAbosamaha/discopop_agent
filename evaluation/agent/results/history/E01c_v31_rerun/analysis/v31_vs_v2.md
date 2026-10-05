# E1c-v3.1 against E1c (agent v2), paired by loop — class R, race-free FASTER, N = 5 per loop

As pre-registered (registry, group E1c-v3.1): v3.1 against v2 paired by loop, one-sided Wilcoxon, N = 5 each, descriptive beside the three-way. v2: E1c's `default` arm (`e1c_r_1`–`e1c_r_4`, agent v2); v3.1: `e1c31_r_1`–`e1c31_r_4` (agent v3.1, `5935bded`). Same loops, sizes, lane split, model (Haiku) and the same pre-fix DiscoPoP. v2's numbers are recomputed here with the same tool (`main_comparison_stats.py e1c_r_*:default ...`).

| loop | v2 race-free FASTER | v3.1 race-free FASTER | v2 unusable | v3.1 unusable |
|---|---:|---:|---:|---:|
| `tsvc/s112` | 0 of 5 | 4 of 5 | 0 | 0 |
| `tsvc/s121` | 2 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s1213` | 2 of 5 | 4 of 5 | 0 | 0 |
| `tsvc/s127` | 5 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s211` | 3 of 5 | 3 of 5 | 0 | 0 |
| `tsvc/s212` | 3 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s241` | 4 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s243` | 2 of 5 | 3 of 5 | 0 | 0 |
| `tsvc/s244` | 0 of 5 | 3 of 5 | 0 | 0 |
| `tsvc/s252` | 4 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s254` | 5 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s255` | 5 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s281` | 1 of 5 | 1 of 5 | 0 | 0 |
| `tsvc/s291` | 5 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s292` | 5 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s293` | 5 of 5 | 5 of 5 | 0 | 0 |
| `tsvc/s331` | 0 of 5 | 2 of 5 | 0 | 0 |
| `tsvc/s341` | 0 of 5 | 1 of 5 | 0 | 0 |

**Total: v2 51 of 90, v3.1 71 of 90.** v3.1 ahead on 10 loops, behind on 0, tied on 8; Wilcoxon signed-rank, one-sided (v3.1 more), W = 55.0, p = 0.002322 (zero differences dropped).
