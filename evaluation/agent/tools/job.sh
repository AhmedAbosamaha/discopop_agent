#!/usr/bin/env bash
# Machine-side half of agent/tools/server.sh. `state` runs on both machines (the Mac compares
# the two outputs); everything else runs on the server. Never pass a token as an argument.
#
#   job.sh state                  facts compared for Mac/server parity
#   job.sh update-agent SHA       fast-forward the agent checkout to SHA, reinstall the wrappers
#   job.sh install-wrappers       copy the compiler wrapper scripts into the venv (after a git update)
#   job.sh launch NODE ARGS...    read the Claude token from stdin and start
#                                 `agent/benchmark run ARGS` detached, pinned to NUMA node NODE
#   job.sh status [LINES]         running jobs and the tail of the latest launcher log
#   job.sh sweep                  look for credentials left on disk (needs no token)
#
# Credential policy: agent/docs/THESIS_EXPERIMENTS.md §4.
set -uo pipefail

SELF="${BASH_SOURCE[0]}"
HARNESS="$(cd "$(dirname "$SELF")/../.." && pwd)"
# evaluation/ lives inside the agent repository (since 2026-09-20); before, they were siblings
if [ -f "$HARNESS/../discopop_agent/__main__.py" ]; then
    AGENT="$(cd "$HARNESS/.." && pwd)"
else
    AGENT="$(cd "$HARNESS/../discopop_agent" && pwd)"
fi
PY="$AGENT/venv/bin/python"
LAUNCH_DIR="$HARNESS/agent/runs/_launcher"

site_packages() { "$PY" -c 'import site; print(site.getsitepackages()[0])'; }

tree_state() {
    if [ -z "$(git -C "$1" status --porcelain)" ]; then echo clean; else echo dirty; fi
}

running_jobs() { pgrep -u "$(id -un)" -f 'job.sh __job' | wc -l | tr -d ' '; }

state() {
    local sp w f
    sp=$(site_packages)
    echo "agent_head=$(git -C "$AGENT" rev-parse HEAD)"
    echo "agent_tree=$(tree_state "$AGENT")"
    echo "harness_head=$(git -C "$HARNESS" rev-parse HEAD)"
    echo "harness_tree=$(tree_state "$HARNESS")"
    w=match
    for f in CC CXX; do
        cmp -s "$AGENT/profiler/scripts/${f}_wrapper.sh" "$sp/discopop-profiler.libs/${f}_wrapper.sh" || w=DIFFER
        cmp -s "$AGENT/hotspot_detection/scripts/${f}_wrapper.sh" \
            "$sp/discopop-hotspot-detection.libs/${f}_wrapper.sh" || w=DIFFER
    done
    echo "wrappers=$w"
    (cd / && "$PY" - <<'EOF'
import importlib.metadata as md
import discopop_explorer, discopop_library
print("explorer=" + discopop_explorer.__file__)
print("library=" + discopop_library.__file__)
for p in ("anthropic", "claude-agent-sdk"):
    print(p.replace("-", "_") + "=" + md.version(p))
EOF
    )
    echo "disk_free=$(df -h "$HOME" | awk 'NR==2 {print $4}')"
    echo "load=$(uptime | sed -E 's/.*load averages?: //')"
    echo "jobs=$(running_jobs)"
}

update_agent() {
    local sha="$1" sp
    git -C "$AGENT" fetch -q origin || { echo "update-agent: fetch failed" >&2; return 1; }
    if ! git -C "$AGENT" merge -q --ff-only "$sha"; then
        echo "update-agent: cannot fast-forward $AGENT to $sha" >&2
        return 1
    fi
    install_wrappers
}

install_wrappers() {
    local sp
    sp=$(site_packages)
    cp "$AGENT"/profiler/scripts/{CC,CXX}_wrapper.sh "$sp/discopop-profiler.libs/"
    cp "$AGENT"/hotspot_detection/scripts/{CC,CXX}_wrapper.sh "$sp/discopop-hotspot-detection.libs/"
    echo "agent at $(git -C "$AGENT" rev-parse --short HEAD), wrappers installed"
}

