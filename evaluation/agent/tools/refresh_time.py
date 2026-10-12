#!/usr/bin/env python3
"""E4 step 3 — what one fast refresh saves where the profiling run is long. No model.

For each program, in the configuration of an archived trial (its command line): the program is profiled in full
once; then an edit that changes nothing — one comment line put in front of the file under study, so that every
line of it moves by one and every dependence has to be carried over — and, REPEATS times, the profile after that
edit is made both ways with the agent's own functions, in turn:

    the fast refresh   `_reprofil_fast`: compile with instrumentation, carry the dependences over, explore
    the full profile   `_reprofil`:      compile with instrumentation, run the instrumented program, explore

Each is timed as a whole and in its parts (the compile, the instrumented run, the explorer; the rest of a fast
refresh is the carrying over). After each, DiscoPoP's patterns are read, so that the read-out can say whether the
fast refresh of an unchanged program gives the patterns of the full profile.

    venv/bin/python evaluation/agent/tools/refresh_time.py --run t0_11_b24_apps_a --arm discopop_capability \\
        --benchmarks rodinia-3.1/hotspot,npb/is --repeats 5 --out /tmp/x

Output: `<out>/results.jsonl` (one record per program), `<out>/manifest.json`, `<out>/logs/`.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refresh_replay as rr  # noqa: E402

COMMENT = "// one comment line: an edit that changes nothing\n"


def patterns(dp: Path) -> List[List[Any]]:
    """DiscoPoP's patterns as the explorer wrote them, sorted: [type, start line, end line, and for each kind of
    data-sharing clause the names in it]. Task patterns are counted, not listed: there are hundreds of them on the
    larger programs and they carry no directive of their own here."""
    f = dp / "explorer" / "patterns.json"
    if not f.is_file():
        return []
    data = json.loads(f.read_text())
    out: List[List[Any]] = []
    for kind, items in (data.get("patterns") or {}).items():
        items = items if isinstance(items, list) else []
        if kind == "task":
            out.append([kind, len(items)])
            continue
        for p in items:
            if isinstance(p, dict):
                clauses = {c: sorted(str(x) for x in (p.get(c) or []))
                           for c in ("first_private", "private", "last_private", "shared", "reduction")}
                out.append([kind, str(p.get("start_line")), str(p.get("end_line")), json.dumps(clauses, sort_keys=True)])
    return sorted(out, key=json.dumps)


@contextlib.contextmanager
def parts_timed(store: Dict[str, float]) -> Iterator[None]:
    """Times the runner's own steps: its subprocesses (the instrumented build, then the instrumented run) and the
    explorer."""
    from discopop_agent.profiling import runner
    real_run, real_explorer = runner.subprocess.run, runner.run_explorer
    calls: List[float] = []
    exploring = [False]

    def run(*a: Any, **kw: Any) -> Any:
        t0 = time.monotonic()
        try:
            return real_run(*a, **kw)
        finally:
            if not exploring[0]:                       # the explorer's own subprocess is not a step of the runner
                calls.append(time.monotonic() - t0)

    def explorer(*a: Any, **kw: Any) -> Any:
        t0 = time.monotonic()
        exploring[0] = True
        try:
            return real_explorer(*a, **kw)
        finally:
            exploring[0] = False
            store["explore_s"] = round(store.get("explore_s", 0.0) + time.monotonic() - t0, 3)

    runner.subprocess.run = run                                     # type: ignore[assignment]
    runner.run_explorer = explorer                                  # type: ignore[assignment]
    try:
        yield
    finally:
        runner.subprocess.run = real_run                            # type: ignore[assignment]
        runner.run_explorer = real_explorer                         # type: ignore[assignment]
        if calls:
            store["compile_s"] = round(calls[0], 3)
        if len(calls) > 1:
            store["run_s"] = round(sum(calls[1:]), 3)


def trial_of(run: str, arm: str, bench_id: str) -> Optional[Path]:
    root = rr.campaign.find_run(run)
    if root is None:
        raise SystemExit(f"run {run} is not in the archive")
    found = sorted(root.glob(f"benchmarks/{bench_id}/{arm}/*/rep*/trial.json"))
    return found[0] if found else None


def one(bench_id: str, tj: Dict[str, Any], repeats: int, work: Path, log: Any) -> Dict[str, Any]:
    from discopop_agent import args as args_mod
    from discopop_agent import project as project_mod
    from discopop_agent.profiling import tools as profiling_tools
    from discopop_agent.profiling.runner import _reprofil, _reprofil_fast
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(rr.PREPARED / bench_id, work)
    cmd = list(tj["agent_cmd"])
    flags = cmd[cmd.index("discopop_agent") + 1:]
    os.chdir(work)
    argv = sys.argv
    try:
        sys.argv = ["discopop_agent"] + flags
        with contextlib.redirect_stdout(log):
            a = args_mod.parse_args()
    finally:
        sys.argv = argv
    project_mod.activate(a.project)
    if a.project is not None:
        project_mod.set_focus(a.source_file)
    profiling_tools.set_explorer_timeout(a.explorer_timeout)
    src, dp, snap, scratch = Path(a.source_file).resolve(), work / ".discopop", work / "_profile_before", work / "_refresh"
    scratch.mkdir(exist_ok=True)
    pre = src.read_text()
    post = COMMENT + pre
    rec: Dict[str, Any] = {"benchmark": bench_id, "file": str(src.relative_to(work.resolve())),
                           "lines": len(pre.splitlines()), "repeats": []}

    def timed(kind: str) -> Dict[str, Any]:
        parts: Dict[str, float] = {}
        t0 = time.monotonic()
        with contextlib.redirect_stdout(log), parts_timed(parts):
            if kind == "fast":
                ok, note = _reprofil_fast(a.source_file, dp, pre, post, scratch)
            else:
                ok, note = bool(_reprofil(a.source_file, dp, a.reprofil_args or None)), ""
        res: Dict[str, Any] = {"ok": bool(ok), "seconds": round(time.monotonic() - t0, 3), **parts}
        if note:
            res["note"] = str(note)[:300]
        res["patterns"] = patterns(dp) if ok else []
        return res

    shutil.rmtree(dp, ignore_errors=True)
    rec["before"] = timed("full")                      # the profile of the unchanged program
    if not rec["before"]["ok"]:
        return rec
    shutil.copytree(dp, snap)
    for k in range(repeats):
        rep: Dict[str, Any] = {}
        for kind in (("fast", "full") if k % 2 == 0 else ("full", "fast")):
            if kind == "fast":                         # from the profile of the program before the edit
                src.write_text(pre)
                shutil.rmtree(dp, ignore_errors=True)
                shutil.copytree(snap, dp)
            src.write_text(post)
            rep[kind] = timed(kind)
        rec["repeats"].append(rep)
        print(f"{bench_id} repeat {k + 1}: fast {rep['fast']['seconds']} s ({'ok' if rep['fast']['ok'] else 'UNUSABLE'}), "
              f"full {rep['full']['seconds']} s; the same patterns: {rep['fast']['patterns'] == rep['full']['patterns']}",
              flush=True)
    src.write_text(pre)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="the archived run whose trials give each program's configuration")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--benchmarks", required=True, help="comma-separated SUITE/NAME")
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    out = a.out.resolve()
    (out / "logs").mkdir(parents=True, exist_ok=True)
    manifest: Dict[str, Any] = {
        "tool": "refresh_time.py", "run": a.run, "arm": a.arm, "benchmarks": a.benchmarks.split(","),
        "repeats": a.repeats, "host": platform.node(),
        "commit": subprocess.run(["git", "-C", str(rr.REPO), "rev-parse", "HEAD"], capture_output=True,
                                 text=True).stdout.strip(),
        "discopop_pass_sha256": rr.pass_digest(), "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    cwd = Path.cwd()
    root = Path(tempfile.mkdtemp(prefix="refresh_time_"))
    try:
        for bench_id in manifest["benchmarks"]:
            t = trial_of(a.run, a.arm, bench_id)
            if t is None:
                print(f"{bench_id}: no trial in {a.run}", flush=True)
                continue
            with open(out / "logs" / (bench_id.replace("/", "__") + ".log"), "a") as log:
                rec = one(bench_id, json.loads(t.read_text()), a.repeats, root / "work", log)
            os.chdir(cwd)
            with open(out / "results.jsonl", "a") as f:
                f.write(json.dumps(rec) + "\n")
    finally:
        os.chdir(cwd)
        shutil.rmtree(root, ignore_errors=True)
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
