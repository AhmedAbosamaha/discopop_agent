# Bugs found in DiscoPoP itself — for the DiscoPoP maintainers

Written for: the DiscoPoP developers (TU Darmstadt). Every change this project made, or
needs, **inside DiscoPoP** (profiler, runtime, explorer) is listed here with symptom, root
cause, a minimal reproducer and the patch, so it can be reported upstream. The agent's own
fixes are in `FIXES.md`; this file holds only what concerns DiscoPoP's code.

Rule of the thesis: a bug found in DiscoPoP is fixed, the **fixed DiscoPoP is used in every
arm** — the DiscoPoP-only baseline included — and the fix is stated in the thesis.

DiscoPoP version: the checkout under this repository (`profiler/`, `rtlib/`, `explorer/`),
LLVM 19 (macOS) and LLVM 20 (Linux).

| # | Component | Status | One line |
|---|---|---|---|
| B1 | explorer, `ASTLoader.build_path_mapping` | fixed (agent Fix 78) | files reached through a relative include path lose every `private`/`firstprivate` clause |
| B2 | explorer, `TaskGraph.__break_cycles` | fixed (agent Fix 80) | a loop with several back edges (`continue`) crashes the task-graph builder |
| B3 | profiler, `utils/CFA.cpp` + `instrumentLoopExit` | **diagnosed, fix pending** | a loop that is the last statement of an `else` block gets no loop markers → explorer `IndexError` at random, and silently wrong loop-state matching |
| B4 | explorer, task-graph traversal order | open (consequence of B3, to re-measure after it) | the explorer's output differs between runs on one unchanged profile |
| L1 | profiler | limitation | NPB-CPP `lu` (4,134 lines): the instrumenting compile exceeds two hours |
| L2 | profiler + explorer | limitation | Rodinia `nw`: 531,606 call-path states; the explorer's state assignment needs ≈ 25 h |

---

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
**Fix (planned).** In `CFA.cpp`, do not require a debug line in the exit block; in
`instrumentLoopExit`, fall back to the loop header's line id when the exit block has none.
Then re-measure explorer determinism (T0.7) and profile stability (T0.2).
**Reproducer.** `agent/prepared/rodinia-3.1/pathfinder/pathfinder.cpp` in the harness;
`discopop_cxx -S -emit-llvm` shows five `__dp_loop_entry` calls in `pf_init`; minimal form:
a function whose last statement inside an `else { … }` is a loop nest.

## B4 — explorer output differs between runs on one profile

Measured (harness T0.7, 60 runs per program): 2mm — the `shared()` clause of some Do-Alls
present or empty, 50 distinct task-pattern sets; `pathfinder` — 10 or 11 Do-Alls; NPB `is`
— 14 task sets. To be re-measured once B3 is fixed, since B3 makes the state matching
depend on traversal order.
