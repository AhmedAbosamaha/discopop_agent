# T0.16 pre-flight — a clean two-file layout, prototype (Mac, 4 Oct 2026, no model)

**Why.** The author (4 Oct): the file a model reads has to be an ordinary code file — no note of ours, no
measurement code, nothing to tell a model to leave alone; the only preparation of a benchmark is removing its
comments. Packaging v4 does not meet that: the file holds `pb_mix` with a three-line note, the repetition
loop, `PB_MAIN`, and every request carries two sentences of ours about them (record §6, 4 Oct).

**The layout tested (called v5 here).** One package = a small project of three files, plus one outside it:

| file | whose | what it holds | a model can |
|---|---|---|---|
| `<name>.c` | the benchmark | one `#include "data.h"` and the loop's function — TSVC's loop text, verbatim | read and change |
| `data.h` | ours | declarations only: the type, the size table, the arrays, the function's prototype | read |
| `main.c` | ours | `main`: set-up, the repetition loop calling the function, `pb_mix` between two calls, the timer | read (a change is discarded) |
| `_harness/<suite>/<name>.h` | ours, outside the package | data, initial values, perturbed input, digest, timing | not open |

`example/k19/` and `example/s211/` hold the files and the first request the agent would send
(`request_first_region.txt`, built by the agent's own code with no model call).

**What was checked, and the result** (prototype of all 43 `tsvc_b1` loops, `tools/v5_proto.py`):

1. **The program is the same.** Plain builds of v4 and v5: digest on the shipped input, digest on the
   perturbed input (seed 7), full dump of every value — byte for byte identical for **43 of 43** at SMALL and
   at MINI (`outputs_small.txt`, `outputs_mini.txt`). One loop needed a standard header the hidden header used
   to supply (`s481` calls `exit`: `#include <stdlib.h>`).
2. **The sequential original is as fast.** Timed region, STANDARD, median of 5, six loops: v5/v4 between 0.96
   and 1.03 (`timing_standard_mac.txt`; Mac — to be repeated on the server).
3. **DiscoPoP's view of the loop under study** (`screen.md`, `screen_details.txt`, one profile per layout,
   the agent's own profiling and planning code, v5 as a project through a unity unit):
   **34 of 43 the same** on every recorded criterion — the agent's candidates (tier, pattern), the Do-All set,
   the blocker of the loop under study, the repetition loop blocked, the order statement. The 9 that differ:
   - **the order statement, 5 loops** (`k48`, `s1213`, `s241`, `s243`, `s323`). Cause: an agent defect, not the
     layout — see below. On the four hidden-order kernels whose result rests on that sentence (`k19`, `k23`,
     `k31`, `k36`) and on `s211` it is word for word the same.
   - `s151`: the function that held the repetition loop is no longer a candidate (it is one call now) — by
     construction; the candidates on TSVC's `s151s` are the same.
   - `s244`: the loop's blocker is the WAW on `a` instead of a RAW on `a` — the RAW is carried between
     repetitions, not by the loop (candidate bug B16 of v4, gone when the repetition loop is in another
     function).
   - `s481`: v4's profile reports the REPETITION loop Do-All (false); v5's blocks it.
   - `s482`: v4's profile blocks the loop on a RAW on `a` carried between repetitions (B16 again); v5's
     reports it Do-All, as E2-B1's selection expects of it.
   4 more differ only in WAR/WAW records of the store line (`k23`, `k31`, `s112`, `s121`) — what two draws
   of ONE layout differ in on 17 of 33 packages (T0.15); a second draw decides, not a failure.
4. **The runner works on it end to end with no code change** (run `mac_v5_preflight`, arm
   `discopop_gate_v3`, budget 0): `s000` — DiscoPoP's Do-All found, its pragma placed in the clean file
   through the gate, verification exact on both inputs; `k19` — no pattern, no change. Verified at SMALL on
   the Mac, so no speed statement.

**What the pre-flight found that has to be fixed before any model reads the layout.**

- **The order statement is unreliable where two statements feed each other — in v4 too.** `order_statement`
  decides whether a flow in the reverse direction is "carried by an enclosing loop" from the variables
  DiscoPoP's Do-All blockers name; DiscoPoP records ONE blocker per loop, the first it finds, so which variable
  stands for the repetition loop is arbitrary. Seen here: `s1213` in v4 has the (correct) order sentence in one
  profile and none in another; `s323`, a true recurrence, gets an ORDER in v4 that is wrong. In v5 the agent
  loads blockers by file and so never sees the repetition loop's: every such pair is called a cycle (`s1213`:
  wrong — the split with line 7's loop first is the solution). Two defects, to keep apart: (a) v5 only — load
  the blockers for the whole program and key a carrying loop by (file, line): back to v4's level, no DiscoPoP
  change; (b) inherited — one blocker per loop by discovery order and no category for a flow inside one
  iteration. Any new rule is replayed on the 86 profiles of the screen (`screen_profiles.tar.gz`: sources,
  `FileMapping.txt` — its paths are the scratch directory's and are rewritten on extraction —, the profiler's
  and the explorer's files; no build product, no AST dump) and on `test_prompt_v2.py`'s truth table
  first; `k19`, `k23`, `k31`, `k36` must keep their sentence word for word.
- **The model alone takes back every unit of a project**, `main.c` included (`bare_llm.py` copies back all
  `--project-units`); the agent takes back the file under work only. For "a harness edit is impossible" to
  hold in every arm the model alone must take back the benchmark's file only.
- **Tools that open a trial's `final.c` by name**: `race_check.py`, `hot_loop_coverage.py` (its line is
  computed on the package file; a project trial's text is all files joined), `routing_check.py`,
  `marginal_replay.py`.
- **`k36`** hides its deciding fact in two accessor MACROS — code, not data. In v5 they sit in a second header
  no model can open (`data.h` includes it); the alternative is to show them, which ends `k36` as a hidden-order
  kernel.
- **`vas`** binds TSVC's index array through a harness name (`pb_ip`) inside the function.
- **The expert references** allocate their scratch array once, outside the timed region; in v5 a solution can
  only allocate inside the function (or keep it between calls): the references are re-rendered and re-measured.

**What changes for a model, to state:** the repetition loop is no longer in its file — it cannot move work in
front of the repetitions, merge them or copy them; the agent's first region is the loop under study itself (in
v4 it was the repetition loop around it); nothing says how long `u` and `v` are (v4's request said, wrongly for
these kernels, that every array has `LEN_1D` elements).

**Checked:** none of the 129 files a model could read (43 × `<name>.c`, `data.h`, `main.c`) holds a comment.

**Not done here:** a second draw per layout (every DiscoPoP verdict above is ONE profile per layout); the server (LLVM 20); the classes (T0.11) and sizes (T0.1) on the
layout; any model call.

**Reproduce** (from the repository root, the agent's venv first on PATH):

    venv/bin/python <this folder>/tools/v5_proto.py /tmp/v5
    venv/bin/python <this folder>/tools/v5_outputs.py /tmp/v5 SMALL
    venv/bin/python <this folder>/tools/v5_discopop.py /tmp/v5 /tmp/v5_dp k19 s211 ...
    venv/bin/python <this folder>/tools/v5_readout.py /tmp/v5_dp --md screen.md
