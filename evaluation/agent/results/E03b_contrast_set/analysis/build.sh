#!/usr/bin/env bash
# E3b's read-out, as registered on 10 Oct 2026 before any of its trials (THESIS_EXPERIMENTS §6, "Plan, E3b
# pre-registration"). One read-out per setup — that setup's and DiscoPoP alone's trials beside Haiku alone's, all
# on the contrast set (suite tsvc_c4) — then the one test. E3's commands with E3b's runs. Run from evaluation/:
#     bash agent/results/E03b_contrast_set/analysis/build.sh
set -euo pipefail
PY=../venv/bin/python
E=agent/results/E03b_contrast_set
O=${1:-$E/analysis}
RUNS="e3b_1 e3b_2 e3b_3 e3b_4"
mkdir -p "$O"
# the group's own read-out and figures (the registry asks for them at analysis/): the agent in either setup, pooled,
# against DiscoPoP alone — the two setups apart are in the sub-folders below
$PY agent/tools/main_comparison_stats.py $RUNS --baseline-arm discopop_gate_v5 --figures --out "$O" > "$O/main_comparison_stats.log" 2>&1
for setup in discopop_writes:default_v5 model_writes:llm_pragmas_v5; do
    d=${setup%%:*}; arm=${setup##*:}
    mkdir -p "$O/$d"
    specs=""; for r in $RUNS; do specs="$specs $r:$arm+discopop_gate_v5"; done
    $PY agent/tools/main_comparison_stats.py $specs e3b_bare_haiku:bare_llm_v4 \
        --arm "$arm" --three-way "$arm" --bare bare_llm_v4 --baseline-arm discopop_gate_v5 \
        --races "$E/checks/e3b_race_check/$d/results.jsonl" --races "$E/checks/e3b_race_check/haiku_alone/results.jsonl" \
        --figures --out "$O/$d" > "$O/$d.log" 2>&1
done
$PY agent/tools/e3b_tests.py --analysis "$O"
