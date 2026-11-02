#!/bin/bash
# E6 pre-flight on the clean package llnl_c1/lulesh, stage B, on the SERVER — the part that is not a harness run (no
# model; registered runs e6c_ref_check, e6c_t0_5_shares), one after the other on the fourth 12-core group (cores 36-47,
# node 1's memory) while the three class draws e6c_classes_a/b/c run on the other three through `server.sh run`:
#   T0.10/T0.14 — LLNL's OpenMP version through the harness's verification at the verification size, 6 and 12 threads;
#   T0.5        — where LULESH's time goes, at the agent size and the verification size.
# T0.13 is not run on LULESH: with its directives removed, LLNL's version reads per-thread slots it never wrote
# (omp_get_max_threads() > 1 outside a parallel region), so it is no correct sequential program — record §6, 2 Nov.
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E06_lulesh/preflight/tools/e6c_stageB.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E6C_STAGEB_DONE` is in runs/_launcher/e6c_stageB_done.log; then
# `server.sh fetch e6c_ref_check e6c_t0_5_shares`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
PIN="numactl --physcpubind=36-47 --membind=1"
mkdir -p $L
rm -f $L/e6c_stageB_*.log
step() {   # name command...
    local name=$1
    shift
    "$@" > $L/e6c_stageB_$name.log 2>&1
    echo "EXIT $name $?" >> $L/e6c_stageB_$name.log
}
step ref $PIN $PY agent/benchmark verify-source llnl_c1/lulesh --label expert_openmp \
    --source agent/reference_solutions/llnl_c1/lulesh --threads 6,12 --repeats 5 --run-id e6c_ref_check
step shares $PIN $PY agent/tools/share_study.py --benchmarks llnl_c1/lulesh --out agent/runs/e6c_t0_5_shares
echo "E6C_STAGEB_DONE $(date -u +%H:%M)" >> $L/e6c_stageB_done.log
