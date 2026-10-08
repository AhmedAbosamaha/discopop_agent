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
| B4 | explorer, `TaskGraph.__duplicate_loop_iterations` | fixed 26 Sep (root cause found: nested loops duplicated in set order) | the explorer's output differs between runs on one unchanged profile — on TSVC s112 it reported the textbook recurrence Do-All in 7 of 8 runs; after the fix the Do-All sets of all 33 TSVC packages repeat run to run |
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
| B10 | explorer (Do-All detector, loop variables) | fixed 27 Sep | a scalar carried across iterations (`x = b[i]` read next iteration; `s += …`) → the patch generator emits `parallel for shared(x)` and a plain `parallel for` on the sum — both races |
| B11 | explorer, `TaskGraph.__assign_state_ids` | explained by B15 (27 Sep) | in TSVC v3's `main`, no access made under the five `pb_emit_array` calls is attached to any context: `pb_emit_array` holds a loop the task graph does not model, so its other loops read the wrong loop-state digit (B15); fixed with B15; harness code only |
| B12 | profiler, `scripts/CC_wrapper.sh`, `CXX_wrapper.sh` | fixed 27 Sep | the compiler wrappers exit 0 when the instrumented compile or link fails — the AST dump after it sets the exit status; the failure surfaces one step later as a missing `a.out` |
| B13 | explorer, `TaskGraph.__insert_data_dependencies_from_files` + Do-All detector | fixed 27 Sep | a loop whose only cross-iteration dependence is a WRITE-AFTER-WRITE on an array element (a scatter `x[idx[i]] = …` whose indices repeat) is reported Do-All: the task graph dropped every WAW as "no data flow"; its pragma races (Rodinia bfs's frontier loop in E2-B1) |
| B14 | profiler, `static_analysis/calltree_construction.cpp` (loop states of the call path) | **fixed 7 Oct** | two loops side by side inside a loop are modelled as nested in each other, and the later loop's iterations are never recorded. Two faces: a dependence carried by the OUTER loop blocks the later loop's Do-All (the shape every loop distribution inside a repetition loop creates), and a dependence BETWEEN the later loop's own iterations is not seen — a recurrence reported Do-All |
| B15 | explorer, `TaskGraph.__assign_loopstate_positions_within_functions` / task-graph loops | fixed 27 Sep | a `do … while` loop gets no loop context in the task graph, so the loop-state digit positions of every loop in the function after it are off by one: no call-path state under the `do … while` matches, every dependence recorded there is lost, and a textbook recurrence nested in it is reported Do-All (Rodinia bfs: all 1,500 dynamic dependences of the kernel lost) |
| B18 | explorer (suspected: the carried-scalar rule of B10's fix) | candidate, 7 Oct | on PolyBench the current DiscoPoP reports no Do-All for outer loops it reported on 20 Sep — `correlation`, `covariance` (one directive, 5–6×, race-clean in three draws then; none now), `gramschmidt`, `fdtd-2d` (the directive now on a smaller loop: 8× → 0.35×, 5× → 0.6×); the blockers it names are the inner loops' own counters (`i`, `j`), declared at the top of the function |
| B19 | explorer (data-sharing classification: `last_private`) | candidate, 7 Oct; found wider 8 Oct | a variable written in the loop and read after it is classified `last_private` without asking whether the sequentially last iteration assigns it. Three faces: a scalar assigned under a condition (`if (a[i] < 0) j = i;`, TSVC `s331`: `parallel for lastprivate(j)` returns the last CHUNK's value — wrong output, the gate refuses it every time); the counter of the enclosing loop on `s481` (`lastprivate(nl)`, never written by the loop: accepted and shipped, right only because the compiler leaves the unspecified value alone); whole stack arrays in the model's rewrites (`lastprivate(a_old)`: wrong output, refused) |
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

## B10 — a scalar carried across iterations reported Do-All (explorer)

**Found** 26 Sep 2026 (T0.15: the inner loop carrying a scalar — `x`, `sum`, `j` — is Do-All in v4 for s254 and
s3112 and in v3 for s341; confirmed on B9's reproducer); systematic on the server 27 Sep. **Status:** FIXED
27 Sep 2026 in the explorer, before E2-B1 by the author's decision ("yes fix b10 go ahead"; D14).

**Symptom.** DiscoPoP's own patch generator writes `#pragma omp parallel for shared(x)` on a loop whose next
iteration reads the `x` this one wrote, and a plain `parallel for` on `for (…) s += a[i] + b[i];` with no
reduction clause — both races; the agent's `prefix_sum.cpp` (`running += …; out[i] = running;`) gets
`shared(running)` on the server in 3 of 3 profiles and on the Mac in about one of six. The carried RAW IS in
the profile (`82 NOM RAW 84|running`). The gate catches every one; no arm ships such a pragma, but DiscoPoP's
verdict decides which regions reach the model.

**Two causes, both in the explorer.** A dependence record without a call-path state (the profiler writes
scalars this way) is inserted as STATIC; the Do-All check gives a static dependence a "second chance" — it is
excused when the variable is first written in the loop (privatizable) or is a loop variable.
- **(A) "First written" by edge order** (`new_do_all_detector.detect_doall_sharing_clauses`). For each CU the
  classification walked its dependence edges and let the first one decide read-first or written-first. A CU
  that both reads and writes a variable (`running += …`) was classified by whichever edge came first — and the
  edges come in the order of the profile's records, which follows how the profiler happened to NUMBER its
  call-path states. The two prefix-sum profiles (Mac, server) are identical but for that numbering (the same 74
  paths); the Mac's explorer on the server's profile reproduced the false Do-All, on its own profile not.
- **(B) Loop variables by line** (`TaskGraph.__determine_loop_variables`, and DiscoPoP's classic `is_loop_index`,
  which has the same rule). A loop variable is recognised by a RAW between the loop header and the body; the
  test is by LINE. On a loop written on one line the body's accesses sit on the header's line, so the scalar the
  body carries (`chk ^= …`, `x = x * … + …`, `s += …`) was taken for a loop variable: its dependences between
  iterations were removed (`__cleanup_loop_dependencies`) and excused.

**Fix.** (A) A CU's accesses are taken in program order: by the line of the access, and on one line a read
before a write when both touch the same memory region and are of the same kind — both the scalar itself, or both an
element reached through an address — i.e. one statement that reads and then writes it (`running += …`,
`a[i] += x`). A plain read under the same name as an element store is the address that store goes through
(`dr[i] = …` loads the pointer `dr`; DiscoPoP's static/dynamic merge even gives that load the array's region): the
store decides, as before. (The first version of the fix put every read of a CU first; DiscoPoP's own end-to-end test
`reduction_pattern/positive/sum_reduction_1` caught it — `dr` came out `first_private` instead of `shared` — before
anything was committed.) (B) A loop variable must be one the loop's `for` header
names: where the AST holds the `for` statement, only candidates its init and increment clauses declare or refer
to are kept (`ASTPatternDetectionHelper.get_for_header_variables`, reading clang's `referencedDecl`); a `while`
loop, or a loop without an AST entry, is left as it was.

**Verified (27 Sep, Mac; the committed explorer with B4 and B9 as the baseline, one pristine profile per case):**
`prefix_sum.cpp` — the running total (18), the one-line recurrence on `x` (20) and the one-line `chk ^=` (26)
blocked on their scalar on both the Mac's and the server's profile (before: 26 and 20 Do-All on both, 18 on the
server's); the parallel initialisation loop (15) stays Do-All. B9's reproducer `k.c` — the `x`-carried loop (16)
and the one-line `s +=` (29) blocked; the parallel loop (26) stays. All 33 TSVC v3 packages, one pristine profile each: two Do-Alls fewer — s291 (136: `im1 = i` carried into the next iteration's `b[im1]`) and s341 (136: the packing counter `j`), both true scalar recurrences; nothing gained, no clause or reduction changed on the other 31. The agent's feature check `b10-carried-scalar` fails on the explorer before the fix (the running total Do-All with `shared(run)`, the one-line recurrence Do-All) and passes after. The feature suite 59 of 59; the explorer's end-to-end tests 31 of 31 (DiscoPoP's own sharing-clause and reduction tests included); mypy and `black --check explorer` clean. On the server (Linux, LLVM 20, synced to `8c7e6066`): the feature suite 59 of 59 — `dependence review`, which B10 had turned into a skip there 3 of 3 times, now runs and passes — and the end-to-end tests 31 of 31.

## B11 — candidate: no access under TSVC v3's `pb_emit_array` calls is attached (explorer)

**Found** 26 Sep 2026 while verifying B9. In s254 (v3) none of the 109 call-path states under
`main-->call_134-->_ZL13pb_emit_arrayPKd…` (the five `pb_emit_array` calls after the kernel) is attached
to any context, before or after B9's fix, while `main`'s earlier calls (`init_array`, the kernel,
`pb_emit(result)`) are; so `pb_emit_array`'s loops, which carry a dependence through `pb_emit`'s counters,
stay Do-All. A 25-line program with the same shape (a direct call to the callee, then two calls of a
function holding four such loops) does NOT reproduce it: B9's fix blocks all four loops there. Harness code
only — the evidence given to the models excludes it and packaging v4 moves it out of the file — so it
blocks nothing; mechanism not investigated.

## B13 — a cross-iteration write-after-write on an array element does not block Do-All (explorer)

**Found** 27 Sep 2026 in E2-B1's pre-flight: on all three T0.11 draws of Rodinia bfs (`t0_11_b1_a/b/c`,
server, fixed DiscoPoP with B4, B8, B9, B10, B12) the explorer reports the frontier loop (bfs.cpp lines
13–27) Do-All with an applicable pattern and no data-sharing clause. The loop stores
`h_cost[id]` and `h_updating_graph_mask[id]` for every unvisited neighbour `id` of a frontier node, and
frontier nodes share neighbours — about half the stores go to an element another iteration of the same
level also stores to (prepare_bfs.py's validation). The profile HAS the dependences:
`dynamic_dependencies.txt` holds WAW records of the `h_cost` store (instruction 122) against itself under
many call-path states, and likewise for `h_updating_graph_mask`. Only the Do-All verdict ignores them. The
agent's gate catches the pragma at the race check (TSan with archer) in every draw, so DiscoPoP alone and
the agent ship nothing wrong; what is wrong is DiscoPoP's EVIDENCE (a Do-All where a conflict exists) and
the routing that follows from it (Tier 1: the region is deferred to Phase B, and reaches the model only
through the v3.1 re-queue).

**Reproduced** on a 12-line program (Mac, the same DiscoPoP): `for (i = 0; i < 1000; i++) x[idx[i]] =
y[i];` with `idx[i] = (7 i) mod 100` — each element written by ten iterations, the final value that of the
last — is reported Do-All, applicable. A nested frontier/edge variant that also reads `cost[tid]` is
correctly blocked, by the RAW on `cost`. So the missing case is a conflict that is only a WAW.

**Root cause.** `TaskGraph.__insert_data_dependencies_from_files` drops every WAW record, static and
dynamic, before any context is linked ("ignore WAW, as there is no data flow"). For the task graph's own
purposes that holds — a WAW carries no value — but the Do-All detector reads its cross-iteration checks
from those same edges, so an output dependence between two iterations never reached it. (The detector's
data-sharing classification even has branches for WAW edges; they were unreachable.)

**Fix** (explorer only; the author's decision, 27 Sep):
1. The dynamic WAW records are kept, after the same-iteration pruning every dynamic dependence goes
   through, in a separate set on the source context (`Context.outgoing_waw_dependencies`) — and only
   when each write is placed in ONE iteration of every loop around it: all the contexts its state
   resolves to share one chain of enclosing iteration contexts. Several contexts on one line are fine (a
   one-line `if`: the condition and the store). A call-path state that does not say which iteration of a
   loop a write belongs to resolves to every iteration copy of that loop; a pair built from it is no
   evidence of a conflict between iterations. See B14 below: in `do_all/stack_access/various/case_5` the
   second of two sibling loops that call a function is never recorded in the states, and without this rule
   a WAW carried by the OUTER loop blocked that inner loop. (The first version of this rule required
   exactly one context per write; a code review on 27 Sep showed that it dropped the real conflict of a
   one-line `if x[dup[i]] = …`, and it was replaced before the merge.) They are not
   edges of the task graph, so every other consumer — the clause classification, the task graph's
   cleanup, the context task graph — reads exactly what it read before. Static WAW records stay dropped
   (over-approximate).
2. The Do-All detector blocks a loop on a WAW between two of its iterations when the variable is an
   array element (`GEPRESULT_…`), is not a loop variable, and is not declared inside the loop's code (by
   DiscoPoP's CU variables and their declaration lines, against the loop's code scope: an array declared
   in the body is private by its scope, although the same stack address is reused). A scalar written in
   every iteration is left to privatization, as before. The blocker is recorded in `doall_prevented.json`
   like any other.

**Limits (found by the code review of 27 Sep and checked on reproducers; none is new, each is a case the
fix does not reach):**
- **Multi-dimensional arrays.** The profiler tags only a one-level subscript: `g[dup[i]][0] = …` is
  recorded under the plain name `g`, so the WAW is not taken as an array element and the loop stays Do-All
  (the profiler's naming, `names.cpp`).
- **Repeat distance a multiple of 3.** DiscoPoP's task graph keeps a loop's iterations as two copies,
  chosen from the profiler's iteration digit, which cycles 0, 1, 2. A scatter whose two writes to one
  element are a multiple of 3 iterations apart (`dup[i] = 7 i mod 99`) has both ends in one copy, so it
  is not seen. Irregular repeats (bfs) are.
- **An array declared in the body whose element is written but never read in the iteration.** The
  profiler records no declaration line for arrays (`defLine` "LineNotFound"), so the exemption cannot fire
  and the loop is blocked. This is conservative: a loop that was parallel is refused, never the reverse.
- **A WAW carried by an outer loop whose iterations fall in the same copy** can be counted for an inner
  loop in rare shapes (`x[(i + t) % N]` rewritten per `t`). Also conservative.

**Verified** (Mac; the reproducer, the controls and the 33 TSVC packages below):
- the scatter with repeated indices is blocked on `WAW GEPRESULT_x`;
- a scatter through a permutation (each element written once — no WAW is ever recorded), a loop with a
  local array in its body, and a loop with a scratch scalar stay Do-All (the scalar `private`);
- feature check `b13-scatter-waw` (the three cases in one program).
- the explorer's end-to-end tests 31 of 31, after one expectation was changed: upstream's
  `do_all/stack_access/various/case_5` expected its OUTER loop (line 14) Do-All, although every one of its
  iterations writes all of `x[]` and `y[]` — equal values, but a write-write race between iterations (the
  test's own gold standard lists the WAW). The fixed explorer blocks it on `WAW GEPRESULT_x`; the test now
  expects lines 16 and 20 only, with this reason in a comment. Feature suite 60 of 60.
- the 33 TSVC packages, one pristine profile each, the committed explorer (B4, B9, B10) against the
  fixed one: Do-All loops, their clauses and the reductions identical on all 33. TSVC's scatters (`vas`,
  `s491`, `s4113`) go through permutations, so no WAW is recorded and nothing changes; T0.15's
  equivalence and E1c-v3.1's DiscoPoP verdicts are untouched.

## B15 — loops nested in a `do … while` (or after any loop the task graph does not model) lose every dependence (explorer)

**Found** 27 Sep 2026 while verifying B13 on Rodinia bfs: with B13 fixed, the explorer still reported bfs's
frontier loop Do-All. Traced: EVERY dynamic dependence of bfs's kernel — RAW, WAR, WAW, INIT, over 1,500
records — resolves to no task-graph context (`__get_work_contexts_by_location_and_state_id` returns
nothing); only 12 of the kernel's call-path states are attached to any context, none inside the level
loop. The Do-All verdicts on bfs's loops therefore rest on no measured dependence at all.

**Reproduced** on a 20-line C program (Mac): `do { for (t = 1; t < N; t++) { for (e = …) a[t] = a[t-1] + 1.0; }
for (t …) if (a[t] < 0) stop = 1; k++; } while (k < 3 && stop == 0);` — the textbook recurrence at the
first `for` is reported Do-All and 5 states are attached; the same code under `for (lv = 0; lv < 3; lv++)`
blocks it (RAW `a`), 23 states attached.

**Root cause.** The profiler numbers the loops of a function by source position and writes one digit per
loop in every call-path state (`main_loopstate30333`: five loops, the `do … while` second). The task graph
creates no loop (no `TGStartLoopNode`, no `LoopParentContext`) for the `do … while` — DiscoPoP's PET has
it (a loop node starting at the `do` line) — and `__assign_loopstate_positions_within_functions`
numbers only the loops the task graph has: the `for` loops after the `do` get positions one lower than
the profiler's digits. Every state under the `do … while` then carries an open digit no context can
consume, and no state matches.

**Fix** (explorer only; the author's decision, 27 Sep; revised after a code review the same day):
1. Where a function has PET loops the task graph does not model, `__assign_loopstate_positions_within_functions`
   numbers ALL of the function's PET loops by position, as the profiler numbers the loops it instruments.
   Each task-graph loop is mapped to its PET loop through its header CU's CHILD in-edge. The first version
   matched by (file, first line); that gave `while (1)` / `for (;;)` loops two positions and dropped a loop
   sharing a line with another. The positions of the loops without a task-graph loop are recorded.
2. `__assign_state_ids` marks those loops' digits processed ("4", as a matched digit is marked) in every
   state it reads, so the loops the task graph does model match their states.
3. Guards: the renumbering applies only when the function's PET loop count equals the digit count the
   profiler wrote for it, and the function's name is unique. Otherwise the numbering stays as it was, with
   a warning. The profiler numbers only the loops CFA instruments, so a loop CFA skips would otherwise get
   a phantom position. Functions with no unmodelled loop are numbered exactly as before.

**What it gives, and its limits.**
- On the reproducer, the recurrence is blocked on its RAW and 21 states are attached (5 before), exactly
  as under a `for` outer loop.
- On bfs's profile, 36 states are attached (12 before), and the frontier loop (13) and its edge loop (17)
  are blocked on `RAW h_cost`. The update loop (29) stays Do-All.
- The limit: the `do … while` still has no context, so a dependence it CARRIES (bfs's `h_cost` written at
  one level and read at the next) is compared as if inside one of its iterations. This can block an inner
  loop whose only dependence is carried by the `do … while`. That is conservative: the fix only adds
  dependences that the lost states had hidden, never removes one. bfs's frontier loop is blocked for that
  reason, not by its within-level write-write conflict. The block is right, and the variable is the
  deciding one, but the dependence kind shown is the cross-level RAW.
- **Beyond `do … while`.** Any loop the task graph does not model is covered the same way. In every TSVC v3
  package the harness's `pb_emit_array` holds one loop that `__break_cycles` does not model, and its other
  loops read the wrong digit. This is B11 below, now explained: those loops lose their false Do-All (they
  carry a dependence through `pb_emit`). They are harness code, excluded from every arm's regions.
- **Not attached.** States whose only active loop is the unmodelled one (the `do … while`'s own body and
  condition) are still not attached to a context.

## B14 — two loops side by side inside a loop are modelled as nested: the second loop's iterations are never recorded (profiler)

**Fixed 7 Oct 2026.** (27 Sep, as a candidate: "the second of two sibling loops that call a
function" — no call is needed, and the warning quoted then is unrelated; see below.)

**Symptom on the campaign.** In E2-v6 the agent splits the hidden-order kernels in the right order, and the
explorer then reports Do-All for the loop of the assignment and none for the loop of `u[…] += …`: the agent's
programs carry a directive on one of two loops (two of three on `k27`) and reach 1.4–1.9× where the expert
versions reach 3.1–4.2×.

**Reproducer** (no model; `k23` of `tsvc_c2` with its file replaced by the split, profiled as the harness
profiles a package):

```c
for (int nl = 0; nl < iterations; nl++) {          /* line 5 */
    for (long i = 1; i < LEN_1D; i++) {            /* line 6 */
        v[i] = x[i] * d[i] + c[i];
    }
    for (long i = 1; i < LEN_1D; i++) {            /* line 9 */
        u[i] += w[i] * c[i];
    }
    dummy(a, b, c, d, e);
}
```

`patterns.json`: Do-All for line 6 only. `doall_prevented.json`: loop 9, RAW, `u` — a dependence carried only by
the loop at line 5 (`u[i]` is read in the next repetition).

**Cause.** `get_loopIDs_in_function_body` collects the loops of one top-level nest as a flat list, in the order
of their `__dp_loop_entry` calls; `get_loop_iteration_instances_and_transitions` reads that list as a CHAIN —
the parent of every loop is the loop before it (`parent_instances = new_instances`; a base instance needs all
earlier loops active). For the list [5, 6, 9] it generates the entry into loop 9 only from states in which loop
6 is active (`…203 → …200`), never from the outer loop's own state (`…233`). At run time loop 6 has ended
before loop 9 begins; `update_callstate` (`rtlib/static_callstate_transitions/utils.cpp`) finds no transition
for loop 9's entry and keeps the outer loop's state without a word — only a function exit reports a missing
transition, and the one line the profiled run prints ("No transition found from state 31 via instruction 1")
is the program's own exit. Every access inside loop 9 is therefore recorded with that loop's digit at 3
(inactive): the load and the store of `u[i]` on line 10 carry the states `033`, `133` and `233`, where the
accesses of line 7 carry `…003`, `…013`, `…023` as they should. The explorer then resolves the store to both
iteration copies of loop 9 and pairs the dependence the outer loop carries across them.

**Scope.** Every loop that holds two or more loops side by side: all but the first lose their iteration state.
None of the 44 `tsvc_c2` originals has that shape (text scan) — DiscoPoP alone is not affected on them; every
loop distribution the agent makes inside the repetition loop creates it, so the defect caps exactly what the
agent can get from DiscoPoP after a split. B16 (`s244`: a RAW of the repetition loop charged to the inner loop)
is NOT this defect: `s244` as packaged has one inner loop, nothing side by side; B16 stays a candidate.

**The second face, found by the replay (7 Oct): a FALSE Do-All.** With its iterations unrecorded, a later loop
shows every dependence between two of its own iterations as a dependence inside one iteration. In four programs
of E2-v6 on `k53` (the unit whose statements feed each other) the model had put the kernel's loop after a copy
loop inside the repetition loop, and the explorer reported that loop — a true recurrence through the index
tables — as Do-All. The agent's gate refused the directive at its race stage in each of the four trials, so none
shipped; DiscoPoP alone would have emitted it. With the fix the loop is not reported.

**Fix** (`profiler/DiscoPoP/static_analysis/calltree_construction.cpp`). `get_loop_parents_in_function_body`
gives every loop its parent — the innermost loop open where its `__dp_loop_entry` stands, from the entry and
exit markers. `get_loop_iteration_instances_and_transitions` creates a loop's instances from the instances of
its PARENT, with every earlier loop of the nest that is not one of its ancestors inactive ("3"), and registers
the entry from that parent state and the exits back to it. The digit order of a loop state is unchanged, so the
explorer needs no change (it reads each loop's digit by position; an inactive sibling's "3" matches no
iteration). A loop whose parent cannot be determined is treated as before.

**Verified** (Mac, LLVM 19, no model). The reproducer: Do-All for lines 6 AND 9; the accesses of line 10 carry
`…030` to `…232`. Programs without side-by-side loops (`k23` as packaged; a 3-deep nest with a separate loop):
the same call-path states and the same transitions as before the fix (compared as sets, state ids resolved),
the same Do-All verdicts. The profiler's unit tests: 184 passed. The end-to-end tests: 31 passed, and a new one,
`test/end_to_end/do_all/stack_access/various/case_6` (two loops side by side, the second `y[j] = y[j] + x[j]`),
which FAILS on the profiler before the fix ("Overlooked expected do_all patterns at lines ['1:18']") and passes
with it. (`case_5`, where B14 was first seen, has two plain writes and passes either way.)

**Verified on the server** (LLVM 20, no model; `evaluation/agent/results/T0_instruments/B14_side_by_side_loops/`,
read-out `analysis/b14_readout.md`). The profiler rebuilt from the fix's commit; `case_6` passes there. The
agent's 257 changed programs of E1-v6 and E2-v6, directives removed, profiled before and after the fix
(`tools/doall_replay.py`): 86 programs gain loops and then have EVERY loop reported — all 35 successes of
E2-v6's arm with evidence at one attempt on `k19`, `k23`, `k27`, `k31` (81 loops reported before, 116 after),
37 and 10 in its three-attempt arms, 4 of 85 in E1-v6 (all `s281`); 4 programs have a loop withdrawn, each the
recurrence of `k53` above; no other loop changes. DiscoPoP alone on the 44 `tsvc_c2` originals, two draws on the
fixed profiler: outcome and number of directives of every package as in the three draws before the fix.

**What the false block needs, precisely:** a loop that is not the first of the loops side by side, and that
both reads and writes an array whose value the enclosing loop carries (`u[i] += …`, `y[j] = y[j] + …`). A later
loop that only writes is not blocked — which is why `k48`, where the `+=` loop comes first, had both loops
reported, and why `case_5` never failed.

## B19 — candidate: a conditionally assigned scalar that is read after the loop is classified `last_private` (explorer)

**Status: candidate, 7 Oct 2026 — seen in every draw, not fixed; what the fix should be is a decision.** TSVC
`s331` searches the last negative element:

```c
j = -1;
for (int i = 0; i < LEN_1D; i++) {
    if (a[i] < (real_t)0.) {
        j = i;
    }
}
chksum = (real_t) j;
```

DiscoPoP's explorer reports the loop Do-All (pattern `do_all`, both server draws of T0.18 and every DiscoPoP-alone
trial) and classifies the variable in the pattern itself — `patterns.json`: `"last_private": ["j"]`, `"reduction":
[]` (read on the Mac's profiles of both packagings; the patch generator's own patch was not looked at). Rendered as
a directive that is `#pragma omp parallel for lastprivate(j)`. `lastprivate` hands back the value of `j` in the thread that ran
the sequentially last iteration; where that iteration does not assign, the value is not the last assignment's. The
harness's gate refuses the directive at the output check in every trial (`e1v6c_v7_agent`, DiscoPoP alone: 5 of 5
"Program output changed"; the same on packaging v6), so no wrong program was shipped — DiscoPoP alone ends
unchanged and the loop is of class R.

The loop is parallel, with a directive DiscoPoP does not produce: `reduction(max: j)` (the last index is the
largest; every model alone writes it, 17 of 20 programs in `e1v6c_v7_bare_*`, FASTER 3.6–4.7×, race-free) or
OpenMP 5.0's `lastprivate(conditional: j)`. T0.13 (21 Sep) had named `s331` as needing "a pragma DiscoPoP cannot
write"; this entry says which one DiscoPoP writes instead and why it is wrong.

**8 Oct 2026 — the archive read for this defect: the root is the clause, and `s331` is not its only face.** The
author asked why it should be left alone. No run: the saved candidates of the runs on the clean packages (E1-v6 and
its corrections, E2-v6, E2-v6b, the class draws) and the explorer's code.

*The root is the clause, not the Do-All verdict.* The clauses of the patterns the explorer writes out are decided in
`explorer/discopop_explorer/pattern_detectors/new_do_all_detector.py`, `detect_doall_sharing_clauses`: a variable
that an iteration writes and that something outside the loop reads afterwards becomes `lastprivate` unless its type
in the source carries `*` or `&` (lines 657–662). Nothing asks whether the sequentially last iteration assigns the
variable — which is what OpenMP's `lastprivate` needs. For `s331` the Do-All verdict is right (the loop is
parallel); the clause is wrong. Not reporting such a loop as Do-All would be a way around the defect, not its
repair. *Corrected 8 Oct, later:* this paragraph first named `utils.py`, `classify_loop_variables` (lines 758–760,
776–778, 805–807). That function holds the same rule, but it is the older classification: of the detectors that
call it only `DoAllInfo`'s constructor still runs, and the new detector overwrites its result
(`pattern_detection.py` runs `new_do_all_detector.run_detection` alone; the older Do-All and reduction detectors
are commented out). Read from the detector's own log on the Mac's profile of `s331`: `written: {i, j}`,
`data_outgoing: {j}`, `it_lastprivate: {j}`.

*On `s331` the clause is written again and again.* The five agent trials on the corrected packages and the fixed
DiscoPoP (`e1v6c_v7_agent`, the normal setup): 51 model calls, $9.69, 94 minutes; 35 of the 51 rewrites passed the
first checks; DiscoPoP wrote `lastprivate` on the search loop 27 times — on the original and on rewrites that had
left the search loop as it was — 26 refused at the output check, 1 that passed the output check refused at the
schedule check. No such directive on the search loop was accepted in any run on either packaging. (Thirteen
accepted `lastprivate(j)` directives of `e1v6_r_4` sit on the REPETITION loop, in which every repetition assigns
`j`: there the clause is right, and what was wrong was the old packaging, which packaging v7 corrected.)

*A second face, shipped: `s481` (class A).* DiscoPoP's directive on the inner loop is

```c
for (int nl = 0; nl < iterations; nl++) {
    #pragma omp parallel for lastprivate(nl)
    for (int i = 0; i < LEN_1D; i++) {
        if (d[i] < (real_t)0.) {
            exit (0);
        }
        a[i] += b[i] * c[i];
    }
    dummy(a, b, c, d, e);
}
```

`nl` is the counter of the enclosing repetition loop; the inner loop never writes it. The gate accepts the
directive in every class draw (9 of 9: `t0_11_c2_a`, `t0_11_c2_b`, `t0_11_c2_c`, `t0_11_c2_b14_a`, `t0_11_c2_b14_b`,
`t0_11_c2_b14_c`, `t0_11_c3_a`, `t0_11_c3_b`, `t0_11_c3_c`) and the program is verified and FASTER (3.7× at 12
threads in `t0_11_c3_a`). By the OpenMP specification a `lastprivate` variable that the sequentially last iteration
does not assign has an unspecified value after the loop — here the counter of the loop around it. The program is
right with this compiler; the specification does not promise it, and no check of ours can see it. Why the explorer
takes `nl` for this loop is not traced.

*A third face, in the model's rewrites: whole arrays.* Where a rewrite keeps a copy in an array on the stack
(`real_t a_old[LEN_1D];`), DiscoPoP wrote `lastprivate(a_old)` on the loop that fills it — every thread then fills a
private array and only the last thread's is copied back. 25 such directives on eight loops (`s211`, `s212`, `s241`,
`s244`, `s252`, `s321`, `k23`, `k53`): 24 before the profiler fix B14 (E1-v6's registered runs, E2-v6) — 22 refused
(20 at the output check, 2 under ThreadSanitizer) and 2 that passed the gate's checks on `s244`, where by the code
only the array's last element is read afterwards; the agent discarded both rewrites at its next step — and 1 after
the fix (`e2v6b_fb_3`, `k53`, repeat 5; refused at the output check). In the same rewrites a loop that only reads
the copy got `firstprivate(a_old)` — right, but every thread copies the whole array; none seen after the fix. A copy
on the heap gets `shared(...)`, which is right. Not traced: why a stack array passes `is_scalar_val`, and whether
the fix of B14 removed most of these or the later runs simply held fewer such rewrites. The two stack-array rewrites
of `s241` that the replay of 8 Oct handed to the fixed DiscoPoP stop before DiscoPoP is asked (they crash at the
timing size).

*A look at the two correct forms — on the Mac, not a measurement* (8 Oct; Homebrew clang 19.1.7 with libomp, 4
threads). The program

```c
#include <stdio.h>
#include <stdlib.h>
#define N 4000000
int main(void) {
    double *a = malloc(N * sizeof(double));
    int i, j = -1;
    for (i = 0; i < N; i++) a[i] = 1.0;
    a[182150] = -1.0;
    #pragma omp parallel for lastprivate(conditional: j)
    for (i = 0; i < N; i++)
        if (a[i] < 0.0)
            j = i;
    printf("%d\n", j);
    return 0;
}
```

prints 182150 with one thread and an arbitrary number with four — as it does with plain `lastprivate(j)` (this
form at -O1 with `-fopenmp-version` unset, 50, 51 and 52; the same loop with braces at -O0 and -O3, as one
combined directive and split in two; no diagnostic). In the unoptimized code the compiler does keep the variable
in a per-thread record with a flag (`%struct.lasprivate.conditional`, the flag set to zero) and adds a barrier
after the loop, but the assignment only stores into that record and the copy-back is the plain one — the thread of
the last iteration writes its own value. Why it does not compare the assigning iterations is not traced. On the `s331` package at 4,000,000 elements the same: both forms change the
output (the search returns 3 where the original returns 182150); `reduction(max: j)` keeps the output and runs in
0.04 s against 0.12–0.20 s. So the conditional form is not a directive DiscoPoP could simply write: with this
compiler it behaves as the plain one. The server's compiler (LLVM 20) is not looked at.

**Possible repairs — not chosen (the author's decision):** (1) *at the root, conservative:* a variable goes into
`last_private` only where the sequentially last iteration is certain to assign it; where that is not certain the
loop is not offered with a directive, because DiscoPoP has no clause that says it. Expected on `s331`: DiscoPoP
alone unchanged as measured, the loop stays of class R, the agent no longer stages a directive known to be wrong.
To be shown without a model: the class draws on the clean packages again (a clause that works today only by the
compiler's grace may go — `s481`) and the explorer's tests. (2) *`lastprivate(conditional: …)`:* by the look above
not usable with clang 19; to be checked on the server's compiler before it is considered at all. (3) *recognising
the search as a maximum reduction:* a new detection, not a repair; `s331` would become of class A and the main
comparison's population would change by one loop. Until one is chosen the loop stays as measured.

## B18 — candidate: outer loops of PolyBench kernels lose their Do-All; the blockers named are inner loop counters (explorer)

**Status: candidate, 7 Oct 2026 — seen, not examined; not B14 as far as the evidence goes.** DiscoPoP alone on the
31 packages of T0.11 outside TSVC, three draws on the current DiscoPoP (`t0_11_b14_apps_a`–`c`), against the three
draws of 20 Sep (`t0_11_classes_a`–`c`): 23 packages as then, 8 differ. Between the two lie eight fixes (B4, B8,
B9, B10, B12, B13, B15 of 26–27 Sep, B17, and B14), a new agent version and the harness's changes — the
comparison does not isolate one of them. What differs:

| package | 20 Sep | 7 Oct |
|---|---|---|
| `polybench/correlation` | FASTER, 1 directive, 5.4–5.8× | no change, no directive |
| `polybench/covariance` | FASTER, 1 directive, 5.1–5.8× | no change, no directive |
| `polybench/gramschmidt` | FASTER, 1 directive, 8.0–8.6× | parallel, not faster: 0.32–0.40× |
| `polybench/fdtd-2d` | FASTER, 3 directives, 4.5–5.7× | parallel, not faster: 0.57–0.60× |
| `polybench/ludcmp` | parallel, not faster: 0.15–0.18× | FASTER, 4.8–5.9× |
| `polybench/adi` | one draw FASTER (4 directives), two without a result | FASTER in three draws, 1.7–1.9× |
| `polybench/atax` | one draw unchanged, two parallel (speed not measurable) | parallel in three draws |
| `rodinia-3.1/pathfinder` | parallel, 1 directive | no change, no directive |

On the current profiles the explorer names as what blocks the outer loops: `correlation` RAW on `j` and on `i`,
`covariance` RAW on `j`, `i` and `mean`, `gramschmidt` RAW on `i`, `fdtd-2d` RAW on `j` — the counters of the
inner loops, which PolyBench declares once at the top of the function; `pathfinder` RAW on `src`. An inner
loop's counter is written before it is read in every iteration of the outer loop; the directive of 20 Sep made
it `private` and passed the race stage in three draws. The natural suspect is the rule that came with B10's fix
(a scalar carried from one iteration to the next blocks Do-All), applied to a scalar that is not carried but
re-initialised. `correlation` and `covariance` have no loops side by side that meet B14's condition. **Owed:** the
same packages on a build before B14 and on one before B10 (PolyBench runs on the Mac; `pathfinder` does not),
then the fix at the root. No TSVC package is affected: their loop counters are declared in the loop header, and
the three TSVC draws on the current DiscoPoP equal the earlier ones.

## B17 — the profile depends on the path of the working directory: an uninitialised flag switches loop tracking off (profiler runtime)

**Status: fixed (3 Oct 2026), one line; regression check `b17-cwd-length`; the harness refuses such a profile.**
`rtlib/loop/LoopManager.hpp` declared `bool alreadyDone;` and its constructor `LoopManager() {}` never set it, so
`new LoopManager()` (`dp_func_entry.cpp`) read whatever the heap held. `__dp_loop_incr` begins with
`if (loop_manager->is_done()) return;` and `__dp_loop_output` with the same test: when the byte was non-zero the
runtime counted no loop iteration and wrote no loop results — the profiled run printed no
`Outputting instrumentation results... done`, `dynamic_dependencies.txt` lacked every dependence between
iterations, and the explorer reported the loops Do-All.

**What decides the byte.** On Linux (glibc, LLVM 20) it is what start-up code left in freed heap memory: text
of the working directory's path. Measured on the server with one instrumented build of `tsvc_b1/k19`, run from
directories of every path length from 30 to 250 characters (path of the profiled file): lengths 105-125 except
110 give the broken profile (59 dependence lines, 2 false Do-Alls — the inner loop and the repetition loop),
every other length the right one (125 lines, no Do-All). The build directory does not matter, the environment's
size does not; moving a good build into a directory of a bad length breaks it, and back repairs it.

**How it was found.** The two Opus pilots of 3 Oct (`pilot_opus_agent_k19`, `pilot_opus_agent_k19_speed`) had the
longest run names of the campaign; their `k19` profiles reported two Do-Alls where 262 other profiles of the
same packages on the server agree with each other. The agent re-queued the "false Do-All" to the model and never
showed prompt version 3's order statement.

**Fix.** `bool alreadyDone = false;`. Verified on the server after rebuilding the runtime: the same scan gives
the right profile at every length. **Guard.** `agent/tools/cli.py` (`profile_once`) refuses a profiled run whose
log lacks the runtime's loop-results line, whatever the cause (PROFILE_ERROR instead of a silent wrong profile).

**Which archived profiles had it** (the line is missing from `profiled_run.log`; 56 of 732): the two pilots;
`t0_11_classes_a`/`_b`/`_c` on 14 PolyBench kernels (covariance, doitgen, dynprog, fdtd-2d, fdtd-apml,
floyd-warshall, gemver, gesummv, jacobi-1d-imper, jacobi-2d-imper, ludcmp, reg_detect, seidel-2d, trisolv) and
Rodinia hotspot and pathfinder; `e10_dp_alone` on floyd-warshall and jacobi-2d-imper; `e1_smoke`-`e1_smoke4` on
floyd-warshall. No profile of TSVC, `tsvc_b1`, LULESH or NPB is affected, and no trial's own working directory
(where the agent re-profiles) has a path in the range (2,395 server trials checked by path length).

## B16 — candidate: a RAW carried by the repetition loop is attributed to the inner loop (explorer)

**Status: candidate, not re-checked on the fixed explorer.** In the V3 pilot's profile of TSVC `s244`
(25–26 Sep, before the B4 fix), DiscoPoP's Do-All blockers charge the RAW on `a` to the inner `i` loop,
although it is carried by the repetition loop `nl` (the value is read in the next repetition); the 20 Sep
profile of the same package (`t0_11_classes_a`) charges it to `nl`. With the old prompt wording the
evidence arms were steered to the wrong loop (E2: s244 evidence arms 1/18 vs 12/18 without). The agent's
order statement (prompt v3, D4) stays silent when the blockers name more than one loop for a variable, so
it cannot act on such a record. Owed (prompt review M4): re-explore s244 and s211 on the fixed explorer
and compare the blockers across draws.

## B12 — the compiler wrappers report success when the instrumented build fails (profiler scripts)

**Found** 27 Sep 2026, running the agent's feature suite on the server (Linux, LLVM 20) for the first time. **Status:**
FIXED 27 Sep 2026.

**Symptom.** `discopop_cc fill.c -o a.out` prints a linker error — on Linux a C link does not pull in `libm`,
and DiscoPoP's runtime (`libDiscoPoP_RT.a`, `runtimeFunctions.cpp`) calls `ceil` — and exits **0**. The caller
learns of it only at the next step (`./a.out: No such file or directory`); the static analysis (`Data.xml`,
call-path states) exists, so a tool that looks at those files sees a profile. Four of the agent's feature checks
failed or skipped on the server for this reason; one of them reported it as an explorer crash.

**Cause.** `CC_wrapper.sh` and `CXX_wrapper.sh` run the instrumented build and then an AST dump
(`-fsyntax-only -Xclang -ast-dump=json`); the script's exit status is the AST dump's.

**Fix.** Keep the build's status and exit with it after the AST dump. The Python entry points (`discopop_cc`,
`discopop_cxx`) already return the wrapper's status. On the agent's side the feature suite now links C with
`-lm`, as the harness always did (`tools/cli.py`); the experiment runs were never affected — every C benchmark
is linked with `-lm` — and a failed build was caught one step later either way.

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

**Status:** FIXED 26 Sep 2026 in the explorer (`TaskGraph.__duplicate_loop_iterations`), before E2-B1 by the
author's decision ("yes fix b4 go ahead"; D14). E1c-v3.1 ran on the pre-fix explorer and is reported as such.

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
run that attaches them (10 → 14 attached states on the pre-B9 explorer, 13 → 17 with B9 fixed) blocks the loop on the RAW
on `a`; every run that does not reports it Do-All. The same on s121, s212, s243 and s244, each with a
true dependence in the kernel's inner loop: Do-All in 7 to 12 of 15 runs per explorer version (B9's
verification). Not a cycle in the state walk (an instrumented copy
counted 0 re-entries of a pair still being answered). The order that decides it is that of a set of task-graph nodes, which
follows object addresses and changes from run to run (root cause below). Consequence for the campaign: DiscoPoP's verdict on a loop is itself a draw (T0.15's "draw
noise" mixed this with profile noise). The gate catches the false Do-All; the verdict decides where the
agent routes a region.

**Root cause.** The task graph gives every loop two iteration copies — the original (iteration ids `[1]`)
and a copy (`[0, 2]`) — so that call-path states of the first, a middle and a later iteration each find a
place. `__duplicate_loop_iterations` does this per function, pass by pass, over the loops' start nodes in
the order of `nx.descendants` (a set). Copying an enclosing loop's iteration copies the loops inside it as
they are at that moment, and copies are never copied again. When the enclosing loop came first, the inner
loop inside the enclosing loop's copy stayed ONE iteration without iteration ids; the context builder then
set them to `[0]` with the warning "Applied fix: set previously unspecified loopstate iteration id … to
[0]". In the enclosing loop's copy, which stands for its first and its later iterations, the inner loop
could then only take the states of its own first iteration: `_loopstate01`, `…02`, `…21`, `…22` were
attached nowhere, the dependences carried between later inner iterations were lost, and the recurrence was
reported Do-All. The warning is the signature: over 87 runs of three packages it appeared in exactly the
58 that reported the false Do-All and in none of the 29 that blocked it.

**Fix.** Inner loops are duplicated before the loops that enclose them: in each pass, an iteration that
still holds a loop not yet duplicated waits for a later pass (with a fallback to the old order should
every remaining loop wait, which a tree of loops cannot produce).

**Verified (26 Sep, Mac, LLVM 19; the B9-fixed explorer as the baseline, each run on a pristine copy of the
same profile):** s112's recurrence blocked in 8 of 8 runs (before: Do-All in 6 of 8), the same 17 states
attached in every run, no warning. All 33 TSVC v3 packages, two runs each: identical Do-All sets (with
clauses) and task counts in 33 of 33, no warning in any of the 66 runs; against one run of the
B9-only explorer, three Do-Alls fewer — s121 (135), s241 (134), s243 (134), each a true dependence, each
in a run that showed the warning — and none gained, no clause changed; the loops that are parallel stay
Do-All (s000, vpvtv, s4112–s491). Explorer time unchanged (median 17 s against 16 s); stalls 8 of 66 runs
against 2 of 33 (L5, retried; to watch in E2-B1's pre-flight). The agent's feature check
`b4-nested-duplication` (one profile, three explorer runs) fails on the B9-only explorer and passes after.
The whole feature suite 58 of 58; the explorer's end-to-end unit tests 31 of 31 with no error (the one
import error seen before came from `mcp_server` not being installed in the venv — CI installs it; now
installed); mypy clean on every package; `black -l 120 --check explorer` clean, as CI checks it.

**What is not the cause:** the call-path state walk (an instrumented copy counted 0 re-entries of a pair
still being answered), the profile (one unchanged profile throughout), Python's string hashing (a fixed
`PYTHONHASHSEED` does not make a run repeatable — node sets are ordered by object address).

**Reproducer:** the agent's `b4-nested-duplication` program — a repetition loop around
`for (i = N - 2; i >= 0; i--) a[i + 1] = a[i] + b[i];` (TSVC s112's shape).

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
