# e1b_marginal_replay — why the agent lost reach: Phase B's speed check, replayed

**The question.** Every one of the agent's 90 class-R TSVC trials in E1 had a rewrite pass Phase A. 44
still ended `no-change`: 15 at Settle (the rewrite copied the array per repetition — slower, confirmed
by E1's `settle_check`), 11 because DiscoPoP's pragmas on the rewrite raced or changed the output
(the gate right), and **18 because Phase B's speed check dropped pragmas that had passed every safety
stage** ("marginal 0.62–0.98× — costs more than it saves"). On several of those loops the model alone
(E1-bare) shipped a comparable program that the harness measured 1.3–3× faster.

**The hypothesis stated before the run — refuted.** The agent times with every core of its lane (24,
OMP_NUM_THREADS unset) on a host at load 3,000–7,000; the harness at 6 and 12 threads. `marginal_replay.py`
was written to test whether the verdict depends on the thread count. **It does not:** a pragma the agent
dropped measures below 1× at 6, 12 and 24 threads alike (`s121` rep 1: 0.95 / 0.92 / 0.94 and
0.91 / 0.89 / 0.83).

**How.** `agent/tools/marginal_replay.py` (commit `4679add5` for `node0/` and `node1/`, `fec42c6c` — patches without a final newline, reverted rewrites skipped as the log says — for `node1b/`; server,
23 Sep 2026 12:54–13:50 UTC, no model; one lane per NUMA node as E1's) rebuilds from each trial's archived
patches the state Phase B measured against — the original plus the Phase-A rewrite the log KEPT — and
calls the agent's own `measure_marginal` (5 interleaved pairs, whole program, the trial's
`--timing-cflags`) on: each safety-passing pragma alone against the rewrite (what Phase B asked), all of
them together against the rewrite, and the rewrite with all of them against the ORIGINAL (what Settle
asks). 18 dropped trials + 3 won trials as controls. `node0/`, `node1/`, `node1b/` hold `results.jsonl`
(59 measurements), `manifest.json` and each rebuilt program (`*_final.c`, rewrite + all safe pragmas);
`logs/` the console. `node1/` stopped at `s281` rep 4 (a patch without a final newline, then a rewrite the
log had reverted); `node1b/` resumed from there with the fixed tool — the results before the stop were
rebuilt from a single kept rewrite and stand.

## Result — the rewrite with all its safe pragmas, against the ORIGINAL (Settle's question)

| trial | 6 threads | 12 | all (24) | reading |
|---|---:|---:|---:|---|
| `s1213` rep 3 | 2.32 | **2.76** | 2.28 | **recoverable** |
| `s1213` rep 1 | 1.55 | **2.27** | 2.28 | **recoverable** |
| `s121` rep 1 | 1.49 | **1.43** | 1.62 | **recoverable** |
| `s121` rep 2 | 1.26 | **1.40** | 1.61 | **recoverable** |
| `s244` rep 1 | 1.25 | **1.30** | 1.47 | **recoverable** |
| `s121` rep 5 | 1.18 | **1.28** | 1.38 | **recoverable** |
| `s112` rep 4 | 1.00 | **1.18** | 1.39 | **recoverable** (not at 6 threads) |
| `s281` reps 1–5 | 0.83–0.97 | 0.79–0.90 | 0.63–0.75 | only ONE half of the split loop had a safe pragma (below) |
| `s341` rep 4, `s212` rep 4, `s252` rep 4 | 0.46–0.56 | 0.48–0.51 | 0.41–0.47 | the rewrite is slow — the drop was right |
| `s244` rep 3, `s341` rep 2, `s121` rep 4 | 0.13–0.15 | 0.13–0.16 | 0.10–0.14 | the rewrite is very slow — the drop was right |
| controls: `s127` / `s254` / `s291` rep 1 (FASTER in E1) | 2.91 / 1.87 / 1.94 | 3.73 / 2.31 / 3.00 | 3.89 / 2.54 / 2.37 | kept verdicts reproduced |

**The finding: the check judges pragmas one at a time, and the rewrite only pays with all of them.**
In the seven recoverable trials the rewrite split a loop into two or three (a buffer loop and a compute
loop, or one loop per statement), DiscoPoP reported a do-all on each, and each passed TSan, the schedule
matrix and the output check. Phase B then measured each pragma ALONE against the sequential rewrite and
dropped all of them (E1: 0.62–0.98×); measured TOGETHER they are **2.5–4.0× faster than the rewrite and
1.2–2.8× faster than the original** at 12 threads. Phase B never measures the set, so the program that
wins never exists. Two things put the single ratios below the threshold:
- **the pairing** — in `s121` reps 1, 2, 5 and `s244` rep 1 each pragma alone measures below 1× in this
  replay as well (0.6–1.1×, at every thread count): one parallel loop beside a sequential one does not
  pay, both together do. Why was not tested here; it is measured, reproducible, and left unexplained;
- **instability near 1.0** — in `s1213` reps 1, 3 and `s112` rep 4 the single pragmas replay mostly at
  1.1–1.25× at 6 and 12 threads (one at 0.91–1.08×, one at 0.86× with 24 threads) where E1 measured
  0.77–0.97×. Single ratios this close to the threshold are not stable on
  a host at load 3,000–7,000 (a point for T0.4); the joint ratios are far from it, so the finding does
  not rest on them.

**`s281` — a gate false reject, not the speed check.** The agent's model wrote the SAME rewrite as the
model alone in all five repeats — the index range split at `LEN/2`. In reps 2–5 DiscoPoP reported a do-all
on both halves; the gate's clause stage rejected DiscoPoP's `private(x)` on the first half ("the loop
writes `x` and later code reads it"), but the only later reads are in the second loop, each after a write
in the same iteration, and nothing reads `x` after the loops — the clause is correct (the model alone wrote
the same one; TSan-clean, 3.0×). In rep 1 DiscoPoP reported a do-all on one half only. With one half
parallel the program is 0.63–0.97× the original, so the speed check was right about what it was given.
A labelled false-reject case for E7.

## What it means

On the agent's own measurement, **7 of the 18 trials Phase B dropped would have been faster than the
original** — with them the agent would have 51 FASTER of 90, not 44 (an estimate: the combined programs
were timed by the agent's `measure_marginal`, not verified by the harness; each pragma in them passed
the gate on its own). Another 5 (`s281`) are lost to the clause false reject. **D33, proposed:** before
dropping any, Phase B measures the rewrite's safety-passing pragmas TOGETHER against the state before them
and removes one at a time only while the set still pays (backward elimination); replayed here it recovers
the seven and changes none of the eleven correct drops. The agent is frozen until E11 by the author's
decision; whether D33 enters before E2 (so E2's `default` differs from E1's and is compared within E2) or
after E11 is the author's call.
