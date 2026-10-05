# E1-bare's read-out — the same model alone, beside the agent, each against DiscoPoP alone

E1-bare ran as two runs, `e1_bare_a` (node 0) and `e1_bare_b` (node 1), on commit `cf0d5d96`,
23 Sep 2026, 04:59–08:12 UTC: TSVC class R, 18 loops × arm `bare_llm` × 5, Haiku 4.5
(`claude-haiku-4-5-20251001`), verification as E1 (per-kernel size, 6 / 12 threads, 5 repeats,
seeded input). Its `default` counterpart and its DiscoPoP-alone baseline are E1's own trials
(`e1_r_a`, `e1_r_b`), so the four runs are read together. Everything here is the TSVC primary set:
E1-bare has no other benchmarks, so there is no separate `tsvc/` folder.

    agent/benchmark plots --runs e1_r_a,e1_r_b,e1_bare_a,e1_bare_b --suite tsvc --name e1_bare_tsvc
    python3 agent/tools/main_comparison_stats.py e1_r_a e1_r_b e1_bare_a e1_bare_b --suite tsvc --arm bare_llm --out <dir>/bare
    python3 agent/tools/main_comparison_stats.py e1_r_a e1_r_b e1_bare_a e1_bare_b --suite tsvc --arm default --out <dir>/default

The `plots` step also writes a `main_comparison_stats.md` that POOLS both arms (the tool pools
every non-baseline arm unless `--arm` is given); it is not copied here — `main_comparison_stats.md`
in this folder is the two per-arm runs one after the other. The `default` half is identical to
E1's primary-set read-out (`E01_main_comparison/analysis/tsvc/`), checked by diff.

| file | what it holds |
|---|---|
| `main_comparison_stats.md` (+ `_bare_llm.json`, `_default.json`) | per arm: rates with Wilson intervals, paired speed statistics, unsafe named |
| `vs_discopop_alone.md` / `.csv` | every trial's verdict against DiscoPoP alone, per loop, both arms |
| `fig_verdict_matrix.png` / `.pdf` | one square per trial, one panel per arm — E1-bare at a glance |
| `fig_vs_discopop_alone.png` / `.pdf` | per loop, every repeat's speedup over the sequential original; BROKEN in red |
| `fig_speedups`, `fig_outcomes`, `fig_gate_stages`, `fig_cost` | as in E1; `fig_gate_stages` shows only the agent's gate (the bare arm has none) |
| `trials.csv`, `gate_failures.csv` | one row per trial (270: 90 DiscoPoP alone, 90 agent, 90 model alone); every gate rejection |

## The comparison (pre-registered read-out: rates and BROKEN named)

