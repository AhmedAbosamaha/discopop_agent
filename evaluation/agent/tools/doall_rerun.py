#!/usr/bin/env python3
"""What does the CURRENT explorer say on a run's own profiles? (no model; a DiscoPoP fix's check)

A DiscoPoP fix in the explorer (B4, B9, B10, B13, ...) changes the verdicts a run recorded on profiles it
already took. This re-runs the checkout's `discopop_explorer` on a COPY of each profile of the given runs
(`runs/<run>/profiles/<suite>/<name>/.discopop`, the run's own draw; the profile trees stay on the
machine that ran them, so run this there) and compares, per profile, the Do-All loops (start lines, with
`applicable_pattern`) and the blockers (`doall_prevented.json`: loop, dependence type, variable) with what
the run's explorer wrote. A stalled explorer is retried (L5: a stall is a draw), up to `--attempts`.

    venv/bin/python evaluation/agent/tools/doall_rerun.py t0_11_b1_a t0_11_b1_b [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

AGENT_DIR = Path(__file__).resolve().parent.parent
RUNS = AGENT_DIR / "runs"
EXPLORER = Path(sys.executable).parent / "discopop_explorer"


def verdicts(dp: Path) -> Tuple[Set[str], Set[Tuple[Any, str, str]]]:
    pats = json.loads((dp / "explorer" / "patterns.json").read_text()).get("patterns", {})
    doall = {str(p.get("start_line")) for p in pats.get("do_all") or [] if str(p.get("applicable_pattern")) == "True"}
    prev = dp / "explorer" / "doall_prevented.json"
    blockers = {(r.get("loop_start"), str(r.get("dep_type", "")).replace("DepType.", ""), str(r.get("var_name")))
                for r in (json.loads(prev.read_text()) if prev.exists() else [])}
    return doall, blockers


def rerun(dp: Path, timeout: int, attempts: int) -> Path:
    """The explorer on a copy of `dp`'s profile; returns the copy's .discopop."""
    work = Path(tempfile.mkdtemp(prefix="doall_rerun_"))
    copy = work / ".discopop"
    shutil.copytree(dp, copy, ignore=shutil.ignore_patterns("explorer"))
    for k in range(1, attempts + 1):
        with open(work / "explorer.log", "w") as log:
            p = subprocess.Popen([str(EXPLORER)], cwd=copy, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                rc = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, 9)
                p.wait()
                shutil.rmtree(copy / "explorer", ignore_errors=True)
                continue
        if rc == 0 and (copy / "explorer" / "patterns.json").exists():
            return copy
        shutil.rmtree(copy / "explorer", ignore_errors=True)
    raise RuntimeError(f"{dp}: the explorer did not finish in {attempts} attempt(s)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--attempts", type=int, default=5)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    rows: List[Dict[str, Any]] = []
    for run_id in a.runs:
        for dp in sorted((RUNS / run_id / "profiles").glob("*/*/.discopop")):
            bench = f"{dp.parent.parent.name}/{dp.parent.name}"
            old_doall, old_block = verdicts(dp)
            copy = rerun(dp, a.timeout, a.attempts)
            new_doall, new_block = verdicts(copy)
            shutil.rmtree(copy.parent, ignore_errors=True)
            rows.append({"run": run_id, "benchmark": bench,
                         "doall_lost": sorted(old_doall - new_doall), "doall_gained": sorted(new_doall - old_doall),
                         "blockers_added": sorted(map(list, new_block - old_block)),
                         "blockers_removed": sorted(map(list, old_block - new_block))})
    lines = [f"# The checkout's explorer on the profiles of {', '.join(a.runs)}", "",
             "| benchmark | draw | Do-All lost | Do-All gained | blockers added | blockers removed |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        fmt = lambda xs: ", ".join(str(x) for x in xs) or "—"  # noqa: E731
        lines.append(f"| `{r['benchmark']}` | {r['run']} | {fmt(r['doall_lost'])} | {fmt(r['doall_gained'])} "
                     f"| {fmt(r['blockers_added'])} | {fmt(r['blockers_removed'])} |")
    changed = sum(1 for r in rows if r["doall_lost"] or r["doall_gained"])
    lines += ["", f"{len(rows)} profile(s); Do-All sets changed on {changed}"]
    text = "\n".join(lines) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text)
        a.out.with_suffix(".json").write_text(json.dumps(rows, indent=1) + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
