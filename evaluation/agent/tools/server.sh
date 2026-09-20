#!/usr/bin/env bash
# Run the experiments on the server from the Mac. Code is never edited on the server: it is
# synced from here, and every launch first proves Mac and server are identical.
#
#   agent/tools/server.sh sync                     the server fetches this commit from GitHub (agent and
#                                                  evaluation are one repository since 2026-09-20)
#   agent/tools/server.sh parity                   compare Mac and server; exit 1 on a difference
#   agent/tools/server.sh run [--node N] [--allow-dirty-harness] -- ARGS
#                                                  launch `agent/benchmark run ARGS` on NUMA node N
#                                                  (default 1) with the Claude token from the Keychain
#   agent/tools/server.sh status [LINES]           running jobs, tail of the latest launcher log
#   agent/tools/server.sh sweep                    check the server for credentials left on disk
#   agent/tools/server.sh fetch [RUN_ID...]        copy runs back (profile trees excluded) and
#                                                  archive them into the tracked agent/results/
#
# One-time token setup on the Mac (the token never leaves the Keychain except into a job's
# environment):  claude setup-token
#                security add-generic-password -a "$USER" -s claude-code-oauth-token -w
set -uo pipefail

# The server's address and account are not in this (public) repository: put them in the
# untracked file next to this script,  agent/tools/server.local :
#     DP_SERVER=user@host
#     DP_SERVER_KEY=$HOME/.ssh/<key>
[ -f "$(dirname "$0")/server.local" ] && . "$(dirname "$0")/server.local"
HOST="${DP_SERVER:-}"
KEY="${DP_SERVER_KEY:-$HOME/.ssh/id_ed25519}"
[ -n "$HOST" ] || { echo "error: no server configured — create agent/tools/server.local (see the comment in $0)" >&2; exit 1; }
KEYCHAIN_SERVICE="claude-code-oauth-token"
HARNESS="$(cd "$(dirname "$0")/../.." && pwd)"
# evaluation/ lives inside the agent repository (since 2026-09-20); before, they were siblings
if [ -f "$HARNESS/../discopop_agent/__main__.py" ]; then
    AGENT="$(cd "$HARNESS/.." && pwd)"
else
    AGENT="$(cd "$HARNESS/../discopop_agent" && pwd)"
fi
R_AGENT="discopop_agent"                 # relative to the server home
R_HARNESS="${DP_R_HARNESS:-$R_AGENT/evaluation}"   # DP_R_HARNESS=new_benchmark_harness: runs started before the move
R_JOB="$R_HARNESS/agent/tools/job.sh"

die() { echo "error: $*" >&2; exit 1; }
remote() { ssh -i "$KEY" -o BatchMode=yes "$HOST" "$@"; }

sync_code() {
    local sha
    sha=$(git -C "$AGENT" rev-parse HEAD)
    [ -z "$(git -C "$AGENT" status --porcelain)" ] || die "agent checkout has uncommitted changes — commit and push first"
    git -C "$AGENT" branch -r --contains "$sha" | grep -q . \
        || die "agent commit ${sha:0:8} is not pushed — the server fetches the agent from GitHub"
    echo "== agent + evaluation → ${sha:0:8} (one repository: the server fetches this commit from GitHub)"
    remote "git -C $R_AGENT fetch -q origin && git -C $R_AGENT merge -q --ff-only $sha" \
        || die "server cannot fast-forward to ${sha:0:8}"
    remote "$R_JOB install-wrappers" || die "wrapper install failed"
    parity
}

field() { printf '%s\n' "$1" | sed -n "s/^$2=//p"; }

where() {  # classify an import path: the checkout (as on the Mac) or an installed copy
    case "$1" in
        */discopop_agent/explorer/discopop_explorer/__init__.py) echo checkout ;;
        */discopop_agent/library/discopop_library/__init__.py) echo checkout ;;
        *) echo "installed copy" ;;
    esac
}

