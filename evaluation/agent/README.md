# Agent experiment harness — how to run it

Runs configurations of the DiscoPoP agent over PolyBench kernels and judges the results
independently. Design decisions and the change log are in `THESIS_EXPERIMENTS.md`.

## Prerequisites

- The harness lives INSIDE the agent repository (since 2026-09-20, `evaluation/README.md`):
  ```
  ~/discopop_agent             (with its venv built: venv/bin/python, venv/bin/discopop_cxx)
  ~/discopop_agent/evaluation  (this harness: agent/, shared/, benchmarks/)
  ```
  The agent repository is found automatically; elsewhere set `AGENT_REPO` or pass `--agent-repo`.
- clang/clang++ 19 or 20 on `PATH` (on macOS: `export PATH="/usr/local/bin:$PATH"`).
- The Claude login the agent uses: on your Mac, Claude Code already logged in; on the server,
  see “On the server” below.

All commands run from the harness root: `cd ~/discopop_agent/evaluation`.

## 1. Prepare the benchmarks (once)

```bash
agent/benchmark prepare --size SMALL            # writes agent/prepared/polybench/*
agent/benchmark prepare --size SMALL --validate # also proves each file prints exactly what
                                                # the original PolyBench program prints
agent/benchmark list-benchmarks
```

`--size` is the dataset the **agent** works at: profiling and the agent's own gate run at
this size, so keep it small. Timing happens later at `--verify-size`.

The files are generated as **C** (`<kernel>.c`), the suite's own language; the agent builds
C with `clang` and profiles it with `discopop_cc`. Benchmarks are never translated to another
language.

## 2. See what can be run

```bash
agent/benchmark list-arms          # the agent configurations, from agent/arms.json
```

## 3. Run

```bash
# the smallest useful test: one kernel, one arm, one model
agent/benchmark run polybench/seidel-2d --arms full --models haiku

# a comparison: two arms, two models, 3 repeats each, timed at 2/4/8 threads
agent/benchmark run polybench/2mm polybench/seidel-2d \
    --arms full_b1,no_evidence_b1 --models haiku,sonnet --trials 3 \
    --threads 2,4,8
# verification uses each kernel's measured size from agent/kernel_sizes.json (T0.1);
# --verify-size STANDARD would force one size for all
```

While it runs, every trial prints the line to follow it live, e.g.

```bash
tail -f agent/runs/<run_id>/benchmarks/polybench/seidel-2d/full/haiku/rep1/agent.log
```

Interrupt with Ctrl-C: the report covers the finished trials. Resume by repeating the same
command with `--run-id <run_id>` — finished trials are skipped.

Useful options:

| Option | Default | Meaning |
|---|---|---|
| `--arms a,b` | `full` | arms from `list-arms` |
| `--models a,b` | `haiku` | Claude Code model aliases (`haiku`, `sonnet`, `opus`) |
| `--trials N` | 1 | repeats of each (benchmark, arm, model) |
| `--verify-size` | `STANDARD` | dataset the harness times the result at |
| `--threads` | `min(8, cores)` | thread counts for timing |
| `--repeats` | 3 | timed runs per build (median is used) |
| `--agent-arg X` | — | extra agent flag, repeatable (e.g. `--agent-arg=--restructure-depth=1`) |
| `--keep-work` | off | keep each trial's `.discopop` copy (large) |
| `--check-seed S` | `7` | perturbed-input seed: given to the agent as `--check-input S` and used by verification; `--check-seed ""` disables |

## 3a. Baselines, without running the agent

A baseline faces the same verification as a trial — same size, same machine, same checks — and
lands in the same run, so `report` and `plots` include it beside the arms.

```bash
# compiler baseline: the untouched source, built differently
agent/benchmark verify-source polybench/2mm --label polly \
    --final-flags "-mllvm -polly -mllvm -polly-parallel -mllvm -polly-process-unprofitable" \
    --cc /usr/lib/llvm-20/bin/clang --threads 24 --run-id e1_baselines

# source baseline: an expert's OpenMP version, or another system's released output
agent/benchmark verify-source polybench/2mm --label expert_openmp \
    --source /path/to/their_version.c --run-id e1_baselines
```

