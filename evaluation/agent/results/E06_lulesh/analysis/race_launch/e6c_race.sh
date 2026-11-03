#!/bin/bash
# E6's registered race check on the SERVER (no model; registered run e6c_race_check): the gate's ThreadSanitizer (archer)
# build and schedule matrix over every program of the agent and of the models alone, and DiscoPoP alone's as the
# positive control (they passed the gate once already, so they must come out clean). race_check.py takes one --arm per
# call and finds the runs in the tracked archive, so this starts only after every E6 run is archived, committed and
# synced; the parts one after the other on lane 0.1 (cores 12-23), beside the timed runs of the second configuration. Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E06_lulesh/analysis/race_launch/e6c_race.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E6C_RACE_DONE` is in runs/_launcher/e6c_race_done.log; then `server.sh fetch e6c_race_check`.
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
export PATH="$PWD/venv/bin:$PATH"
A=evaluation/agent
O=$A/runs/e6c_race_check
L=$A/runs/_launcher
mkdir -p $O $L
rm -f $L/e6c_race_*.log
part() {   # name runs arm cores node
    local name=$1 runs=$2 arm=$3 cores=$4 node=$5
    numactl --physcpubind=$cores --membind=$node venv/bin/python $A/tools/race_check.py --runs $runs \
        --arm $arm --out $O/$name > $L/e6c_race_$name.log 2>&1
    echo "RACE_EXIT $name $?" >> $L/e6c_race_$name.log
}
part agent e6c_smoke3,e6c_r1,e6c_r2,e6c_r3b llm_pragmas_v5 12-23 0
part bare e6c_bare bare_llm_v4 12-23 0
part control e6c_r1,e6c_r2,e6c_r3b discopop_gate_v5 12-23 0
echo "E6C_RACE_DONE $(date -u +%H:%M)" >> $L/e6c_race_done.log
