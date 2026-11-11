#!/bin/bash
# E7's registered pilot, on the SERVER, no model (record §6, 11 Nov 2026, "E7 reopened and registered as it will run"):
# 40 candidates of corpus A1 drawn with seed 7, 20 rewrites and 20 directives —
#   judge   the harness on each distinct program of the draw (J1 `verify-source`: the verification size, threads 6 and
#           12, five repeats, both inputs; J2 for a program with a directive: ThreadSanitizer with archer at the
#           verification size, 12 threads, 3 runs), run id e7_pilot;
#   checks  the gate again on each (base, program) pair of the draw at the gate's own size: the whole safety gate (the
#           fidelity against the recorded verdict), then each check alone, into e7_pilot_checks.
# One 12-core group (cores 0-11, node 0's memory), one step after the other, so that the seconds per candidate are
# those of one lane. Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E07_gate_as_classifier/analysis/e7_pilot.sh > /dev/null 2>&1 < /dev/null &'
# and done when `E7_PILOT_DONE` is in runs/_launcher/e7_pilot_done.log; then `server.sh fetch e7_pilot e7_pilot_checks`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
C=agent/results/E07_gate_as_classifier/corpus
PIN="numactl --physcpubind=0-11 --membind=0"
mkdir -p $L
rm -f $L/e7_pilot_*.log
echo "START judge $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_pilot_progress.log
$PIN $PY agent/tools/gate_study.py judge --corpus $C/a1 --sample 20,20 --seed 7 --run-id e7_pilot > $L/e7_pilot_judge.log 2>&1
echo "EXIT judge $? $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_pilot_progress.log
$PIN $PY agent/tools/gate_study.py checks --corpus $C/a1 --sample 20,20 --seed 7 --out agent/runs/e7_pilot_checks > $L/e7_pilot_checks.log 2>&1
echo "EXIT checks $? $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_pilot_progress.log
echo "E7_PILOT_DONE $(date -u +%H:%M)" >> $L/e7_pilot_done.log
