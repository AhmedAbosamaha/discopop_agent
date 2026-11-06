#!/bin/bash
# E11 part 1's two registered checks, on the SERVER, no model (record §6, 6 Nov, "E11 — the smoke, the main runs and
# the read-out"), once e11_r_ep, e11_r_cg and e11_bare are fetched, archived, committed and synced:
#   e11_race_check   — race_check.py on every program of the agent (llm_pragmas_v5) and of Sonnet alone (bare_llm_v4),
#                      DiscoPoP alone's (discopop_gate_v5) as the positive control, and the three judged programs of
#                      e11_ref_check (repoomp_claude, claude_code, expert_openmp); one 12-core group per part;
#   e11_second_class — analysis/second_class.py: NPB's verification at the second class (EP class B, CG class A) on
#                      every program of the three main runs (the judged programs' are e11_ref_npb_verdicts).
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E11_repoomp/analysis/e11_checks.sh > /dev/null 2>&1 < /dev/null &'
# and done when `E11_CHECKS_DONE` is in runs/_launcher/e11_checks_done.log; then
# `server.sh fetch e11_race_check e11_second_class`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
O=agent/runs/e11_race_check
mkdir -p $L $O
rm -f $L/e11_checks_*.log
pin() { numactl --physcpubind="$1" --membind="$2" "${@:3}"; }
run() {   # name cores mem command...
    local name=$1 cores=$2 mem=$3
    shift 3
    pin "$cores" "$mem" "$@" > $L/e11_checks_$name.log 2>&1
    echo "EXIT $name $?" >> $L/e11_checks_$name.log
}
(
    run agent 0-11 0 $PY agent/tools/race_check.py --runs e11_r_ep,e11_r_cg --arm llm_pragmas_v5 --out $O/agent
) &
(
    run bare 12-23 0 $PY agent/tools/race_check.py --runs e11_bare --arm bare_llm_v4 --out $O/bare
) &
(
    run control 24-35 1 $PY agent/tools/race_check.py --runs e11_r_ep,e11_r_cg --arm discopop_gate_v5 --out $O/control
) &
(
    for label in repoomp_claude claude_code expert_openmp; do
        run judged_$label 36-47 1 $PY agent/tools/race_check.py --runs e11_ref_check --arm $label --out $O/judged_$label
    done
    run second_class 36-47 1 $PY agent/results/E11_repoomp/analysis/second_class.py --sizes ep=EXTRALARGE,cg=LARGE \
        --runs e11_r_ep,e11_r_cg,e11_bare --out agent/runs/e11_second_class
) &
wait
echo "E11_CHECKS_DONE $(date -u +%H:%M)" >> $L/e11_checks_done.log
