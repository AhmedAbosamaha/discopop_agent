# How speed and correctness are judged — the agent, the harness and the model alone

Written for the thesis (the author, 3 Oct 2026: "record this info … for the thesis writing"). It explains what
"faster", "parallel, not faster", "unusable" and "noise" mean in every read-out of the campaign, why the agent's
own speed decision and the harness's verdict can disagree, and how a model-alone program is judged correct. Every
number is from the archived runs; every rule is the code's (paths given).

## 1. Noise

Timing the same, unchanged program several times on the server does not give the same time twice: other jobs, the
CPU's clock, memory traffic and caches move every run a little. For example (illustrative):

```
run 1: 1.000 s   run 2: 1.012 s   run 3: 0.991 s   run 4: 1.020 s   run 5: 0.996 s
```

That spread is the **noise**. It decides how small a speed difference can be told apart from chance. Measured
before the campaign (T0.4 at four lanes, `t0_4_four_lanes`, no model): with the median of 5 runs, two timings of an
identical TSVC program differ by up to **1.016×** serial and **1.008×–1.011×** parallel (`s211`, `s254`); a
memory-bound PolyBench program by up to 1.123× (which is why the applications keep two lanes). A difference below
about 2 % on TSVC is indistinguishable from noise.

## 2. The harness's verdict: FASTER means at least 1.1×

The harness is the independent judge — the agent never grades itself (`agent/tools/cli.py`, `verify`). For every
trial of every arm it builds the original and the final program itself, at the kernel's **verification size**
(T0.1: the smallest size whose sequential kernel takes at least 1 s), and runs:

- the original sequentially, 5 times;
- the final program at **6 and at 12 threads**, 5 times each.

It takes the **median** of each set of five (the middle value, so one unlucky run cannot distort it). The
speedup at a thread count is the original's median ÷ the final program's median. The outcome is **FASTER** when
the final program is correct (§4) and its speedup is **at least 1.1×** at either thread count; **parallel, not
faster** when it is correct, carries parallel code, and stays below 1.1×; a correct program below **0.91×**
(1/1.1) is **slower** and counts as an unusable program (H13).

**Why 1.1× and not "anything above 1×".** (1) Noise: an unchanged program measures above 1.000× about half the
time by chance, so a bar at 1×, or at 1.001×, would call unchanged programs FASTER; (2) practical value: putting a
loop on 6–12 threads for a 3 % gain is not a parallelisation anyone would keep; (3) the value was fixed before the
experiments (EXPERIMENT_PLAN §2), and a primary definition is not changed after seeing data. "Any reliable gain,
however small" is answered properly by a statistical test on the repeats ("significantly above 1×"), whose
smallest detectable gain is set by the noise (≈ 1–2 %), not by a chosen number — proposed to the author as a
secondary scoring beside 1.1×.

## 3. The agent's own speed decision: "not slower", not "1.1× faster"

The agent decides during its run, with speed check ON in every arm since D22 except the E2 experiments (§5). It
measures at the kernel's **timing size** (T0.1: the smallest size reaching 0.25 s — smaller than the verification
size, because the agent times the program many times per decision) and it measures **paired**: the program before
and after a change are timed in alternation (before, after, before, after …), so both see the same state of the
machine, and the median of the per-pair ratios is the decision statistic (`gate/timing.py`, `measure_marginal`).

At the start of every run it measures its own noise: the same statistic on two IDENTICAL builds of the unchanged
program, three times, taking the worst median (`gate/timing.py`, `noise_floor`). Its keep threshold is that floor
minus 0.01, at most 0.99 (`phases/phase_b.py`; fallback 0.97, `phases/verdicts.py`). In E1-final's 90 class-R agent
trials the thresholds were **0.884–0.990, median ≈ 0.985**.

A change is **kept unless it is measurably slower** than the program before it: ratio (before ÷ after) at or above
the threshold. This one rule is used at every speed decision — D40 in Phase A (a rewrite with DiscoPoP's pragmas
against the program before the rewrite), Phase B (each pragma's marginal gain; D33 for sets), Settle (the finished
file against the original), and the floor (the agent's program against DiscoPoP's own) — so the agent never ships
a program it measured as slower, but it can ship one that is only as fast. The "≥ 1.1× measured" in the agent's
start-up banner is `--min-measured-speedup`, used only by the gate's performance stage, which runs only when the
model writes the pragmas (`--llm-pragmas`, off by default, D23).

## 4. Why the two disagree — "parallel, not faster"

