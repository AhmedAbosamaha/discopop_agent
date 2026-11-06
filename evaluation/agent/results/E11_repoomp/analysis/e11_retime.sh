#!/bin/bash
# E11 part 1 re-timed on a quiet server (record §6, 6 Nov, "E11 part 1 re-timed on a quiet server — pre-registered"),
# no model. Why: part 1's runs were timed with three 12-core groups busy (e11_r_ep and e11_r_cg both on node 0's memory,
# e11_bare beside them) and the three judged programs (e11_ref_check) beside three DiscoPoP-alone draws, against the
# rule of 24 Sep (T0.4 at four lanes) that PolyBench and the applications run with two groups at most.
# What: every program E11 part 1 judged — DiscoPoP alone's 10 and the agent's 10 (e11_r_ep, e11_r_cg), Sonnet 4.5
# alone's 10 (e11_bare), NPB's OpenMP version, RepoOMP's Claude program and its Claude Code program on EP and CG — 36
# programs, each through `verify-source` exactly as judged (the verification size of config/kernel_sizes.json, threads
# 6 and 12, five repeats, seed 7), from the archived files, ONE AT A TIME on cores 0-11 with node 0's memory, with no
# other campaign job on the server. The load average is written before and after each program.
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E11_repoomp/analysis/e11_retime.sh > /dev/null 2>&1 < /dev/null &'
# and done when `E11_RETIME_DONE` is in runs/_launcher/e11_retime_done.log; then `server.sh fetch e11_retime`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
A=agent/results/E11_repoomp/runs
M=claude-sonnet-4-5-20250929
PIN="numactl --physcpubind=0-11 --membind=0"
mkdir -p $L
rm -f $L/e11_retime_*.log
one() {   # kernel label repeat source
    echo "START $1 $2 rep$3 $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e11_retime_progress.log
    $PIN $PY agent/benchmark verify-source npbc_c1/$1 --label $2 --repeat $3 --source "$4" \
        --threads 6,12 --repeats 5 --run-id e11_retime >> $L/e11_retime_verify.log 2>&1
    echo "EXIT $1 $2 rep$3 $? $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)" >> $L/e11_retime_progress.log
}
for k in ep cg; do
    for arm in discopop_gate_v5 llm_pragmas_v5; do
        for rep in 1 2 3 4 5; do
            one $k $arm $rep $A/e11_r_$k/benchmarks/npbc_c1/$k/$arm/$M/rep$rep/final
        done
    done
    for rep in 1 2 3 4 5; do
        one $k bare_llm_v4 $rep $A/e11_bare/benchmarks/npbc_c1/$k/bare_llm_v4/$M/rep$rep/final
    done
    one $k expert_openmp 1 agent/reference_solutions/npbc_c1/$k
    for label in repoomp_claude claude_code; do
        one $k $label 1 agent/comparison_programs/$label/npbc_c1/$k
    done
done
echo "E11_RETIME_DONE $(date -u +%H:%M)" >> $L/e11_retime_done.log
