#!/usr/bin/env python3
"""T0.2 — how much does DiscoPoP's own answer move between profiles of the same program?

Every arm in an experiment is compared on one profile per kernel per run, so the spread
measured here is the reason that rule exists. For each kernel the program is profiled from
scratch `--repeats` times (``discopop_cc`` → instrumented run → ``discopop_explorer``) and
each profile is reduced to:

* ``patterns_sha``    sha1 of ``explorer/patterns.json`` — DiscoPoP's suggestions
* ``patterns``        how many suggestions, in total and per pattern type
* ``blockers``        entries in ``explorer/doall_prevented.json`` — why loops are not Do-All
* ``deps_sha``        sha1 of ``profiler/dynamic_dependencies.txt`` as written
* ``deps_masked_sha`` the same file with memory-region ids and ``@`` callpath numbers masked
  and lines sorted — a WEAK measure, kept for comparison: DiscoPoP may group the same
  dependences into a different number of lines, which changes this hash although no
  dependence changed (measured on floyd-warshall)
* ``deps_triples_sha`` every dependence as (sink, type, source, variable) without the per-run
  labels, counted — the dependence FACTS, independent of grouping and labelling

Measured over six kernels (2026-09-16, THESIS_EXPERIMENTS.md §7): ``deps_triples_sha`` was
identical across profiles of a kernel, while ``patterns_sha`` differed in every one of 60
profiles and the suggestion count moved by up to a factor of three (2mm 27–78). So the split
this tool reports is: the dependences DiscoPoP OBSERVES are deterministic, what it REPORTS
from them is not.

    numactl --cpunodebind=1 --membind=1 ~/discopop_agent/venv/bin/python \
        agent/tools/profile_stability.py --out agent/runs/t0_2_stability

Writes ``profiles.csv`` (one row per profile) and ``summary.json`` (per kernel: how many
distinct values of each, and the range of suggestion and blocker counts) into ``--out``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import tempfile
import time
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
import bench as bench_tools  # noqa: E402
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

AGENT_DIR = Path(__file__).resolve().parent.parent
PREPARED = AGENT_DIR / "prepared" / "polybench"
# The PolyBench kernels of the core ten (kernel_groups.json); applications join once packaged.
CORE_TEN_KERNELS = ["2mm", "jacobi-2d-imper", "floyd-warshall", "seidel-2d", "trisolv", "lu"]
# Per-run labels, not facts: (S-123) / (4549325885) memory regions, @17 callpath states.
_ID_RE = re.compile(r"\(S?-?\d+\)")
_STATE_RE = re.compile(r"@\d+")


def _sha(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def _masked(path: Path) -> str:
    """The dependence file without its per-run labels: ids masked, lines sorted."""
    if not path.exists():
        return ""
    lines = sorted(_STATE_RE.sub("@#", _ID_RE.sub("(#)", ln)) for ln in path.read_text().splitlines())
    return _sha("\n".join(lines))


def _triples(path: Path) -> str:
    """Every dependence as (sink, type, source, variable), counted, without per-run labels.

    A whole-line hash overstates variation: two profiles of floyd-warshall produced the same
    376 masked lines, differing only in the order of entries within a line and in how one
    sink's dependences were split across lines — no dependence had changed.
    """
    if not path.exists():
        return ""
    counts: Counter[str] = Counter()
    for line in path.read_text().splitlines():
        f = line.split()
        if len(f) < 4 or f[1] != "NOM":
            continue                                   # BGN/END loop markers, not dependences
        sink = _STATE_RE.sub("", f[0])
        rest = f[2:]
        for i in range(0, len(rest) - 1, 2):           # pairs: <type> <source>|<var>(<region>)
            src, _, var = rest[i + 1].partition("|")
            counts[f"{sink} {rest[i]} {_STATE_RE.sub('', src)} {_ID_RE.sub('', var)}"] += 1
    return _sha("\n".join(f"{k}\t{v}" for k, v in sorted(counts.items())))


def _profile_once(work: Path, meta: dict, size: str, env: Dict[str, str], timeout: int) -> Optional[str]:
    """One full profile in `work` (already staged); returns None on success, else which step failed."""
    instrument, unity = bench_tools.wrapper_cmd(work, meta, extra_flags=[f"-D{size}_DATASET"])
    for name, cmd in (("instrument", instrument), ("instrumented run", ["./a.out"])):
        r = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=timeout, env=env)
        if unity is not None and cmd is instrument:
            unity.unlink(missing_ok=True)
        if r.returncode != 0:
            return f"{name}: {(r.stderr or r.stdout)[-160:].strip()}"
    r = subprocess.run(["discopop_explorer"], cwd=work / ".discopop", capture_output=True,
                       text=True, timeout=timeout, env=env)
    if r.returncode != 0:
        return f"explorer: {(r.stderr or r.stdout)[-160:].strip()}"
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--kernels", default=",".join(CORE_TEN_KERNELS))
    ap.add_argument("--repeats", type=int, default=10)
    ap.add_argument("--size", default="SMALL", help="dataset profiled at — the agent's size (default: SMALL)")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds per profiling step")
    _inside = AGENT_DIR.parent.parent                      # evaluation/ lives inside the agent repository
    _repo = _inside if (_inside / "discopop_agent" / "__main__.py").exists() else _inside / "discopop_agent"
    ap.add_argument("--agent-repo", default=os.environ.get("AGENT_REPO", str(_repo)),
                    help="agent checkout whose venv provides discopop_cc and discopop_explorer")
    a = ap.parse_args()

    # The tools come from the agent's venv, as they do for a trial: a detached job does not
    # inherit an interactive PATH, and the first attempt died on `discopop_cc` not found.
    venv_bin = Path(a.agent_repo).resolve() / "venv" / "bin"
    if not (venv_bin / "discopop_cc").exists():
        raise SystemExit(f"discopop_cc not found in {venv_bin} — pass --agent-repo")
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(venv_bin), str(Path.home() / ".local" / "bin"),
                                   env.get("PATH", "")])
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for kernel in [k for k in a.kernels.split(",") if k]:
        meta = json.loads((PREPARED / kernel / "meta.json").read_text())
        for i in range(1, a.repeats + 1):
            work = Path(tempfile.mkdtemp(prefix=f"dp_t02_{kernel}_"))
            bench_tools.stage(PREPARED / kernel, work, meta)
            t0 = time.perf_counter()
            try:
                failure = _profile_once(work, meta, a.size, env, a.timeout)
            except subprocess.TimeoutExpired:
                failure = f"timed out after {a.timeout} s"
            seconds = round(time.perf_counter() - t0, 1)
            dp = work / ".discopop"
            patterns_file, blockers_file = dp / "explorer" / "patterns.json", dp / "explorer" / "doall_prevented.json"
            per_type: Dict[str, int] = {}
            total = blockers = None
            if patterns_file.exists():
                pj = json.loads(patterns_file.read_text())
                pj = pj.get("patterns", pj)
                per_type = {k: len(v) for k, v in pj.items() if isinstance(v, list) and v}
                total = sum(per_type.values())
            if blockers_file.exists():
                blockers = len(json.loads(blockers_file.read_text()))
            deps = dp / "profiler" / "dynamic_dependencies.txt"
            rows.append({
                "kernel": kernel, "profile": i, "seconds": seconds, "failure": failure or "",
                "patterns_sha": _sha(patterns_file.read_text()) if patterns_file.exists() else "",
                "patterns": total, "patterns_by_type": json.dumps(per_type, sort_keys=True),
                "blockers": blockers,
                "deps_sha": _sha(deps.read_text()) if deps.exists() else "",
                "deps_masked_sha": _masked(deps),
                "deps_triples_sha": _triples(deps),
            })
            print(f"{kernel:18s} {i:3d}/{a.repeats}  {seconds:7.1f}s  patterns={total} "
                  f"blockers={blockers}  {failure or ''}", flush=True)
            shutil.rmtree(work, ignore_errors=True)

    with (out / "profiles.csv").open("w", newline="") as f:
        fields: List[str] = []
        for row in rows:
            fields += [k for k in row if k not in fields]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    summary: Dict[str, Any] = {}
    for kernel in {r["kernel"] for r in rows}:
        rs = [r for r in rows if r["kernel"] == kernel and not r["failure"]]
        counts = [r["patterns"] for r in rs if r["patterns"] is not None]
        blocks = [r["blockers"] for r in rs if r["blockers"] is not None]
        summary[kernel] = {
            "profiles": len(rs),
            "failures": sum(1 for r in rows if r["kernel"] == kernel and r["failure"]),
            "distinct_patterns_sha": len({r["patterns_sha"] for r in rs}),
            "distinct_deps_sha": len({r["deps_sha"] for r in rs}),
            "distinct_deps_masked_sha": len({r["deps_masked_sha"] for r in rs}),
            "distinct_deps_triples_sha": len({r["deps_triples_sha"] for r in rs}),
            "patterns_min": min(counts) if counts else None,
            "patterns_max": max(counts) if counts else None,
            "blockers_distribution": dict(sorted(Counter(blocks).items())),
            "median_profile_seconds": sorted(r["seconds"] for r in rs)[len(rs) // 2] if rs else None,
        }
    (out / "summary.json").write_text(json.dumps({
        "study": "T0.2 DiscoPoP profile stability",
        "repeats": a.repeats, "dataset": a.size, "host": platform.node(),
        "started": started, "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": ("deps_triples_sha counts every dependence as (sink, type, source, variable) without "
                 "per-run labels: one distinct value means the observed dependences did not change. "
                 "deps_masked_sha is the weaker line-level measure and can differ from regrouping alone"),
        "kernels": summary,
    }, indent=2))
    print(f"wrote {out / 'profiles.csv'} and {out / 'summary.json'}")


if __name__ == "__main__":
    main()
