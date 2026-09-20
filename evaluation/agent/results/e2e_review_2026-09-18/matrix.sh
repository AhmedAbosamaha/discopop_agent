#!/bin/bash
# End-to-end matrix: the whole agent on one small program under different argument sets.
# usage: matrix.sh BENCH OUTDIR
set -u
BENCH=$1; OUT=$2
H=/Users/ahmedsamir/new_benchmark_harness/agent/prepared/calib
A=/Users/ahmedsamir/discopop_agent
EXC="init_array,pb_emit,pb_report,pb_seed,pb_uniform,pb_timer_start,pb_timer_stop,main"
COMMON="--no-require-speedup --min-runtime-share 0.01 --exclude-functions $EXC --model sonnet --check-input 7"
export CLAUDE_CODE_OAUTH_TOKEN="$(security find-generic-password -a "$USER" -s claude-code-oauth-token -w 2>/dev/null)"
mkdir -p "$OUT"
run() {
  name=$1; shift
  d="$OUT/$name"; rm -rf "$d"; mkdir -p "$d"; cp "$H/$BENCH/$BENCH.c" "$d/"
  cd "$A"
  venv/bin/python -m discopop_agent --source-file "$d/$BENCH.c" --discopop-dir "$d/.discopop" --profile-only > "$d/profile.log" 2>&1
  t0=$(date +%s)
  DP_LLM_USAGE_LOG="$d/usage.jsonl" venv/bin/python -m discopop_agent --source-file "$d/$BENCH.c" --discopop-dir "$d/.discopop" $COMMON "$@" > "$d/run.log" 2>&1
  rc=$?; t1=$(date +%s)
  calls=$( [ -f "$d/usage.jsonl" ] && wc -l < "$d/usage.jsonl" | tr -d ' ' || echo 0)
  prag=$(grep -c "#pragma omp" "$d/$BENCH.c")
  echo "$name | rc=$rc | $((t1-t0))s | model calls=$calls | pragmas in file=$prag | $(grep 'SUMMARY' "$d/run.log" | sed 's/^ *//')"
}
run dp_annotates      --budget 2 --no-llm-pragmas --no-fast-refresh
run full_depth1       --budget 2 --restructure-depth 1
run dp_recon          --budget 2 --no-llm-pragmas --llm-recon
