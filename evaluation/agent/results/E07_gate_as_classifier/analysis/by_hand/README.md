# E7 — what was read by hand

The read-outs (`analysis/readout_a1.md`, `readout_a2.md`, `readout_drb.md`) count. This folder holds what the counts
cannot say: why each disagreement between the gate and the judge exists, read from the program texts, the trials'
own logs and records, and a few runs made for the purpose. Everything here can be repeated with the scripts beside
this file (run from `evaluation/`, with the project's `venv`).

| script | what it shows |
|---|---|
| `inspect_prog.py a1\|a2 <benchmark> <number> [--diff]` | one program: its candidates, the judge's records, each replayed check with its diagnostic, the diff from its base |
| `fa_diffs.py a1\|a2 false_accepts\|false_refusals` | every program of that list: the lines the candidate added and removed, the trial's candidates, how the trial ended |
| `fate19.py [--full]` | for each accepted rewrite the judge finds wrong: the log block of the step that reverted it |
| `exact_check.py a1\|a2` | every candidate whose archived patch does not apply exactly to the base the corpus gives it |
| `nv_trials.py a1 [filter]` | the trials whose replayed history does not end in the archived final file, candidate by candidate, beside the log |
| `pairs_table.py a1\|a2 [--all]` | one line per directive pair: the recorded verdict, the judge's two instruments, and each check's runs (a refusal by a time limit marked apart); then the pairs counted by kind of check, and the judge's race check beside the gate's |
| `md_dump_test.py` | (server, piped on stdin) which of `md`'s dumped values differ for the directive with `reduction(+:pe,ke)` |
| `tsan_test.py`, `tsan_test2.py` | (server, piped on stdin) a program under ThreadSanitizer at the gate's size and at the verification size, built with `-O1` and with `-O2`; the second with the sanitizer's history at its default and at its largest setting |
| `stack_test.py`, `stack_test2.py` | (server, piped on stdin, nothing left behind) a program built as the harness builds it, run under the default stack limit and with the limit raised; the second also without optimisation |

`readout_a1_before_repair.md` is the first read-out of A1, on the corpus as first built. It is kept because it is
how the builder's defect was found (below); nothing in it counts.

## 1. The corpus builder's defect (found 12 Nov, repaired before any number was read)

Two of the first read-out's 21 false accepts were DiscoPoP's directive on the repetition loop of `tsvc_c2/s331`
with `dummy` inside the loop. Today's replay refuses that text in every run by every check. The trial's log
(`e1v6_r_4 tsvc_c2/s331 default_v4 rep3`) shows the directive judged on another text: an earlier rewrite, kept at
that time, had moved `dummy` into a loop of its own, and Settle dropped that rewrite after the last candidate.
The builder had taken "kept" from `accepted.json`, the state after the last step. The record's row of 12 Nov 2026
("E7: the corpus builder …") gives the cause, the repair and what changed (13 candidates re-placed, 11 rebuilt
that could not be before, 8 programs out, 13 in; A2 unchanged). `nv_trials.py` and `exact_check.py` are the two
checks that showed the extent; on the repaired corpus `exact_check.py` reports none.

The 15 candidates of the agent's floor step are each the only candidate of their step and sit on the original
(`floor/floor.log` of each trial), so no history is involved there.

## 2. Accepted rewrites the judge finds wrong: 19, one kind

`fa_diffs.py a1 false_accepts`. All 19 give exactly the original's values on both inputs at the small size
(`dump_exact` true twice) and end with a segmentation fault (return code −11) in the first run at the verification
size.

- **18 hold an automatic array of the loop's length** (`real_t x[LEN_1D]`; 32 MB at STANDARD, 256 MB at LARGE,
  1.5 GB at EXTRALARGE, against a stack limit of 8 MB on the server): `k53` #127 #140, `s211` #5 #7 #30,
  `s212` #2, `s241` #3 #27 #43, `s244` #6 #13, `s252` #7 #18 #26, `s3112` #18, `s321` #41 (all `tsvc_c2`),
  and `tsvc_c3/s241` #26 #37.
- **1 allocates a copy of the array for every repetition** (`tsvc_c2/s000` #14,
  `malloc(iterations * LEN_1D * sizeof(real_t))`).

