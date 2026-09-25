# Bugs found in DiscoPoP itself — for the DiscoPoP maintainers

Written for: the DiscoPoP developers (TU Darmstadt). Every change this project made, or
needs, **inside DiscoPoP** (profiler, runtime, explorer) is listed here with symptom, root
cause, a minimal reproducer and the patch, so it can be reported upstream. The agent's own
fixes are in `FIXES.md`; this file holds only what concerns DiscoPoP's code.

Rule of the thesis: a bug found in DiscoPoP is fixed, the **fixed DiscoPoP is used in every
arm** — the DiscoPoP-only baseline included — and the fix is stated in the thesis.

DiscoPoP version: this work branches from **`new_explorer`**, not `master` — merge base
`6a2ef0fa` (25 June 2026, "Merge pull request #806"). Everything below was found on that base
plus this project's own commits. **`new_explorer` has since advanced by 178 commits, 19 of them
touching `TaskGraph.py`**, which is where B2, B4, B5 and P1 live — so those four should be
re-checked against current `new_explorer` before they are reported, in case they are already
fixed. `CFA.cpp` (B3) has had no upstream commit since the base. The checkout under this
repository (`profiler/`, `rtlib/`, `explorer/`),
LLVM 19 (macOS) and LLVM 20 (Linux).

| # | Component | Status | One line |
|---|---|---|---|
| B1 | explorer, `ASTLoader.build_path_mapping` | fixed (agent Fix 78) | files reached through a relative include path lose every `private`/`firstprivate` clause |
| B2 | explorer, `TaskGraph.__break_cycles` | fixed (agent Fix 80) | a loop with several back edges (`continue`) crashes the task-graph builder |
| B3 | profiler, `utils/CFA.cpp` + `instrumentLoopExit` | fixed (agent Fix 81) | a loop that is the last statement of an `else` block gets no loop markers → explorer `IndexError` at random, and silently wrong loop-state matching |
| B5 | explorer, `TaskGraph.recursive_assignment` | fixed (agent Fix 82) | a loop state of one function is matched against loops of another → `IndexError` (NPB `mg`, every attempt) or a silent wrong match |
| B4 | explorer, task-graph traversal order | open (consequence of B3, to re-measure after it) | the explorer's output differs between runs on one unchanged profile |
| P1 | explorer, `TaskGraph.__assign_state_ids` | fixed (agent Fix 83) | performance: the state assignment re-answers the same (context, call path) pair exponentially often — hours on `mg`/`nw`, seconds once memoised |
| B6 | `discopop_patch_generator` (called by the explorer) | open | hangs on some runs: 3 of 20 explorer runs on one unchanged profile of a 40-line program never return from the patch-generator subprocess |
| B7 | profiler runtime, `dp_loop_output.cpp` → `loop_counter_output.txt` | root cause found, patch written, worked around (agent Fix 88); present in upstream `new_explorer` `28ac4d47` | the per-loop iteration counts are paired with the WRONG loops: 277 of 337 counts (82 %) over 41 profiles disagree with the `BGN loop` markers of the same run |
| N1 | hotspot detection (`hotspot_detection/private/`) | usage hazard, not a bug (agent Fix 87) | region ids and results ACCUMULATE across builds and runs by design; re-instrumenting a CHANGED program into the same directory reports the old program's lines, halved times, and nothing for new regions |
| L1 | profiler | limitation | NPB-CPP `lu` (4,134 lines): the instrumenting compile exceeds two hours |
| L2 | profiler + explorer | limitation | Rodinia `nw`: 531,606 call-path states; the explorer's state assignment needs ≈ 25 h |
| L5 | explorer | limitation (a cheap reproducer of B4) | TSVC-2, ~30 lines per loop: the explorer normally finishes in **4 s**, but on a RANDOM ~2 loops of 25 per profile it does not finish at all — `s291` 5,403 s, `s3112` > 80 min on one draw and **5.8 s** on the next, `s322` and `s331` 4 s on one draw and stalled on the next. Every stall stops at the same point, a progress bar at `0/11`. Instrumentation and the profiled run take 0.2 s, so it is the explorer alone; `s291`'s profile holds **117 task patterns** for one loop nest — the signature of L3 (NPB `mg`) at a tiny scale, which may make these the smallest reproducers of it |
| L4 | profiler | limitation | PolyBench `adi` (~130 lines): the instrumenting compile takes **2,387 s (40 min)** per profile, ~40x the next slowest PolyBench kernel. The profile is usable (19 Do-Alls, gate-verified parallel), so this is a cost limitation, not a failure |
| L3 | explorer | limitation | NPB-CPP `mg`: with P1's fix the state assignment is fast, but the run then stays in task-pattern detection (`new_task_detector`) — a first run was read at 4 h 19 min, the same run was stopped unfinished after **11 h 24 min** at 100 % CPU on the server (19–20 Sep); the Do-All detector is not reached. Not usable per trial |

