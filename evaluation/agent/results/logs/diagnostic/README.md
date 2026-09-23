# Diagnostic logs — the evidence behind the DiscoPoP bug reports

These are not experiment runs. They are the probes that located the bugs and limitations
reported upstream in `discopop_agent/docs/DISCOPOP_BUG_REPORTS.md`, kept because the report
cites what they show and the directories they lived in were deleted with the old harness
checkout on 2026-09-20.

| directory | what it holds | what it is evidence for |
|---|---|---|
| `_b3_check` | Rodinia `pathfinder` instrumented and explored repeatedly | **B3** — the profiler leaves a loop that ends an `else` block without loop markers, so the explorer's `IndexError` appears on some runs and not others (40 of 60 before Fix 81, 0 after) |
| `_b3_mg` | NPB-CPP `mg` as a unity unit, with its IR | **B3 / B5** — the loop-state widths that showed the matching was one position short |
| `_diag_nw` | Rodinia `nw` instrument and explore logs | **B2 / L2** — the multi-back-edge crash, and the 531,606 call-path states behind the ≈ 25 h explorer run |
| `_mgprof` | NPB-CPP `mg` profile, explored under Fixes 82 and 83 (`explore_fix82.log`, `explore_fix83.log`) | **L3** — `mg` is past the state-assignment phase after Fix 83 but never leaves task detection; the run was stopped unfinished after 11 h 24 min |
| `_prepare`, `_t0` | packaging and instrument-chain launch logs | provenance for the T0 studies and the packaging validations |

| `_prefix_determinism` | `prefix_sum.cpp`, the probe behind §5b | **DiscoPoP's Do-All verdict varies between profiles of the same program** — loop 18 is a true recurrence, and 8 of 11 Mac profiles reported 4 blockers while 3 reported none. The finding that made "one profile per benchmark per run" a rule, and T0.2 an instrument |
| `_build_dp_2026-08-23` | the original server build script and its log | how DiscoPoP was first built on the experiment host (LLVM 20), kept because the record cites it |

Fetched from `~/new_benchmark_harness/agent/runs/` on the server before that directory was
removed, and from the probe directories in the server's home on 2026-09-20. Binaries, IR dumps of no evidentiary value and profile trees were left behind; only
logs, `meta.json` and CSVs were kept.
