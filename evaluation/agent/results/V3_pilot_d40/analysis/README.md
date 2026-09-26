# V3 pilot — read-out

Generated 26 Sep 2026 from the archived runs `v3_pilot_1`–`4` (agent v3, `701bf895`) and, for the baselines, E1c's `discopop_gate` and `bare_llm` trials on the same ten loops (`e1c_r_1`–`3`).

```
L=s112,s121,s1213,s211,s212,s241,s243,s244,s252,s281
# the funnel, v3 and its v2 baseline (E1c default, E2 no_evidence)
agent/tools/failure_funnel.py v3_pilot_1 v3_pilot_2 v3_pilot_3 v3_pilot_4 --arms default,no_evidence --out <here>/why_trials_fail_v3.md
agent/tools/failure_funnel.py e1c_r_1 e1c_r_2 e1c_r_3 e2c_ab_1 e2c_ab_2 e2c_ab_3 --arms default,no_evidence --loops $L --out <here>/why_trials_fail_v2_baseline.md
# the main comparison, once per agent arm (RUN:ARM+ARM keeps only those arms of a run)
agent/tools/main_comparison_stats.py v3_pilot_1 v3_pilot_2 v3_pilot_3 v3_pilot_4 \
    e1c_r_1:discopop_gate+bare_llm e1c_r_2:discopop_gate+bare_llm e1c_r_3:discopop_gate+bare_llm \
    --benchmarks $L --arm <arm> --three-way <arm> --races results/E01c_clean_three_way/checks/e1c_race_check/bare/results.jsonl
# figures: `default` here, `no_evidence` in no_evidence/
agent/benchmark plots --runs v3_pilot_1:<arm>,v3_pilot_2:<arm>,v3_pilot_3:<arm>,v3_pilot_4:<arm>,e1c_r_1:discopop_gate,e1c_r_2:discopop_gate,e1c_r_3:discopop_gate --benchmarks $L --name v3pilot_<arm>
```

`main_comparison_stats.md` holds both arms (the per-arm files `plots` writes are not copied). N = 3 per cell: descriptive, as registered.