---

## B8 — a true recurrence reported as Do-All when the program spans two files (explorer, call-path states)

**Found** 25 Sep 2026 (T0.15, `evaluation/agent/tools/harness_equivalence.py`), while moving a benchmark's
measurement code into a second file. **Status:** open — not yet fixed; the campaign keeps its benchmarks
in one file until it is (D39).

**Reproducer:** TSVC `s211` (`a[i] = b[i-1] + c[i]*d[i]; b[i] = b[i+1] - e[i]*d[i];` inside a repetition
loop). Profiled as ONE file: no pattern on either loop (5 of 5 explorer draws on macOS/LLVM 19, 3 of 3 on
Linux/LLVM 20); `explorer/doall_prevented.json` holds the dynamic RAW on `b` that blocks both. The SAME
code with the helper functions moved into a second file (`#include`d, one translation unit, every
function inside the project root, so all instrumented): Do-All on the inner loop AND on the repetition
loop in every draw; `doall_prevented.json` is empty.

**What is not the cause:** the profiler — `dynamic_dependencies.txt` holds the same 9 RAW records on `b`
from the `b[i]` write into the `b[i-1]` read in both layouts (same instruction pairs, different call-path
state numbers); file ids are consistent across `FileMapping.txt`, `instructionID_to_lineID_mapping.txt`,
`Data.xml` and the loop markers; the allocation site (moved into instrumented code, same result).

**Where:** `new_do_all_detector.identify_simple_doall_and_reduction` blocks a loop only for a dependence
between nodes of two DIFFERENT iteration contexts of that loop, and the iteration contexts come from the
task graph's assignment of call-path states (`TaskGraph.__assign_state_ids`, `__duplicate_loop_iterations`).
With a second file the recurrence's states are evidently not placed in the loop's iteration contexts — the
same family as B5 (a loop state matched against loops of another function).

**Narrowing it:** the agent's own feature check `project-mode` profiles a two-FILE program through a unity
unit (`#include "kern.c"` after the other units) and there the recurrences ARE blocked. The s211 case that
fails includes the second file as a header whose functions are defined BEFORE the loop's function — the
order of function definitions across files is the first thing to test.

## B1 — clauses lost for files included through a relative path

**Symptom.** A Do-All in a file that clang records as `./src/kern.c` (a unit `#include`d
from another unit, compiled with `-I.`) is reported with empty `private`/`firstprivate`
lists; the generated pragma races.
**Cause.** `ASTLoader.build_path_mapping` matches AST file names to `FileMapping.txt` by
`endswith("/" + path)`; `./src/kern.c` never matches `…/src/kern.c`.
**Fix.** Normalise `./` and `..` segments before matching.
**Reproducer.** agent feature check `project-mode` (two-file program, unity unit).

## B2 — a loop with several back edges crashes the task-graph builder

