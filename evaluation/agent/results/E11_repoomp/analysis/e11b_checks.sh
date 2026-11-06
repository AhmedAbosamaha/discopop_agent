#!/bin/bash
# E11 part 2's registered race check, on the SERVER, no model (record §6, 6 Nov, "E11 part 2 pre-registered": "After
# them, no model: e11b_race_check on every program of the four setups (DiscoPoP alone's as the positive control)"),
# once e11b_r_repoomp, e11b_r_agent_1, e11b_r_agent_2 and e11b_bare are fetched, archived, committed and synced
# (race_check.py reads the trials from the archive):
#   repoomp — RepoOMP's release (repoomp_release) on e11b_r_repoomp;
#   agent   — the agent (llm_pragmas_v5) on e11b_r_agent_1 and e11b_r_agent_2;
#   bare    — Sonnet 4.5 alone (bare_llm_v4) on e11b_bare;
#   control — DiscoPoP alone (discopop_gate_v5) on e11b_r_agent_1 and e11b_r_agent_2.
# One 12-core group per part. Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E11_repoomp/analysis/e11b_checks.sh > /dev/null 2>&1 < /dev/null &'
# and done when `E11B_CHECKS_DONE` is in runs/_launcher/e11b_checks_done.log; then `server.sh fetch e11b_race_check`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
O=agent/runs/e11b_race_check
mkdir -p $L $O
rm -f $L/e11b_checks_*.log
pin() { numactl --physcpubind="$1" --membind="$2" "${@:3}"; }
run() {   # name cores mem command...
    local name=$1 cores=$2 mem=$3
    shift 3
    pin "$cores" "$mem" "$@" > $L/e11b_checks_$name.log 2>&1
    echo "EXIT $name $?" >> $L/e11b_checks_$name.log
}
(
    run repoomp 0-11 0 $PY agent/tools/race_check.py --runs e11b_r_repoomp --arm repoomp_release --out $O/repoomp_release
) &
(
    run agent 12-23 0 $PY agent/tools/race_check.py --runs e11b_r_agent_1,e11b_r_agent_2 --arm llm_pragmas_v5 \
        --out $O/llm_pragmas_v5
) &
(
    run bare 24-35 1 $PY agent/tools/race_check.py --runs e11b_bare --arm bare_llm_v4 --out $O/bare_llm_v4
) &
(
    run control 36-47 1 $PY agent/tools/race_check.py --runs e11b_r_agent_1,e11b_r_agent_2 --arm discopop_gate_v5 \
        --out $O/discopop_gate_v5
) &
wait
echo "E11B_CHECKS_DONE $(date -u +%H:%M)" >> $L/e11b_checks_done.log
