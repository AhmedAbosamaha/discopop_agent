#!/bin/bash
# E7's main runs, on the SERVER, no model (record §6, 11 Nov 2026, "E7 reopened and registered as it will run"),
# after the pilot is read. Four 12-core groups; on each, one after the other:
#   corpus A1, share k of 4:  judge → run id e7_a1_judge_k ;  checks → e7_a1_checks/part_k
# and then, on the first two groups only (A2 holds PolyBench and the applications, which are judged with at most two
# groups busy):
#   corpus A2, share k of 2:  judge → run id e7_a2_judge_k ;  checks → e7_a2_checks/part_k
# Every step is resumable: a program or pair already judged is skipped. Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E07_gate_as_classifier/analysis/e7_main.sh > /dev/null 2>&1 < /dev/null &'
# and done when `E7_MAIN_DONE` is in runs/_launcher/e7_main_done.log; then `server.sh fetch` of the ten run ids.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
C=agent/results/E07_gate_as_classifier/corpus
mkdir -p $L
rm -f $L/e7_main_done.log
CORES=(0-11 12-23 24-35 36-47)
MEM=(0 0 1 1)
step() {   # name lane command...
    local name=$1 lane=$2
    shift 2
    echo "START $name $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_main_progress.log
    numactl --physcpubind="${CORES[$lane]}" --membind="${MEM[$lane]}" "$@" >> $L/e7_main_$name.log 2>&1
    echo "EXIT $name $? $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_main_progress.log
}
for k in 1 2 3 4; do
    (
        step a1_judge_$k $((k - 1)) $PY agent/tools/gate_study.py judge --corpus $C/a1 --part $k/4 --run-id e7_a1_judge_$k
        step a1_checks_$k $((k - 1)) $PY agent/tools/gate_study.py checks --corpus $C/a1 --part $k/4 --out agent/runs/e7_a1_checks/part_$k
    ) &
done
wait
for k in 1 2; do
    (
        step a2_judge_$k $((k - 1)) $PY agent/tools/gate_study.py judge --corpus $C/a2 --part $k/2 --run-id e7_a2_judge_$k
        step a2_checks_$k $((k - 1)) $PY agent/tools/gate_study.py checks --corpus $C/a2 --part $k/2 --out agent/runs/e7_a2_checks/part_$k
    ) &
done
wait
echo "E7_MAIN_DONE $(date -u +%H:%M)" >> $L/e7_main_done.log