| TSVC class R, 18 loops × 5 | model alone (`bare_llm`) | DiscoPoP + agent (`default`, E1) | DiscoPoP alone |
|---|---|---|---|
| verified parallel program | **71 of 88** (81 %, CI 71–88 %) | 46 of 90 (51 %, CI 41–61 %) | 0 of 90 |
| FASTER (≥ 1.1× over the sequential original) | **58 of 88** (66 %, CI 56–75 %) | 44 of 90 (49 %, CI 39–59 %) | 0 of 90 |
| FASTER and race-free (the gate's TSan + schedule matrix, run afterwards, `checks/e1b_race_check/`) | **53 of 88** (4 races on `s293`, 1 not judgeable) | 44 of 90 (all passed the gate) | 0 of 90 |
| **BROKEN — a wrong program shipped** | **17 of 88** (19 %), in 9 of 18 loops | **0** | 0 |
| correct but slower (`worse`, ≤ 0.91×) shipped | 12 | 0 (Settle dropped 15 such programs) | 0 |
| invalid (no verdict) | 2 (s243 rep 4 moved the timer calls; s244 rep 2 does not compile) | 0 | 0 |
| loops with at least one FASTER trial | 16 of 18 | 14 of 18 | 0 |
| loops FASTER in 5 of 5 | 8 | 5 | 0 |
| model calls / cost | 90 calls, 7.82 USD-eq. (per trial median 0.08; 81 s wall-clock) | 125 calls, 13.95 USD-eq. (per trial median 0.12; 287 s wall-clock) | none |

Rates are over the trials with a verdict (88 for the model alone: 2 invalid). The paired speed
statistic of the bare arm (median model-alone ÷ DiscoPoP-alone 2.41×, Wilcoxon p = 0.0002) is
over its CORRECT trials only — a wrong program is given no speed — and over 17 loops, because
`s211` has no correct trial at all; the agent's 1.08× counts every `no-change` as 1.00×. The two
numbers are therefore not comparable and are not set against each other.

**Per loop** (FASTER of 5; the model alone's BROKEN in brackets). What happened on the agent's side is read from its archived patches and logs and, for the speed check, measured again (`../checks/e1b_marginal_replay/`):

| loop | agent | model alone | what decides it |
|---|---|---|---|
| `s127` `s254` `s291` `s293` | 5 | 5 | the same rewrite (closed-form index, carried scalar replaced, peeled wrap-around) |
| `s292` `s255` | 5, 4 | 5, 5 | the same; the model alone is faster on `s292` (3.91× vs 2.34× median) |
| `s281` | **0** | **5** | BOTH models split the index range at `LEN/2` — the agent's in all 5 repeats. The agent lost it after the model: in reps 2–5 the gate's clause stage rejected DiscoPoP's correct `private(x)` on one half (a false reject), in rep 1 DiscoPoP reported a do-all on one half only; one half parallel is 0.63–0.97× the original (`checks/e1b_marginal_replay/`). *Corrected: the first version of this row said the agent's model copied the array* |
| `s331` | **0** | **5** | a max reduction — `reduction(max: j)` in 4 trials, by hand with `critical` in 1: the pragma DiscoPoP cannot write (T0.13); the agent's pragmas are DiscoPoP's (D23) |
| `s121` | 0 | 3 | both buffer `a` with a loop. In the agent's reps 1, 2, 5 DiscoPoP reported a do-all on both loops, and Phase B's speed check dropped each one ALONE (0.6–1.0×); together they are 1.3–1.4× faster than the original (replay). Rep 3 used `memcpy` (Settle, 0.73×), rep 4 is a slow variant (0.13×). *Corrected: the first version said the agent's rewrites used `memcpy`* |
| `s244` | 1 | 3 (1) | all 3 FASTER trials of the model alone remove the dead store (`a[i+1]` is overwritten by the next iteration except at the last). The agent's rep 1 had three safe do-alls dropped one by one, together 1.30× (replay); reps 2, 4: TSan rejected DiscoPoP's pragma; rep 3 slow (0.15×) |
| `s212` `s243` `s1213` | 3, 3, 2 | 4 (1), 3 (1), 2 (2) | similar rates; the model alone's wrong ones are the distributions below |
| `s252` | **3** | 1 (1) | the agent's scalar expansion vs the model alone's slower or wrong variants |
| `s112` | **1** | 0 (2) | `s112` is a WAR recurrence: the agent's gate rejected 3 wrong rewrites, the model alone shipped 2 |
| `s211` | **1** | 0 (**5**) | every model-alone trial is wrong (below); the agent's gate rejected 3 wrong rewrites |
| `s241` | 1 | 1 (3) | the agent's gate rejected 5 wrong rewrites; the model alone shipped 3 |
| `s341` | 0 | 1 (1) | a compaction; the model alone's other trials are 0.6× |

**On these 18 loops E1's gate rejected 23 wrong rewrites in 19 of the agent's trials (Phase A,
correctness)** — on `s112` 3, `s1213` 4, `s211` 3, `s212` 2, `s241` 5, `s243` 2, `s244` 3,
`s281` 1 — seven of the nine loops on which the model alone shipped its wrong programs
(`E01_main_comparison/analysis/gate_failures.csv`); on the other two, `s252` and `s341`, the
agent's model never produced a wrong rewrite for Phase A to reject, and on `s281` it did where
the model alone did not. The Phase-B rejections of the `default` arm
(59 TSan, 6 correctness / schedules) are of DiscoPoP's own racy pragmas, which `discopop_gate`
meets too, and are not counted as the model's.

## Every BROKEN trial, by cause (read from `final.c` against `original.c`)

| cause | trials | what the program does |
|---|---|---|
| **loop distribution that reverses a dependence** | `s211` reps 1, 2, 3 · `s212` rep 5 · `s241` rep 2 · `s243` rep 3 · `s244` rep 4 · `s1213` rep 2 | the statements are split into two (three) parallel loops in an order where a later loop reads the NEW value of an element the original read OLD (`s212`: `b[i] += a[i+1]*d[i]` after all of `a` was already multiplied), or the reverse (`s211` reps 1–3: `a[i] = b[i-1]…` computed before `b` is updated — the same code in all three, differing only in comments; identical errors). `s1213` rep 2 declares and fills a snapshot `a_old` and then never reads it. The order error is deterministic — wrong at any thread count; `s211` reps 1–3 and `s243` rep 3 also carry a WAR race in a later loop, which the gate's TSan flags first (`checks/e1b_race_check/`) |
| **distribution in the right order, the remaining loop still races** | `s211` reps 4, 5 | `b` first, correctly — but `b[i] = b[i+1] - …` in parallel reads an element another thread may already have overwritten (WAR); dump error 0.04 |
| **pragma on the unchanged recurrence** | `s112` reps 1, 3 | `#pragma omp parallel for` on `a[i+1] = a[i] + b[i]` running backwards (WAR); error 0.03 |
| **a race kept inside the parallel loop** | `s241` rep 1 | reads `a[i+1]` into a local first — still racing with the thread that writes it |
| **Jacobi instead of Gauss–Seidel** | `s1213` rep 4 | double buffers `a_new`/`b_new`: every iteration reads the OLD `b[i-1]` where the original reads the one just computed — the Gauss–Seidel → Jacobi change the first seidel-2d smoke made (record §2, §7), here in a TSVC loop |
| **snapshot taken at the wrong point** | `s241` rep 3 | copies `a` into `a_prev` at the end of each repetition, BEFORE `pb_mix(nl)` changes `a[k]` and `a[0]`, so the next repetition reads two stale elements; dump error 0.93, digest error 5e-6 |
| **a different algorithm** | `s252` rep 3 | turns `a[i] = s_i + s_{i-1}` into a full prefix scan (log-step, two parallel loops per step); error 1.0, and 0.09–0.12× |
| **order-destroying compaction** | `s341` rep 2 | the packed index comes from a `critical` counter, so the order of `a` depends on thread timing (dump error 0.88); the timed run at 6 threads then exited non-zero |

Eight of the seventeen are one shape — a loop distribution that ignores which value the original
read — and all seventeen are wrong on the output check alone; none needed TSan to be found.
The two invalid trials: `s243` rep 4 reordered the scaffold calls (the timer no longer brackets
the computation; `SCAFFOLD_MODIFIED`, a correct program otherwise), `s244` rep 2 wrote
`private(i)` for an `i` declared inside the `for` (does not compile).

**Race-checked afterwards (`checks/e1b_race_check/`).** The harness runs no TSan and no schedule
variation; the agent's gate does. Every model-alone program was therefore put through the gate's
own race and output stages on the server (no model), with the agent's 46 parallel programs as the
control — all 46 clean. Of the model alone's 58 FASTER programs **53 are clean**, 4 are races
(`s293` reps 1–4: a pragma on `a[i] = a[0]`, benign in effect, a data race nonetheless) and 1
cannot be judged by the gate (`s341` rep 5 calls the OpenMP runtime, which the gate's first compile
does not link). Its 13 parallel-not-faster programs are clean; the gate stops all 17 BROKEN ones.
Race-checked, the model alone is FASTER in 53 of 88 trials, the agent in 44 of 90.

## Process

90 trials, 90 model calls, 0 failed. The harness profiled each loop with DiscoPoP although the
arm reads nothing from it (the runner profiles every benchmark before its trials): 18 profiles,
7 of them hit the random explorer stall (600 s each, draw repeated) — cost only, no effect on a
trial. The `main_comparison_stats.md` process lines sum the stall count over every TRIAL record of
all four runs (each record repeats its loop's profile: 35 = 7 × 5 for E1-bare) and give one host
load range for all four runs; E1-bare alone ran at host load 3,027–7,392 (median 4,288).

## What was done about it — agent v2 (23 Sep evening)

The author approved D32 and D33 and the two gate fixes (Fixes 91–94, `ad57f134`). E1 was not rerun
(D34): the programs it would have ended with under v2 were rebuilt from the archived patches and
verified by the harness (`../checks/e1b_v2_sources/`, `../checks/e1b_v2_verify/`) — the 7 D33 trials
FASTER 1.49–3.00×, the 4 `s281` trials FASTER 2.55–3.25×, both controls as in E1. **E1 under v2: FASTER
in 55 of 90, 0 unsafe**, against the model alone's 53 of 88 race-checked.

