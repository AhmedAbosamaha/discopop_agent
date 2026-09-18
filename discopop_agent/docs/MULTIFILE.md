# Multi-file programs — what was measured, what was built

**Status:** implemented 2026-09-17 (`project.py`, the build seam in `gate/patching.py`,
`profiling/tools.py`, file-aware planning, evidence, fast refresh, phases and Settle).
Single-file runs are unchanged: with no `--project-dir` no new code path is taken, and the
28 feature checks pass as before.

## The question

The agent took exactly one `--source-file`, so every benchmark had to be merged into one
translation unit. That is a packaging deviation a thesis has to declare. DiscoPoP itself
ships `CC/CXX/CMAKE/LINKER_wrapper.sh` for whole projects and identifies every region by
**file id and line** (`FileMapping.txt`). So: is merging necessary, and if not, what is the
right way to handle a program made of several files?

## Measurement 1 — DiscoPoP's unit-by-unit profile is unsafe outside `main`'s unit

A two-file program (`docs` reproducer: `src/kern.c` with `kernel()` and `smooth()`,
`src/main.c` calling them; feature check `project-mode`):

```c
void kernel(int n) {                       void smooth(int n) {
  for (i = 0; i < n; i++)        /* L7  */   for (i = 1; i < n; i++)          /* L14 */
    for (t = 1; t < T; t++)      /* L8  */     b[i] = b[i-1]*0.5 + a[i][T-1];
      a[i][t] = a[i][t-1]*0.5 + 1.0;       }
}
```

L7 is independent; **L8 and L14 are recurrences**.

