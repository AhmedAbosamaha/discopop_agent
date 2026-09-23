# evaluation/ — the experiment harness of the thesis

Everything that runs, judges, records and plots the thesis experiments lives here, next to the
system it evaluates. One commit of this repository identifies an experiment's whole state.

**Where to start:** the results → [`agent/results/README.md`](agent/results/README.md) (one folder per
experiment, each with a `REPORT.md`); how to run and the rule for every experiment →
[`agent/docs/RUNBOOK.md`](agent/docs/RUNBOOK.md); why everything is as it is →
[`agent/docs/THESIS_EXPERIMENTS.md`](agent/docs/THESIS_EXPERIMENTS.md).

| Path | What it is | In git |
|---|---|---|
| `agent/results/` | **every result, one folder per experiment or instrument** — `REPORT.md`, `analysis/` (statistics, verdicts, figures), `exhibits/` (case studies), `runs/` (the archived runs); `campaign.json` registers every run and exhibit; `INDEX.md`, `EXHIBITS.md` list them | yes |
| `agent/docs/` | `RUNBOOK.md` (how to run, the definition of done), `THESIS_EXPERIMENTS.md` (**the record**: every decision, change, instrument and run, with reasons), `EXPERIMENT_PLAN.html` and `FLOW.html` (the published plan and pipeline pages, repository copies) | yes |
| `agent/config/` | what the harness reads: `arms.json` (every agent configuration and every experiment's arms), `benchmark_classes.json` (the measured classes, T0.11), `kernel_sizes.json` (T0.1), `kernel_groups.json` | yes |
| `agent/benchmark` | the harness CLI: `run`, `verify-source`, `plots`, `archive`, `report`, `rescore` | yes |
| `agent/tools/` | packagers (`prepare_*.py`), instruments (T0.x), figures, exhibits, `campaign.py` (layout, reports, the completeness check), `server.sh` / `job.sh`, the harness's tests (`test_*.py`) | yes |
| `agent/reference_solutions/` | expert solutions of the restructuring benchmarks, by suite — never staged into a trial | yes |
| `agent/runs/`, `agent/prepared/`, `agent/prepared_single/`, `agent/analysis/` | working directories: fetched runs with their DiscoPoP profile trees, generated benchmark packages, scratch read-outs. Everything that matters from them is copied into `agent/results/` | no (ignored) |
| `shared/run_store.py` | the run store (one self-contained directory per run) | yes |
| `benchmarks/` | the SOURCES of the suites used: PolyBench/C 3.2, NPB, RepoOMP's NPB-C, TSVC-2, LULESH (as shipped, serial path, LLNL's OpenMP), burkardt `md`, Rodinia. Each suite keeps its own licence file | yes |

All commands run from this directory (`cd evaluation`); every `agent/...` path in the documents is
relative to it. Type check: `venv/bin/python -m mypy --config-file=evaluation/mypy.ini
evaluation/agent/tools/*.py evaluation/shared/*.py` (from the repository root).

## Where it came from

Until 2026-09-19 this was the `agent-experiments` branch of the research group's
`new_benchmark_harness` (RWTH GitLab), a harness built to compare DiscoPoP versions. Of that
repository the thesis used its own `agent/` directory, one helper (`shared/run_store.py`) and the
benchmark sources; the rest — three other harnesses, a GUI, and 4 GB of reference outputs and data
files — it never touched, and the repository could not be cloned in full from GitLab. On
2026-09-20 the used part was copied here from commit `1514ceb` (tracked files only: 5,350 files,
42 MB). The old branch is frozen and tagged `moved-to-discopop_agent`; runs archived up to `e10`
record its commit hashes, later runs record this repository's.

**Proof that the move changed nothing:** a FRESH CLONE of this repository (53 MB) regenerates all 70
benchmark packages byte-identical to the ones generated in the old repository — every file, every
metadata field (the clone test caught two things the working copy hid: the root `.gitignore`'s
`data*/` swallowed PolyBench's `datamining/` kernels, and the PolyBench packager discovered kernels
through the old harness's config directories; both fixed); the integrity test (30 checks) and the scaffold test
pass; a no-model smoke run reproduces the earlier outcome. The only code changes are how the agent
repository is located and `server.sh sync` (one `git` fast-forward instead of `git` plus `rsync`).
Record: `agent/docs/THESIS_EXPERIMENTS.md`, change log, D20.
