# Figures

Built from 150 trial(s) in run(s): e2c_ab_1.
Data: `trials.csv` (one row per trial), `gate_failures.csv` (long format), `vs_discopop_alone.csv` / `.md` (the main comparison: every agent trial paired with DiscoPoP alone on the same benchmark).

## `fig_verdict_matrix.pdf`

THE MAIN COMPARISON, TRIAL BY TRIAL — arms `full_b1`, `no_evidence`, `no_evidence_b1`, `twin_dp`, `twin_full`, `twin_no_evidence`, claude-haiku-4-5-20251001 (one panel each). One square per agent trial, coloured by its verdict against DiscoPoP alone on the same benchmark and profile; rows grouped by MEASURED class (R: DiscoPoP alone reaches no verified parallel program; A: it does; D: a true recurrence, must decline). On class R every green square is a verified parallel program that only the agent reached; hatched = reached, but not 1.1× faster (or too short to time). Counts, rates with intervals and the paired test: main_comparison_stats.md.

## `fig_outcomes.pdf`

Outcome of every trial as judged by the harness (not the agent), per arm and model. BROKEN = accepted but computes different values (unsafe acceptance); no verdict = verification, agent or profiling error; hatched = correct and parallel on a kernel too short to time (T0.1), so no speed verdict.

## `fig_speedups.pdf`

Best measured speedup per trial at the verify size, on the timed kernel region (PolyBench convention; whole-program speedup is in trials.csv), correct parallel results only (BROKEN trials are never given a speedup). Grey lines: 1× and the 1.1× acceptance threshold. Kernel labels carry the plan's group (A ready, B restructurable, C order matters).

## `fig_gate_stages.pdf`

Which part of the gate rejected the model's rewrites, cheapest first: static checks (clause, dependences), build (apply, compile, OpenMP compile), races (TSan, schedule stress), correctness, performance. Per-stage counts are in gate_failures.csv. Build-error rejections are refunded by the agent and still counted here.

## `fig_evidence_model.pdf`

Evidence × model (E2). Left: share of trials with a correct parallel speedup ≥ 1.1×. Right: unsafe acceptances as counts, never rates. One LLM attempt per region in both arms.

## `fig_cost.pdf`

Cost per trial: agent wall-clock time and model calls. Dots are trials; the black tick is the median. Two measures of different scale, so two panels.
