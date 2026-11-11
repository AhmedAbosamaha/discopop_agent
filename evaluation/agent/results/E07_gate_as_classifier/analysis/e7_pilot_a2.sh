#!/bin/bash
# E7's second pilot, on the SERVER, no model (record §6, 11 Nov 2026, "E7: the pilot read out; a second pilot on corpus
# A2 registered"): the first pilot drew only from corpus A1 (TSVC), so nothing of A2's packages — PolyBench's two-unit
# kernels with their own flags, the single-file C++ applications md and pathfinder — had gone through the judge or the
# checks, and no time for them was known. Of every benchmark of A2 the first distinct program (by hash), 39 programs:
#   judge   J1 as in the main runs; J2 with ONE ThreadSanitizer run (the time of one run and whether the 1800 s limit
#           holds; nothing of this pilot is counted), a quarter each on the four 12-core groups → e7_pilot_a2_k;
#   checks  the gate again on those (base, program) pairs, as in the main runs → e7_pilot_a2_checks/part_k.
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E07_gate_as_classifier/analysis/e7_pilot_a2.sh > /dev/null 2>&1 < /dev/null &'
# and done when `E7_PILOT_A2_DONE` is in runs/_launcher/e7_pilot_a2_done.log; then
#   server.sh fetch e7_pilot_a2_1 e7_pilot_a2_2 e7_pilot_a2_3 e7_pilot_a2_4 e7_pilot_a2_checks
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
C=agent/results/E07_gate_as_classifier/corpus
mkdir -p $L
rm -f $L/e7_pilot_a2_*.log
CORES=(0-11 12-23 24-35 36-47)
MEM=(0 0 1 1)
step() {   # name lane command...
    local name=$1 lane=$2
    shift 2
    echo "START $name $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_pilot_a2_progress.log
    numactl --physcpubind="${CORES[$lane]}" --membind="${MEM[$lane]}" "$@" >> $L/e7_pilot_a2_$name.log 2>&1
    echo "EXIT $name $? $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_pilot_a2_progress.log
}
for k in 1 2 3 4; do
    (
        step judge_$k $((k - 1)) $PY agent/tools/gate_study.py judge --corpus $C/a2 --per-benchmark 1 --part $k/4 \
            --tsan-runs 1 --run-id e7_pilot_a2_$k
        step checks_$k $((k - 1)) $PY agent/tools/gate_study.py checks --corpus $C/a2 --per-benchmark 1 --part $k/4 \
            --out agent/runs/e7_pilot_a2_checks/part_$k
    ) &
done
wait
echo "E7_PILOT_A2_DONE $(date -u +%H:%M)" >> $L/e7_pilot_a2_done.log
