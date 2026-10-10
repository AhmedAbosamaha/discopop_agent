#!/usr/bin/env bash
# E3, the corrected read-out (10 Oct 2026), beside the registered one (analysis/). As registered, with `s341` of
# e3c_v8_s341 — both setups and DiscoPoP alone on `tsvc_c4/s341`, the data in which the positions move between
# repetitions (the author's decision of 10 Oct, record §6) — in place of its `tsvc_c2` trials in e3_r_4, and Haiku
# alone's `s341` from e1v6c_v8_bare_haiku in place of e1v6_bare_haiku's. Run from evaluation/:
#     bash agent/results/E03_who_writes_the_pragmas/analysis/corrected/build.sh
set -euo pipefail
PY=../venv/bin/python
E=agent/results/E03_who_writes_the_pragmas
E1=agent/results/E01v6_clean_files_three_way
O=${1:-$E/analysis/corrected}
RUNS="e3_r_1 e3_r_2 e3_r_3 e3_r_4 e3_d_1 e3_d_2 e3_d_3 e3_d_4 e3_a e3c_v8_s341"
mkdir -p "$O"
$PY agent/tools/main_comparison_stats.py $RUNS --baseline-arm discopop_gate_v5 --drop e3_r_4:tsvc_c2/s341 --figures --out "$O" > "$O/main_comparison_stats.log" 2>&1
for setup in discopop_writes:default_v5 model_writes:llm_pragmas_v5; do
    d=${setup%%:*}; arm=${setup##*:}
    mkdir -p "$O/$d"
    specs=""; for r in $RUNS; do specs="$specs $r:$arm+discopop_gate_v5"; done
    $PY agent/tools/main_comparison_stats.py $specs e1v6_bare_haiku:bare_llm_v4 e1v6c_v7_bare_haiku:bare_llm_v4 e1v6c_v8_bare_haiku:bare_llm_v4 \
        --arm "$arm" --three-way "$arm" --bare bare_llm_v4 --baseline-arm discopop_gate_v5 \
        --races "$E/checks/e3_race_check/$d/results.jsonl" --races "$E/checks/e3c_v8_race_check/$d/results.jsonl" \
        --races $E1/checks/e1v6_race_check/haiku/results.jsonl --races $E1/checks/e1v6c_race_check/v7_haiku/results.jsonl \
        --races $E1/checks/e1v6c_v8_race_check/v8_haiku/results.jsonl \
        --same-loop tsvc_c2/s241=tsvc_c3/s241 \
        --drop e3_r_4:tsvc_c2/s341 --drop e1v6_bare_haiku:tsvc_c2/s331 --drop e1v6_bare_haiku:tsvc_c2/s313 --drop e1v6_bare_haiku:tsvc_c2/s341 \
        --figures --out "$O/$d" > "$O/$d.log" 2>&1
done
$PY agent/tools/e3_tests.py --analysis "$O"
