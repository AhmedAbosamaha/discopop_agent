#!/usr/bin/env python3
"""T0.5 — where does each benchmark's time go, region by region?

Evidence for two agent settings that decide which regions reach the model:

* ``--min-runtime-share F`` skips regions below a fraction F of measured runtime. What a
  value of F removes, and what it can cost, depends on how runtime is spread over regions.
* excluding ``main`` from targeting. Whether that loses anything depends on what ``main``
  holds and whether any of it lies inside the timed region.

For every packaged benchmark, DiscoPoP's own hotspot detection is run exactly as the agent
runs it (instrument, one run, analyse) at the agent's size (the packaged default) and, where
T0.1 fixed one, at the verification size. Each measured region is placed in its function,
given its source span, and marked as in scope (not inside an excluded function), inside
``main`` or not, and inside the timed region or not.

Amdahl's law turns the shares into bounds that need no model and no guess: a region with a
share s can raise whole-program speed by at most 1 / (1 − s), however well it is
parallelised. So the time a threshold can lose is bounded by the shares of the regions it
drops that no kept region contains.

Writes ``regions.csv`` (one row per region per size) and ``summary.json`` into ``--out``.
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
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench as bench_tools  # noqa: E402
from scaffold import _strip_comments  # noqa: E402  (same comment handling as the check)

AGENT_DIR = Path(__file__).resolve().parent.parent
PREPARED = AGENT_DIR / "prepared"
SIZES_FILE = AGENT_DIR / "kernel_sizes.json"
THRESHOLDS = [0.005, 0.01, 0.02, 0.05, 0.10]


# ---- source spans -------------------------------------------------------------------

def _match(s: str, i: int, open_c: str, close_c: str) -> int:
    """Index of the bracket closing the one at s[i]."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == open_c:
            depth += 1
        elif s[j] == close_c:
            depth -= 1
            if depth == 0:
                return j
    return len(s) - 1


def _stmt_end(s: str, i: int) -> int:
    """Index of the last character of the C statement starting at or after s[i]."""
    while True:
        while i < len(s) and s[i].isspace():
            i += 1
        if s.startswith("#", i):                     # a pragma or other directive line
            nl = s.find("\n", i)
            i = len(s) if nl < 0 else nl + 1
            continue
        break
    if i >= len(s):
        return len(s) - 1
    if s[i] == "{":
        return _match(s, i, "{", "}")
    m = re.match(r"(for|while|if|switch)\b", s[i:])
    if m:
        p = s.index("(", i + len(m.group(1)))
        end = _stmt_end(s, _match(s, p, "(", ")") + 1)
        if m.group(1) == "if":
            e = re.match(r"\s*else\b", s[end + 1:])
            if e:
                end = _stmt_end(s, end + 1 + e.end())
        return end
    if re.match(r"do\b", s[i:]):
        body_end = _stmt_end(s, i + 2)
        return s.find(";", body_end + 1)
    j = s.find(";", i)
    return len(s) - 1 if j < 0 else j


def _line_of(s: str, idx: int) -> int:
    return s.count("\n", 0, idx) + 1


def _loop_span(s: str, starts: List[int], line: int) -> Tuple[int, int]:
    """(first, last) line of the loop whose header is on `line`."""
    off = starts[line - 1]
    m = re.compile(r"\b(for|while|do)\b").search(s, off)
    if not m or _line_of(s, m.start()) > line + 1:
        return line, line
    return line, _line_of(s, _stmt_end(s, m.start()))


def _func_span(s: str, starts: List[int], line: int) -> Tuple[int, int]:
    off = starts[line - 1]
    b = s.find("{", off)
    if b < 0:
        return line, line
    return line, _line_of(s, _match(s, b, "{", "}"))


def _timed_windows(s: str) -> List[Tuple[int, int]]:
    """Line ranges strictly between a pb_timer_start() call and the next pb_timer_stop() call."""
    out = []
    for m in re.finditer(r"^[ \t]*pb_timer_start\s*\(\s*\)\s*;", s, re.M):
        st = re.compile(r"^[ \t]*pb_timer_stop\s*\(\s*\)\s*;", re.M).search(s, m.end())
        if st:
            out.append((_line_of(s, m.start()) + 1, _line_of(s, st.start()) - 1))
    return out


