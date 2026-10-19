#!/bin/bash
# E4 step 4's race check on the SERVER (no model; registered run e4live_race_check): the gate's ThreadSanitizer
# (archer) build and schedule matrix over every changed program of the four live runs. race_check.py takes one --arm
# per call and finds a run in the tracked archive (campaign.find_run), so this starts only after the runs are
# archived, committed and synced; one part per run, each on its run's 12-core group. Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E04_fast_refresh/analysis/live_launch/e4live_race.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E4LIVE_RACE_DONE` is in runs/_launcher/e4live_race_done.log; then `server.sh fetch e4live_race_check`.
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
export PATH="$PWD/venv/bin:$PATH"
A=evaluation/agent
O=$A/runs/e4live_race_check
L=$A/runs/_launcher
mkdir -p $O $L
rm -f $L/e4live_race_*.log
part() {   # run cores node
    local run=$1 cores=$2 node=$3
    numactl --physcpubind=$cores --membind=$node venv/bin/python $A/tools/race_check.py --runs $run \
        --arm fast_recon_v5 --out $O/$run > $L/e4live_race_$run.log 2>&1
    echo "RACE_EXIT $run $?" >> $L/e4live_race_$run.log
}
part e4live_1 0-11 0 &
part e4live_2 12-23 0 &
part e4live_3 24-35 1 &
part e4live_4 36-47 1 &
wait
echo "E4LIVE_RACE_DONE $(date -u +%H:%M)" >> $L/e4live_race_done.log
