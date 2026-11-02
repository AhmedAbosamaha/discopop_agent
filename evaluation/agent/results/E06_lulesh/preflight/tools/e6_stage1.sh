#!/bin/bash
# E6 pre-flight, stage 1 on the SERVER (no model; registered runs e6_t0_1_sizes and e6_t0_6_dp_main), side by side:
#   T0.1 on NUMA node 0 — the size at which LULESH's serial run reaches 1 s (verification size) and 0.25 s (timing size);
#   T0.6 on NUMA node 1 — one profile as the harness takes it: does DiscoPoP alone propose patterns inside main (D4)?
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E06_lulesh/preflight/tools/e6_stage1.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E6_STAGE1_DONE` is in runs/_launcher/e6_stage1_done.log; then `server.sh fetch e6_t0_1_sizes e6_t0_6_dp_main`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
mkdir -p $L
rm -f $L/e6_stage1_*.log
numactl --cpunodebind=0 --membind=0 $PY agent/tools/size_table.py --kernels llnl/lulesh --out agent/runs/e6_t0_1_sizes \
    > $L/e6_stage1_sizes.log 2>&1 && echo "SIZES_EXIT 0" >> $L/e6_stage1_sizes.log || echo "SIZES_EXIT $?" >> $L/e6_stage1_sizes.log &
numactl --cpunodebind=1 --membind=1 $PY agent/tools/dp_main_study.py --benchmarks llnl/lulesh --out agent/runs/e6_t0_6_dp_main \
    > $L/e6_stage1_dp_main.log 2>&1 && echo "DP_MAIN_EXIT 0" >> $L/e6_stage1_dp_main.log || echo "DP_MAIN_EXIT $?" >> $L/e6_stage1_dp_main.log &
wait
echo "E6_STAGE1_DONE $(date -u +%H:%M)" >> $L/e6_stage1_done.log
