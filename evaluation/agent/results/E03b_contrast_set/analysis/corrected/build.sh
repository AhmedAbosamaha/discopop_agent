#!/usr/bin/env bash
# E3b, the corrected read-out (11 Oct 2026), beside the registered one (analysis/). As registered, with `s316` of
# e3bc_s316 — both setups and DiscoPoP alone on the DiscoPoP with B23 repaired (a minimum was reported as a
# maximum; the author's "Ok" of 10 Oct, record §6) — in place of that loop's trials in e3b_1. Haiku alone as
# registered: no DiscoPoP runs in it. The same test on corrected data (the family stays 53). The table then holds
# trials on two DiscoPoP versions: `s316` on the repaired one, the other loops on the one before the repair, on
# which the repair changes nothing (group B23: no package stores a minimum call). Run from evaluation/:
#     bash agent/results/E03b_contrast_set/analysis/corrected/build.sh
set -euo pipefail
PY=../venv/bin/python
E=agent/results/E03b_contrast_set
O=${1:-$E/analysis/corrected}
RUNS="e3b_1 e3b_2 e3b_3 e3b_4 e3bc_s316"
mkdir -p "$O"
$PY agent/tools/main_comparison_stats.py $RUNS --baseline-arm discopop_gate_v5 --drop e3b_1:tsvc_c4/s316 --figures --out "$O" > "$O/main_comparison_stats.log" 2>&1
for setup in discopop_writes:default_v5 model_writes:llm_pragmas_v5; do
    d=${setup%%:*}; arm=${setup##*:}
    mkdir -p "$O/$d"
    specs=""; for r in $RUNS; do specs="$specs $r:$arm+discopop_gate_v5"; done
    $PY agent/tools/main_comparison_stats.py $specs e3b_bare_haiku:bare_llm_v4 \
        --arm "$arm" --three-way "$arm" --bare bare_llm_v4 --baseline-arm discopop_gate_v5 \
        --races "$E/checks/e3b_race_check/$d/results.jsonl" --races "$E/checks/e3bc_race_check/$d/results.jsonl" \
        --races "$E/checks/e3b_race_check/haiku_alone/results.jsonl" \
        --drop e3b_1:tsvc_c4/s316 \
        --figures --out "$O/$d" > "$O/$d.log" 2>&1
done
$PY agent/tools/e3b_tests.py --analysis "$O"
