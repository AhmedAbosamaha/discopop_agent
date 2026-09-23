# E1's main comparison — DiscoPoP alone vs DiscoPoP + agent

E1 ran as four runs — `e1_r_a`, `e1_r_b` (class R, two NUMA lanes, ×5), `e1_a` (class A, ×1)
and `e1_d` (class D, ×3) — all on commit `00d4594f`, Haiku 4.5, arms `discopop_gate` vs
`default`. No single run's `figures/` holds the comparison, so it is produced by combining them
and copied here: `agent/analysis/` is a working directory and git ignores it.

    agent/benchmark plots --runs e1_r_a,e1_r_b,e1_a,e1_d --name e1_all
    python3 agent/tools/main_comparison_stats.py e1_r_a e1_r_b e1_a e1_d --suite tsvc --out <dir>/tsvc

The narrative, the deviations and the exhibits are in `agent/docs/THESIS_EXPERIMENTS.md` §7
(`e1_r_a`, `e1_r_b` and `e1_a`, `e1_d`); the raw trials in `agent/results/<run>/`.

| file | what it holds |
|---|---|
| `tsvc/main_comparison_stats.md` | **the headline**: the primary set of D30 (TSVC-2) per class — Wilson intervals, Wilcoxon signed-rank on per-loop medians, Cliff's δ, bootstrap CI, unsafe named |
| `main_comparison_stats.md` | the same statistics on the registered set (all 33 benchmarks, incl. the non-TSVC class-R ones) |
| `vs_discopop_alone.md` / `.csv` | every paired verdict (gained, gained-not-faster, better, equal, worse, lost, neither, unsafe, invalid) per benchmark and per class |
| `fig_verdict_matrix.png` / `.pdf` | one cell per trial, grouped by class — E1 at a glance |
| `fig_vs_discopop_alone.png` / `.pdf` | per benchmark: DiscoPoP alone vs the agent, median speedup over the sequential original (a loop gained in 2 of 5 trials has median 1.00×; the matrix shows those gains) |
| `fig_speedups`, `fig_outcomes`, `fig_gate_stages`, `fig_cost` | speedups per thread count, outcome counts, where the gate rejected, model cost per trial |
| `trials.csv` | one row per trial (290), every recorded field |
| `gate_failures.csv` | every gate rejection, by run, benchmark, arm, repeat, phase and stage |

The ten Settle-dropped programs re-verified on the server are in `agent/results/E01_main_comparison/checks/settle_check/`.
