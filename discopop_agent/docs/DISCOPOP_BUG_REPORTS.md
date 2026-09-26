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
| B4 | explorer, task-graph construction order | open — re-measured 26 Sep after B3: still present, mechanism narrowed (below); fixing it is the author's decision | the explorer's output differs between runs on one unchanged profile — on TSVC s112 it misses the textbook recurrence in 6–7 of 8 draws |
| P1 | explorer, `TaskGraph.__assign_state_ids` | fixed (agent Fix 83) | performance: the state assignment re-answers the same (context, call path) pair exponentially often — hours on `mg`/`nw`, seconds once memoised |
| B6 | `discopop_patch_generator` (called by the explorer) | open | hangs on some runs: 3 of 20 explorer runs on one unchanged profile of a 40-line program never return from the patch-generator subprocess |
| B7 | profiler runtime, `dp_loop_output.cpp` → `loop_counter_output.txt` | root cause found, patch written, worked around (agent Fix 88); present in upstream `new_explorer` `28ac4d47` | the per-loop iteration counts are paired with the WRONG loops: 277 of 337 counts (82 %) over 41 profiles disagree with the `BGN loop` markers of the same run |
| N1 | hotspot detection (`hotspot_detection/private/`) | usage hazard, not a bug (agent Fix 87) | region ids and results ACCUMULATE across builds and runs by design; re-instrumenting a CHANGED program into the same directory reports the old program's lines, halved times, and nothing for new regions |
| L1 | profiler | limitation | NPB-CPP `lu` (4,134 lines): the instrumenting compile exceeds two hours |
| L2 | profiler + explorer | limitation | Rodinia `nw`: 531,606 call-path states; the explorer's state assignment needs ≈ 25 h |
| L5 | explorer | limitation (a cheap reproducer of B4) | TSVC-2, ~30 lines per loop: the explorer normally finishes in **4 s**, but on a RANDOM ~2 loops of 25 per profile it does not finish at all — `s291` 5,403 s, `s3112` > 80 min on one draw and **5.8 s** on the next, `s322` and `s331` 4 s on one draw and stalled on the next. Every stall stops at the same point, a progress bar at `0/11`. Instrumentation and the profiled run take 0.2 s, so it is the explorer alone; `s291`'s profile holds **117 task patterns** for one loop nest — the signature of L3 (NPB `mg`) at a tiny scale, which may make these the smallest reproducers of it |
| L4 | profiler | limitation | PolyBench `adi` (~130 lines): the instrumenting compile takes **2,387 s (40 min)** per profile, ~40x the next slowest PolyBench kernel. The profile is usable (19 Do-Alls, gate-verified parallel), so this is a cost limitation, not a failure |
| B8 | profiler, `llvm_hooks/runOnBasicBlock.cpp` (call-path states) | fixed 26 Sep (f6b41f57) | a call into a function the pass does not instrument (defined outside the project root) enters its call state for good → every later dependence carries the wrong call path → a true recurrence reported Do-All |
| B9 | explorer, `TaskGraph.__assign_state_ids` | fixed 26 Sep | the accesses of a function called inside a loop iteration are attached to no context → a loop carrying a dependence through a callee is reported Do-All (every TSVC package's repetition loop) |
| B10 | explorer (Do-All detector / reduction detection) | open, confirmed with a 30-line reproducer | a scalar carried across iterations (`x = b[i]` read next iteration; `s += …`) → the patch generator emits `parallel for shared(x)` and a plain `parallel for` on the sum — both races |
| B11 | explorer, `TaskGraph.__assign_state_ids` | candidate | in TSVC v3's `main`, no access made under the five `pb_emit_array` calls is attached to any context (before and after B9's fix); harness code only |
| L3 | explorer | limitation | NPB-CPP `mg`: with P1's fix the state assignment is fast, but the run then stays in task-pattern detection (`new_task_detector`) — a first run was read at 4 h 19 min, the same run was stopped unfinished after **11 h 24 min** at 100 % CPU on the server (19–20 Sep); the Do-All detector is not reached. Not usable per trial |

---

## B9 — a loop reported Do-All although a function it calls carries a dependence into its next iteration (explorer)

**Found** 26 Sep 2026 (T0.15 repeated on the fixed profiler; E1c's logs). **Status:** FIXED 26 Sep 2026 in
the explorer (`TaskGraph.__assign_state_ids`, `recursive_assignment_uncached`); fixed before E2-B1 by the
author's decision (D14; E2-B1 had not started; it restores D38's matched twin). E1c-v3.1 ran on the pre-fix
explorer and is reported as such.

