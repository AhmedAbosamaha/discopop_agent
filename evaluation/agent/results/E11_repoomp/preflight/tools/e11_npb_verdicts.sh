#!/bin/bash
# E11 pre-flight (server, no model; registered run e11_ref_npb_verdicts): NPB's own verification of the three judged
# programs (e11_ref_check) — at the class the harness judged them (EP W, CG B) and at the second class (EP B, CG A),
# 12 threads, cores 36-47 (analysis/second_class.py). The judge compares values with the input's; this reads NPB's
# verdict against NPB's published reference values, which is what tells a program that prints more (NPB's own EP)
# from one that computes something else.
# Started from the Mac with ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E11_repoomp/preflight/tools/e11_npb_verdicts.sh > /dev/null 2>&1 < /dev/null &'
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
L=agent/runs/_launcher
O=agent/runs/e11_ref_npb_verdicts
mkdir -p $L $O
A=agent/results/E11_repoomp/analysis/second_class.py
numactl --physcpubind=36-47 --membind=1 "$R/venv/bin/python" $A --runs e11_ref_check --sizes ep=STANDARD,cg=EXTRALARGE \
    --out $O/judged_class > $L/e11_npb_verdicts.log 2>&1
numactl --physcpubind=36-47 --membind=1 "$R/venv/bin/python" $A --runs e11_ref_check --sizes ep=EXTRALARGE,cg=LARGE \
    --out $O/second_class >> $L/e11_npb_verdicts.log 2>&1
echo "E11_NPB_VERDICTS_DONE $(date -u +%H:%M)" >> $L/e11_npb_verdicts.log
