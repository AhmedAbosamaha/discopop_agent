# `agent/results/` — every result of the campaign

**Start here.** The block below names, for each question of the campaign, the ONE folder that holds the result
that counts, what to open first in it, and the earlier versions with the reason each was replaced. Inside any
folder, `REPORT.md` is the report: the question, the status, the result in one paragraph, what the folder holds,
every run with its purpose. Everything here is tracked in git.

<!-- BEGIN GENERATED: where the final results are -->

## Where the final results are

*This block is generated from `campaign.json` (`lines`) by `agent/tools/campaign.py reports` — edit the registry, not this text.* One folder per question holds the result that counts; every other folder of that question is an earlier version, kept as history and never cited as the result.

### E1 — the main comparison: DiscoPoP alone · DiscoPoP + agent · the model alone

**Current: [`E01v6_clean_files_three_way/`](E01v6_clean_files_three_way/REPORT.md)** — E1-v6 — the headline three-way comparison on clean files in TSVC's own form (packaging v6, prompt version 4).  
Status: done.

Open first: [`analysis/e1v6_tests.md`](E01v6_clean_files_three_way/analysis/e1v6_tests.md), [`analysis/vs_e1_final.md`](E01v6_clean_files_three_way/analysis/vs_e1_final.md), [`analysis/repetition_loop.md`](E01v6_clean_files_three_way/analysis/repetition_loop.md), [`analysis/haiku/main_comparison_stats.md`](E01v6_clean_files_three_way/analysis/haiku/main_comparison_stats.md), [`REPORT.md`](E01v6_clean_files_three_way/REPORT.md).

Class R, 18 loops × 5, race-checked: DiscoPoP alone 0 of 90; the Haiku agent 73 race-free FASTER with 0 unusable; Haiku alone 38 with 50 unusable; Sonnet alone 77 with 11 (5 racy); Opus alone 89 with 0; Fable alone 89 with 1. T1 (agent > DiscoPoP alone, median 1.70×), T2 (fewer unusable than Haiku alone) and T6 (more reach than Haiku alone) rejected; against Sonnet, Opus and Fable alone no advantage in reach (Opus and Fable ahead on 6 loops). Controls: every setup but Haiku alone FASTER on the three class-A loops; the agent declines all 12 class-D trials. One of the agent's 73 (s331) parallelizes the repetition loop itself and is right only for the tested data; on s313 the agent removes the 47 unused repetitions (164×) — both possible because the result of those two loops is a scalar that our `dummy` call does not take. 821 model calls, $134 API-equivalent, 8.5 h + re-runs.

Read out 5 Oct 2026, complete: the nine tests, the controls, the race check with its positive control (all 85 of the agent's parallel programs clean), the cost, and what every program did to the repetition loop (`analysis/repetition_loop.md`).

Earlier versions (history):

| folder | what it was | why it is not the result |
|---|---|---|
| [`history/E01v5_clean_files_three_way/`](history/E01v5_clean_files_three_way/REPORT.md) | the same experiment on the first clean layout — the function was one repetition, called 48 times (4 Oct) | stopped by the author after 8 trials, none analysed: that layout made every temporary array be created 48 times |
| [`history/E01f_final_three_way/`](history/E01f_final_three_way/REPORT.md) | E1 on the one-file packages with four models alone (2–3 Oct) | its files carried our note and protected lines, every request a false size sentence, and the agent was sent a false order sentence on three loops; kept for the comparison between packagings |
| [`history/E01c_v31_rerun/`](history/E01c_v31_rerun/REPORT.md) | the three-way E1 re-run with agent v3.1 (27 Sep) | an older agent version, one model alone |
| [`history/E01c_clean_three_way/`](history/E01c_clean_three_way/REPORT.md) | the first three-way E1 on packages without the solution hint (25 Sep) | agent v2; replaced by the re-runs above |
| [`history/E01b_bare_llm/`](history/E01b_bare_llm/REPORT.md) | the model alone, first version (23 Sep) | its packages named the solving transformation in a comment (D36) |
| [`history/E01_main_comparison/`](history/E01_main_comparison/REPORT.md) | the first main comparison (21–22 Sep) | its packages named the solving transformation in a comment (D36); agent v1 |

### E2 — does DiscoPoP's evidence help the model, and what do retries with feedback add?

**Current: [`E02v6_hidden_order_clean_files/`](E02v6_hidden_order_clean_files/)** — E2-v6 — the hidden order on clean files: does DiscoPoP's evidence let the agent find a split no reading of the file can find, and can retries with feedback stand in for it?.  
Status: pre-flight.

Planned 5 Oct, not run yet. Until it is read out, the latest FINISHED results on this question are the first rows of the list below — all on the old one-file packages.

Earlier versions (history):

| folder | what it was | why it is not the result |
|---|---|---|
| [`history/E02o3_hidden_order_kernels/`](history/E02o3_hidden_order_kernels/REPORT.md) | the hidden order on three more kernels (3 Oct): with evidence 29 of 30, without 0 of 30 | old packages (our note, a false size sentence) and the order sentence of prompt version 3; E2-v6 re-tests exactly this on clean files |
| [`history/E12_stronger_models_alone/`](history/E12_stronger_models_alone/REPORT.md) | Opus and Fable alone on the hidden-order kernels (30 Sep – 3 Oct) | old packages; several of their failures were caused by our false size sentence |
| [`history/E02v3_order_statement/`](history/E02v3_order_statement/REPORT.md) | the order sentence on the first hidden-order kernel, two models (29–30 Sep) | old packages; version 3's sentence is wrong on several other loops |
| [`history/V3_pilot_d40/`](history/V3_pilot_d40/REPORT.md) | pilot of agent v3 — the speed verdict inside the model's attempts (26 Sep) | a pilot, not an experiment |
| [`history/E02b1_hidden_facts/`](history/E02b1_hidden_facts/REPORT.md) | hidden facts on TSVC loops, the earlier wording (27–29 Sep) | its primary test was not supported; the wording was replaced |
| [`history/E02_evidence_feedback_model/`](history/E02_evidence_feedback_model/REPORT.md) | evidence, feedback and model strength on the 18 TSVC loops (25 Sep) | on those loops the dependences are in plain sight and the evidence added nothing; agent v2 |

### Everything else

| folder | what it is | status |
|---|---|---|
| [`E10_speed_check/`](E10_speed_check/REPORT.md) | E10 — does the speed check keep unnecessary changes out? | done |
| [`E11_repoomp/`](E11_repoomp/REPORT.md) | E11 — against RepoOMP on its NPB-C kernels | pre-flight |
| [`T0_instruments/`](T0_instruments/) | the studies that prove the instruments before an experiment is read (sizes, classes, timing noise, package equivalence …), one sub-folder each | see each |
| [`audit_benchmark_suitability/`](audit_benchmark_suitability/REPORT.md) | Benchmark suitability audit (§5k, D18) | done |
| [`history/pilots/`](history/pilots/REPORT.md) | Pilots (before the campaign's design was fixed) | done |
| [`history/harness_checks/`](history/harness_checks/REPORT.md) | Harness and pipeline checks (not experiments) | done |
| [`logs/`](logs/) | Logs | done |

`history/` holds every folder a later experiment replaced, and the first pilots and harness checks (moved there on 5 Oct 2026; a path `results/E0…` in an older entry of the experiment record now starts `results/history/`). Nothing in `history/` is cited as a result.

<!-- END GENERATED -->

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
