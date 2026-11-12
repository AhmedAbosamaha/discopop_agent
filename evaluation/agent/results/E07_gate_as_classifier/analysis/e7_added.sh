#!/bin/bash
# E7, corpus A1: what the repair of the corpus added (record §6, 12 Nov 2026, "E7: the corpus builder ..."), on the
# SERVER, no model, one 12-core group, when nothing else of E7 runs:
#   the 14 programs the repaired corpus holds and the first build did not:  judge  → run id e7_a1_judge_5
#   the 15 (base, program) pairs likewise:                                  checks → e7_a1_checks_2/part_1
# The same commands as the main runs (analysis/e7_main.sh), restricted by --added-since to what the first build of the
# corpus (corpus/a1/corpus_2026-11-11.json) lacks. Resumable. Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E07_gate_as_classifier/analysis/e7_added.sh > /dev/null 2>&1 < /dev/null &'
# and done when `E7_ADDED_DONE` is in runs/_launcher/e7_added_done.log; then `server.sh fetch e7_a1_judge_5 e7_a1_checks_2`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
C=agent/results/E07_gate_as_classifier/corpus
mkdir -p $L
rm -f $L/e7_added_done.log
step() {   # name command...
    local name=$1
    shift
    echo "START $name $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_added_progress.log
    numactl --physcpubind=0-11 --membind=0 "$@" >> $L/e7_added_$name.log 2>&1
    echo "EXIT $name $? $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e7_added_progress.log
}
step a1_judge_5 $PY agent/tools/gate_study.py judge --corpus $C/a1 --added-since $C/a1/corpus_2026-11-11.json --run-id e7_a1_judge_5
step a1_checks_2 $PY agent/tools/gate_study.py checks --corpus $C/a1 --added-since $C/a1/corpus_2026-11-11.json --out agent/runs/e7_a1_checks_2/part_1
echo "E7_ADDED_DONE $(date -u +%H:%M)" >> $L/e7_added_done.log