**Symptom.** `ValueError: Invalid iteration structure found at node: Start IT …` in
`__assign_loop_contexts`, on every run. Rodinia `nw`'s traceback loop:
`for (i, j; i >= 0 && j >= 0;) { …; if (a) { i--; j--; continue; } else if (b) { j--; continue; } else if (c) { i--; continue; } }`.
**Cause.** `__break_cycles` takes ONE cycle from `nx.find_cycle`, marks its back edge as the
iteration exit and re-wires every other predecessor of the header to the new StartLoop
marker — including the loop's remaining back edges. That closes a second cycle through the
same header; the next pass chains a second StartIteration onto the first.
**Fix.** Every predecessor of the header that lies in the loop's own body (CUs in the
subtree of the innermost PET loop containing the header) is a back edge and gets its own
EndIteration marker in the first pass.
**Reproducer.** agent feature check `explorer-multi-backedge` (fails before, passes after;
Do-All and reduction sets on 2mm, a vector sum and NPB `is` byte-identical before/after).

## B3 — a loop ending an `else` block is not instrumented (root cause of the random `IndexError`)

**Symptom.** `IndexError: string index out of range` in `TaskGraph.recursive_assignment`
(`loopstate_info[loopstate_position]`), on some runs of the explorer and not on others, on
one unchanged profile: Rodinia `pathfinder` 40 of 60 runs, NPB `mg` 29 of 29 attempts.
**Cause (profiler).** `CFA.cpp` instruments a loop only if its header **and its exit block**
pass `sanityCheck` (contain an instruction with a debug line). Clang gives the branch that
ends an `else` block no debug location, so for

```c
if (argc > 1) { for (i…) for (j…) …; }      // for.end26:  br label %if.end, !dbg !824   → instrumented
else          { for (i…) for (j…) …; }      // for.end45:  br label %if.end              → NOT instrumented
```

the outer loop of the `else` branch gets neither `__dp_loop_entry` nor `__dp_loop_exit`
(the inner one does). `loop_meta.txt` and the CU graph still list it. The static call-path
states are built from the `__dp_loop_entry` calls found in the IR
(`get_loopIDs_in_function_body`), so `pf_init`'s loop-state strings have **5 positions for
6 loops**. The explorer numbers loop positions from the CU graph (6), so (a) position 5
indexes past the string — the `IndexError` — and (b) **every loop after the missing one is
matched to the wrong position without any error**, which changes which dependences count
as loop-carried. Whether a run crashes depends only on whether the traversal
(`ret_val or recursive_assignment(...)`, over sets) reaches the out-of-range context before
it short-circuits — hence "random", and independent of `PYTHONHASHSEED`.
**Fix.** `CFA.cpp` no longer requires a debug line in the exit block (a valid header is
enough); `instrumentLoopExit(bb, id, fallbackLID)` marks an exit block that has no line id
with the loop header's. **Measured:** `pathfinder`, one profile, explorer run ten times —
before 1 of 6 runs finished, after **10 of 10**; `pf_init`'s loop states have 6 positions
for its 6 loops. DiscoPoP's own profiler tests: 184 of 184 pass; the agent's suite passes.
What remains after the fix is B4 (1 run in 10 still reports 11 Do-Alls instead of 10).
**Reproducer.** agent feature check `profiler-else-loop` (5 positions before, 6 after);
`agent/prepared/rodinia-3.1/pathfinder/pathfinder.cpp` in the harness;
`discopop_cxx -S -emit-llvm` shows five `__dp_loop_entry` calls in `pf_init`; minimal form:
a function whose last statement inside an `else { … }` is a loop nest.

## B4 — explorer output differs between runs on one profile

Measured (harness T0.7, 60 runs per program): 2mm — the `shared()` clause of some Do-Alls
present or empty, 50 distinct task-pattern sets; `pathfinder` — 10 or 11 Do-Alls; NPB `is`
— 14 task sets. To be re-measured once B3 is fixed, since B3 makes the state matching
depend on traversal order.