**Symptom.** Every TSVC package's repetition loop calls `pb_mix(nl)`, which changes a few input elements
between repetitions, so repetition `nl+1` reads what `pb_mix` wrote in repetition `nl` — a true dependence
that makes the loop sequential. DiscoPoP reports that loop Do-All on 9 of the 18 class-R loops of E1c (s127,
s252, s254, s255, s291, s292, s293, s331, s341; one profile per run, all trials), in both packaging layouts.
The gate rejects the pragma at `correctness` every time, so no arm ever shipped it: DiscoPoP alone, the
agent's Phase B and T0.11's classes are unaffected. With agent v3.1's re-queue the rejected region goes to
the model (E1c-v3.1: the re-queue fired on exactly this false Do-All).

**Not the profiler:** in s254's profile `dynamic_dependencies.txt` holds the RAW from `pb_mix`'s write of
`b[k]` (line 100) to the kernel's read of `b[i]` (lines 137, 138) and from the write of `b[LEN_1D-1]` (102)
to `x = b[LEN_1D-1]` (135). The explorer's Do-All check (`new_do_all_detector`) blocks a loop only for a
dependence between nodes of two different iteration contexts of that loop — and the callee's accesses were
in no context at all.

**Root cause.** A call-path state names the path from `main` to an access, e.g.
`main-->call_44-->_ZL6kerneli-->_ZL6kerneli_loopstate03-->call_125-->_ZL3mixi` for `mix`'s accesses inside
the kernel's repetition loop (after the pre-processing that keeps only the last of consecutive loop states,
a loop state can be followed only by `call_N` or by nothing). `recursive_assignment_uncached` walks the task
graph along it: a `FunctionContext` consumes the function name, an `IterationContext` rewrites its loop's
digit of the loop-state element to the processed marker `4`, an `InlinedFunctionContext` consumes
`call_<id>`. Once no open iteration digit (0/1/2) was left, the loop-state element was dropped ONLY if it
was the last element (`len(callstate) == 1`). When a call followed, the processed element stayed at the
head: the `InlinedFunctionContext` requires a `call_` head and missed, a `FunctionContext` strips the
element and then compares its name against `call_125` and missed — the state was attached nowhere. So every
access a callee makes inside a loop iteration was lost to the task graph, and with it every dependence that
runs through the callee: into the caller's next iteration (`pb_mix` → the kernel's reads) or inside the
callee itself (a counter incremented per call).

**Fix** (five lines). Drop a fully processed loop-state element whenever no open iteration digit remains,
whether or not elements follow; matching then continues with the call. Reach, by construction: the changed
branch fires only for a state whose path continues after a fully matched loop state — a callee invoked
inside a loop — and those states were previously attached nowhere; every other state takes the identical
code path. The fix can therefore only ADD attachments, i.e. dependences: it can block a loop or change a
clause, never create a Do-All.

**Verified (26 Sep, Mac, LLVM 19; the pre-fix explorer run from a copy of HEAD on the SAME profile, each
explorer run on a pristine copy of `.discopop`):**

- Reproducer below: loop 14 Do-All in 5 of 5 pre-fix runs; after the fix 5 of 5 not, blocked
  (`doall_prevented.json`) by the RAW on `b`, whose only writes inside the loop are `mix`'s. With `mix`
  inlined by hand: `patterns.json` identical before and after (3 runs each).
- A counter in the callee (`emit`: `cnt++`), called in a loop: Do-All before, blocked on `cnt` after; the
  same with the call under an `if`, and with a callee holding four such loops, called twice.
- A pure callee (`sq`: only its own locals, fresh per call): the loop stays Do-All before and after (2 of 2
  each) — the fix does not make a call itself a dependence.
- s254 (v3), one profile, two runs each: the repetition loop (134) Do-All before, blocked on `b` after;
  every other Do-All unchanged.
- TSVC-2, all 33 v3 packages, one profile each, one pristine run of each explorer: the repetition loop's
  false Do-All is gone on 18 (s000, s127, s252, s254, s255, s291, s292, s293, s3112, s313, s323, s331, s341,
  s4113, s4114, s4115, s4117, s491); 11 packages identical; no clause and no reduction changed anywhere.
  On four (s121, s212, s243, s244) a kernel loop that carries a TRUE dependence got different verdicts in
  the two single runs. Over 15 pristine runs of each explorer it is reported Do-All 11, 8, 7, 10 times
  before the fix and 12, 11, 11, 11 after (pooled 36/60 against 45/60, Fisher two-sided p = 0.12) — a draw
  either way (B4). To separate the fix from B4, the state assignment was run twice IN ONE PROCESS on the SAME
  task graph, with the old rule and with the fixed one: in 12 of 12 runs over five packages (s112, s121,
  s212, s243, s244) exactly three states are attached differently, all three `pb_mix`'s (a callee in the
  loop), and every kernel state is attached identically — also in the runs that report the recurrence
  Do-All. The rate difference comes from how each process builds the graph (identical code in both
  versions), not from the rule.
