#!/usr/bin/env bash
# E4 step 4 — the four live runs (THESIS_EXPERIMENTS §6, 18 Oct 2026, "Plan, E4 step 4"), one per 12-core group,
# launched together; then wait for all of them, fetch and archive them, sweep the server. Started with
# agent/tools/detach.py (and caffeinate -w on its pid) after the smoke passed its criterion; last line E4LIVE_DONE.
set -uo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)/evaluation" || exit 1
S=agent/tools/server.sh
MODEL=claude-haiku-4-5-20251001
COMMON=(--arms fast_recon_v5 --models "$MODEL" --trials 5 --threads 6,12 --repeats 5)
stamp() { date -u '+%Y-%m-%d %H:%M:%S UTC'; }
idle() { "$S" status 1 2>/dev/null | grep -q "No job running"; }
echo "== $(stamp) e4live wave: is the server idle?"
idle || { echo "a job is running on the server: not launching"; exit 1; }
"$S" run --node 0.0 -- tsvc_c2/s212 tsvc_c2/s243 tsvc_c2/s244 tsvc_c2/s252 tsvc_c3/s241 tsvc_c4/s318 \
    "${COMMON[@]}" --run-id e4live_1 || { echo "launch of e4live_1 failed"; exit 1; }
"$S" run --node 0.1 -- tsvc_c2/s292 tsvc_c2/s293 tsvc_c3/s331 tsvc_c4/s341 tsvc_c4/s3113 tsvc_c4/s319 \
    "${COMMON[@]}" --run-id e4live_2 || { echo "launch of e4live_2 failed"; exit 1; }
"$S" run --node 1.0 -- tsvc_c2/s112 tsvc_c2/s121 tsvc_c2/s1213 tsvc_c2/s127 tsvc_c2/s211 tsvc_c4/s314 tsvc_c4/s316 \
    "${COMMON[@]}" --run-id e4live_3 || { echo "launch of e4live_3 failed"; exit 1; }
"$S" run --node 1.1 -- tsvc_c2/s254 tsvc_c2/s255 tsvc_c2/s281 tsvc_c2/s291 tsvc_c4/s315 tsvc_c4/s311 \
    "${COMMON[@]}" --run-id e4live_4 || { echo "launch of e4live_4 failed"; exit 1; }
echo "== $(stamp) all four launched; waiting"
sleep 120
until idle; do sleep 300; done
echo "== $(stamp) all jobs have ended; fetching"
"$S" fetch e4live_1 e4live_2 e4live_3 e4live_4
"$S" sweep
echo "E4LIVE_DONE $(stamp)"
