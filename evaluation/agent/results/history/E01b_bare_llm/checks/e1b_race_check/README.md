# e1b_race_check — the gate's race stages over programs that never went through the gate

**Why.** The harness judges every trial by its output: the full value dump on the shipped and the
perturbed input, and a digest repeated five times at each of 6 and 12 threads (which also catches a
program that does not repeat itself at a fixed thread count). It runs no ThreadSanitizer and does not
vary the OpenMP schedule — only the agent's gate does. So E1-bare's FASTER programs were
output-checked while the agent's were output- and race-checked. This check closes that gap.

**How.** `agent/tools/race_check.py` (commit `a5eda509`, server, 23 Sep 2026 12:45–12:49 UTC, no model)
hands each archived program — original → final of the trial — to the agent's own
`validate(mode="safety")`, the call Phase B makes for a pragma: apply, compile, the `-fopenmp` build
under TSan (clang-20, **libarcher loaded**, `/usr/lib/llvm-20/lib/libarcher.so`), the schedule matrix
(1/2/4 threads × static / dynamic,1 / guided, loops given `schedule(runtime)`), and the output against
the ORIGINAL on the shipped input and on `--check-input 7`, with the reference and numerical noise floor
captured as the agent captures them. `validate()` is called directly, so the macOS barrier re-run cannot
hide a race; it would have fired on none. Pinned with `numactl` to one NUMA node (24 cores) as E1's lanes.

    numactl --cpunodebind=0 --membind=0 venv/bin/python evaluation/agent/tools/race_check.py \
        --runs e1_bare_a,e1_bare_b --arm bare_llm --out .../bare
    numactl --cpunodebind=1 --membind=1 venv/bin/python evaluation/agent/tools/race_check.py \
        --runs e1_r_a,e1_r_b --arm default --suite tsvc --outcomes FASTER,parallel-not-faster --out .../control

`bare/` and `control/` hold `manifest.json` (toolchain, archer, commit) and `results.jsonl` (one record
per program: the gate's verdict, the stage, its diagnostic, the schedules covered); `logs/` the console.

## Result

**Positive control: all 46 of the agent's parallel TSVC programs from E1 come out clean** (44 FASTER,
2 parallel-not-faster) — the tool reproduces the gate.

| the model alone (`bare_llm`), harness outcome | gate: clean | TSan | schedules | output | cannot judge |
|---|---:|---:|---:|---:|---:|
| FASTER (58) | **53** | **4** | 0 | 0 | 1 |
| parallel-not-faster (13) | 13 | 0 | 0 | 0 | 0 |
| BROKEN (17) | 0 | 9 | 1 | 7 | 0 |
| invalid (2) | 1 (`s243` rep 4, the scaffold move is a harness rule) | 0 | 0 | 0 | 1 (`s244` rep 2 does not compile) |

- **Four FASTER programs are races: `s293` reps 1–4.** The model put `#pragma omp parallel for` on
  `a[i] = a[0]` unchanged, so iteration 0 writes `a[0]` while other threads read it. It rewrites the
  same value, so no output ever changes — benign in effect, but a data race, which C and OpenMP leave
  undefined. Its rep 5, and the agent's version, read `a[0]` once before the loop.
- **One FASTER program the gate cannot judge: `s341` rep 5.** It calls the OpenMP runtime
  (`omp_get_thread_num`, `omp_get_max_threads`); the gate's first compile links without OpenMP, so it
  fails there whatever the program does. A blind spot of the gate (a false reject class for E7), not a
  verdict on the program.
- **The gate stops all 17 BROKEN programs** — TSan 9 (`s112` r1, r3; `s211` r1–r5; `s241` r1; `s243` r3),
  output 7 (`s1213` r2, r4; `s212` r5; `s241` r2, r3; `s244` r4; `s252` r3), schedule matrix 1
  (`s341` r2). `s211` reps 1–3, read before as a wrong loop order only, also carry the WAR race of the
  `b` loop that reps 4–5 have.

**So:** race- and output-checked, the model alone is FASTER in **53 of 88** trials (60 %), the agent in
44 of 90 (49 %). The race check lowers the bare arm's count by 4 (5 with the unjudgeable one) and
does not change the reading: the model alone still reaches more.
