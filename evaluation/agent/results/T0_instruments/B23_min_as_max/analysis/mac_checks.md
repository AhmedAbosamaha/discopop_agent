# DiscoPoP B23 — what was measured on the Mac before the server was touched (10 Oct 2026, no model)

LLVM 19 (Homebrew clang 19.1.7), the profiler installed with `venv/bin/pip install ./profiler`, the explorer run
from the checkout. Every command was run with `venv/bin` first on PATH.

## The file of thirteen loops (`repro/mm.c`)

`discopop_cc mm.c -o prog -lm`, `./prog`, `discopop_explorer` in `.discopop`. The profiler's reduction file and
the directives DiscoPoP suggests, before the repair (`repro/before/`) and after both halves (`repro/after/`):

| line | the loop's statement | before | after |
|---:|---|---|---|
| 9 | `x = fmax(x, a[i]);` | `>` · `reduction(max:x)` | `>` · `reduction(max:x)` |
| 16 | `x = fmin(x, a[i]);` | `>` · `reduction(max:x)` | `<` · `reduction(min:x)` |
| 23 | `x = fminf(x, (float)a[i]);` | `>` · `reduction(max:x)` | `<` · `reduction(min:x)` |
| 30 | `x = fmin(a[i], x);` | `>` · `reduction(max:x)` | `<` · `reduction(min:x)` |
| 37, 45, 53, 61 | `v = a[i]; x = (v > x) ? v : x;` and the three other `?:` forms | not reported | not reported |
| 69, 78 | `if (a[i] > x) { x = a[i]; }`, `if (a[i] < x) { x = a[i]; }` | not reported | not reported |
| 87 | `x = (a[i] > x) ? a[i] : x;` | not reported | not reported |
| 94 | `x = hypot(x, a[i]);` | `>` · `reduction(max:x)` | unchanged (B24, not repaired) |
| 101 | `x = fabs(x - a[i]);` | `>` · `reduction(max:x)` | unchanged (B24, not repaired) |

`diff before/patches.txt after/patches.txt` is the three minimum lines and nothing else.

## The explorer's half

With the profiler repaired and the explorer as it was, the six entries (`>`, `<`, `<`, `<`, `>`, `>`, the last one
a `>`) gave `max` on all six loops. The same six entries with the entry of line 16 moved to the end
(`repro/reduction_reordered.txt`) gave `min` on all six, the maximum of line 9 included: the operation came from
the last entry of the file. With the explorer repaired, both orders give `max` on line 9, `min` on lines 16, 23
and 30, and `max` on lines 94 and 101.

## The tests

* New: `test/end_to_end/reduction_pattern/positive/min_max_calls` (C; `fmax`, `fmin`, `fminf` with the variable as
  the second argument) asserts the operation of each reduction. Passes with the repair; with the explorer's half
  taken out it fails (`max` on all three loops).
* DiscoPoP's end-to-end tests, `venv/bin/python -m unittest -v -k "*.end_to_end.*"`: 37 tests, OK (329 s).
* The profiler's unit tests, `DP_TEST_PROFILER_CONFIG=build_hybrid ../../venv/bin/python -m pytest` in
  `test/profiler`: 184 passed (258 s).
* `venv/bin/python -m mypy --config-file=mypy.ini -p discopop_explorer`: no issues in 214 files.

## The mechanism on the experiment's own loop (`pilot/`)

DiscoPoP alone, profiled as a trial does:

| program | DiscoPoP reports on the kernel's loop |
|---|---|
| `tsvc_c4/s316` as packaged (`if (a[i] < x) x = a[i];`) | nothing — blocked by the dependence on `x`; the reduction file is empty |
| the rewrite of E3b's trial `e3b_1` rep1 (`pilot/s316_fmin.c`: `x = fmin(x, a[i]);`) | a reduction, `min:x` (it wrote `reduction(max:x)` in the trial) |
| `tsvc_c4/s314` as packaged (`if (a[i] > x) x = a[i];`) | nothing — blocked; the reduction file is empty |
| the same loop with `x = fmax(x, a[i]);` (`pilot/s314_fmax.c`) | a reduction, `max:x`, as in the trials |

## Where the repair can act among the 84 packages (`reduction_files_before.txt`)

The reduction file of every package, from the profiles of the last draws before the repair
(`t0_11_c3_b19r_a`, `t0_11_c4_a`, `t0_11_b19r_apps_a`; `reduction_files_scan.sh`, read-only on the server):

* `tsvc_c3` (44): 30 without an entry, 13 with `+` only, one with a single `>` (`s293`, on the array `a`).
* `tsvc_c4` (9): 7 without an entry, 2 with one `+`.
* outside TSVC (31): one without an entry, 23 with one operation, seven with more than one — `burkardt/md`
  and `npb/is` (`+`, `-`), `polybench/adi` (`+`, `-`, `>`), `covariance` (`+`, `-`), `lu` (`+`, `>`), `syr2k` and
  `syrk` (`*`, `+`).

The profiler's half can act only where a minimum call is stored: none of these files holds one (confirmed by
the files after the rebuild, `b23_readout.md` §4: no `<`, no file with other operations). The explorer's half can act only in the seven packages with more than
one operation; in the profiles read, every reduction pattern DiscoPoP reports there (`lu`, `syrk`, `md`) belongs
to a `+` entry and the last entry of the file is a `+` as well, so no operation is expected to change.
