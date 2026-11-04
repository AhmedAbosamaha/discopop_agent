# E6 analysis — how each file here was made

Everything below is computed from the archive (`../runs/`, `../preflight/`, `../checks/`); nothing is measured here.

| file | what it holds | made by |
|---|---|---|
| `readout.md` | the registered read-out: outcomes per setup (after the race check), speedups at 6 and 12 threads against the sequential program and against LLNL's OpenMP version, the agent against DiscoPoP alone trial by trial, what each agent trial kept, the models alone trial by trial | `python3 evaluation/agent/results/E06_lulesh/analysis/readout.py > evaluation/agent/results/E06_lulesh/analysis/readout.md` |
| `main_comparison_stats.md`, `vs_discopop_alone.md`, `fig_*.png`, `trials.csv` | the campaign's statistics and figures for the pre-registered first configuration (`llm_pragmas_v5`) against DiscoPoP alone, with the models alone: rates with Wilson intervals, unsafe acceptances by name | `agent/tools/main_comparison_stats.py e6c_r1 e6c_r2 e6c_r3b e6c_bare --arm llm_pragmas_v5 --baseline-arm discopop_gate_v5 --three-way llm_pragmas_v5 --bare bare_llm_v4 --races results/E06_lulesh/checks/e6c_race_check/bare/results.jsonl --figures --out results/E06_lulesh/analysis` |
| `stats_c2/` | the same for the second configuration (`llm_pragmas_v5_exact`) | the same with `e6x_1 e6x_2 e6x_3 e6c_bare --arm llm_pragmas_v5_exact --three-way llm_pragmas_v5_exact --figures --out results/E06_lulesh/analysis/stats_c2` |
| `ranking/` | the agent's queue beside the queue without the measurement, on each run's initial profile (no model) | `ranking/queue_compare.py` (record §6, 3 Nov) |
| `race_launch/e6c_race.sh` | the launcher of the race check | — |

**How to read them.**

- One program, five trials per setup: the read-out is descriptive, as pre-registered — **no test**. The statistics tool's
  Wilcoxon line says so itself ("fewer than 6 non-zero pairs: no test"), and its three-way section is empty because the tool
  groups by measured class and LULESH has none; the three-way comparison is `readout.md` §1.
- `--baseline-arm discopop_gate_v5` is required: the tools' default DiscoPoP-alone arm is `discopop_gate`, so without it every
  E6 trial reads `no-baseline` (the runs' own `figures/vs_discopop_alone.md`, written at archiving, show exactly that).
- *usable* in `readout.md` = FASTER by the harness and clean in `race_check.py`. `vs_discopop_alone.md` pairs by the harness verdict only: its one `better` for Haiku alone is the program the race check found racy. *BROKEN* in the first configuration is the
  harness's reproducibility verdict (the digest not identical over 5 runs at a fixed thread count; every value within 1e-11);
  the race check, which compares within the measured noise floor, finds no data race in those programs.
- The first configuration's five agent trials are `e6c_r1` ×2, `e6c_r2` ×2 and `e6c_r3b`; the smoke trial `e6c_smoke3`
  (pre-flight) and `e6c_r3`, whose first profile failed (B28) before any trial, are not counted.
