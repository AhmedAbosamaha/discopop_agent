#!/usr/bin/env bash
# The instrument studies (T0.x, no model) on the ORIGINAL-FORMAT packages, one after the
# other, detached, pinned to one NUMA node — the re-run owed by decision D6 (RUNBOOK §5).
# Runs on the server:   agent/tools/t0_chain.sh            (from the harness root)
# Log:                  agent/runs/_t0/<stamp>.log ; each study writes its own run directory.
#
# Order: cheap and timing-sensitive first (T0.1 sizes, T0.5 shares), then the profiling
# studies (T0.6 patterns in main, T0.2 stability, T0.8 packaging equivalence, T0.7 explorer).
# The calibration programs (never in an experiment) and NPB `lu` (DiscoPoP does not
# instrument it within an hour, in either layout) are left out of every profiling study.
set -uo pipefail
HARNESS="$(cd "$(dirname "$0")/../.." && pwd)"
# evaluation/ lives inside the agent repository (since 2026-09-20); before, they were siblings
if [ -f "$HARNESS/../discopop_agent/__main__.py" ]; then
    AGENT="$(cd "$HARNESS/.." && pwd)"
else
    AGENT="$(cd "$HARNESS/../discopop_agent" && pwd)"
fi
PY="$AGENT/venv/bin/python"
NODE="${DP_NUMA_NODE:-1}"
PIN=(numactl --cpunodebind="$NODE" --membind="$NODE")
cd "$HARNESS" || exit 1

if [ "${1:-}" != "__run" ]; then
    mkdir -p agent/runs/_t0
    log="agent/runs/_t0/$(date +%Y%m%d_%H%M%S).log"
    setsid nohup "$0" __run > "$log" 2>&1 < /dev/null &
    echo "launched pid $!  log: $log"
    exit 0
fi

step() { echo; echo "== $* — $(date -Is)"; "$@"; echo "== exit $? — $(date -Is)"; }
# DP_T0_STEPS="T0.6 T0.2 T0.8 T0.7" runs a subset (default: all); DP_T0_TAG names the run dirs
STEPS="${DP_T0_STEPS:-T0.1 T0.5 T0.6 T0.2 T0.8 T0.7}"
TAG="${DP_T0_TAG:-}"
want() { case " $STEPS " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

# every packaged benchmark except the calibration programs; profiling studies also drop npb/lu
ALL=$("$PY" - <<'EOF'
import json, pathlib
names = [f"{m.parent.parent.name}/{m.parent.name}" for m in sorted(pathlib.Path("agent/prepared").glob("*/*/meta.json"))
         if json.loads(m.read_text()).get("suite") != "calibration"]
print(",".join(names))
EOF
)
# not profilable in practice (upstream report L1-L3): npb/lu (instrumentation > 2 h), rodinia nw and
# npb/mg (the explorer's call-path state assignment takes hours once it no longer crashes)
PROFILABLE=$(printf '%s' "$ALL" | tr ',' '\n' | grep -Ev '^(npb/lu|npb/mg|rodinia-3.1/nw)$' | paste -sd, -)
echo "benchmarks: $ALL"
echo "host: $(hostname)  node: $NODE  load: $(cut -d' ' -f1-3 /proc/loadavg)"

# T0.1 — verification and timing size per benchmark (serial -O3 timing; cholesky/trmm/durbin are out)
want T0.1 && step "${PIN[@]}" "$PY" agent/tools/size_table.py --out agent/runs/t0_1_sizes_v2$TAG \
    --kernels "$(printf '%s' "$ALL" | tr ',' '\n' | grep -Ev '/(cholesky|trmm|durbin)$' | paste -sd, -)"

# T0.5 — runtime share per region (DiscoPoP hotspot detection at the agent size and the verification size)
want T0.5 && step "${PIN[@]}" "$PY" agent/tools/share_study.py --out agent/runs/t0_5_shares$TAG --benchmarks "$PROFILABLE"

# T0.6 — DiscoPoP's own patterns inside main (decides D4 for nw)
want T0.6 && step "${PIN[@]}" "$PY" agent/tools/dp_main_study.py --out agent/runs/t0_6_dp_main_v2$TAG --benchmarks "$PROFILABLE"

# T0.2 — profile stability, 10 profiles per core kernel
want T0.2 && step "${PIN[@]}" "$PY" agent/tools/profile_stability.py --out agent/runs/t0_2_stability_v2$TAG --agent-repo "$AGENT"

# T0.8 — merged file vs original layout, PolyBench and NPB (the other applications were one file to begin with)
want T0.8 && step "$PY" agent/tools/prepare_polybench.py --layout single --out agent/prepared_single/polybench
want T0.8 && step "$PY" agent/tools/prepare_apps.py --layout single --out agent/prepared_single --cxx clang++-20 is mg
want T0.8 && step "${PIN[@]}" "$PY" agent/tools/packaging_equivalence.py --single agent/prepared_single/polybench \
    --project agent/prepared/polybench --out agent/runs/t0_8_packaging$TAG/polybench
want T0.8 && step "${PIN[@]}" "$PY" agent/tools/packaging_equivalence.py --single agent/prepared_single/npb \
    --project agent/prepared/npb --out agent/runs/t0_8_packaging$TAG/npb is

# T0.7 — explorer determinism on one profile (20 runs free, 20 per fixed seed)
want T0.7 && step "${PIN[@]}" "$PY" agent/tools/explorer_determinism.py --out agent/runs/t0_7_explorer$TAG \
    --benchmarks polybench/2mm,rodinia-3.1/pathfinder,npb/is --repeats 20

echo; echo "T0 CHAIN DONE — $(date -Is)"
