# A write-after-read between passes — 17 lines (DiscoPoP candidate B22)

Mac, 8 Oct 2026, the explorer of commit `855dd0093`, Homebrew clang 19.1.7. Not a measurement of speed.

`k.c` — line 9 `for (int i = 0; i < N; i++) x[i] = x[i + 1] * 0.5;` (each pass reads the element the NEXT pass
overwrites) and line 11 `for (int i = 1; i <= N; i++) y[i] = y[i - 1] * 0.5;` (each pass reads what the pass before
wrote).

| | line 9 | line 11 |
|---|---|---|
| DiscoPoP's explorer, one profile, four runs | Do-All, 4 of 4 | blocked, read-after-write on `y`, 4 of 4 |

With `#pragma omp parallel for` on line 9 (what DiscoPoP writes): the program without the directive prints
`501250.000000`; with it, on 1 thread `501250.000000` (five runs), on 4 threads `500937.750000`, `501000.250000`,
`501125.125000` (five runs, three different sums), on 8 threads `500563.125000`, `500688.000000`, `500875.375000`.

`k_in_repetition_loop.c` — the same, with `for (int r = 0; r < 3; r++)` around the first loop (as every TSVC kernel
loop has a repetition loop around it). DiscoPoP's explorer: the inner loop (line 10) is blocked, "RAW on `x`", and so
is the repetition loop (line 9). From the second repetition on, a pass reads what the NEXT pass wrote one repetition
earlier; the explorer counts that against the inner loop (the shape of candidate B16). So on a kernel inside a
repetition loop the two defects cancel: B16 repaired alone would make such a loop a false Do-All.
