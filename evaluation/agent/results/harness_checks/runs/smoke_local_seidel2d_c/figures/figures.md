# Figures

Built from 1 trial(s) in run(s): smoke_local_seidel2d_c.
Data: `trials.csv` (one row per trial), `gate_failures.csv` (long format).

## `fig_outcomes.pdf`

Outcome of every trial as judged by the harness (not the agent), per arm and model. BROKEN = accepted but computes different values (unsafe acceptance); no verdict = verification, agent or profiling error.

## `fig_speedups.pdf`

Best measured speedup per trial at the verify size, correct parallel results only (BROKEN trials are never given a speedup). Grey lines: 1× and the 1.1× acceptance threshold. Kernel labels carry the plan's group (A ready, B restructurable, C order matters).

## `fig_cost.pdf`

Cost per trial: agent wall-clock time and model calls. Dots are trials; the black tick is the median. Two measures of different scale, so two panels.
