#!/usr/bin/env python3
"""T0.6 — does DiscoPoP, on its own, propose parallelisations inside ``main``?

Decision D4 (THESIS_EXPERIMENTS.md §5d): ``main`` is excluded from the agent's targeting only
if DiscoPoP itself never proposes a pragma there. Otherwise excluding it would also remove
DiscoPoP's own suggestions from the comparison against DiscoPoP.

Each packaged benchmark is profiled exactly as the harness profiles it (``discopop_cc`` /
``discopop_cxx`` → one run → ``discopop_explorer``), and every pattern in the unfiltered
``patterns.json`` is placed in the function that contains it, using the function spans
DiscoPoP itself writes into ``Data.xml`` (C++ names demangled with the agent's helper, or `c++filt` where that is unavailable).

Writes ``patterns.csv`` (one row per pattern) and ``summary.json`` into ``--out``.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scaffold import TOKEN, _strip_comments  # noqa: E402
import bench as bench_tools  # noqa: E402

AGENT_DIR = Path(__file__).resolve().parent.parent
EXPLORER_ATTEMPTS = 20   # as the harness (cli.py): 0.75^20 leaves a 0.3 % chance of losing a benchmark to the explorer's random crash
PREPARED = AGENT_DIR / "prepared"


def _run(cmd: List[str], cwd: Path, env: Dict[str, str], timeout: float) -> Tuple[bool, str]:
    """Run a command in its own process group, killing the GROUP on timeout.

    `subprocess.run(timeout=…)` kills only the direct child; DiscoPoP's wrapper scripts exec
    the compiler, which then survives. Measured: the compile of NPB `lu` ran on for over an
    hour after this study's timeout had given up on it."""
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            p.kill()
        p.wait(timeout=10)
        return False, "timeout"
    return p.returncode == 0, (err or out)[-300:]


_PLAIN_CACHE: Dict[str, str] = {}


def _plain(name: str) -> str:
    """Plain name of a possibly mangled C++ symbol.

    Prefers the agent's own helper, so names resolve exactly as the agent's exclusion list
    resolves them. Falls back to `c++filt` where the agent checkout predates that helper
    (the server between syncs), and finally to the raw name, so this study never depends on
    which agent version happens to be installed."""
    if name in _PLAIN_CACHE:
        return _PLAIN_CACHE[name]
    out = name
    try:
        from discopop_agent.plan.regions import demangle
        out = demangle(name)
    except ImportError:
        if name.startswith("_Z") and shutil.which("c++filt"):
            # No `-p`: the Mac's LLVM c++filt rejects it, the server's GNU one accepts it.
            # Without it both print `pb_emit(double)`, so the signature is trimmed here.
            r = subprocess.run(["c++filt", name], capture_output=True, text=True)
            text = (r.stdout or "").strip()
            if text and text != name:
                out = text.split("(")[0].strip().split("::")[-1] or name
    _PLAIN_CACHE[name] = out
    return out


def _functions(data_xml: Path) -> List[Tuple[str, int, int, int]]:
    """(plain name, file id, first line, last line) of every function DiscoPoP recorded."""
    out = []
    for m in re.finditer(r"<Node [^>]*>", data_xml.read_text()):
        n = m.group(0)
        if 'type="1"' not in n:
            continue
        name = re.search(r'name="([^"]*)"', n)
        a = re.search(r'startsAtLine\s*=\s*"(\d+):(\d+)"', n)
        b = re.search(r'endsAtLine\s*=\s*"(\d+):(\d+)"', n)
        if name and a and b:
            out.append((_plain(name.group(1)), int(a.group(1)), int(a.group(2)), int(b.group(2))))
    return out


