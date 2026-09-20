# `agent/results/` — the thesis's record of every run

This directory is **tracked in git**. Every experiment and instrument study the harness
runs — on the server or on the Mac — is copied here by `agent/benchmark archive` and
committed, so the numbers, tables, figures and every program the agent produced are in the
repository's history and can be cited, re-plotted and re-checked without the machine that
produced them. `INDEX.md` (generated) lists the runs; `THESIS_EXPERIMENTS.md` (one level
up) says what each run is for and what it found.

The raw runs stay under `agent/runs/` (ignored by git): the same files plus the DiscoPoP
profile trees (`profiles/**/.discopop/`, several MB per benchmark, regenerable, and
digested in `profile.json`), the trials' scratch copies (`work/`) and binaries. Those three
are the only things an archive drops; `ARCHIVE.json` in every run lists what it kept, with
each file's size and sha256, and where the run came from.

## Layout of an archived trial run

```
<run_id>/
  ARCHIVE.json                 what was archived, from where, sha256 per file, run status/outcomes
  manifest.json                the invocation: benchmarks, arms, models, flags, host, git heads
                               of agent and harness, tool versions, sizes, timeout, seed
  results.json                 every trial record in one file (what results.json holds is
                               exactly the union of the trial.json files below)
  overview.md, tables/*.md     the run's summary table and per-trial table (Markdown)
  figures/
    trials.csv                 ONE ROW PER TRIAL — the table every thesis number comes from
    gate_failures.csv          long format: (trial, phase, gate stage, count)
    fig_*.pdf / fig_*.png      figures (PDF for the thesis, PNG for slides)
    figures.md                 what each figure shows, which experiment it serves, n
  profiles/<suite>/<kernel>/
    <sources>                  the program every trial of this benchmark started from
    meta.json                  the package's provenance (generator version, digests)
    profile.json               DiscoPoP timings, explorer attempts, pattern counts,
                               profile_sha256 (the profile tree's digest)
    instrument.log, profiled_run.log, explore_*.log
  benchmarks/<suite>/<kernel>/<arm>/<model>/rep<N>/
    trial.json                 the trial: agent exit, LLM calls/tokens, verdicts of the
                               independent verification, outcome, package_integrity
                               (before/after digests), timings
    original.* / original/     the program as given to the agent
    final.* / final/           the program the agent left
    changes.diff               unified diff between the two
    agent.log                  the agent's full log (plan, every candidate, every gate verdict)
    llm_usage.jsonl            one line per model call (tokens, latency, model id)
    agent_patches/             every candidate the model produced, accepted or not:
      candidates.jsonl, candidates/, accepted.json, region_*.patch
```

An instrument study (T0.x) archives its own files: `summary.json` / `chosen.json` with the
study's name and host, and the CSV it produced (`sizes.csv`, `profiles.csv`, `regions.csv`,
`patterns.csv`, …).

## Where the thesis's numbers come from

| Thesis material | File |
|---|---|
| any table of outcomes, speedups, pragmas, cost, tokens | `figures/trials.csv` (combined over runs with `agent/benchmark plots --runs a,b --name X` → `agent/analysis/X/`, archive that too) |
| gate stage failure counts (E2/E3 read-outs) | `figures/gate_failures.csv` |
| outcome and speedup figures | `figures/fig_outcomes`, `fig_speedups`, `fig_evidence_model`, `fig_gate_stages`, `fig_cost` |
| a specific rewrite (for a listing or a case study) | `benchmarks/.../changes.diff`, `final.*`, `agent_patches/` |
| why a candidate was rejected | `agent.log` (gate verdicts) and `agent_patches/candidates.jsonl` |
| what DiscoPoP saw | `profiles/.../profile.json` (counts); the tree itself only in `agent/runs/` |
| that a trial ran on an unmodified program | `trial.json` → `package_integrity.before/after` |
| verification sizes, profile stability, runtime shares, patterns in `main`, packaging equivalence | the `t0_*` runs |

## Procedure (also in RUNBOOK.md)

After every experiment on the server:

```
agent/tools/server.sh fetch <run_id>     # copies the run back and archives it here
git add agent/results && git commit -m "results: <run_id> (<experiment>)" && git push
```

`fetch` with no run id fetches and archives every run. Archiving a run again replaces its
directory (git history keeps the earlier state), so a resumed or re-scored run is archived
again after it changes.
