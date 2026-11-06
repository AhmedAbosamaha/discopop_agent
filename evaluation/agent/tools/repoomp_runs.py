#!/usr/bin/env python3
"""E11 part 2 — trials of RepoOMP's RELEASED pipeline (`repoomp_release.py`) on packaged kernels, each one judged by
the harness like every other setup's program. One job on one lane (`server.sh tool --node N -- repoomp_runs.py ...`):

  for every benchmark, for every trial number:
    1. a fresh `claude_openai_shim.py` on a free local port, its log inside the trial (`shim_calls.jsonl`: every call's
       usage, failure, prompt and answer) — none with `--no-model` (the release's rules path only);
    2. `repoomp_release.py BENCH --out TRIAL/repoomp` — the release's own analysis, hot functions, rules, prompt and
       attempts, its own choice of the program; ours only its build, check and time (that tool's docstring);
    3. the shim stopped; the candidate builds (`work/build*`: copies of the package with a binary) deleted;
    4. `agent/benchmark verify-source BENCH --label repoomp_release --source TRIAL/repoomp/final --repeat N` — the
       harness's own verification at the benchmark's verification size, the same judge as every other setup;
    5. the release's own record and the calls' count, failures and cost added to the trial's `trial.json`.

A trial whose shim log has a failed call is moved to `runs/_set_aside/` and run once more (RUNBOOK §6: a failed call
is infrastructure, never counted); a second failure is kept and counted as `call-failed` by the read-out. A trial with
a `trial.json` is done and skipped, so a stopped job resumes; a half-done one is moved aside first.

    venv/bin/python evaluation/agent/tools/repoomp_runs.py --run-id e11b_r_repoomp \
        --benchmarks tsvc_c2/k19,tsvc_c2/k23 --trials 5 --repoomp-python ~/repoomp_venv/bin/python
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
AGENT_DIR = HERE.parent
HARNESS_ROOT = AGENT_DIR.parent
LABEL = "repoomp_release"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _wait_port(port: int, proc: subprocess.Popen, seconds: float = 90.0) -> bool:
    end = time.time() + seconds
    while time.time() < end:
        if proc.poll() is not None:
            return False
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def _calls(log: Path) -> Dict[str, Any]:
    recs: List[Dict[str, Any]] = []
    if log.exists():
        for line in log.read_text().splitlines():
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError:
                recs.append({"ok": False, "error": "unreadable log line"})
    cost = sum(float(r.get("total_cost_usd") or 0.0) for r in recs)
    return {"llm_calls": len(recs), "llm_call_failures": sum(1 for r in recs if not r.get("ok")),
            "llm_usage": {"calls_recorded": len(recs), "cost_usd": round(cost, 4),
                          "model_seconds": round(sum(float(r.get("seconds") or 0.0) for r in recs), 1),
                          "thinking_off_all": all(bool(r.get("thinking_off")) for r in recs) if recs else None}}


def _set_aside(run_id: str, trial: Path, why: str) -> Path:
    dest = AGENT_DIR / "runs" / "_set_aside" / f"{run_id}_{why}_{time.strftime('%Y%m%d_%H%M%S')}" / \
        trial.relative_to(AGENT_DIR / "runs" / run_id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(trial), str(dest))
    return dest


def one_trial(a: argparse.Namespace, bench: str, rep: int, trial: Path) -> Dict[str, Any]:
    trial.mkdir(parents=True, exist_ok=True)
    out = trial / "repoomp"
    shim: Optional[subprocess.Popen] = None
    api_base = ""
    log = trial / "shim_calls.jsonl"
    t0 = time.time()
    if not a.no_model:
        port = _free_port()
        shim = subprocess.Popen([sys.executable, str(HERE / "claude_openai_shim.py"), "--port", str(port),
                                 "--log", str(log)], stdout=subprocess.DEVNULL, stderr=open(trial / "shim_stderr.txt", "w"))
        if not _wait_port(port, shim):
            shim.terminate()
            return {"error": "the shim did not start", "rc": None}
        api_base = f"http://127.0.0.1:{port}/v1"
    try:
        cmd = [sys.executable, str(HERE / "repoomp_release.py"), bench, "--out", str(out), "--api-base", api_base,
               "--model", a.model, "--repoomp-python", a.repoomp_python, "--cc", a.cc, "--threads", str(a.threads),
               "--runs", str(a.runs)]
        with open(trial / "repoomp_stdout.txt", "w") as so, open(trial / "repoomp_stderr.txt", "w") as se:
            try:
                rc: Optional[int] = subprocess.run(cmd, stdout=so, stderr=se, timeout=a.timeout).returncode
            except subprocess.TimeoutExpired:
                rc = None
    finally:
        if shim is not None:
            shim.terminate()
            try:
                shim.wait(timeout=30)
            except subprocess.TimeoutExpired:
                shim.kill()
    for d in sorted((out / "work").glob("build*")):
        if d.is_dir():
            shutil.rmtree(d)
    rec: Dict[str, Any] = {"rc": rc, "release_seconds": round(time.time() - t0, 1)}
    rec.update(_calls(log) if not a.no_model else {"llm_calls": 0, "llm_call_failures": 0})
    return rec


def judge(a: argparse.Namespace, bench: str, rep: int, trial: Path) -> int:
    cmd = [sys.executable, str(AGENT_DIR / "benchmark"), "verify-source", bench, "--label", LABEL,
           "--source", str(trial / "repoomp" / "final"), "--threads", a.judge_threads,
           "--repeats", str(a.judge_repeats), "--run-id", a.run_id, "--repeat", str(rep)]
    with open(trial / "judge_stdout.txt", "w") as so:
        return subprocess.run(cmd, cwd=HARNESS_ROOT, stdout=so, stderr=subprocess.STDOUT).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--benchmarks", required=True, help="comma-separated packaged kernels")
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--no-model", action="store_true", help="the release's rules path only (a no-model probe)")
    ap.add_argument("--model", default="claude-sonnet-4-5-20250929")
    ap.add_argument("--repoomp-python", default=os.path.expanduser("~/repoomp_venv/bin/python"))
    ap.add_argument("--cc", default="clang-20")
    ap.add_argument("--threads", type=int, default=12, help="the release's threads (its default 4, the paper's 16)")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--judge-threads", default="6,12")
    ap.add_argument("--judge-repeats", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=4 * 3600, help="seconds for one release pipeline")
    a = ap.parse_args()

    root = AGENT_DIR / "runs" / a.run_id
    root.mkdir(parents=True, exist_ok=True)
    summary = root / "repoomp_runs.jsonl"
    rc_all = 0
    for bench in [b for b in a.benchmarks.split(",") if b]:
        for rep in range(1, a.trials + 1):
            trial = root / "benchmarks" / bench / LABEL / "none" / f"rep{rep}"
            if (trial / "trial.json").exists():
                print(f"{bench} rep{rep}: done before — skipped", flush=True)
                continue
            if trial.exists():
                print(f"{bench} rep{rep}: half done before — moved to {_set_aside(a.run_id, trial, 'incomplete')}",
                      flush=True)
            for attempt in (1, 2):
                rec = one_trial(a, bench, rep, trial)
                if rec.get("llm_call_failures", 0) > 0 and attempt == 1:
                    print(f"{bench} rep{rep}: {rec['llm_call_failures']} failed call(s) — moved to "
                          f"{_set_aside(a.run_id, trial, 'call_failed')}, run again", flush=True)
                    continue
                break
            final = trial / "repoomp" / "final"
            jrc = judge(a, bench, rep, trial) if final.is_dir() else None
            tj = trial / "trial.json"
            t: Dict[str, Any] = json.loads(tj.read_text()) if tj.exists() else {
                "benchmark": bench, "arm": LABEL, "model": "none", "repeat": rep, "kind": "baseline",
                "outcome": "TOOL_ERROR", "error": "the release produced no final program"}
            res_p = trial / "repoomp" / "repoomp_result.json"
            t["repoomp"] = json.loads(res_p.read_text()) if res_p.exists() else None
            t["repoomp_model"] = None if a.no_model else a.model
            t["repoomp_rc"], t["judge_rc"], t["release_seconds"] = rec.get("rc"), jrc, rec.get("release_seconds")
            for k in ("llm_calls", "llm_call_failures", "llm_usage"):
                if k in rec:
                    t[k] = rec[k]
            if rec.get("error"):
                t["runner_error"] = rec["error"]
            tj.write_text(json.dumps(t, indent=1, default=str) + "\n")
            line = {"benchmark": bench, "repeat": rep, "outcome": t.get("outcome"),
                    "opt_method": (t.get("repoomp") or {}).get("opt_method"), "llm_calls": t.get("llm_calls"),
                    "llm_call_failures": t.get("llm_call_failures"),
                    "cost_usd": (t.get("llm_usage") or {}).get("cost_usd"), "release_seconds": rec.get("release_seconds"),
                    "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
            with summary.open("a") as f:
                f.write(json.dumps(line) + "\n")
            print(json.dumps(line), flush=True)
            if t.get("outcome") == "TOOL_ERROR":
                rc_all = 1
    return rc_all


if __name__ == "__main__":
    raise SystemExit(main())