*The cause, tested* (`stack_test.py`, server, 12 Nov): `s241` #3 at EXTRALARGE, `k53` #127 at STANDARD and `s211` #7
at LARGE return −11 under the default limit and 0 with the stack limit raised to unlimited; `s000` #14 returns −11
under both.

*What became of them* (`fate19.py`; the trial's log, its candidate records and the request the model received
next). None is a trial's final file. Each was reverted in the step that followed the gate's acceptance, in which
the agent applies DiscoPoP's directives to the rewritten loop and times the result against the program before the
rewrite:

- 12 because the program with DiscoPoP's directive crashed at the timing size. In 11 the next request to the model
  says so in these words ("the program with DiscoPoP's pragmas CRASHED at the timing size, which the correctness
  checks never reach"): `s3112` #18, `s321` #41, `s211` #5 #7 #30, `s241` #27 #43, `s244` #6 #13,
  `tsvc_c3/s241` #26 #37. In the twelfth, `s252` #26, no request followed (the region's attempts were used up);
  one of DiscoPoP's two directives had passed the gate, and with a passing directive the agent of that version
  reaches the verdict `pattern_broken` only through a crash of the timed run (`phases/verdicts.py` at
  `c15b7212d~1`).
- 5 because DiscoPoP's only directive for the rewritten loop failed the gate at `correctness`: `s212` #2, `s241` #3,
  `s252` #7 #18, and `k53` #127, whose arm ran with the speed check off, so no timed run existed there.
- 1 because the program was not faster than before the rewrite (`s000` #14, 0.13×).
- 1 because DiscoPoP found no parallel loop in the rewritten lines (`k53` #140).

*The same construct in a shipped program.* Of the 136 distinct programs that are a trial's final file, one holds an
automatic array of the loop's length: `tsvc_c2/s244` #14 (`e1v6_r_2`, rep2, FASTER), with its rewrite #11. It
copies the array and reads only the copy's last element. Built as the harness builds it (`-O2`) it runs under the
8 MB limit, because the compiler removes the copy; built with `-O0` it returns −11 under that limit and 0 with the
limit raised (`stack_test2.py`, 12 Nov). The judge and the trial's own verification both find it right.

## 3. Refused rewrites the judge finds right: 10, one kind

`fa_diffs.py a1 false_refusals`. All ten change the order of floating-point operations: `s3112` #5 #16 #28 #31 #38
(a running sum computed by doubling strides, or as total minus suffix), `s323` #6 #19 #24 #27 (the recurrence
written as a running sum of `c[i] * (d[i] + e[i])`), `s322` #38 (`a[i] = a[i] + x + y` written as `a[i] += x + y`);
all `tsvc_c2`. Their values differ from the original's by 7·10⁻¹⁶ to 4·10⁻¹¹ relative in the judge's full
comparison, under the harness's tolerance of 10⁻⁹ (`DIGEST_REL_TOL`). The gate compares these benchmarks' output
byte for byte: the six builds of each original agree exactly, so its measured numerical noise is zero
(`gate/equivalence.py`, `compare_outputs`). Which input refused: both 5, the perturbed one only 4 (`s3112` #5 #28
#31 #38), the shipped one only 1 (`s322` #38).

## 4. The refused directive the judge finds right: 1, and it is not right

`tsvc_c2/s341` #16 (`inspect_prog.py a1 tsvc_c2/s341 16`): `#pragma omp parallel for shared(pos,count)` on
`pos[i] = pos[i-1] + count[i-1]`, a running sum, so each iteration reads what the one before it wrote. The gate's
sanitizer reported the race at the small size in the trial and in each of the replay's four runs. The judge finds
identical values on both inputs, an identical digest at the verification size, the same result in repeated runs,
and no report in three sanitizer runs at EXTRALARGE. By the registered definition it counts as a right program
the gate refused; read by hand the gate is right and the judge's instruments did not show the fault. Why they did
not was not tested.

## 5. A2: refused directives the judge finds right: 7, two causes, neither a judgment of the program

`pairs_table.py a2`; `inspect_prog.py a2 burkardt/md <n> --diff`.

- **Six were refused by a time limit** (`burkardt/md` #4 #5 #7 #9 #12 #13). Each is DiscoPoP's directive on a loop
  of three iterations (`nd`, the number of dimensions) that is entered for every pair of particles: the force
  update in `compute` (#4 #5 #13) and the distance in `dist`, with `reduction(+:d)` (#7 #9 #12). The judge finds
  the values exact on both inputs, the digest exact at STANDARD and the result stable, and no report in three
  sanitizer runs (305 to 860 s each); it measures the program at 0.006 to 0.021 of the original's speed. In the
  replay every sanitizer run of the gate ended at its limit of 300 s and every run of the schedule matrix at 120 s
  (`t` in the table); the output runs ended at 120 s in some or all runs. The verdict recorded in the trial is
  the same limit (`tsan`, "TSan run timed out (300 s)").
- **One was refused by the dependence stage** (`polybench/mvt` #3, trial `t0_11_b19r_apps_a`, 8 Oct, agent at
  `b6297e53b`): "DiscoPoP OBSERVED 1 loop-carried dependence(s) in lines 79-81 … RAW on x2[] in the loop at line
  80". The directive sits on the outer loop; the dependence belongs to the inner one. This is the defect that
  Fix 105 repaired on 9 Oct (`d1fb3b144`, after this trial): with a directive already inserted above, the stage
  read the profile one line off. The two other draws, run the same evening on the same agent, accepted the
  directive on that loop: `mvt` #5 was judged on the original, where no line had shifted, and `mvt` #1 in the
  same shifted position, in a draw where DiscoPoP reports the inner loop itself as parallel (its pattern at lines
  80–81). Whether that draw's profile holds a blocker at the line the stage read was not looked up. The replay
  gives the stage no profile and accepts; the judge finds the program right and free of races. The one fidelity
  difference of A2 is this pair.

## 6. A2: the 71 wrong directive programs, none accepted

`pairs_table.py a2`. No refusal of a wrong pair is a time limit. By kind of check (each alone, at least one run;
the generated read-out counts the two inputs as two checks, this count is an addition made after the result was
seen):

| refused by | pairs | which |
|---|---:|---|
| the sanitizer, the matrix and the output | 33 | |
| the sanitizer and the output, on the perturbed input only | 22 | `dynprog` #1 #3 #4 #5 #7 #8, `gramschmidt` #2 #4 #7, `jacobi-2d-imper` #3, `lu` #4, `ludcmp` #4 #6 #8 #9, `seidel-2d` #1 #3 #4, `trisolv` #1 #3 #4 #5 |
| the sanitizer only | 8 | `doitgen` #3 #12, `floyd-warshall` #1 #3 #4, `reg_detect` #2 #7 #12 |
| the matrix and the output | 5 | `burkardt/md` #8 #10 #11, `rodinia-3.1/pathfinder` #1 #2 |
| the output only | 3 | `burkardt/md` #1 #2 #3 |

- **The sanitizer only (8).** The printed values are exact in every run of the gate and of the judge; the judge
  counts the program wrong on its own sanitizer report. The racing accesses, from the judge's reports and the
  source: in `doitgen` #3 #12 the counter `s` of an inner loop is missing from the directive's private list, and
  every thread writes the one `s` on the main thread's stack (line 74); in `reg_detect` #2 #7 #12 the same with
  the counter `cnt` (line 76); in `floyd-warshall` #1 #3 #4 one thread reads `path[i][k]` or `path[k][j]` while
  another writes that element (line 67).
- **The perturbed input only (22).** The output comparison passes on the shipped input in all three runs and
  fails on the perturbed one in all three. The shipped inputs of these PolyBench kernels are regular:
  `seidel-2d` and `jacobi-2d-imper` start from `(i*(j+2)+2)/n`, which the stencil's average leaves unchanged, and
  `lu`, `ludcmp`, `gramschmidt` and `trisolv` from a matrix that is the product of the row and the column index.
  The packages' own note says why the second input exists ("A shipped input can be one the kernel leaves
  unchanged …"). The sanitizer reports all 22.
- **`pathfinder` #1 #2.** The directive is on the loop that fills the grid with `rand()`. The C library locks
  the generator, so the sanitizer has nothing to report, and the numbers land in another order in every run:
  the matrix finds two runs at the same thread count that differ, and the output differs from the original's on
  the shipped input. On the perturbed input the output is the same in all runs.
- **`md` #1 #2 #3.** The directive makes `nd` private, so every thread reads it uninitialised; the printed sums
  are NaN. No race, and the same wrong output at every thread count, so only the output comparison refuses.
- **`md` #8 #10 #11 are correct up to the order of two sums.** The directive is the textbook one for this
  program (`reduction(+:pe,ke)`, the work arrays private), and the judge measures it 5.6 to 7.3 times faster.
  `md_dump_test.py` (server, 12 Nov): against the original, the potential and the kinetic energy differ by at
  most 7.5·10⁻¹⁵ relative; the only values beyond the harness's tolerance are the third column of the energy
  table, the relative energy error `(potential + kinetic - e0) / e0`, a difference of nearly equal numbers
  (1.75·10⁻¹¹) that moves by up to 5·10⁻⁴ of itself. The gate refuses on the last digit of the digest; the
  judge on that column. By the registered definition the three count as wrong and refused; read by hand both
  instruments refuse a correct program here, for the reason of section 3.

## 7. The judge's race check beside the gate's (both corpora)

`pairs_table.py a1`, `pairs_table.py a2`, last lines. The gate runs ThreadSanitizer at the package's small size on
a build with `-O1`; the judge's race check (J2) runs it at the verification size on the harness's build with `-O2`,
three runs at 12 threads. On the pairs where the gate's sanitizer, run alone, reports a race in each of its three
runs, J2 reports one

- in A1 on 2 of 13 (`s341` #18, `s481` #3; silent on `s211` #8, `s241` #20, `s3112` #15 #30, `s321` #14 #26 #30,
  `s322` #5 #6, `s323` #16 and on `s341` #16 of section 4),
- in A2 on 57 of 63 (silent on `adi` #3 #5 #14 #16 #17 and `seidel-2d` #3).

In 16 of the 17 silent cases the judge's value comparison finds the program wrong, so the race is real and the
program is counted wrong all the same; the seventeenth is `s341` #16.

*Tested* (`tsan_test.py`, `tsan_test2.py`, server, 12 Nov, clang 20.1.2, archer loaded, 12 threads) on `adi` #3,
`seidel-2d` #3 and `s341` #16:

| size | build | runs with a report |
|---|---|---|
| the package's small size | `-O1` | 6 of 6 |
| the package's small size | `-O2` | 6 of 6 |
| the verification size | `-O1` | 1 of 6 (`adi`, one of two runs) |
| the verification size | `-O2` | 0 of 13 |
| the verification size | `-O2`, `history_size=7` | 0 of 7 |

So the size decides and the optimisation level does not. Why the larger size hides the report was not established:
the sanitizer's largest history did not bring it back. What follows for the read-outs: the judge calls a directive
program right on its values (every value on both inputs at the small size, the digest at the verification size,
repeated runs) and on a race check that is weak at that size; "no wrong directive accepted" means none the judge
could see. The gate's own sanitizer passed each accepted directive at the small size in the trial and again in
each of the replay's runs.

## 8. The run the repair added (A1, `e7_a1_judge_5`, `e7_a1_checks_2`)

14 programs and 15 pairs, all of trial family `e1v6_r_4 tsvc_c2/s331 default_v4` (rep2 to rep5) except `s244` #10.
No disagreement between the gate and the judge among them: the five rewrites the gate accepted are right
(`s331` #40 #43 #47 #50 #51), the five directive programs it accepted are right and faster (`s331` #41 #44 #45 #46,
`s244` #10), and the four directive programs it refused at `correctness` are wrong (`s331` #42 #48 #49 #52).
`s331` #41 #44 #45 #46 are the texts on which the gate had judged the directives that the first build of the corpus
had placed on another text (section 1).

## 9. The named cases of the registration (R5)

- *The clause refusal.* The registration names "the `s281` clause refusal in A1". A1 holds one refusal by the
  clause check, and it is on `tsvc_c3/s331` (#75, `e1v6c_v7_agent` rep2): DiscoPoP's
  `parallel for firstprivate(j) private(chksum,nl)` on a loop that holds a `break`. The clause check refused it
  in the trial; the replay, which does not hold that check, refuses it at the OpenMP build, and the judge's build
  fails too. The naming in the registration was an error of mine; no `s281` candidate was refused by that check.
- *`mvt`.* Section 5.
- *`floyd-warshall`.* Five directive programs, all refused by the gate's sanitizer: #1 #3 #4 print the right
  values in every run (section 6), #5 #6 print wrong ones.
- *`hotspot`.* The three draws that hold it recorded no candidate for it (outcome no-change, no directive
  judged), so A2 holds none.

