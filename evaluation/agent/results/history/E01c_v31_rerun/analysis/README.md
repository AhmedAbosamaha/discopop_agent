# E1c-v3.1 — read-out

Generated 27 Sep 2026 from the archived runs `e1c31_r_1`–`e1c31_r_4` (class R), `e1c31_a` (class A) and `e1c31_d`
(class D) — agent v3.1 at `5935bded`, Haiku, the pre-B8/B9/B4 DiscoPoP, as registered — and, for the baselines
no agent version changes, E1c's `discopop_gate` and `bare_llm` trials (`e1c_r_1`–`e1c_r_4`, `e1c_a`, `e1c_d`) with
E1c's race checks.

```
# the three-way main comparison, class R (RUN:ARM+ARM keeps only those arms of a run)
agent/tools/main_comparison_stats.py e1c31_r_1 e1c31_r_2 e1c31_r_3 e1c31_r_4 \
    e1c_r_1:discopop_gate+bare_llm e1c_r_2:discopop_gate+bare_llm e1c_r_3:discopop_gate+bare_llm e1c_r_4:discopop_gate+bare_llm \
    --arm default --three-way default --races agent/results/E01c_clean_three_way/checks/e1c_race_check/bare/results.jsonl --out <here>
# the controls, classes A and D → controls/
agent/tools/main_comparison_stats.py e1c31_a e1c31_d e1c_a:discopop_gate+bare_llm e1c_d:discopop_gate+bare_llm \
    --arm default --three-way default --races agent/results/E01c_clean_three_way/checks/e1c_ad_race_check/bare/results.jsonl --out <here>/controls
# v3.1 against v2 (E1c's default arm), paired by loop → v31_vs_v2.md: v2's per-loop counts from the same tool on
#   e1c_r_1:default … e1c_r_4:default (+ the same baselines), then a one-sided Wilcoxon over the 18 loops (script in the record, §7)
# where the trials stop → why_trials_fail_v31.md (the funnel counts D41's "APPLIED as D40 judged it" since 27 Sep)
agent/tools/failure_funnel.py e1c31_r_1 e1c31_r_2 e1c31_r_3 e1c31_r_4 --arms default --out <here>/why_trials_fail_v31.md
# figures against DiscoPoP alone (the plots' own main_comparison_stats.* are not copied: the file here is the three-way)
agent/benchmark plots --runs e1c31_r_1:default,e1c_r_1:discopop_gate,…,e1c31_r_4:default,e1c_r_4:discopop_gate --name e1c31_classR
```

The re-queued / not re-queued split (trials whose `requeued_regions` > 0) is computed from `trials.csv` / the trial
records and reported in the record (§7, `e1c31_r_1`–`4`).
