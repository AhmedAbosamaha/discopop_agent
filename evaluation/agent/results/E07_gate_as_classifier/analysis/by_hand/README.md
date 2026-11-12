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