def study(bench: Path, meta: dict, timeout: float) -> Tuple[List[dict], str, float, List[str]]:
    src = bench / meta["file"]
    with tempfile.TemporaryDirectory() as tmp:
        work = bench_tools.stage(bench, Path(tmp) / "src", meta)
        env = dict(os.environ)
        env["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{env.get('PATH', '')}"
        t0 = time.perf_counter()
        # One file, or a project through its unity unit (bench.py) — as the harness profiles it.
        instrument, unity = bench_tools.wrapper_cmd(work, meta)
        for cmd, cwd in ((instrument, work), (["./a.out"], work)):
            ok, err = _run(cmd, cwd, env, timeout)
            if unity is not None and cmd is instrument:
                unity.unlink(missing_ok=True)
            if not ok:
                return [], f"{cmd[0]} failed: {err}", time.perf_counter() - t0, []
        # The explorer has been seen to crash on one profile and succeed on the same
        # profile when run again, so it is retried on the SAME profile, and every
        # failure is kept: that separates a bad profile from a nondeterministic explorer.
        explorer_failures: List[str] = []
        for _ in range(EXPLORER_ATTEMPTS):
            shutil.rmtree(work / ".discopop" / "explorer", ignore_errors=True)
            ok, err = _run(["discopop_explorer"], work / ".discopop", env, timeout)
            if ok:
                break
            explorer_failures.append(err.strip().splitlines()[-1][:160] if err.strip() else "failed")
        else:
            return [], "discopop_explorer failed on every attempt", time.perf_counter() - t0, explorer_failures
        secs = time.perf_counter() - t0
        # Line text per DiscoPoP file id: a project has several files.
        fmap: Dict[int, Path] = {}
        for raw in (work / ".discopop" / "FileMapping.txt").read_text().splitlines():
            parts = raw.split("\t", 1) if "\t" in raw else raw.split(None, 1)
            if len(parts) == 2:
                fmap[int(parts[0])] = Path(parts[1].strip())
        texts = {fid: _strip_comments(p.read_text(errors="replace")).splitlines()
                 for fid, p in fmap.items() if p.exists()}
        funcs = _functions(work / ".discopop" / "profiler" / "Data.xml")
        pats = json.loads((work / ".discopop" / "explorer" / "patterns.json").read_text())["patterns"]
        excluded = set(meta.get("exclude_functions") or [])
        rows = []
        for kind, items in pats.items():
            for p in items:
                fid, line = (int(x) for x in str(p.get("start_line", "0:0")).split(":"))
                end = int(str(p.get("end_line", f"{fid}:{line}")).split(":")[1])
                # A suggestion on the packaging's own code (a line using pb_*/PB_*) does not
                # exist in the original benchmark and says nothing about DiscoPoP on it.
                span = texts.get(fid, [])[max(line - 1, 0):max(end, line)]
                on_scaffolding = any(TOKEN.search(x) for x in span) and not any(
                    x.strip() and not TOKEN.search(x) and x.strip() not in "{}" for x in span)
                owners = [f for f in funcs if f[1] == fid and f[2] <= line <= f[3]]
                owner = min(owners, key=lambda f: f[3] - f[2])[0] if owners else ""
                rows.append({
                    "kind": kind, "line": line, "function": owner,
                    "applicable": str(p.get("applicable_pattern")) == "True",
                    "pragma": str(p.get("pragma", ""))[:120],
                    "in_main": owner == "main",
                    "in_excluded_function": owner in excluded,
                    "on_scaffolding": on_scaffolding,
                    "end": end,
                })
        return rows, "ok", secs, explorer_failures


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--benchmarks", default="")
    ap.add_argument("--timeout", type=float, default=3600)
    a = ap.parse_args()
    wanted = {x for x in a.benchmarks.split(",") if x}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    all_rows: List[dict] = []
    summary: Dict[str, dict] = {}
    for m in sorted(PREPARED.glob("*/*/meta.json")):
        name = f"{m.parent.parent.name}/{m.parent.name}"
        if wanted and name not in wanted:
            continue
        meta = json.loads(m.read_text())
        rows, note, secs, failures = study(m.parent, meta, a.timeout)
        if note != "ok":
            print(f"{name:28s} FAILED {note}: {failures}", flush=True)
            summary[name] = {"error": note, "explorer_failures": failures}
            continue
        all_rows += [{"benchmark": name, **r} for r in rows]
        in_main = [r for r in rows if r["in_main"]]
        real = [r for r in in_main if not r["on_scaffolding"]]
        summary[name] = {
            "seconds": round(secs, 1), "patterns": len(rows), "explorer_failures": failures,
            "in_main_not_scaffolding": len(real),
            "applicable_in_main_not_scaffolding": sum(r["applicable"] for r in real),
            "applicable": sum(r["applicable"] for r in rows),
            "in_main": len(in_main), "applicable_in_main": sum(r["applicable"] for r in in_main),
            "in_main_detail": [f"{r['kind']} L{r['line']}-{r['end']} applicable={r['applicable']} "
                               f"scaffolding={r['on_scaffolding']} {r['pragma'][:60]}" for r in in_main],
        }
        s = summary[name]
        print(f"{name:28s} {secs:7.1f}s  patterns {s['patterns']:3d} (applicable {s['applicable']:3d})  "
              f"in main {s['in_main']:2d} (applicable {s['applicable_in_main']:2d}; not scaffolding: "
              f"{s['in_main_not_scaffolding']}, applicable {s['applicable_in_main_not_scaffolding']})"
              f"{'  explorer crashed ' + str(len(failures)) + 'x' if failures else ''}", flush=True)
    fields: List[str] = []
    for r in all_rows:
        fields += [k for k in r if k not in fields]
    with (out / "patterns.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields or ["benchmark"])
        w.writeheader()
        w.writerows(all_rows)
    (out / "summary.json").write_text(json.dumps(
        {"study": "T0.6 DiscoPoP patterns inside main", "host": platform.node(),
         "benchmarks": summary}, indent=2))
    print(f"wrote {out / 'patterns.csv'} and {out / 'summary.json'}")


if __name__ == "__main__":
    main()