- The agent's feature check `b9-callee-in-loop` (the three loops above in one program): fails on the
  pre-fix explorer (3 of 3 runs), passes after (3 of 3). The whole feature suite 57 of 57; the explorer's
end-to-end unit tests 31 of 31 (run with the venv's `bin` first on `PATH` — otherwise another DiscoPoP
installation on `PATH` is the one tested); mypy clean on `TaskGraph.py`.

**Reproducer** (`k.c`, 30 lines; the loop at line 14 is the one reported Do-All before the fix; line 16 and
line 29 are B10):

```c
#include <stdio.h>
#include <stdlib.h>
#define N 2000
static double a[N], b[N];
static void mix(int nl)
{
    long k = ((long)nl * 7919L + 13L) % N;
    a[k] += 0.25; b[k] += 0.25;
    b[N - 1] += 0.125;
}
static double kernel(int reps)
{
    double x;
    for (int nl = 0; nl < reps; nl++) {
        x = b[N - 1];
        for (int i = 0; i < N; i++) {
            a[i] = (b[i] + x) * 0.5;
            x = b[i];
        }
        mix(nl);
    }
    return 0.0;
}
int main(void)
{
    for (int i = 0; i < N; i++) { a[i] = 0.5 + i % 7; b[i] = 1.0 + i % 5; }
    kernel(6);
    double s = 0.0;
    for (int i = 0; i < N; i++) s += a[i] + b[i];
    printf("%.6f\n", s);
    return 0;
}
```

## B10 — a scalar carried across iterations: the patch generator emits a racy pragma (explorer)

