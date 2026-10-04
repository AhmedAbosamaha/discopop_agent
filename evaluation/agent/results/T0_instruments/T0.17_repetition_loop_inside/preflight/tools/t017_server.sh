#!/bin/bash
# T0.17 on the server: two draws of the layout comparison, packaging v4 (tsvc_b1) against v6 (tsvc_c2) — no model.
# One lane (cores 36-47, node 1); detached; logs under runs/_launcher/. The sequential times are the speed probe's.
cd "$HOME/discopop_agent" || exit 1
export PATH="$PWD/venv/bin:$PATH"
A=evaluation/agent
mkdir -p $A/runs/_launcher
for d in a b; do
    numactl --physcpubind=36-47 --membind=1 venv/bin/python $A/tools/layout_equivalence.py --old tsvc_b1 --new tsvc_c2 \
        --out $A/runs/t0_17_server_$d > $A/runs/_launcher/t0_17_server_$d.log 2>&1
    echo "DRAW_EXIT $?" >> $A/runs/_launcher/t0_17_server_$d.log
done