parity() {
    local allow_dirty_harness="${1:-no}" L R k lv rv v failed=0
    L=$("$HARNESS/agent/tools/job.sh" state) || die "local state failed"
    R=$(remote "$R_JOB state") || die "server state failed — run 'sync' first"
    printf '%-17s %-22s %-22s %s\n' item mac server verdict
    for k in agent_head harness_head agent_tree harness_tree wrappers explorer library \
             anthropic claude_agent_sdk disk_free load jobs; do
        lv=$(field "$L" "$k")
        rv=$(field "$R" "$k")
        case "$k" in
            agent_head|harness_head|anthropic|claude_agent_sdk)
                if [ "$lv" = "$rv" ]; then v=ok; else v=DIFFER; fi
                lv=${lv:0:12}; rv=${rv:0:12} ;;
            agent_tree)
                if [ "$lv" = clean ] && [ "$rv" = clean ]; then v=ok; else v=DIRTY; fi ;;
            harness_tree)
                if [ "$lv" = clean ] && [ "$rv" = clean ]; then v=ok
                elif [ "$allow_dirty_harness" = yes ] && [ "$lv" = "$rv" ]; then v="ok (dirty allowed)"
                else v=DIRTY; fi ;;
            wrappers)
                if [ "$lv" = match ] && [ "$rv" = match ]; then v=ok; else v=DIFFER; fi ;;
            explorer|library)
                lv=$(where "$lv"); rv=$(where "$rv")
                if [ "$lv" = checkout ] && [ "$rv" = checkout ]; then v=ok; else v=DIFFER; fi ;;
            *) v=info ;;
        esac
        case "$v" in ok*|info) ;; *) failed=1 ;; esac
        printf '%-17s %-22s %-22s %s\n' "$k" "$lv" "$rv" "$v"
    done
    if [ "$failed" -eq 0 ]; then echo "PARITY OK"; else echo "PARITY FAILED"; return 1; fi
}

run_job() {
    local node=1 allow=no token
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --node) node="$2"; shift 2 ;;
            --allow-dirty-harness) allow=yes; shift ;;
            --) shift; break ;;
            *) die "unknown option $1 (benchmark arguments go after --)" ;;
        esac
    done
    [ "$#" -gt 0 ] || die "no benchmark arguments; example: run -- polybench/seidel-2d --arms full --models haiku"
    parity "$allow" || die "Mac and server differ — run 'sync' (and commit) before launching"
    token=$(security find-generic-password -a "$USER" -s "$KEYCHAIN_SERVICE" -w 2> /dev/null) \
        || die "no Claude token in the Keychain; see the setup lines at the top of this script"
    printf '%s\n' "$token" | remote "$R_JOB launch $node $(printf '%q ' "$@")"
    token=""
}

fetch_runs() {
    # Copy runs back (profile trees, scratch copies and binaries excluded) and archive them
    # into the tracked agent/results/ — every result reaches the repository the moment it
    # is fetched; committing it is the one manual step (agent/results/README.md).
    local id
    mkdir -p "$HARNESS/agent/runs"
    if [ "$#" -eq 0 ]; then
        rsync -az --exclude '.discopop/' --exclude 'work/' --exclude 'a.out' --exclude '*.dSYM' \
            -e "ssh -i $KEY -o BatchMode=yes" \
            "$HOST:$R_HARNESS/agent/runs/" "$HARNESS/agent/runs/" || die "fetch failed"
        echo "fetched all runs → agent/runs/"
        python3 "$HARNESS/agent/benchmark" archive --all || die "archive failed"
    else
        for id in "$@"; do
            rsync -az --exclude '.discopop/' --exclude 'work/' --exclude 'a.out' --exclude '*.dSYM' \
                -e "ssh -i $KEY -o BatchMode=yes" \
                "$HOST:$R_HARNESS/agent/runs/$id" "$HARNESS/agent/runs/" || die "fetch of $id failed"
            echo "fetched $id → agent/runs/$id"
        done
        python3 "$HARNESS/agent/benchmark" archive "$@" || die "archive failed"
    fi
    echo "now: git -C $AGENT add evaluation/agent/results && git commit -m 'results: ...' && git push"
}

cmd="${1:-}"
shift || true
case "$cmd" in
    sync) sync_code ;;
    parity) parity no ;;
    run) run_job "$@" ;;
    status) remote "$R_JOB status ${1:-25}" ;;
    sweep) remote "$R_JOB sweep" ;;
    fetch) fetch_runs "$@" ;;
    *) sed -n '2,19p' "$0"; exit 2 ;;
esac