`--label` takes the place of an arm's name in tables and figures; reuse one `--run-id` to collect
baselines together. A single flag must be written with `=` (`--final-flags=-funroll-loops`) — a
lone dashed word is otherwise read as an option; a quoted string containing spaces works as
written. Each record carries `kind: baseline` and the candidate's SHA-256.

First measurement (server, 2026-09-16): Polly on `2mm` at STANDARD verified clean — identical
dump, digest error 0, seeded input identical — at **35.2× on 24 threads** (kernel 7.32 s →
0.21 s). That is above the thread count because Polly tiles as well as parallelises, so quote it
as a compiler baseline, never as a scaling result.

## 4. Read the results

```bash
agent/benchmark list-runs
agent/benchmark report                 # latest run; or --run <run_id>
```

Each run is one directory:

```
agent/runs/<run_id>/
├── manifest.json      what ran: code versions (git HEAD + diff hash), host, flags
├── results.json       every trial, machine-readable
├── overview.md        summary table + all trials — start here
├── tables/            summary.md, trials.md
├── profiles/<bench>/  the one DiscoPoP profile all trials of that benchmark start from
└── benchmarks/<suite>/<kernel>/<arm>/<model>/rep<k>/
    ├── original.cpp  final.cpp  changes.diff
    ├── agent.log                     the agent's full output
    ├── agent_patches/accepted.json   what the agent kept
    └── trial.json                    this trial's record and verdict
```

Outcome words are explained in `THESIS_EXPERIMENTS.md` §3. `BROKEN` must never appear: it
means the agent accepted a change that computes different values.

## 5. Data and figures for the thesis

Every finished run writes `agent/runs/<run_id>/figures/` automatically:

```
trials.csv            one row per trial (outcome, speedups, pragmas, model calls, times, …)
gate_failures.csv     one row per trial × gate phase × stage
fig_outcomes.pdf/png  outcome composition per arm · model
fig_speedups.pdf/png  best speedup per kernel (correct results only)
fig_gate_stages.*     which gate stage rejected the model's rewrites
fig_evidence_model.*  E2: evidence × model (only when both E2 arms are present)
fig_cost.pdf/png      agent time and model calls per trial
figures.md            caption for each figure
```

Rebuild or combine runs:

```bash
agent/benchmark plots                                   # latest run
agent/benchmark plots --runs e1_core                    # one run
agent/benchmark plots --runs e1_core,e3 --name e3_matrix  # combined → agent/analysis/e3_matrix/
```

Needs `matplotlib` in the Python that runs the harness (`pip install matplotlib`).

## On the server

Code on the server is never edited directly. Change it on the Mac, then:

```bash
agent/tools/server.sh sync      # server fetches the agent commit from GitHub; this harness is rsynced
agent/tools/server.sh parity    # Mac and server compared item by item — must end with PARITY OK
```

The agent commit must be pushed, because the server pulls it from GitHub. The harness is
copied as it is on the Mac: GitLab would need a login on the server, and no login is kept there.
`parity` compares both commits, clean working trees, the installed DiscoPoP wrappers, where
`discopop_explorer` and `discopop_library` are imported from (the checkout, on both machines),
and the `anthropic` / `claude-agent-sdk` versions.

**Claude token — once, on the Mac.** Run `claude setup-token`, then store the token in the
Keychain with `security add-generic-password -a "$USER" -s claude-code-oauth-token -w` (paste
it at the prompt). It is never typed on the server.

**Launch, follow, fetch.** Everything after `--` is passed to `agent/benchmark run`:

```bash
agent/tools/server.sh run --node 1 -- polybench/seidel-2d --arms full --models haiku --run-id pilot_seidel
agent/tools/server.sh status              # running job + last 25 lines of its log
agent/tools/server.sh fetch pilot_seidel  # results → agent/runs/pilot_seidel (profile copies left out)
agent/tools/server.sh sweep               # confirm no credential is left on the server
```

`run` refuses to start unless parity holds; `--allow-dirty-harness` accepts uncommitted
harness edits for pilots (`sync` copied them, so both sides still match). The job runs
detached — the laptop can be closed — pinned with `numactl` to one NUMA node and using the
agent's venv Python. The token exists only in the job's environment, next to a throw-away
`CLAUDE_CONFIG_DIR`. When the job ends that directory is deleted and every file written during
the job is scanned for the token; the result is in the `SWEEP:` lines at the end of the job's
log in `agent/runs/_launcher/`.
