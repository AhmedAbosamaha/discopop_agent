# E10's main comparison — the agent against DiscoPoP alone

The comparison the thesis leads with (D19) spans THREE runs — `e10` (the agent's three arms),
`e10_dp_alone` (the DiscoPoP-alone baseline on five of the kernels) and `e10_lu_fix84` (`lu`,
all four arms, after Fix 84) — so no single run's `figures/` directory contains it. It is
produced by combining them and copied here, because `agent/analysis/` is a working directory
and git cannot un-ignore a file inside an ignored directory.

    agent/benchmark plots --runs e10,e10_dp_alone,e10_lu_fix84

| file | what it holds |
|---|---|
| `vs_discopop_alone.md` | the verdict table: per arm and per benchmark, gained / better / equal / worse / lost / neither / unsafe |
| `vs_discopop_alone.csv` | one row per agent trial, paired with its DiscoPoP-alone baseline |
| `fig_vs_discopop_alone.pdf` / `.png` | one dumbbell per benchmark, DiscoPoP alone → agent, on the speedup-over-sequential axis |
| `trials.csv`, `figures.md` | the tidy data and the captions behind them |

**Result:** `speed_gate_large` 2 gained · 6 better · 2 equal · 4 worse · **0 lost** · 0 unsafe;
`full` 1 · 4 · 5 · 5 · 0 lost · **1 unsafe**; `speed_gate_small` 0 · 0 · 0 · 2 worse · **10 LOST**.
Median agent ÷ DiscoPoP alone = 1.00× on a set that is five-sixths class A, which is the expected
answer there: the agent must do no harm, not win. See THESIS_EXPERIMENTS.md §7 `e10_dp_alone`.
