#!/bin/bash
# E6 pre-flight, stage 2 on the SERVER, the part that is not a harness run (no model; registered runs e6_ref_check,
# e6_t0_13_ceiling, e6_t0_5_shares), one after the other on the fourth 12-core group (cores 36-47, node 1's memory) while
# the three class draws e6_classes_a/b/c run on the other three through `server.sh run`:
#   T0.10/T0.14 — LLNL's OpenMP version through the harness's verification at the verification size, 6 and 12 threads;
#   T0.13       — LLNL's version with its directives removed, the agent with budget 0: are DiscoPoP's directives kept?
#   T0.5        — where LULESH's time goes, at the agent size and the verification size.
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E06_lulesh/preflight/tools/e6_stage2.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E6_STAGE2_DONE` is in runs/_launcher/e6_stage2_done.log; then
# `server.sh fetch e6_ref_check e6_t0_13_ceiling e6_t0_5_shares`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
PIN="numactl --physcpubind=36-47 --membind=1"
mkdir -p $L
rm -f $L/e6_stage2_*.log
step() {   # name command...
    local name=$1
    shift
    "$@" > $L/e6_stage2_$name.log 2>&1
    echo "EXIT $name $?" >> $L/e6_stage2_$name.log
}
step ref $PIN $PY agent/benchmark verify-source llnl/lulesh --label expert_openmp \
    --source agent/reference_solutions/llnl/lulesh --threads 6,12 --repeats 5 --run-id e6_ref_check
step ceiling $PIN $PY agent/tools/default_arm_ceiling.py llnl/lulesh --out agent/runs/e6_t0_13_ceiling
step shares $PIN $PY agent/tools/share_study.py --benchmarks llnl/lulesh --out agent/runs/e6_t0_5_shares
echo "E6_STAGE2_DONE $(date -u +%H:%M)" >> $L/e6_stage2_done.log
