#!/usr/bin/env python3
"""What DiscoPoP reports on the programs the agent shipped — no model.

For every archived trial of the given runs and arm whose shipped benchmark file differs from the original, the
file WITHOUT its OpenMP directives is profiled the way the harness profiles a package (`cli.profile_once`:
instrument, run, explore), and the loops DiscoPoP reports as Do-All are listed beside the directives the trial
shipped, loop by loop in the order of the file.

Written for DiscoPoP B14 (7 Oct 2026; `discopop_agent/docs/DISCOPOP_BUG_REPORTS.md`): the profiler modelled two
loops side by side inside a loop as nested in each other, so the second loop of a split never got its Do-All.
Run once with the profiler as it was and once with the fix, on the same archived programs, the two result files
say on how many of the agent's programs DiscoPoP now reports more loops — the size of what a re-run could
change. The manifest records which profiler build answered (the digest of the installed pass).

    venv/bin/python evaluation/agent/tools/doall_replay.py --runs e2v6_agent_1,e2v6_agent_2 \\
        --arm full_b1_nospeed_v4 --out evaluation/agent/runs/b14_replay_before/full_b1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "shared"))
sys.path.insert(0, str(REPO))
import campaign  # noqa: E402
import cli  # noqa: E402
import harness_include  # noqa: E402
harness_include.install()   # every build finds prepared/_harness (D39)

PRAGMA = re.compile(r"\s*#\s*pragma\s+omp\b")
LOOP = re.compile(r"\s*(for|while)\s*\(")
REPETITION = re.compile(r"\s*for\s*\(\s*(?:int\s+)?nl\b")


def pass_digest() -> Optional[str]:
    """sha256 of the installed DiscoPoP pass (the library the wrappers load) — which profiler build answered."""
    hits = sorted((REPO / "venv").glob("lib/python*/site-packages/**/LLVMDiscoPoP*"))
    hits = [h for h in hits if h.is_file()]
    return hashlib.sha256(hits[0].read_bytes()).hexdigest() if hits else None


def loop_lines(text: str) -> List[int]:
    """1-based lines of the loop headers of a file, the repetition loop left out."""
    return [n for n, ln in enumerate(text.split("\n"), 1) if LOOP.match(ln) and not REPETITION.match(ln)]


def shipped_directives(text: str) -> List[bool]:
    """For every loop of the shipped file (repetition loop left out): does a directive stand directly above it?"""
    lines = text.split("\n")
    out: List[bool] = []
    for n in loop_lines(text):
        k = n - 2
        while k >= 0 and not lines[k].strip():
            k -= 1
        out.append(k >= 0 and bool(PRAGMA.match(lines[k])))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, help="comma-separated archived runs")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--limit", type=int, default=0, help="stop after this many profiled programs (a smoke test)")
    a = ap.parse_args()

    runs = [r for r in a.runs.split(",") if r]
    trials: List[Path] = []
    for run in runs:
        root = campaign.find_run(run)
        if root is None:
            sys.exit(f"run {run} is not in the archive")
        trials += [p.parent for p in sorted(root.glob(f"benchmarks/*/*/{a.arm}/*/rep*/trial.json"))]
    a.out.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    manifest: Dict[str, Any] = {"tool": "doall_replay.py", "commit": head, "host": platform.node(),
                                "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "runs": runs, "arm": a.arm,
                                "trials": len(trials), "discopop_pass_sha256": pass_digest()}
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"{len(trials)} trial(s); DiscoPoP pass {str(manifest['discopop_pass_sha256'])[:12]}")
    results = a.out / "results.jsonl"
    done = set()
    if results.exists():
        done = {json.loads(ln)["trial"] for ln in results.read_text().splitlines() if ln.strip()}
    benches = cli._prepared_benchmarks()
    profiled = 0
    for i, d in enumerate(trials, 1):
        if a.limit and profiled >= a.limit:
            break
        t = json.loads((d / "trial.json").read_text())
        key = str(d.relative_to(campaign.RESULTS))
        if key in done or int(t.get("llm_call_failures") or 0) > 0:
            continue
        editable = list(t.get("editable") or [])
        rec: Dict[str, Any] = {"trial": key, "benchmark": t.get("benchmark"), "arm": t.get("arm"),
                               "repeat": t.get("repeat"), "harness_outcome": t.get("outcome")}
        if len(editable) != 1 or not (d / "final" / editable[0]).is_file():
            rec["verdict"] = "not-checked"
        elif (d / "final" / editable[0]).read_text() == (d / "original" / editable[0]).read_text():
            rec["verdict"] = "unchanged"
        else:
            name = editable[0]
            final = (d / "final" / name).read_text()
            bare = "\n".join(ln for ln in final.split("\n") if not PRAGMA.match(ln))
            t0 = time.time()
            with tempfile.TemporaryDirectory(prefix="doall_replay_") as tmp:
                pkg = Path(tmp) / "package"
                shutil.copytree(d / "final", pkg)
                (pkg / name).write_text(bare)
                shutil.copy2(benches[str(t.get("benchmark"))] / "meta.json", pkg / "meta.json")
                dest = Path(tmp) / "profile"
                prof = cli.profile_once(pkg, name, dest, REPO, a.timeout)
                rec["shipped"] = shipped_directives(final)
                rec["loops"] = len(loop_lines(bare))
                if prof.get("error"):
                    rec.update(verdict="profile-failed", error=str(prof["error"])[:400])
                else:
                    pats = json.loads((dest / ".discopop" / "explorer" / "patterns.json").read_text())["patterns"]
                    mapping = (dest / ".discopop" / "FileMapping.txt").read_text().splitlines()
                    fid = next((ln.split("\t")[0] for ln in mapping if ln.rstrip().endswith("/" + name)), "1")

                    def starts(kind: str) -> List[int]:
                        return sorted(int(str(p["start_line"]).split(":")[1]) for p in pats.get(kind, [])
                                      if str(p["start_line"]).split(":")[0] == fid)

                    do_all, reduction = starts("do_all"), starts("reduction")
                    rec["doall"] = [n in do_all for n in loop_lines(bare)]
                    rec["reduction"] = [n in reduction for n in loop_lines(bare)]
                    rec["verdict"] = "profiled"
            profiled += 1
            rec["seconds"] = round(time.time() - t0, 1)
        with results.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[{i}/{len(trials)}] {rec['benchmark']} rep{rec['repeat']} ({rec['harness_outcome']}): {rec['verdict']}"
              + (f"  shipped {sum(rec['shipped'])} of {rec['loops']} loops, Do-All now {sum(rec['doall'])}"
                 if rec["verdict"] == "profiled" else ""), flush=True)
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