# ---- measurement --------------------------------------------------------------------

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


def measure(bench: Path, meta: dict, size: Optional[str], bin_dir: Path,
            timeout: float) -> Tuple[Optional[List[dict]], str, float]:
    """Hotspot detection as the agent runs it. Returns (regions, note, seconds)."""
    with tempfile.TemporaryDirectory() as tmp:
        work = bench_tools.stage(bench, Path(tmp) / "src", meta)
        env = dict(os.environ)
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
        env["DOT_DISCOPOP"] = str(work / ".discopop")
        flags = [f"-D{size}_DATASET"] if size else []
        t0 = time.perf_counter()
        # One file, or a project through its unity unit (bench.py) — as the agent does it.
        cmd, unity = bench_tools.wrapper_cmd(work, meta, hotspot=True, extra_flags=flags, out="hs.out")
        ok, err = _run(cmd, work, env, timeout)
        if unity is not None:
            unity.unlink(missing_ok=True)
        if not ok:
            return None, f"instrumentation failed: {err}", 0.0
        ok, err = _run(["./hs.out"], work, env, timeout)
        if not ok:
            return None, f"run failed: {err}", 0.0
        ok, err = _run(["discopop_hotspot_analyzer"], work / ".discopop", env, timeout)
        if not ok:
            return None, f"analyzer failed: {err}", 0.0
        secs = time.perf_counter() - t0
        data = json.loads((work / ".discopop" / "hotspot_detection" / "Hotspots.json").read_text())
        return data["code_regions"], "ok", secs


def _plain(name: str) -> str:
    """Demangled name, with the agent's own helper, so exclusions match as the agent matches them."""
    try:
        from discopop_agent.plan.regions import demangle
    except ImportError:
        return name
    return demangle(name)


def analyse(text: str, regions: List[dict], excluded: List[str]) -> List[dict]:
    # Only the benchmark's own file: a region from a system header has no span in this text.
    fid = next((r["fid"] for r in regions if r["typ"] == "FUNCTION" and _plain(r["name"]) == "main"), None)
    regions = [dict(r, name=_plain(r["name"])) for r in regions if fid is None or r["fid"] == fid]
    s = _strip_comments(text)
    starts = [0] + [m.end() for m in re.finditer(r"\n", s)]
    total = max((r["avr"] for r in regions), default=0.0) or 1.0
    funcs = []
    for r in regions:
        if r["typ"] == "FUNCTION":
            a, b = _func_span(s, starts, r["lineNum"])
            funcs.append((r["name"], a, b))
    windows = _timed_windows(s)
    rows = []
    for r in regions:
        line = r["lineNum"]
        if r["typ"] == "FUNCTION":
            a, b = _func_span(s, starts, line)
        else:
            a, b = _loop_span(s, starts, line)
        owners = [f for f in funcs if f[1] <= line <= f[2]]
        # innermost containing function (a loop's own function, not main around it)
        owner = min(owners, key=lambda f: f[2] - f[1])[0] if owners else ""
        in_excl = any(n in excluded and fa <= line <= fb for n, fa, fb in funcs)
        rows.append({
            "type": r["typ"].lower(), "line": line, "end": b, "name": r["name"],
            "function": r["name"] if r["typ"] == "FUNCTION" else owner,
            "share": r["avr"] / total, "seconds": r["avr"], "hotness": r["hotness"],
            "excluded": in_excl,
            "in_main": owner == "main" and r["name"] != "main",
            "in_timed_region": any(wa <= line <= wb for wa, wb in windows),
        })
    return rows


def _contains(outer: dict, inner: dict) -> bool:
    return outer is not inner and outer["line"] <= inner["line"] and inner["end"] <= outer["end"] \
        and (outer["line"], outer["end"]) != (inner["line"], inner["end"])


