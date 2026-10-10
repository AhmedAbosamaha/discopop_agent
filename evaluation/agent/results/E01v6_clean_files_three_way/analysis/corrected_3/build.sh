#!/usr/bin/env bash
# E1-v6, the third corrected read-out (10 Oct 2026), beside the registered one (analysis/) and the two corrected
# ones (analysis/corrected/, analysis/corrected_2/). As the second, with `s341` of the runs on packaging v8
# (`tsvc_c4/s341`: data in which the positions move between repetitions, so that the form every winning program
# had taken — the positions computed once, in front of the repetition loop — fails the output check; the
# author's decision of 10 Oct, record §6) in place of its `tsvc_c2` trials: the agent and DiscoPoP alone from
# e1v6c_v8_agent, each model alone from e1v6c_v8_bare_<model>. Run from evaluation/:
#     bash agent/results/E01v6_clean_files_three_way/analysis/corrected_3/build.sh
set -euo pipefail
PY=../venv/bin/python
E=agent/results/E01v6_clean_files_three_way
O=${1:-$E/analysis/corrected_3}
AD="default_v4+discopop_gate_v4"
DROPS="--drop e1v6_r_3:tsvc_c2/s281 --drop e1v6_r_4:tsvc_c2/s331 --drop e1v6_a:tsvc_c2/s313 --drop e1v6_r_2:tsvc_c2/s241 --drop e1v6_r_4:tsvc_c2/s341"
mkdir -p "$O"
$PY agent/tools/main_comparison_stats.py e1v6_r_1 e1v6_r_2 e1v6_r_3 e1v6_r_4 e1v6_a e1v6_d e1v6c_s281 e1v6c_v7_agent e1v6c_v7_control e1v6c_s241 e1v6c_v8_agent \
    --arm default_v4 --baseline-arm discopop_gate_v4 $DROPS --figures --out "$O" > "$O/main_comparison_stats.log" 2>&1
for m in haiku sonnet opus fable; do
    $PY agent/tools/main_comparison_stats.py e1v6_r_1:$AD e1v6_r_2:$AD e1v6_r_3:$AD e1v6_r_4:$AD e1v6_a:$AD e1v6_d:$AD \
        e1v6c_s281:$AD e1v6c_v7_agent:$AD e1v6c_v7_control:$AD e1v6c_s241:$AD e1v6c_v8_agent:$AD \
        e1v6_bare_$m:bare_llm_v4 e1v6c_v7_bare_$m:bare_llm_v4 e1v6c_v8_bare_$m:bare_llm_v4 \
        --arm default_v4 --three-way default_v4 --bare bare_llm_v4 --baseline-arm discopop_gate_v4 \
        --races $E/checks/e1v6_race_check/$m/results.jsonl --races $E/checks/e1v6c_race_check/v7_$m/results.jsonl \
        --races $E/checks/e1v6_race_check/control_agent/results.jsonl --races $E/checks/e1v6c_race_check/s281_agent/results.jsonl \
        --races $E/checks/e1v6c_race_check/v7_agent/results.jsonl --races $E/checks/e1v6c_s241_race_check/s241_agent/results.jsonl \
        --races $E/checks/e1v6c_v8_race_check/v8_agent/results.jsonl --races $E/checks/e1v6c_v8_race_check/v8_$m/results.jsonl \
        --same-loop tsvc_c2/s241=tsvc_c3/s241 \
        $DROPS --drop e1v6_bare_$m:tsvc_c2/s331 --drop e1v6_bare_$m:tsvc_c2/s313 --drop e1v6_bare_$m:tsvc_c2/s341 --out "$O/$m" > "$O/$m.log" 2>&1
done
$PY agent/tools/e1f_tests.py --analysis "$O" --name E1-v6 --registered "5 Oct 2026" --family 52 --out-name e1v6_tests_corrected_3.md