The agent's bar is *not slower beyond noise, at the timing size*; the harness's is *at least 1.1×, at the larger
verification size, at 6 or 12 threads*. A loop that gains a little at the timing size can gain less or nothing at
the verification size (memory bandwidth). E1-final, class R: the Haiku agent shipped **82 correct parallel
programs; 65 are FASTER; 17 are "parallel, not faster"** with harness speedups:

| harness speedup | programs |
|---|---:|
| 1.00× – 1.10× (a little faster, below the bar) | 12 (1.01, 1.016, 1.037, 1.071, 1.075, 1.078, 1.082, 1.083 ×3, 1.089, 1.094) |
| 0.94× – 0.997× (as fast as the original, or slightly slower) | 5 (`s212` 0.94, 0.951, 0.997; `s252` 0.965, 0.984) |

None is slower than 0.91×, so none is unusable; none is FASTER. **The author's decision (3 Oct): the agent keeps
its rule** (no 1.1× bar inside the agent); the disagreement is reported as above.

## 5. The speed check in the E2 experiments (E2-B1, E2-V3, E2-O3): off

E2 asks whether DiscoPoP's evidence helps the model find a CORRECT parallel version (RQ4); its primary outcome is a
race-free verified parallel program covering the hot loop. With the speed check on, a correct but slow program is
retried or reverted and the effect of the evidence mixes with speed; the model alone is told the same speed-off
goal in the agent's own words (`bare_llm --no-require-speedup`). **We still know which programs are faster**: the
harness times every program as in §2 whatever the agent's own check did, and every E2 read-out reports FASTER
beside the primary outcome. **The author's decision (3 Oct): E2-O3 keeps the speed check off**, as pre-registered
and as E2-V3 ran (its ORDER-2 cells and the `k48` control are reused).

## 6. Is a model-alone program semantically correct?

The model alone has no gate during its run — that is what the comparison asks (D37). Its finished program is
judged afterwards by the same two tests every agent program passes:

1. **The harness** (§2, `cli.py`): the full output — a digest and a dump of every result array — compared with
   the original's, relative error ≤ 1e-9, on the shipped input AND on a perturbed input (seed 7: every input
   value scaled by up to ±20 %, signs kept, so a program right only for the shipped data fails); at 6 and 12 threads, 5 runs each,
   which must also agree with each other; a program that does not compile is unusable; a program that edits the
   measurement code is redone (Fix 103).
2. **The race check** (`tools/race_check.py`): the agent's OWN gate stages, run after the fact on every
   model-alone parallel program — ThreadSanitizer with libarcher (which sees OpenMP's barriers), the schedule
   matrix (1, 2, 4 threads × static, dynamic,1, guided) and the output against the original on both inputs at the
   agent size, within the numerical noise floor of legal rebuilds of the original. A model-alone FASTER counts as
   race-free only when this check is clean.

So a model-alone program counts as valid only by the standard the agent's programs meet. E1-final, class R
(unusable = wrong output, racy, slower than 0.91×, or not compiling): Haiku alone 47, Sonnet 9, Opus 1 (did not
compile), Fable 0; the agent 1. Class D, where the agent and DiscoPoP alone declined all 12: Opus's prefix scans on
`s3112` (3) and Fable's on `s3112` and `s323` (4) passed the harness but failed the agent's gate on the perturbed
input — not counted as valid. Every unusable model-alone program is a point for the agent.

**Limits.** This is testing, not proof: a race that never manifests and that TSan misses, or a program right only
for both tested inputs, can pass. The agent's own "never ships a wrong program" holds only as far as its gate can
see — E1-final's `s341` rep1 (a prefix sum under `parallel for`, excused by the gate's OpenMP-barrier heuristic)
was caught by this same race check and is counted unusable (Fix 104). A stricter **semantic audit** for every arm
(more inputs, sizes and thread counts; DiscoPoP's dependences on every final program) was considered and **not
adopted (the author, 3 Oct)**: the question — are the model-alone changes valid by the agent's own standard — is
answered by the two tests above.

## Sources

`agent/tools/cli.py` (verify, classify), `discopop_agent/gate/timing.py` (`measure_marginal`, `noise_floor`),
`discopop_agent/phases/phase_b.py`, `settle.py`, `floor.py`, `verdicts.py`; `agent/tools/race_check.py`,
`main_comparison_stats.py`; T0.1 and T0.4 in THESIS_EXPERIMENTS §6; E1-final's archived trials
(`results/E01f_final_three_way/runs/`) and read-out (`analysis/`).
