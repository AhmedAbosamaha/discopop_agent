# Figures

Built from 7 trial(s) in run(s): e2_smoke_a.
Data: `trials.csv` (one row per trial), `gate_failures.csv` (long format), `vs_discopop_alone.csv` / `.md` (the main comparison: every agent trial paired with DiscoPoP alone on the same benchmark).

## `fig_vs_discopop_alone.pdf`

THE MAIN COMPARISON, trial by trial — every repeat of DiscoPoP alone (upper dots) and of DiscoPoP + agent (lower dots) on the same axis: speedup over the sequential original, which is the reference both are timed against (a program left unchanged sits at 1×). Grouped by the measured class: R is the claim; in A the agent must not do worse than DiscoPoP alone; in D declining — 1× — is the correct answer. At the right: in how many repeats each reached a FASTER program (≥ 1.1×). Verdicts per trial: vs_discopop_alone.md; statistics: main_comparison_stats.md.

## `fig_verdict_matrix.pdf`

THE MAIN COMPARISON, TRIAL BY TRIAL — arms `compiler_remarks_b1`, `default`, `full_b1`, `hotspot_only_b1`, `no_evidence`, `no_evidence_b1`, claude-haiku-4-5-20251001 (one panel each). One square per agent trial, coloured by its verdict against DiscoPoP alone on the same benchmark and profile; rows grouped by MEASURED class (R: DiscoPoP alone reaches no verified parallel program; A: it does; D: a true recurrence, must decline). On class R every green square is a verified parallel program that only the agent reached; hatched = reached, but not 1.1× faster (or too short to time). Counts, rates with intervals and the paired test: main_comparison_stats.md.

## `fig_outcomes.pdf`

Outcome of every trial as judged by the harness (not the agent), per arm and model. BROKEN = accepted but computes different values (unsafe acceptance); no verdict = verification, agent or profiling error; hatched = correct and parallel on a kernel too short to time (T0.1), so no speed verdict.

## `fig_evidence_model.pdf`

Evidence × model (E2). Left: share of trials with a correct parallel speedup ≥ 1.1×. Right: unsafe acceptances as counts, never rates. One LLM attempt per region in both arms.

## `fig_cost.pdf`

Cost per trial: agent wall-clock time and model calls. Dots are trials; the black tick is the median. Two measures of different scale, so two panels.
