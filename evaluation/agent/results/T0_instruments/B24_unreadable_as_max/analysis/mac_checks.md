# DiscoPoP B24 — what was measured on the Mac before the server was touched (12 Oct 2026, no model)

LLVM 19 (Homebrew clang 19.1.7), the profiler installed with `venv/bin/pip install ./profiler`, the explorer run
from the checkout, `venv/bin` first on PATH. "Before" is the DiscoPoP with B23 repaired (commit `c89952852`).

## The second file of loops (`repro/mm2.c`)

`discopop_cc mm2.c -o prog -lm`, `./prog`, `discopop_explorer` in `.discopop`. What DiscoPoP reports per loop,
before (`repro/before/`) and after (`repro/after/`):

| line | the loop's statement | before | after |
|---:|---|---|---|
| 12 | `x = fmax(x, a[i]);` | reduction `max:x` | reduction `max:x` |
| 19 | `x = fmin(x, a[i]);` | reduction `min:x` | reduction `min:x` |
| 26 | `x = fmax(x, fabs(a[i]));` | reduction `max:x` | reduction `max:x` |
| 33 | `float x; x = fmax(x, a[i]);` | reduction `max:x` | reduction `max:x` |
| 40 | `x = fmax(fmax(x, a[i]), b[i]);` | reduction `max:x` (right) | nothing — given up on purpose |
| 47 | `x = fmin(fmax(x, a[i]), 0.25);` | reduction `max:x` | nothing |
| 54 | `x = fmax(x, x + a[i]);` | reduction `max:x` (wrong) | nothing |
| 61 | `x = min2(x, a[i]);` (a helper that returns the smaller) | reduction `max:x` (wrong) | nothing |
| 68 | `x = hypot(x, a[i]);` | reduction `max:x` (wrong) | nothing |
| 75 | `x = fabs(x - a[i]);` | reduction `max:x` (wrong) | nothing |
| 82 | `x = x / (2.0 + b[i]);` | reduction `max:x` (wrong) | nothing |
| 88 | `b[i] = b[0];` | reduction `max:b` and a Do-All (wrong) | nothing |

The reduction file holds twelve entries before (eleven `>`, one `<`) and four after (lines 12, 19, 26, 33).

The first file (`../B23_min_as_max/analysis/repro/mm.c`) after this repair: the maximum `max:x`, the three minima
`min:x`; `hypot` (line 94) and `fabs` of a difference (line 101), which the repair of B23 had left as `max:x`, get
nothing.

## The tests

* New: `test/end_to_end/reduction_pattern/negative/min_max_unreadable` (C): `fmax(x, fabs(a[i]))` is a reduction
  with `max`; the helper function, `hypot`, `fabs` of a difference, the division and the maximum with the
  variable in both arguments get no pattern — neither a reduction nor a Do-All. Passes; `min_max_calls` of B23
  passes.
* The profiler's unit tests (`test/profiler`, `DP_TEST_PROFILER_CONFIG=build_hybrid`): 184 passed.
* Eight feature checks of the agent (`reduction-carry`, `clause`, `pattern-choice`, `pragma-sibling-loops`,
  `profiler-else-loop`, `explorer-multi-backedge`, `fast-refresh`, `fast-refresh-eq`): 8 passed.
* DiscoPoP's end-to-end tests, 38 with the new one: 37 pass; **one existing test failed in the run of the whole
  set and passes when run again** — `sharing_clauses/do_all/shared/case_4` (a stack array filled by a loop and
  read after it; expected `shared(Arr)`, got `lastprivate(Arr)`). Not this repair's doing, see below.

## The test that fails now and then (`flaky_test/`)

`sharing_clauses/do_all/shared/case_4` on the Mac, with this repair installed: 2 failures in 24 runs of the test.

* ONE instrumented binary run 31 times, the explorer after each run: `shared(Arr)` 28 times, `lastprivate(Arr)`
  3 times. In the three, the profile's `dynamic_dependencies.txt` lacks the three `INIT` lines of the array
  (`37@20`, `37@21`, `37@22 NOM INIT 0@0|GEPRESULT_Arr(…)`); nothing else differs
  (`flaky_test/dynamic_dependencies_shared_run.txt`, `…_lastprivate_run.txt`).
* ONE kept profile, the explorer run 40 times with 40 hash seeds: `shared(Arr)` 40 times.

So the difference is made by the profiler's RUNTIME from one run of the same binary to the next, not by the
explorer and not by the pass this repair changes: the repair only ever removes entries of the reduction file, and
this program's reduction file is empty — before and after the repair, checked on the server, where the build
before it was still installed and the test passed 30 of 30 times on either build (`server_checks.md`). Entered
in the bug list as a candidate, B25.

## The two PolyBench kernels with division loops (`pilot/`)

Profiled on the Mac with the repair: `polybench/lu` and `polybench/adi` keep every Do-All the server's last draws
show (lu: lines 29, 30, 64, 67 and the reduction `+:A` on 67; adi: all fifteen loops of the kernel and its
initialisation) — the division loops included, whose maximum entries are gone from the reduction file
(`pilot/lu_reduction_after_mac.txt`, `pilot/adi_reduction_after_mac.txt`). `tsvc_c3/s293` had no pattern before.

## The experiment's own rewrites

DiscoPoP alone with the repair, profiled as a trial does: the rewrite of `s316` with `x = fmin(x, a[i]);`
(`../B23_min_as_max/analysis/pilot/s316_fmin.c`) — a reduction, `min:x`; `s314` with `x = fmax(x, a[i]);`
(`s314_fmax.c`) — a reduction, `max:x`. As after the repair of B23.
