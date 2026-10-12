# DiscoPoP B24 — the same checks on the server (12 Oct 2026, no model)

Ubuntu clang 20.1.2; the checkout at commit `2c7e95fb3`; `server_checks_output.txt` is the script's output
(scratch `b24/b24_server.sh`: both files of loops with the profiler as installed, the rebuild from the synced
commit, the wrappers, both files again, the tests).

* **Before the rebuild** (the profiler with B23 repaired): the first file has six reduction entries (`hypot` and
  `fabs` of a difference as maxima), the second twelve; DiscoPoP writes `reduction(max:…)` on nine loops that are
  no maximum, and for the copy loop both `reduction(max:b)` and a plain `parallel for`.
* **After the rebuild:** four entries in each file — in the first the maximum and the three minima, in the second
  `fmax`, `fmin`, `fmax` with `fabs` in the other argument and `fmax` through a conversion — and one directive for
  each of them, with the right operation. Nothing on the other loops. The same as on the Mac.
* **Tests:** the two end-to-end tests of B23 and B24 pass; all 38 end-to-end tests pass (65 s).
* **The test that fails now and then on the Mac** (`sharing_clauses/do_all/shared/case_4`, B25): 30 of 30 runs
  pass before the rebuild and 30 of 30 after it. Its program's reduction file is empty before and after — the
  repair only ever removes entries of that file, so it cannot reach this program. (The script also meant to keep
  the program's instrumented code before and after; the test's Makefile left no `code.ll` to copy, so that
  comparison was not made.)
