#!/bin/bash
# E6 pre-flight on the clean package llnl_c1/lulesh, stage A, on the SERVER (no model; registered runs e6c_prepare,
# e6c_t0_1_sizes, e6c_t0_6_dp_main):
#   e6c_prepare      — the server builds the package with the generator's validation (clang-20); its meta.json, the
#                      validation and the digests of the package and of the harness header go to runs/e6c_prepare/;
#   e6c_t0_1_sizes   — T0.1 on NUMA node 0, then
#   e6c_t0_6_dp_main — T0.6 on NUMA node 1, side by side with T0.1.
# The reference (reference_solutions/llnl_c1/lulesh) is tracked and arrives with the sync; it is not regenerated here.
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E06_lulesh/preflight/tools/e6c_stageA.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E6C_STAGEA_DONE` is in runs/_launcher/e6c_stageA_done.log; then
# `server.sh fetch e6c_prepare e6c_t0_1_sizes e6c_t0_6_dp_main`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
P=agent/runs/e6c_prepare
mkdir -p $L $P
rm -f $L/e6c_stageA_*.log
$PY agent/tools/prepare_apps.py lulesh_c1 --out agent/prepared --validate --cxx clang++-20 > $L/e6c_stageA_prepare.log 2>&1
echo "PREPARE_EXIT $?" >> $L/e6c_stageA_prepare.log
cp agent/prepared/llnl_c1/lulesh/meta.json $P/meta.json
cp agent/prepared/apps_validation.json $P/apps_validation.json
( cd agent/prepared && sha256sum llnl_c1/lulesh/* _harness/llnl_c1/lulesh_harness.h ) > $P/files.sha256
numactl --cpunodebind=0 --membind=0 $PY agent/tools/size_table.py --kernels llnl_c1/lulesh --out agent/runs/e6c_t0_1_sizes \
    > $L/e6c_stageA_sizes.log 2>&1 && echo "SIZES_EXIT 0" >> $L/e6c_stageA_sizes.log || echo "SIZES_EXIT $?" >> $L/e6c_stageA_sizes.log &
numactl --cpunodebind=1 --membind=1 $PY agent/tools/dp_main_study.py --benchmarks llnl_c1/lulesh --out agent/runs/e6c_t0_6_dp_main \
    > $L/e6c_stageA_dp_main.log 2>&1 && echo "DP_MAIN_EXIT 0" >> $L/e6c_stageA_dp_main.log || echo "DP_MAIN_EXIT $?" >> $L/e6c_stageA_dp_main.log &
wait
echo "E6C_STAGEA_DONE $(date -u +%H:%M)" >> $L/e6c_stageA_done.log
