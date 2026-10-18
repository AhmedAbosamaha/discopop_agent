#!/usr/bin/env bash
# E4 step 4 — the live trials' smoke (THESIS_EXPERIMENTS §6, 18 Oct 2026, "Plan, E4 step 4"): one run on cores
# 0-11, then wait for it, fetch and archive it, sweep the server. Started with agent/tools/detach.py (and
# caffeinate -w on its pid); its last line is E4LIVE_SMOKE_DONE. The criterion: agent/tools/e4live_readout.py --smoke.
set -uo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)/evaluation" || exit 1
S=agent/tools/server.sh
MODEL=claude-haiku-4-5-20251001
stamp() { date -u '+%Y-%m-%d %H:%M:%S UTC'; }
idle() {  # the status into a variable first: with pipefail, grep -q stopping early would fail the pipe
    local out; out=$("$S" status 1 2>/dev/null); grep -qi "no job running" <<< "$out"; }
echo "== $(stamp) e4live_smoke: is the server idle?"
idle || { echo "a job is running on the server: not launching"; exit 1; }
"$S" run --node 0.0 -- tsvc_c2/s254 tsvc_c4/s316 --arms fast_recon_v5 --models "$MODEL" --trials 1 \
    --threads 6,12 --repeats 5 --run-id e4live_smoke || { echo "launch failed"; exit 1; }
echo "== $(stamp) launched; waiting"
sleep 90
until idle; do sleep 120; done
echo "== $(stamp) the job has ended; fetching"
"$S" fetch e4live_smoke
"$S" sweep
echo "E4LIVE_SMOKE_DONE $(stamp)"