launch() {
    local node="$1" token stamp log cfg
    shift
    if [ "$#" -eq 0 ]; then
        echo "launch: no arguments for agent/benchmark run" >&2
        return 2
    fi
    IFS= read -r token || true
    if [ -z "$token" ]; then
        echo "launch: no token on stdin" >&2
        return 2
    fi
    mkdir -p "$LAUNCH_DIR"
    stamp=$(date +%Y%m%d_%H%M%S)
    log="$LAUNCH_DIR/$stamp.log"
    cfg=$(mktemp -d /tmp/dpcfg.XXXXXX)     # mode 0700; deleted when the job ends
    touch "$LAUNCH_DIR/$stamp.start"
    # The token reaches the job only through its environment (not argv, not a file).
    CLAUDE_CODE_OAUTH_TOKEN="$token" CLAUDE_CONFIG_DIR="$cfg" DP_LAUNCH_STAMP="$stamp" \
        setsid nohup "$0" __job "$node" "$@" > "$log" 2>&1 < /dev/null &
    token=""
    echo "launched pid $! on NUMA node $node"
    echo "log: $log"
}

# Scan files written during the job for the token value. The pattern goes to grep through a
# process substitution, so the token never appears in a command line.
sweep_token() {
    local marker="$1" hits=0 f
    while IFS= read -r -d '' f; do
        if grep -qF -f <(printf '%s\n' "$CLAUDE_CODE_OAUTH_TOKEN") -- "$f" 2>/dev/null; then
            echo "SWEEP: TOKEN FOUND in $f"
            hits=$((hits + 1))
        fi
    done < <(find "$HOME/.claude" "$HOME/.config" "$HOME/.cache" "$HOME/.local/state" \
                  "$HARNESS/agent/runs" "$AGENT" /tmp -xdev -user "$(id -un)" -type f \
                  -newer "$marker" -size -64M -not -path '*/.discopop/*' -print0 2>/dev/null)
    for f in "$HOME/.claude.json" "$HOME/.bash_history"; do
        if [ -f "$f" ] && grep -qF -f <(printf '%s\n' "$CLAUDE_CODE_OAUTH_TOKEN") -- "$f"; then
            echo "SWEEP: TOKEN FOUND in $f"
            hits=$((hits + 1))
        fi
    done
    if [ "$hits" -eq 0 ]; then
        echo "SWEEP: token value not found in any file written during the job"
    fi
}