## B5 — a loop state is matched against loops of another function

**Symptom.** Same `IndexError` as B3, but on every run, and with every function's loop-state
width correct (NPB `mg` after B3's fix).
**Cause.** In `recursive_assignment`, an `IterationContext` reads digit
`loopstate_position` of `callstate[0]` without checking that the string belongs to the
function owning that loop. After a missed state the search continues with
`ctx.successor`, which can be a context of the *caller*; its position then indexes the
callee's (shorter) string — or silently matches the wrong digit when it fits.
**Fix.** Return a miss unless `callstate[0].split("_loopstate")[0]` equals the name of the
loop's parent function.
**Reproducer.** NPB-CPP `mg` (class S) profiled through a unity unit; the explorer fails
within five minutes on every run without the check.

## P1 — call-path state assignment is exponential

`recursive_assignment` explores `ctx.get_contained_contexts()` and then `ctx.successor` for
every context, with no record of what it has already answered; the same (context, remaining
call path) pair is reached along many routes. Fix: memoise per state id (agent Fix 83).
NPB-C `CG`: > 20 min → < 1 s for this phase, identical Do-All/reduction sets. L2 and L3
below were measured BEFORE this fix and are to be re-measured.

## B7 — `loop_counter_output.txt` pairs iteration counts with the wrong loops

The profiler writes two records of how often a loop ran: the `BGN loop` markers in
`dynamic_dependencies.txt` (`<file>:<line> BGN loop <total> <entries> <avg> <max>`) and
`loop_counter_output.txt` (`<file> <line> <total>`). They disagree, and the markers are right.

Minimal reproducer (the agent's feature check `loop-counts`): an outer loop of 7 iterations
around two sibling loops of 998.

```c
for (int r = 0; r < R; r++) {                                   /* line 7:  R = 7   */
  for (int i = 1; i < N - 1; i++) { b[i] = b[i + 1] - a[i]; }   /* line 8:  7 x 998 */
  for (int i = 1; i < N - 1; i++) { a[i] = b[i - 1] + a[i]; }   /* line 9:  7 x 998 */
}
```

| loop | true total | `BGN loop` marker | `loop_counter_output.txt` |
|---|---:|---:|---:|
| line 7 (outer) | 7 | 7 | **6,986** |
| line 8 | 6,986 | 6,986 | 6,986 |
| line 9 | 6,986 | 6,986 | **1,000** (the count of the init loop at line 6) |

**Root cause** — `profiler/rtlib/injected_functions/dp_loop_output.cpp`, two defects in the
same ten lines. The counters are indexed by LOOP ID, and ids start at 0; the writer reads
`loop_meta.txt` (`<file> <loop id> <line>`) into a vector behind a dummy element and then
pairs by POSITION, starting at 1:

```cpp
loop_infos.push_back(loop_info_t()); // dummy
... loop_infos.push_back(loop_info);           // in FILE order, which is not id order
for (auto i = 1; i < loop_counters.size(); ++i) {
  loop_info_t &loop_info = loop_infos[i];      // the i-th LINE of loop_meta.txt, i.e. id i-1
  ofile << ... loop_info.line_nr_ << " " << loop_counters[i];   // the count of id i
```

So (a) every count is written against the loop whose id is one LOWER (the dummy shifts the
vector by one while the ids are 0-based), the count of id 0 is never written and the last
loop never gets one; and (b) where `loop_meta.txt` is not sorted by id — it lists ids
`0 1 2 3 4 8 7 6 5` for the `s211` rewrite — position and id disagree further. This reproduces
the file exactly: line 160 (id 0) gets id 1's 32,000, line 109 (id 1) gets id 2's 48, line 136
gets 137's 1,535,904, line 140 (id 4) gets id 5's 160.

**Patch** — pair by id, from 0:

```cpp
std::unordered_map<int, loop_info_t> by_id;          // instead of the vector + dummy
...   if (cnt == 3) by_id[loop_info.loop_id_] = loop_info;
for (size_t i = 0; i < loop_counters.size(); ++i) {
  auto it = by_id.find(static_cast<int>(i));
  if (it == by_id.end()) continue;
  ofile << it->second.file_id_ << " " << it->second.line_nr_ << " " << loop_counters[i] << "\n";
}
```

**Upstream status (checked 2026-09-21):** `dp_loop_output.cpp` is byte-identical in
`new_explorer` at `28ac4d47` (17 Sep 2026), so the defect is present there. **Who is affected:**
NOT the explorer's pattern detection — it takes its loop data (`LoopData`: total, entries,
average, maximum) from the `BGN loop` markers of the dependence file
(`utilities/PEGraphConstruction/parser.py`; `loop_counter_file` is still passed around, with a
`TODO` saying it should not be needed). So DiscoPoP's own suggestions are correct, and this
project's DiscoPoP-alone baseline is untouched. Affected is whoever reads the file itself —
this agent did, until Fix 88. **Not yet patched in this project's DiscoPoP:** the runtime is
linked into every profiled binary, a rebuild on two machines in the middle of a running
experiment is not acceptable, and since Fix 88 nothing here reads the file; the patch above
goes in after the campaign together with the rebase onto current `new_explorer`. Extent, over 41 profiles of the evaluation's
benchmarks (PolyBench, TSVC-2, `md`, `is`, `hotspot`, `pathfinder`): **277 of 337 loop counts
(82 %) differ from the marker of the same run, in 38 of 41 programs** — typically the outer
repetition loop carries its inner loop's total (TSVC: 48 reported as 1,536,000).

Consequence for any consumer of the file: workload estimates are wrong by orders of
magnitude in both directions. In the agent it fed the ranking proxy used when no hotspot
measurement exists, and the "N iterations" stated to the model in every prompt header.
Workaround (agent Fix 88): read the totals from the `BGN loop` markers; the file is only the
fallback for a loop without a marker.

## N1 — hotspot detection accumulates across builds (usage hazard)

`discopop_hotspot_cxx` APPENDS the region ids of every build to
`hotspot_detection/private/cs_id.txt` (`temp.txt` holds the running id count: `19`, then
`39`), every run of the instrumented binary writes another `hotspot_result_<n>.txt`, and
`discopop_hotspot_analyzer` averages over the runs. For several inputs of ONE program that is
the intended design. After the SOURCE changes it silently produces a wrong answer: the
analyzer reports the first build's region table — the old line numbers (`main` at 147 where
the edited file has it at 149), every average halved by a run that never executed those ids,
and no entry for a region the edit created — without any warning. A tool that re-measures an
edited program must delete `hotspot_detection/` first (agent Fix 87). A cheap upstream guard:
store a hash of the source beside `cs_id.txt` and refuse, or reset, on a mismatch.

Where: `hotspot_detection/HotspotDetection/HotspotDetection.cpp` opens `cs_id.txt` (lines 515, 723)
and `temp.txt` (784) with `std::ios_base::app`. **Upstream status (checked 2026-09-21):** the pass is
unchanged in `new_explorer` at `28ac4d47`; `hotspot_analyzer.py` has been reworked there (83 lines),
so the averaging should be re-checked after the rebase, but the appending is the same.

## B6 — the patch generator sometimes never returns

`discopop_explorer` ends by running `discopop_patch_generator` as a subprocess
(`discopop_explorer.py:327`). On the agent's `explorer-multi-backedge` program (40 lines,
two loops with `continue`s), 3 of 20 explorer runs on one unchanged profile hang in that
subprocess (stack: `subprocess.communicate`), with or without Fix 83. Not yet diagnosed;
callers should give the explorer a timeout — the agent and the harness do since 2026-09-21
(`--explorer-timeout`, 600 s per attempt, a stalled draw repeated up to 5 times).
