#!/bin/bash
# E6 diagnostic on the SERVER (no model; registered run e6c_nofold_patterns): which of the clean package's edits changes
# DiscoPoP's task patterns (record §6, 2-3 Nov)? The variant llnl_c1_nofold is llnl_c1 with the per-thread minimum left as
# LLNL wrote it — never an experiment's package, never read by a model. It is built with the generator's validation and
# profiled once as the harness profiles it (dp_main_study.py, NUMA node 1); its patterns.csv places every pattern in its
# function, to be set beside the profiles of e6_classes_a (version 1) and e6c_classes_a (llnl_c1).
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E06_lulesh/preflight/tools/e6c_nofold.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E6C_NOFOLD_DONE` is in runs/_launcher/e6c_nofold_done.log; then `server.sh fetch e6c_nofold_patterns`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
mkdir -p $L
rm -f $L/e6c_nofold_*.log
$PY agent/tools/prepare_apps.py lulesh_c1_nofold --out agent/prepared --validate --cxx clang++-20 > $L/e6c_nofold_prepare.log 2>&1
echo "PREPARE_EXIT $?" >> $L/e6c_nofold_prepare.log
numactl --cpunodebind=1 --membind=1 $PY agent/tools/dp_main_study.py --benchmarks llnl_c1_nofold/lulesh \
    --out agent/runs/e6c_nofold_patterns > $L/e6c_nofold_dp.log 2>&1
echo "DP_EXIT $?" >> $L/e6c_nofold_dp.log
echo "E6C_NOFOLD_DONE $(date -u +%H:%M)" >> $L/e6c_nofold_done.log