sweep() {
    local found=0 f d creds
    creds=$(find "$HOME" -xdev -maxdepth 4 -name .credentials.json 2>/dev/null)
    if [ -n "$creds" ]; then
        echo "SWEEP: credential file(s) present:"
        echo "$creds"
        found=1
    fi
    for f in "$HOME/.claude.json" "$HOME"/.claude/*.json; do
        if [ -f "$f" ] && grep -qE '"(oauthAccount|primaryApiKey|apiKey)"' "$f"; then
            echo "SWEEP: credential key in $f"
            found=1
        fi
    done
    for f in "$HOME/.bash_history" "$HOME/.bashrc" "$HOME/.profile"; do
        if [ -f "$f" ] && grep -qE 'CLAUDE_CODE_OAUTH_TOKEN=|sk-ant-' "$f"; then
            echo "SWEEP: token-like entry in $f"
            found=1
        fi
    done
    if [ "$(running_jobs)" -eq 0 ]; then
        for d in /tmp/dpcfg.*; do
            if [ -d "$d" ]; then
                rm -rf "$d"
                echo "SWEEP: removed stale config directory $d"
            fi
        done
    fi
    if [ "$found" -eq 0 ]; then
        echo "SWEEP: clean — no credential files, credential keys or history entries"
    fi
}

# One cheap model call before any trial starts. It exists because a rejected
# credential does not look like a failure anywhere else: the CLI reports it as a
# result with is_error set, subtype "success", AND exit code 0, so a bad token
# silently turns every trial into a clean "no-change" with zero tokens. The first
# server pilot was lost exactly that way (thesis record §7, pilot_seidel).
auth_check() {
    "$PY" - <<'PY'
import asyncio
import sys

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query


async def main() -> int:
    opts = ClaudeAgentOptions(system_prompt="Reply with one word.",
                              model="claude-haiku-4-5-20251001", max_turns=1,
                              allowed_tools=[], permission_mode="dontAsk",
                              setting_sources=[])
    bad = ""
    # Never return from inside the loop: leaving the async generator suspended
    # makes its own close fail and prints an irrelevant traceback over the real
    # message — the same trap as in the agent's providers.py (Fix 58).
    try:
        async for m in query(prompt="Say: ok", options=opts):
            if isinstance(m, ResultMessage) and getattr(m, "is_error", False):
                bad = str(getattr(m, "result", "") or m.subtype)
    except Exception as e:
        # The CLI exits non-zero after an error result, so the SDK raises before
        # the loop ends. Its exception says only "error result: success" — the
        # reason the CLI itself gave is what the operator needs, since a bad
        # token, a missing token and an exhausted usage limit each call for a
        # different response.
        bad = bad or str(e)
    if bad:
        print(f"   {bad}")
        return 1
    return 0


try:
    sys.exit(asyncio.run(main()))
except Exception as e:                      # no CLI, no network, rejected token
    print(f"   {e}")
    sys.exit(1)
PY
}

job() {
    local node="$1" rc=0
    shift
    local marker="$LAUNCH_DIR/$DP_LAUNCH_STAMP.start"
    finish() {
        echo "== benchmark exit $rc  $(date -Is)"
        rm -rf "$CLAUDE_CONFIG_DIR"
        sweep_token "$marker"
        unset CLAUDE_CODE_OAUTH_TOKEN
        sweep
        rm -f "$marker"
    }
    trap finish EXIT
    trap 'rc=143; exit 143' TERM INT
    echo "== job $DP_LAUNCH_STAMP  host $(hostname)  NUMA node $node  $(date -Is)"
    echo "== agent $(git -C "$AGENT" rev-parse --short HEAD) ($(tree_state "$AGENT"))" \
         " harness $(git -C "$HARNESS" rev-parse --short HEAD) ($(tree_state "$HARNESS"))"
    echo "== load $(cut -d' ' -f1-3 /proc/loadavg)"
    echo "== args: $*"
    cd "$HARNESS" || exit 1
    echo "== auth check"
    if ! auth_check; then
        echo "== ABORT: the model credential is rejected — not a single trial was started."
        echo "== Mint a new one (claude setup-token), replace the Keychain item, re-launch."
        rc=2
        exit 2
    fi
    echo "== auth ok"
    if command -v numactl > /dev/null; then
        # "N" = the whole NUMA node N; "N.H" = half H (0 or 1) of node N's cores, with node N's
        # memory — four lanes of 12 cores instead of two of 24 (the author, 23 Sep; checked by
        # T0.4 at four lanes before the first experiment used them).
        case "$node" in
            *.*)
                local nn="${node%.*}" half="${node#*.}" cpus n k
                cpus=$(numactl -H | awk -v n="$nn" '$1=="node" && $2==n && $3=="cpus:" {for (i=4;i<=NF;i++) print $i}')
                n=$(printf '%s
' "$cpus" | grep -c .)
                k=$((n / 2))
                if [ "$half" = 0 ]; then cpus=$(printf '%s
' "$cpus" | head -n "$k"); else cpus=$(printf '%s
' "$cpus" | tail -n "$((n - k))"); fi
                cpus=$(printf '%s
' "$cpus" | paste -sd, -)
                echo "== lane: node $nn, cores $cpus"
                numactl --physcpubind="$cpus" --membind="$nn" "$PY" agent/benchmark run "$@" ;;
            *)
                numactl --cpunodebind="$node" --membind="$node" "$PY" agent/benchmark run "$@" ;;
        esac
    else
        echo "== WARNING: numactl missing, running unpinned"
        "$PY" agent/benchmark run "$@"
    fi
    rc=$?
    exit "$rc"
}

status() {
    local last
    if [ "$(running_jobs)" -gt 0 ]; then
        pgrep -u "$(id -un)" -af 'job.sh __job'
    else
        echo "no job running"
    fi
    last=$(ls -1t "$LAUNCH_DIR"/*.log 2> /dev/null | head -1)
    if [ -n "$last" ]; then
        echo "== $last"
        tail -n "${1:-25}" "$last"
    fi
}

cmd="${1:-}"
shift || true
case "$cmd" in
    state) state ;;
    update-agent) update_agent "$@" ;;
    install-wrappers) install_wrappers ;;
    launch) launch "$@" ;;
    __job) job "$@" ;;
    status) status "$@" ;;
    sweep) sweep ;;
    *) sed -n '2,14p' "$0"; exit 2 ;;
esac
