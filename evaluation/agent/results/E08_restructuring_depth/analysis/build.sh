#!/bin/bash
# E8's read-out as registered (THESIS_EXPERIMENTS §6, 14 Oct 2026: "Plan, E8 pre-registration"): tools/e8_readout.py over
# the four runs, with the race check's nine parts (one per run and arm, `e8v5_race_check`). Run from the repository root.
set -euo pipefail
E=evaluation/agent/results/E08_restructuring_depth
races=()
for p in "$E"/checks/e8v5_race_check/*/results.jsonl; do races+=(--races "$p"); done
venv/bin/python evaluation/agent/tools/e8_readout.py --out "$E/analysis" "${races[@]}"
