#!/usr/bin/env python3
"""T0.7 — is DiscoPoP's explorer deterministic on ONE fixed profile?

Each benchmark is profiled once, exactly as the harness profiles it (``bench.py``: one file,
or a project through its unity unit), and then ``discopop_explorer`` is run ``--repeats``
times on that same profile — with the hash seed free, and again with ``PYTHONHASHSEED``
fixed to each value in ``--seeds``. The profile is never touched between runs; only the
explorer's output directory is removed. For every run the tool records the exit status, the
sha256 of ``patterns.json`` (with the counter-assigned ``pattern_id`` removed, and the
explorer's other outputs — including its pattern-id counter — cleared before every run),
the count per pattern type, and the crash message if any.

Output: ``runs.csv`` (one row per explorer run), ``sets/`` (one canonical copy of every
distinct Do-All and reduction set seen, named by its digest), ``summary.json`` (per benchmark: distinct
pattern SETS and distinct files — the explorer writes the same patterns in a different order
on every run — crash count, Do-All min/max, task min/max), and ``run.log``.

    ~/discopop_agent/venv/bin/python agent/tools/explorer_determinism.py \\
        --out agent/runs/t0_7_explorer --benchmarks polybench/2mm,rodinia-3.1/pathfinder --repeats 20

First taken by hand on the Mac (THESIS_EXPERIMENTS.md §5b, 2026-09-16); this tool makes the
repeat reproducible.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench as bench_tools  # noqa: E402

AGENT_DIR = Path(__file__).resolve().parents[1]
PREPARED = AGENT_DIR / "prepared"


def _run(cmd: List[str], cwd: Path, env: Dict[str, str], timeout: float) -> tuple[int, str, float]:
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)[-2000:], time.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return -9, "timeout", time.perf_counter() - t0


def _reset_to_profile(dp: Path) -> None:
    """Remove everything the explorer (and the patch generator it runs) wrote, so every run
    starts from the pristine profile — including `next_free_pattern_id.txt`, whose counter
    would otherwise give every run different pattern ids and make every output 'distinct'."""
    for p in dp.iterdir():
        if p.name in PROFILE_PARTS:
            continue
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        else:
            p.unlink(missing_ok=True)


def _canonical(raw: bytes, order: bool) -> bytes:
    """patterns.json with the per-run labels removed (counter-assigned pattern ids, task group
    numbers). With ``order=False`` the
    patterns of each type and every list inside a pattern (clauses, CU ids, …) are sorted
    as well, so two outputs that differ only in ORDER hash the same: the explorer writes
    the same set of patterns in a different order on every run (found on `vecsum`)."""
    data = json.loads(raw)
    for kind, items in data.get("patterns", {}).items():
        for item in items:
            item.pop("pattern_id", None)
            item.pop("task_group", None)     # group numbers are assigned in traversal order too
            if not order:
                for k, v in item.items():
                    if isinstance(v, list):
                        item[k] = sorted(v, key=json.dumps)
        if not order:
            data["patterns"][kind] = sorted(items, key=lambda it: json.dumps(it, sort_keys=True))
    return json.dumps(data, sort_keys=True).encode()


def _kind_digests(raw: bytes) -> Dict[str, str]:
    """One digest per pattern type over the SET of its patterns (labels and order removed):
    the Do-All and reduction sets are what the agent consumes; task patterns are not."""
    data = json.loads(_canonical(raw, order=False))
    return {kind: hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()
            for kind, items in data.get("patterns", {}).items()}


def _explore(work: Path, env: Dict[str, str], timeout: float, keep_sets: Optional[Path] = None,
             name: str = "") -> dict:
    _reset_to_profile(work / ".discopop")
    rc, tail, secs = _run(["discopop_explorer"], work / ".discopop", env, timeout)
    rec: dict = {"rc": rc, "seconds": round(secs, 2), "sha256": "", "sha256_ordered": "",
                 "kind_sha256": {}, "counts": {}, "error": ""}
    patterns = work / ".discopop" / "explorer" / "patterns.json"
    if rc == 0 and patterns.exists():
        raw = patterns.read_bytes()
        rec["sha256"] = hashlib.sha256(_canonical(raw, order=False)).hexdigest()   # the SET of patterns
        rec["sha256_ordered"] = hashlib.sha256(_canonical(raw, order=True)).hexdigest()
        rec["kind_sha256"] = _kind_digests(raw)
        if keep_sets is not None:
            # one canonical copy per distinct Do-All / reduction set, so a difference between
            # runs can be read (which loop, which clause) instead of only counted
            data = json.loads(_canonical(raw, order=False))["patterns"]
            for kind in ("do_all", "reduction"):
                f = keep_sets / f"{name.replace('/', '_')}__{kind}__{rec['kind_sha256'][kind][:12]}.json"
                if not f.exists():
                    f.write_text(json.dumps(data.get(kind, []), indent=1, sort_keys=True) + "\n")
        rec["counts"] = {k: len(v) for k, v in json.loads(raw).get("patterns", {}).items()}
    else:
        lines = [l for l in tail.strip().splitlines() if l.strip()]
        rec["error"] = (lines[-1] if lines else f"rc={rc}")[:200]
    return rec


def study(name: str, bench: Path, repeats: int, seeds: List[str], timeout: float,
          log, keep_sets: Optional[Path] = None) -> tuple[List[dict], Optional[str]]:
    meta = bench_tools.load_meta(bench)
    rows: List[dict] = []
    with tempfile.TemporaryDirectory(prefix="t07_") as tmp:
        work = bench_tools.stage(bench, Path(tmp) / "src", meta)
        env = dict(os.environ)
        env["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{env.get('PATH', '')}"
        env.pop("PYTHONHASHSEED", None)
        instrument, unity = bench_tools.wrapper_cmd(work, meta)
        for cmd, cwd in ((instrument, work), (["./a.out"], work)):
            rc, tail, secs = _run(cmd, cwd, env, timeout)
            if unity is not None and cmd is instrument:
                unity.unlink(missing_ok=True)
            print(f"  {cmd[0]}: rc={rc} {secs:.1f}s", file=log, flush=True)
            if rc != 0:
                return rows, f"{cmd[0]} failed: {tail[-300:]}"
        profile_sha = _tree_sha(work / ".discopop")
        for seed in [None, *seeds]:
            e = dict(env)
            e["PYTHONHASHSEED"] = ""     # unset below; a harness PYTHONHASHSEED must not leak in
            e.pop("PYTHONHASHSEED")
            if seed is not None:
                e["PYTHONHASHSEED"] = seed
            for i in range(1, repeats + 1):
                rec = _explore(work, e, timeout, keep_sets, name)
                rec.update({"benchmark": name, "seed": seed if seed is not None else "free", "run": i,
                            "profile_sha256": profile_sha})
                rows.append(rec)
                print(f"  seed={rec['seed']} run {i}: rc={rec['rc']} {rec['seconds']}s "
                      f"{rec['sha256'][:10]} {rec['counts'] or rec['error']}", file=log, flush=True)
                # The PROFILE (what the profiler wrote) must be untouched between runs, or the
                # runs are not comparable. The explorer's own outputs — explorer/,
                # patch_generator/, patch_applicator/, line_mapping.json,
                # next_free_pattern_id.txt — are what varies and are not part of it.
                if _tree_sha(work / ".discopop") != profile_sha:
                    return rows, "the explorer modified the profiler's output between runs"
    return rows, None


PROFILE_PARTS = ("profiler", "FileMapping.txt")     # what the profiler wrote; the rest is the explorer's


def _tree_sha(root: Path) -> str:
    """Digest of the profiler's output under `.discopop` (not the explorer's)."""
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p.is_file() and rel.parts[0] in PROFILE_PARTS:
            h.update(str(rel).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def summarise(rows: List[dict]) -> dict:
    out: dict = {}
    for r in rows:
        key = r["benchmark"]
        for seed_key in ("all", f"seed={r['seed']}"):
            s = out.setdefault(key, {}).setdefault(seed_key, {
                "runs": 0, "crashed": 0, "distinct_outputs": set(), "distinct_ordered": set(),
                "distinct_sets_by_kind": {}, "do_all": [], "task": [], "reduction": [], "errors": {}})
            s["runs"] += 1
            if r["rc"] != 0:
                s["crashed"] += 1
                s["errors"][r["error"]] = s["errors"].get(r["error"], 0) + 1
            else:
                s["distinct_outputs"].add(r["sha256"])
                s["distinct_ordered"].add(r["sha256_ordered"])
                for kind, h in r["kind_sha256"].items():
                    s["distinct_sets_by_kind"].setdefault(kind, set()).add(h)
                for k in ("do_all", "task", "reduction"):
                    s[k].append(r["counts"].get(k, 0))
    for key in out:
        for seed_key, s in out[key].items():
            s["distinct_outputs"] = len(s["distinct_outputs"])       # distinct SETS of patterns
            s["distinct_ordered"] = len(s["distinct_ordered"])       # distinct files (order counts)
            s["distinct_sets_by_kind"] = {k: len(v) for k, v in s["distinct_sets_by_kind"].items()}
            for k in ("do_all", "task", "reduction"):
                vals = s.pop(k)
                s[k] = {"min": min(vals), "max": max(vals)} if vals else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--benchmarks", default="polybench/2mm,rodinia-3.1/pathfinder",
                    help="comma list of suite/name")
    ap.add_argument("--repeats", type=int, default=20, help="explorer runs per seed setting")
    ap.add_argument("--seeds", default="0,7", help="PYTHONHASHSEED values to fix, besides free")
    ap.add_argument("--timeout", type=float, default=1800)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    log = open(out / "run.log", "a")
    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    rows: List[dict] = []
    errors: Dict[str, str] = {}
    seeds = [s for s in a.seeds.split(",") if s]
    for name in [b for b in a.benchmarks.split(",") if b]:
        bench = PREPARED / name
        if not (bench / "meta.json").exists():
            errors[name] = "not packaged"
            continue
        print(f"== {name}", file=log, flush=True)
        print(f"== {name}", flush=True)
        (out / "sets").mkdir(exist_ok=True)
        brows, err = study(name, bench, a.repeats, seeds, a.timeout, log, out / "sets")
        rows.extend(brows)
        if err:
            errors[name] = err
            print(f"   ERROR {err[:160]}", flush=True)
        with open(out / "runs.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["benchmark", "seed", "run", "rc", "seconds", "sha256_set", "sha256_ordered",
                        "sha256_do_all_set", "sha256_reduction_set", "sha256_task_set",
                        "do_all", "task", "reduction", "error", "profile_sha256"])
            for r in rows:
                w.writerow([r["benchmark"], r["seed"], r["run"], r["rc"], r["seconds"], r["sha256"],
                            r["sha256_ordered"], r["kind_sha256"].get("do_all", ""),
                            r["kind_sha256"].get("reduction", ""), r["kind_sha256"].get("task", ""),
                            r["counts"].get("do_all", ""), r["counts"].get("task", ""),
                            r["counts"].get("reduction", ""), r["error"], r["profile_sha256"]])
        summary = {"study": "T0.7 DiscoPoP explorer determinism on one profile", "host": platform.node(),
                   "started": started, "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "repeats": a.repeats, "seeds": seeds, "benchmarks": summarise(rows), "errors": errors}
        (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        for seed_key, s in summarise(brows).get(name, {}).items():
            by_kind = s["distinct_sets_by_kind"]
            print(f"   {seed_key:10s} runs {s['runs']} crashed {s['crashed']} distinct sets "
                  f"{s['distinct_outputs']} (files {s['distinct_ordered']}; do_all sets "
                  f"{by_kind.get('do_all', '-')}, reduction sets {by_kind.get('reduction', '-')}, "
                  f"task sets {by_kind.get('task', '-')}) do_all {s['do_all']} task {s['task']}", flush=True)
    print(f"wrote {out / 'runs.csv'} and summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
