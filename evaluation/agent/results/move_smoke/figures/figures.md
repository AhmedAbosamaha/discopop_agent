# Figures

Built from 1 trial(s) in run(s): move_smoke.
Data: `trials.csv` (one row per trial), `gate_failures.csv` (long format), `vs_discopop_alone.csv` / `.md` (the main comparison: every agent trial paired with DiscoPoP alone on the same benchmark).

## `fig_outcomes.pdf`

Outcome of every trial as judged by the harness (not the agent), per arm and model. BROKEN = accepted but computes different values (unsafe acceptance); no verdict = verification, agent or profiling error; hatched = correct and parallel on a kernel too short to time (T0.1), so no speed verdict.

## `fig_cost.pdf`

Cost per trial: agent wall-clock time and model calls. Dots are trials; the black tick is the median. Two measures of different scale, so two panels.