def threshold_effect(rows: List[dict], t: float) -> dict:
    """What a share floor t removes from the in-scope loops, and the Amdahl bound on its cost."""
    loops = [r for r in rows if r["type"] == "loop" and not r["excluded"] and r["share"] > 0]
    kept = [r for r in loops if r["share"] >= t]
    dropped = [r for r in loops if r["share"] < t]
    # Time that is really given up: a dropped loop that no kept loop contains (a kept outer
    # loop covers it) and no other dropped loop contains (its time is already counted).
    free = [d for d in dropped
            if not any(_contains(k, d) for k in kept)
            and not any(_contains(o, d) for o in dropped)]
    lost = min(sum(d["share"] for d in free), 0.999)
    return {"loops_in_scope": len(loops), "dropped": len(dropped),
            "dropped_uncovered": len(free),
            "max_dropped_share": max((d["share"] for d in dropped), default=0.0),
            "lost_share_bound": lost,
            "max_speedup_lost": 1.0 / (1.0 - lost)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--benchmarks", default="", help="comma list of suite/name (default: all packaged)")
    ap.add_argument("--no-verify-size", action="store_true", help="measure the agent size only")
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--bin-dir", default=str(Path(sys.executable).parent),
                    help="directory holding discopop_hotspot_cc/cxx/analyzer")
    a = ap.parse_args()

    sizes = json.loads(SIZES_FILE.read_text()) if SIZES_FILE.exists() else {}
    sizes = sizes.get("kernels", sizes)
    metas = sorted(PREPARED.glob("*/*/meta.json"))
    wanted = {x for x in a.benchmarks.split(",") if x}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    all_rows: List[dict] = []
    summary: Dict[str, dict] = {}
    for m in metas:
        name = f"{m.parent.parent.name}/{m.parent.name}"
        if wanted and name not in wanted:
            continue
        meta = json.loads(m.read_text())
        text = (m.parent / meta["file"]).read_text()
        excluded = list(meta.get("exclude_functions") or [])
        vsize = (sizes.get(name) or {}).get("verification_size")
        runs = [("agent", None)] + ([] if a.no_verify_size or not vsize else [("verify", vsize)])
        summary[name] = {"excluded_functions": excluded}
        for label, size in runs:
            regions, note, secs = measure(m.parent, meta, size, Path(a.bin_dir), a.timeout)
            if regions is None:
                print(f"{name:28s} {label:6s} FAILED {note}", flush=True)
                summary[name][label] = {"error": note}
                continue
            rows = analyse(text, regions, excluded)
            for r in rows:
                all_rows.append({"benchmark": name, "size_label": label, "size": size or "default", **r})
            in_scope = [r for r in rows if not r["excluded"] and r["share"] > 0]
            main_rows = [r for r in rows if r["in_main"]]
            kernel = max((r for r in in_scope if r["name"] != "main"), key=lambda r: r["share"], default=None)
            summary[name][label] = {
                "size": size or "default", "seconds": round(secs, 2),
                "regions": len(rows), "in_scope": len(in_scope),
                "top_region": {"line": kernel["line"], "type": kernel["type"], "name": kernel["name"],
                               "function": kernel["function"], "share": kernel["share"]} if kernel else None,
                "main": {
                    "loops": len([r for r in main_rows if r["type"] == "loop"]),
                    "loops_in_timed_region": len([r for r in main_rows if r["type"] == "loop" and r["in_timed_region"]]),
                    "max_loop_share_outside_timed_region": max(
                        (r["share"] for r in main_rows if r["type"] == "loop" and not r["in_timed_region"]), default=0.0),
                    "max_loop_share_inside_timed_region": max(
                        (r["share"] for r in main_rows if r["type"] == "loop" and r["in_timed_region"]), default=0.0),
                },
                "thresholds": {str(t): threshold_effect(rows, t) for t in THRESHOLDS},
            }
            s5 = summary[name][label]["thresholds"]["0.05"]
            print(f"{name:28s} {label:6s} {size or 'default':10s} {secs:6.1f}s  in-scope {len(in_scope):3d}  "
                  f"top {kernel['share']*100 if kernel else 0:5.1f}%  @5%: drop {s5['dropped']:2d}, "
                  f"lost ≤ {s5['lost_share_bound']*100:4.1f}%", flush=True)

    fields: List[str] = []
    for r in all_rows:
        fields += [k for k in r if k not in fields]
    with (out / "regions.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_rows)
    (out / "summary.json").write_text(json.dumps({
        "study": "T0.5 runtime share per region", "host": platform.node(),
        "thresholds": THRESHOLDS, "benchmarks": summary}, indent=2))
    print(f"wrote {out / 'regions.csv'} and {out / 'summary.json'}")


if __name__ == "__main__":
    main()
