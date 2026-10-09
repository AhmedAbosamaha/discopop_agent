#!/usr/bin/env bash
# E3's read-out, as registered on 9 Oct 2026 before any of its trials (THESIS_EXPERIMENTS §6, "Plan, E3
# pre-registration" and "Plan, E3 launch"). One read-out per setup — that setup's and DiscoPoP alone's trials of E3
# beside Haiku alone's of E1-v6 (the corrected table's: `s331` and `s313` from the v7 runs; `s241` ran on `tsvc_c2`
# only, the same kernel file byte for byte, counted in the row of `tsvc_c3/s241`) — then the two tests. Run from
# evaluation/:
#     bash agent/results/E03_who_writes_the_pragmas/analysis/build.sh
set -euo pipefail
PY=../venv/bin/python
E=agent/results/E03_who_writes_the_pragmas
E1=agent/results/E01v6_clean_files_three_way
O=${1:-$E/analysis}
RUNS="e3_r_1 e3_r_2 e3_r_3 e3_r_4 e3_d_1 e3_d_2 e3_d_3 e3_d_4 e3_a"
for setup in discopop_writes:default_v5 model_writes:llm_pragmas_v5; do
    d=${setup%%:*}; arm=${setup##*:}
    mkdir -p "$O/$d"
    specs=""; for r in $RUNS; do specs="$specs $r:$arm+discopop_gate_v5"; done
    $PY agent/tools/main_comparison_stats.py $specs e1v6_bare_haiku:bare_llm_v4 e1v6c_v7_bare_haiku:bare_llm_v4 \
        --arm "$arm" --three-way "$arm" --bare bare_llm_v4 --baseline-arm discopop_gate_v5 \
        --races "$E/checks/e3_race_check/$d/results.jsonl" \
        --races $E1/checks/e1v6_race_check/haiku/results.jsonl --races $E1/checks/e1v6c_race_check/v7_haiku/results.jsonl \
        --same-loop tsvc_c2/s241=tsvc_c3/s241 \
        --drop e1v6_bare_haiku:tsvc_c2/s331 --drop e1v6_bare_haiku:tsvc_c2/s313 \
        --figures --out "$O/$d" > "$O/$d.log" 2>&1
done
$PY agent/tools/e3_tests.py --analysis "$O"
