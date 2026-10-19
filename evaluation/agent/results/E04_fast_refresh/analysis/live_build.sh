#!/bin/bash
# E4 step 4's read-out as registered (THESIS_EXPERIMENTS §6, 18 Oct 2026: "Plan, E4 step 4"; R3's whole count added
# 19 Oct before the race check): tools/e4live_readout.py over the four live runs with the race check's four parts (one
# per run, `e4live_race_check`), then Fig. 10 with its live panel. Run from the repository root.
set -euo pipefail
E=evaluation/agent/results/E04_fast_refresh
races=()
for p in "$E"/checks/e4live_race_check/*/results.jsonl; do races+=(--races "$p"); done
venv/bin/python evaluation/agent/tools/e4live_readout.py --out "$E/analysis" "${races[@]}"
# Fig. 10 only (fig_e4_e8.py's main also redraws E8's Fig. 11, whose PDF would change by its timestamp alone)
venv/bin/python -c "import sys; sys.path.insert(0, 'evaluation/agent/tools'); import fig_e4_e8; print(*fig_e4_e8.fig_refresh(), sep='\n')"
