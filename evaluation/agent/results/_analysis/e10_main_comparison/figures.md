# Figures

Built from 81 trial(s) in run(s): e10, e10_dp_alone, e10_lu_fix84.
Data: `trials.csv` (one row per trial), `gate_failures.csv` (long format), `vs_discopop_alone.csv` / `.md` (the main comparison: every agent trial paired with DiscoPoP alone on the same benchmark).

## `fig_vs_discopop_alone.pdf`

THE MAIN COMPARISON — DiscoPoP alone against DiscoPoP + agent, per benchmark. Both programs are timed against the same sequential original (the reference axis; a program left unchanged sits at 1×); the number at the right is agent ÷ DiscoPoP alone, medians over repeats. Rows sorted by that ratio. Verdict counts and every pair: vs_discopop_alone.md / .csv.

## `fig_outcomes.pdf`

Outcome of every trial as judged by the harness (not the agent), per arm and model. BROKEN = accepted but computes different values (unsafe acceptance); no verdict = verification, agent or profiling error; hatched = correct and parallel on a kernel too short to time (T0.1), so no speed verdict.

## `fig_speedups.pdf`

Best measured speedup per trial at the verify size, on the timed kernel region (PolyBench convention; whole-program speedup is in trials.csv), correct parallel results only (BROKEN trials are never given a speedup). Grey lines: 1× and the 1.1× acceptance threshold. Kernel labels carry the plan's group (A ready, B restructurable, C order matters).

## `fig_gate_stages.pdf`

Which part of the gate rejected the model's rewrites, cheapest first: static checks (clause, dependences), build (apply, compile, OpenMP compile), races (TSan, schedule stress), correctness, performance. Per-stage counts are in gate_failures.csv. Build-error rejections are refunded by the agent and still counted here.

## `fig_cost.pdf`

Cost per trial: agent wall-clock time and model calls. Dots are trials; the black tick is the median. Two measures of different scale, so two panels.
