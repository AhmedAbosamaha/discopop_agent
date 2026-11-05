#!/bin/bash
# E11 pre-flight, stage B, on the SERVER — the part that is not a harness run (no model; registered runs e11_ref_check,
# e11_requests), on the fourth 12-core group (cores 36-47, node 1's memory) while the three DiscoPoP-alone class draws
# e11_classes_a/b/c run on the other three lanes through `server.sh run`:
#   e11_ref_check — the three programs judged without a model, each a whole file in the same package (Fix 114: the
#                   timed region is checked), through the harness's verification at the verification size, 6 and 12
#                   threads, 5 repeats: NPB's own OpenMP version (expert_openmp), RepoOMP's Claude program
#                   (repoomp_claude), its Claude Code program (claude_code), on EP and CG;
#   e11_requests  — once e11_classes_a has its profiles: show_requests.py on them — the agent's first request in the
#                   model-writes mode at prompt version 5 (llm_pragmas_v5) and the model alone's mirror at version 4
#                   (bare_llm_v4): what Sonnet 4.5 will read (the rule of 4 Oct; archived under the standing instruction).
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E11_repoomp/preflight/tools/e11_stageB.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E11_STAGEB_DONE` is in runs/_launcher/e11_stageB_done.log; then
# `server.sh fetch e11_ref_check e11_requests`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
PIN="numactl --physcpubind=36-47 --membind=1"
mkdir -p $L
rm -f $L/e11_stageB_*.log
step() {   # name command...
    local name=$1
    shift
    "$@" > $L/e11_stageB_$name.log 2>&1
    echo "EXIT $name $?" >> $L/e11_stageB_$name.log
}
for k in ep cg; do
    step ref_${k}_expert $PIN $PY agent/benchmark verify-source npbc_c1/$k --label expert_openmp \
        --source agent/reference_solutions/npbc_c1/$k --threads 6,12 --repeats 5 --run-id e11_ref_check
    for label in repoomp_claude claude_code; do
        step ref_${k}_$label $PIN $PY agent/benchmark verify-source npbc_c1/$k --label $label \
            --source agent/comparison_programs/$label/npbc_c1/$k --threads 6,12 --repeats 5 --run-id e11_ref_check
    done
done
for k in ep cg; do   # the class draw's profile of each program, once its trial is judged (at most two hours)
    P=agent/runs/e11_classes_a/profiles/npbc_c1/$k
    for i in $(seq 1 120); do
        ls agent/runs/e11_classes_a/benchmarks/npbc_c1/$k/discopop_capability/*/rep1/trial.json > /dev/null 2>&1 && break
        sleep 60
    done
    step req_${k}_agent $PY agent/tools/show_requests.py $P agent/runs/e11_requests/$k/agent_v5_llm_pragmas \
        --prompt-version 5 --llm-pragmas
    step req_${k}_alone $PY agent/tools/show_requests.py $P agent/runs/e11_requests/$k/model_alone_v4 --prompt-version 4
done
echo "E11_STAGEB_DONE $(date -u +%H:%M)" >> $L/e11_stageB_done.log
