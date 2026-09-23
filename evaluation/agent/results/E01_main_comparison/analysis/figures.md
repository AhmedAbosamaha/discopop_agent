# Figures

Built from 290 trial(s) in run(s): e1_a, e1_d, e1_r_a, e1_r_b.
Data: `trials.csv` (one row per trial), `gate_failures.csv` (long format), `vs_discopop_alone.csv` / `.md` (the main comparison: every agent trial paired with DiscoPoP alone on the same benchmark).

## `fig_vs_discopop_alone.pdf`

THE MAIN COMPARISON, trial by trial — every repeat of DiscoPoP alone (upper dots) and of DiscoPoP + agent (lower dots) on the same axis: speedup over the sequential original, which is the reference both are timed against (a program left unchanged sits at 1×). Grouped by the measured class: R is the claim; in A the agent must not do worse than DiscoPoP alone; in D declining — 1× — is the correct answer. At the right: in how many repeats each reached a FASTER program (≥ 1.1×). Verdicts per trial: vs_discopop_alone.md; statistics: main_comparison_stats.md.

## `fig_verdict_matrix.pdf`

THE MAIN COMPARISON, TRIAL BY TRIAL — arm `default`, claude-haiku-4-5-20251001. One square per agent trial, coloured by its verdict against DiscoPoP alone on the same benchmark and profile; rows grouped by MEASURED class (R: DiscoPoP alone reaches no verified parallel program; A: it does; D: a true recurrence, must decline). On class R every green square is a verified parallel program that only the agent reached; hatched = reached, but not 1.1× faster (or too short to time). Counts, rates with intervals and the paired test: main_comparison_stats.md.

## `fig_outcomes.pdf`

Outcome of every trial as judged by the harness (not the agent), per arm and model. BROKEN = accepted but computes different values (unsafe acceptance); no verdict = verification, agent or profiling error; hatched = correct and parallel on a kernel too short to time (T0.1), so no speed verdict.

## `fig_speedups.pdf`

Best measured speedup per trial at the verify size, on the timed kernel region (PolyBench convention; whole-program speedup is in trials.csv), correct parallel results only (BROKEN trials are never given a speedup). Grey lines: 1× and the 1.1× acceptance threshold. Kernel labels carry the plan's group (A ready, B restructurable, C order matters).

## `fig_gate_stages.pdf`

Which part of the gate rejected the model's rewrites, cheapest first: static checks (clause, dependences), build (apply, compile, OpenMP compile), races (TSan, schedule stress), correctness, performance. Per-stage counts are in gate_failures.csv. Build-error rejections are refunded by the agent and still counted here.

## `fig_cost.pdf`

Cost per trial: agent wall-clock time and model calls. Dots are trials; the black tick is the median. Two measures of different scale, so two panels.