**Found** 26 Sep 2026 (T0.15: the inner loop carrying a scalar — `x`, `sum`, `j` — is Do-All in v4 for
s254 and s3112 and in v3 for s341; confirmed on B9's reproducer). **Status:** open, confirmed; root cause
not located.

**Symptom.** On B9's reproducer above (with B9 fixed), DiscoPoP's own patch generator writes
`#pragma omp parallel for shared(x)` on line 16 — `x = b[i]` is read by the next iteration — and a plain
`#pragma omp parallel for` on line 29, `s += a[i] + b[i]`, with no reduction clause (`reduction.txt` is
empty for this program). Both are races: on the first profile in 10 of 10 explorer runs (5 before B9's
fix, 5 after), and on two fresh profiles in the one run made on each.

**What is known.** Not the profiler: the carried RAW is in the profile (`106 NOM RAW 117|x`, and on `s`)
in 3 of 3 fresh profiles (the first profile lacked it; the explorer's verdict is the same either way). Not B9's
mechanism: no call is involved. The same-shaped inner loop of s254 (line 136, `x = b[i]` read next
iteration) IS blocked on the RAW on `x` (2 of 2) — the contrast between the two programs is the lead.
Scalar records carry no call-path state (`NOM RAW 117|x`, no `@state`), so how they reach the iteration
contexts is the first thing to read. The gate catches both loops at `correctness`; no arm ships them.

## B11 — candidate: no access under TSVC v3's `pb_emit_array` calls is attached (explorer)

**Found** 26 Sep 2026 while verifying B9. In s254 (v3) none of the 109 call-path states under
`main-->call_134-->_ZL13pb_emit_arrayPKd…` (the five `pb_emit_array` calls after the kernel) is attached
to any context, before or after B9's fix, while `main`'s earlier calls (`init_array`, the kernel,
`pb_emit(result)`) are; so `pb_emit_array`'s loops, which carry a dependence through `pb_emit`'s counters,
stay Do-All. A 25-line program with the same shape (a direct call to the callee, then two calls of a
function holding four such loops) does NOT reproduce it: B9's fix blocks all four loops there. Harness code
only — the evidence given to the models excludes it and packaging v4 moves it out of the file — so it
blocks nothing; mechanism not investigated.

## B8 — a true recurrence reported as Do-All when the program spans two files (explorer, call-path states)

**Found** 25 Sep 2026 (T0.15, `evaluation/agent/tools/harness_equivalence.py`), while moving a benchmark's
measurement code into a second file. **Status:** FIXED 26 Sep 2026 in the profiler (root cause below); the
explorer analysis in the original note was a symptom.

**Root cause (26 Sep, profiler — the call-path state machine).** `main` calls a harness function
(`pb_setup`) defined in the same translation unit but in a header OUTSIDE `DP_PROJECT_ROOT_DIR`, so
`runOnFunction` does not instrument it. The call site IS instrumented (`__dp_call`), and the pass passed
`isLibraryFunction = F->isDeclaration()` — false for a definition — so the runtime entered the callee's
call state (`update_callstate_from_call`). The callee has no instrumented exit, so that state was never
left: every later access — the kernel's included — was recorded under `main-->call-->pb_setup`
(`stateID_to_callpath_mapping.txt`, state 37 on the `b` recurrence of s211), the runtime printed "No
transition found … State might be incorrect from here on!", and the explorer, matching call paths
function by function (`TaskGraph.__assign_state_ids`), could place none of those dependences inside the
kernel's loop contexts: the loop's iteration contexts carried only the loop counters' dependences, so it
was reported Do-All. Reproduced 26 Sep with s211 in packaging v4 (harness header via CPATH outside the
package): both kernel loops Do-All in every draw; the same code in v3: neither.

**Fix.** One decision for "does this pass instrument F?" (`DiscoPoP::isInstrumentedFunction`: a
definition inside the project root, not one of the helper names, with a file id), used by
`runOnFunction` and at every call site: `isLibraryFunction = F->isDeclaration() ||
!isInstrumentedFunction(*F)` (`llvm_hooks/runOnBasicBlock.cpp`). A call into a function this pass does not
instrument no longer enters its call state — exactly as for a library function.

**Why the first note missed it.** It said every function lay inside the project root and was instrumented.
It did not: `DP_PROJECT_ROOT_DIR` defaults to the directory `discopop_cxx` runs in (the trial's working
copy, `CXX_wrapper.sh`), and v4's harness headers live in `prepared/_harness/`, outside it — so the
harness's functions were compiled into the unit but never instrumented. Any program that calls a function
defined outside the project root (a header-only library in an include directory, say) was exposed.

**Verified (26 Sep, Mac, LLVM 19).** Profiler tests 184 of 184. s211 in packaging v4: Do-All on both kernel
loops before, none after. One-file programs unchanged: s211, s000, s1213, s331 and s4113 (packaging v3),
profiled with the pre-fix build (a separate venv built from the commit before the fix) and with the fixed
one — every dependence (run-specific stack ids and order normalised), every call-path state, every
transition and `Data.xml` identical. The agent's feature suite 56 of 56 on the fixed build, with a
regression check (`b8-outside-root`) that fails on the pre-fix profile and passes after.

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

**Where (the original analysis — the symptom, not the cause):** `new_do_all_detector.identify_simple_doall_and_reduction` blocks a loop only for a dependence
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

**Re-measured 26 Sep 2026 (B3, B5, B8 fixed; while verifying B9) — still present, and it decides a
verdict.** TSVC s112 (v3), `a[i+1] = a[i] + b[i]` run backwards — a textbook recurrence. ONE profile,
every explorer run on a pristine copy of `.discopop`, 8 runs each: the inner loop (line 134) is reported
Do-All in **7 of 8** runs of the pre-fix explorer and **6 of 8** with B9 fixed. The outcome follows one
thing exactly: whether four of the kernel's call-path states — `_ZL11kernel_s112v_loopstate01`, `…02`,
`…21`, `…22` (inner iterations 1 and 2 inside outer iterations 0 and 2) — are attached to a context. Every
run that attaches them (10 → 14 attached states before the fix, 13 → 17 after) blocks the loop on the RAW
on `a`; every run that does not reports it Do-All. The same on s121, s212, s243 and s244, each with a
true dependence in the kernel's inner loop: Do-All in 7 to 12 of 15 runs per explorer version (B9's
verification). Not a cycle in the state walk (an instrumented copy
counted 0 re-entries of a pair still being answered). `Context.contained_contexts` is a Python `set` of
context objects, so its iteration order follows object addresses and changes from run to run; the task
graph built from it — which iteration contexts exist and where the inner loop's copies sit — is the
suspect. Consequence for the campaign: DiscoPoP's verdict on a loop is itself a draw (T0.15's "draw
noise" mixed this with profile noise). The gate catches the false Do-All; the verdict decides where the
agent routes a region.

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
