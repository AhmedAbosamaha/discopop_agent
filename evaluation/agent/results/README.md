# `agent/results/` — every result of the campaign, one folder per experiment

**Start here.** Each folder below is one experiment or instrument. Inside each, `REPORT.md` is the
report: the question, the status, the result in one paragraph, the figures, what the folder
holds, every run with its purpose and status, the case studies, and the experiment record's own
entries for it. Everything here is tracked in git.

| Folder | What it is | Status |
|---|---|---|
| [`E01_main_comparison/`](E01_main_comparison/REPORT.md) | **E1 — the main comparison: DiscoPoP alone vs DiscoPoP + agent** (the thesis's headline) | done |
| [`E01b_bare_llm/`](E01b_bare_llm/REPORT.md) | E1-bare — the same model with no DiscoPoP and no gate | done 23 Sep; superseded by E1c's model-alone arm (D36) |
| [`E01c_clean_three_way/`](E01c_clean_three_way/REPORT.md) | E1c — the clean three-way E1: DiscoPoP alone · the agent · the model alone | done 25 Sep |
| [`E02_evidence_feedback_model/`](E02_evidence_feedback_model/REPORT.md) | E2 — evidence, feedback and model strength | A+B done 25 Sep; the rest waits for the V3 pilot |
| [`V3_pilot_d40/`](V3_pilot_d40/REPORT.md) | The agent v3 pilot (D40) — the speed verdict inside the model's budget | running 26 Sep |
| [`E10_speed_check/`](E10_speed_check/REPORT.md) | E10 — does the speed check keep unnecessary changes out? | done |
| [`E11_repoomp/`](E11_repoomp/REPORT.md) | E11 — against RepoOMP on its NPB-C kernels | pre-flight |
| [`T0_instruments/`](T0_instruments/) | T0.1–T0.14 — the studies that prove the instruments before any experiment is read | done |
| [`audit_benchmark_suitability/`](audit_benchmark_suitability/REPORT.md) | DiscoPoP alone on every benchmark: which can show the contribution at all (§5k) | done |
| [`pilots/`](pilots/REPORT.md) | the first agent runs, before the design was fixed | history |
| [`harness_checks/`](harness_checks/REPORT.md) | smokes and observed runs that tested the harness and the agent (not experiments) | history |
| [`logs/`](logs/) | launcher and diagnostic logs | reference |

Two lists span all folders: [`INDEX.md`](INDEX.md) — every run, by experiment, with its purpose
and status (valid · superseded · void · running); [`EXHIBITS.md`](EXHIBITS.md) — every case study,
by experiment, with the claim it supports and its verdict against DiscoPoP alone.

**Inside an experiment folder**

```
<EXPERIMENT>/
  REPORT.md       the report — generated, do not edit (see below)
  analysis/       the read-out: statistics (main_comparison_stats.md), every paired verdict
                  (vs_discopop_alone.md/.csv), trials.csv, figures (fig_*.png/.pdf);
                  analysis/tsvc/ = the same for the primary set (D30)
  exhibits/       case studies: one folder per trial worth showing (before_after.png, diff.tex,
                  console.png, attempts.md, facts.json; rejected_attempt.png where the gate
                  caught a wrong rewrite)
  runs/           the archived runs — the evidence
  checks/         verifications made during the read-out (e.g. programs re-verified on the server)
  preflight/      smoke runs before the launch
  superseded/     runs a later run replaced (kept, never cited as a result)
```

**How it stays complete.** `campaign.json` is the registry: every run, read-out and exhibit, the
experiment it belongs to, what it is for, whether it is still valid. `agent/benchmark archive`
puts a run where the registry says; `agent/tools/campaign.py reports` writes the reports and the
two lists; `agent/tools/campaign.py check` fails when anything is missing — an unregistered or
unarchived run, a run the record never names, an experiment without its report or read-out, an
exhibit without its verdict against DiscoPoP alone, uncommitted results. The RUNBOOK's definition
of done ends with that check printing `OK`. Run ids never change; only the folder they sit in
follows the registry.

The raw runs stay under `agent/runs/` (ignored by git): the same files plus the DiscoPoP
profile trees (`profiles/**/.discopop/`, several MB per benchmark, regenerable, and
digested in `profile.json`), the trials' scratch copies (`work/`) and binaries. Those three
are the only things an archive drops; `ARCHIVE.json` in every run lists what it kept, with
each file's size and sha256, and where the run came from. `agent/analysis/` is scratch.

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
| an experiment's result, its statistics and its figures | `<EXPERIMENT>/analysis/` — `main_comparison_stats.md`, `vs_discopop_alone.md`, `fig_*.pdf`; `analysis/tsvc/` for the primary set |
| any table of outcomes, speedups, pragmas, cost, tokens | `<EXPERIMENT>/analysis/trials.csv` (combined over the experiment's runs); one run alone: `runs/<run>/figures/trials.csv` |
| gate stage failure counts | `analysis/gate_failures.csv` |
| a case study (listing, before/after, console) | `<EXPERIMENT>/exhibits/<name>/` — `diff.tex`, `before_after.pdf`, `console.png`, `facts.json` |
| a specific rewrite | `runs/<run>/benchmarks/.../changes.diff`, `final.*`, `agent_patches/` |
| why a candidate was rejected | `agent.log` (gate verdicts) and `agent_patches/candidates.jsonl` |
| what DiscoPoP saw | `profiles/.../profile.json` (counts); the tree itself only in `agent/runs/` |
| that a trial ran on an unmodified program | `trial.json` → `package_integrity.before/after` |
| verification sizes, profile stability, runtime shares, patterns in `main`, packaging equivalence, classes, ceilings | `T0_instruments/T0.xx_*/` |

## Procedure (also in RUNBOOK.md)

After every experiment on the server:

```
# BEFORE launching: register the run ids in results/campaign.json (group, section, role, status "running")
agent/tools/server.sh fetch <run_id>     # copies the run back and archives it into its experiment folder
agent/tools/campaign.py reports          # REPORT.md per experiment, INDEX.md, EXHIBITS.md
agent/tools/campaign.py check            # must print OK — the RUNBOOK's definition of done
git add agent/results && git commit -m "results: <run_id> (<experiment>)" && git push
```

`fetch` with no run id fetches and archives every run. Archiving a run again replaces its
directory (git history keeps the earlier state), so a resumed or re-scored run is archived
again after it changes.
