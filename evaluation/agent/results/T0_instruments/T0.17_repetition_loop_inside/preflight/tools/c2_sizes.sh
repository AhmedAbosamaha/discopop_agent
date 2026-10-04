#!/bin/bash
# T0.1 on packaging v6 (server, no model): the sizes of the 44 tsvc_c2 packages, measured on NUMA node 0.
cd "$HOME/discopop_agent/evaluation" || exit 1
export PATH="$HOME/discopop_agent/venv/bin:$PATH"
PY="$HOME/discopop_agent/venv/bin/python"
L=agent/runs/_launcher
mkdir -p $L
KERNELS=$(ls -d agent/prepared/tsvc_c2/*/ | xargs -n1 basename | sed 's|^|tsvc_c2/|' | paste -sd, -)
numactl --cpunodebind=0 --membind=0 $PY agent/tools/size_table.py --out agent/runs/t0_1_c2_sizes --kernels "$KERNELS" \
    > $L/t0_1_c2_sizes.log 2>&1
echo "SIZES_EXIT $?" >> $L/t0_1_c2_sizes.log
