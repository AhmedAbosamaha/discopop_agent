#!/bin/bash
# E11 pre-flight, stage A, on the SERVER (no model; registered runs e11_prepare, e11_t0_1_sizes, e11_exact_repeat_test):
#   e11_prepare           — the server builds npbc_c1/ep and npbc_c1/cg with the generator's validation (clang-20) at
#                           every size, with --references (NPB's own OpenMP version, RepoOMP's Claude program, the Claude
#                           Code program, in package form); the digests of the packages and of the harness header go to
#                           runs/e11_prepare/files.sha256 to be compared with the Mac's, and `git status` of the tracked
#                           copies afterwards (they must come out unchanged);
#   e11_t0_1_sizes        — T0.1 on NUMA node 0 (size_table.py): the verification and timing size of each;
#   e11_exact_repeat_test — the gate's --exact-repeat on E6's archived LULESH programs (race_check.py, every program
#                           of e6c_race_check again), on node 1 beside T0.1: does it refuse the four programs the
#                           harness found unrepeatable and keep the others? (record §6, 5 Nov: the criterion).
# Started from the Mac with
#   ssh SERVER 'nohup discopop_agent/evaluation/agent/results/E11_repoomp/preflight/tools/e11_stageA.sh \
#               > /dev/null 2>&1 < /dev/null &'
# and done when `E11_STAGEA_DONE` is in runs/_launcher/e11_stageA_done.log; then
# `server.sh fetch e11_prepare e11_t0_1_sizes e11_exact_repeat_test`.
R="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
cd "$R/evaluation" || exit 1
export PATH="$R/venv/bin:$PATH"
PY="$R/venv/bin/python"
L=agent/runs/_launcher
P=agent/runs/e11_prepare
X=agent/runs/e11_exact_repeat_test
mkdir -p $L $P $X
rm -f $L/e11_stageA_*.log
$PY agent/tools/prepare_apps.py npbc_ep npbc_cg --out agent/prepared --validate \
    --validate-sizes MINI,SMALL,STANDARD,LARGE,EXTRALARGE --references --cxx clang++-20 > $L/e11_stageA_prepare.log 2>&1
echo "PREPARE_EXIT $?" >> $L/e11_stageA_prepare.log
git status --porcelain -- agent/reference_solutions/npbc_c1 agent/comparison_programs > $P/git_status_after.txt
cp agent/prepared/npbc_c1/ep/meta.json $P/meta_ep.json
cp agent/prepared/npbc_c1/cg/meta.json $P/meta_cg.json
cp agent/prepared/apps_validation.json $P/apps_validation.json
( cd agent/prepared && sha256sum npbc_c1/ep/* npbc_c1/cg/* _harness/npbc_c1/npbc_harness.h ) > $P/files.sha256
( numactl --cpunodebind=0 --membind=0 $PY agent/tools/size_table.py --kernels npbc_c1/ep,npbc_c1/cg \
      --out agent/runs/e11_t0_1_sizes > $L/e11_stageA_sizes.log 2>&1
  echo "SIZES_EXIT $?" >> $L/e11_stageA_sizes.log ) &
part() {   # name runs arm cores
    local name=$1 runs=$2 arm=$3 cores=$4
    numactl --physcpubind=$cores --membind=1 $PY agent/tools/race_check.py --exact-repeat --runs $runs \
        --arm $arm --out $X/$name > $L/e11_stageA_x_$name.log 2>&1
    echo "RACE_EXIT $name $?" >> $L/e11_stageA_x_$name.log
}
( part agent e6c_smoke3,e6c_r1,e6c_r2,e6c_r3b llm_pragmas_v5 24-35
  part exact e6x_1,e6x_2,e6x_3 llm_pragmas_v5_exact 24-35 ) &
( part bare e6c_bare bare_llm_v4 36-47
  part control e6c_r1,e6c_r2,e6c_r3b,e6x_1,e6x_2,e6x_3 discopop_gate_v5 36-47 ) &
wait
echo "E11_STAGEA_DONE $(date -u +%H:%M)" >> $L/e11_stageA_done.log