| how it was profiled | L7 | L8 | L14 | `doall_prevented.json` |
|---|---|---|---|---|
| merged into one file | Do-All ✓ | blocked ✓ | blocked ✓ | RAW on `a` (L8), RAW on `b` (L14) |
| two units, one wrapper call (`discopop_cc a.c b.c`) | Do-All | **Do-All ✗** | **Do-All ✗** | empty |
| two units, compiled separately and linked (DiscoPoP's documented way) | Do-All | **Do-All ✗** | **Do-All ✗** | empty |
| **unity unit** (one file that `#include`s both) | Do-All ✓ | blocked ✓ | blocked ✓ | same as merged |

**Cause.** This DiscoPoP build classifies a dependence as loop-carried from *call-path
states*. The state graph is constructed statically while compiling the unit that contains
`main`, and nothing links it across units: in the two-unit profile
`main-->call_38-->kernel` is a leaf — the 20 loop states the merged profile has beneath it
(`kernel-->kernel_loopstate03-->…`) do not exist, the runtime warns `No transition found
from state 18`, and every dependence inside `kernel`/`smooth` carries the same state. The
explorer cannot then tell one iteration from the next and reports the loop parallel. The
error is in the **unsafe** direction. Instruction ids, by contrast, are unique across units
(the counter is persisted), and the dependences themselves are recorded correctly.

So merging was not only a convenience: with this DiscoPoP version a whole-program view is
what makes its analysis correct for every function outside `main`'s unit.

## Measurement 2 — a unity unit gives the whole-program view without merging anything

```c
/* dp_agent_unity.c — generated, removed again after the compile */
#include "src/kern.c"
#include "src/main.c"
```

Compiled by the wrapper as ONE unit, DiscoPoP sees one module and builds one state graph.
Because `#include` keeps file names and line numbers in the debug information,
`FileMapping.txt` lists the **real files** (`1 src/kern.c`, `2 src/main.c`) and every region
is reported at its **real line**. No source is merged, no line number is translated, and
the result is identical to the merged-file analysis (table above).

Limit: a unity unit does not compile when two units define the same `static` symbol or
leak conflicting macros. That is detected (the wrapper fails) and reported; such a program
needs `--build-cmd` plus a per-unit profile, with the warning that DiscoPoP's verdicts
outside `main`'s unit are then not to be trusted — the gate still is.

## Design

```
                 profile (DiscoPoP)                    judge (gate)                 edit
 project ──► unity unit ─► wrapper ─► run ─► explorer   stage tree ─► replace the    the region's
             (whole program, real file ids)             focus file ─► build ALL      OWN file
                                                        units ─► TSan/stress/output
```

* **`Project`** (`project.py`): root, translation units, include directories, flags,
  optional `--build-cmd`. Discovered from the tree unless given. It can `stage()` itself
  into a temp directory with some files replaced, and write its unity unit.
* **One build seam** (`gate/patching.run_build`): every compile the gate performs — plain,
  `-fopenmp`, ThreadSanitizer, the schedule-stress build, timing, the numerical calibration
  variants, the reference — already handed ONE candidate file to one of three functions.
  Those now share `run_build`. Single file: the same command as before. Project: the tree is
  staged fresh, the candidate replaces the **focus** file, all units are compiled (or
  `--build-cmd` runs with `CC/CXX/CFLAGS/CXXFLAGS/LDFLAGS` and `{cc} {cxx} {flags} {out}`).
  The user's tree is only ever read. What is judged is the real multi-file program.
* **The focus** (`project.work_on`): "the file under work". Phases point it at each
  region's own file; `args.source_file` follows. With no project it never changes.
* **Planning and evidence by file**: a region's file is resolved through `FileMapping.txt`
  (regions outside the project root are not editable and are skipped); dependences,
  reductions and static-only variables are filtered by file id, and an endpoint in another
  file is reported as unplaced instead of as that line number in this file.
* **Fast refresh by file**: the line map describes the ONE rewritten file. Instruction
  positions, loop markers and counters of every other file pass through unchanged. Without
  that, 22 of `main.c`'s 23 observed dependences were lost on a refresh after an edit to
  `kern.c` (mutation-tested).
* **Settle over a set of files**: originals are kept per file; the change log names each
  change's file; the rebuild restores and replays per file; the final check builds the
  finished program with the file that carries a pragma as its focus, so the parallel track
  of the gate covers every pragma in the program.
* **Direct edit mode**: the model's private working copy is the whole staged tree, with the
  file to edit at its real relative path — it can read the headers and callers; only its
  changes to that one file are taken back.

New arguments (all optional; without `--project-dir` nothing changes):

```
--project-dir DIR        the program's root; turns project mode on
--project-units a.c,b.c  translation units in build order   (default: discovered, sorted)
--project-include d1,d2  include directories                (default: directories holding headers)
--project-cflags "..."   extra compile flags for every build
--project-ldflags "..."  extra link flags
--build-cmd CMD          the project's own build, run in the staged copy
--project-binary NAME    what --build-cmd produces           (default: a.out)
--profile-only           take the (unity) profile and stop — lets a harness profile once
```

`--discopop-dir` must be `<project-dir>/.discopop`. When no profile exists the agent takes
it itself, because a profile taken the documented DiscoPoP way is the unsafe one.

## A trap in the unity build: the path clang records

The explorer classifies a loop's variables (`private`, `firstprivate`, `shared`) from the
AST dump the wrapper writes, and matches AST file names to `FileMapping.txt` by suffix.
Compiled by a **relative** name with `-I.`, clang records an included unit as
`./src/kern.c`, the suffix match fails, every declaration in that file is invisible, and
every Do-All in it loses its clauses — a `private` missing is a data race, which the gate
then rejects. Measured: `privtemp` as a project, DiscoPoP's pragma dropped at `tsan`;
compiled by the absolute path, the same loop gets `private(t, i)` and the pragma is applied
and verified FASTER. The agent always compiles the unity unit by its absolute path (and
`-I<root>` absolute); the harness does the same; and the explorer's matcher
(`ASTLoader.build_path_mapping`) now normalises `./` and `..` segments first
(23 explorer tests pass). The feature check `project-mode` asserts the clauses.

## What this means for measurements already taken

Everything measured so far was measured on merged single files. None of it becomes wrong;
some of it becomes *specific to that packaging*, and the thesis says which:

* **T0.1 sizes, T0.5 runtime shares, T0.6 DiscoPoP suggestions** — per packaged file. They
  are re-run for any benchmark whose packaging changes. For a benchmark that was one file
  to begin with (all 30 PolyBench kernels) nothing changes.
* **T0.2 / T0.7** (DiscoPoP's variation) are properties of DiscoPoP; the explorer crash rate
  may differ per program and is re-measured where packaging changes.
* **Pilots and `local_obs1`** stay valid as records of the single-file configuration.
* A benchmark is measured in ONE packaging; merged and project results never share a table.
* **Merged ≡ unity for DiscoPoP's analysis** (Measurement 2), so switching a benchmark from
  its merged file to its original files is not expected to change what DiscoPoP reports —
  which is itself checked per benchmark before a switch (same patterns, same blockers).

## Costs that are NOT the merge

NPB `lu`: DiscoPoP's instrumenting compile exceeds one hour both as the merged 4,134-line
file and as the original make project (it stalls in `erhs`); `mg` (2,133 lines merged)
takes 6.4 s. The cost is in `lu.cpp`, not in the packaging.
