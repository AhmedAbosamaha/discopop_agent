#!/bin/bash
# E7, Part B, on the SERVER, no model (record §6, 11 Nov 2026, "E7, Part B registered"): the gate's safety validation on
# every C and C++ kernel of DataRaceBench 1.4.1 (evaluation/benchmarks/LLNL_DataRaceBench, PROVENANCE.txt), five runs per
# kernel, four 12-core groups with a quarter of the kernels each, into e7_drb/part_k. Resumable. Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E07_gate_as_classifier/analysis/e7_drb.sh > /dev/null 2>&1 < /dev/null &'
# and done when `E7_DRB_DONE` is in runs/_launcher/e7_drb_done.log; then `server.sh fetch e7_drb`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
mkdir -p $L
rm -f $L/e7_drb_*.log
CORES=(0-11 12-23 24-35 36-47)
MEM=(0 0 1 1)
for k in 1 2 3 4; do
    (
        echo "START part $k $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_drb_progress.log
        numactl --physcpubind="${CORES[$((k - 1))]}" --membind="${MEM[$((k - 1))]}" \
            $PY agent/tools/gate_study.py drb --part $k/4 --runs 5 --out agent/runs/e7_drb/part_$k > $L/e7_drb_part_$k.log 2>&1
        echo "EXIT part $k $? $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_drb_progress.log
    ) &
done
wait
echo "E7_DRB_DONE $(date -u +%H:%M)" >> $L/e7_drb_done.log
