# evaluation/ — the experiment harness of the thesis

Everything that runs, judges, records and plots the thesis experiments lives here, next to the
system it evaluates. One commit of this repository identifies an experiment's whole state.

| Path | What it is |
|---|---|
| `agent/benchmark` | the harness CLI: `run`, `verify-source`, `report`, `plots`, `archive`, `rescore` |
| `agent/tools/` | packagers (`prepare_*.py`), instruments (T0.x), figures, exhibits, `server.sh` / `job.sh` |
| `agent/THESIS_EXPERIMENTS.md` | **the record**: every decision, change, instrument and run, with reasons |
| `agent/RUNBOOK.md` | how to run things, and the checklist for every experiment |
| `agent/EXPERIMENT_PLAN.html` | the evaluation plan (published copy: see the record) |
| `agent/results/` | tracked archive of every run (`ARCHIVE.json` with a sha256 per file, `INDEX.md`) |
| `agent/thesis_material/` | exhibits: before/after code images, diffs, consoles, the numbers to quote |
| `agent/reference_solutions/` | expert solutions of the restructuring benchmarks — never staged into a trial |
| `agent/runs/`, `agent/prepared/` | working directories, git-ignored: fetched runs, generated packages |
| `shared/run_store.py` | the run store (one self-contained directory per run) |
| `benchmarks/` | the SOURCES of the suites used: PolyBench/C 3.2, NPB, RepoOMP's NPB-C, TSVC-2, LULESH (as shipped and serial-path-only), burkardt `md`, Rodinia `nw` / `pathfinder` / `hotspot`. Each suite keeps its own licence file |

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
Record: `agent/THESIS_EXPERIMENTS.md`, change log, D20.
