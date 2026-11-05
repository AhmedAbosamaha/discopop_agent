#!/usr/bin/env python3
"""E11 — NPB's own verification of every judged program at a SECOND class (no model; record §6, 5 Nov).

The harness judges a program at the verification size against the sequential original, and NPB's verdict at that
class is one of the values it compares. NAS programs read no input, so the harness's second input does not exist
for them (a limit stated in the design); in its place this builds each program's final files at another class
and runs it once at 12 threads: NPB's verification compares the result with NPB's published reference values for
that class. One line per program in `<out>/results.jsonl`: built, ran, NPB's verdict.

    venv/bin/python evaluation/agent/results/E11_repoomp/analysis/second_class.py --sizes ep=EXTRALARGE,cg=LARGE \
        --runs e11_r1,e11_r2,e11_ref_check --out evaluation/agent/runs/e11_second_class

The second class is the other of NPB's classes A and B (those RepoOMP measured): the harness judges EP at class W
and CG at class B (T0.1, e11_t0_1_sizes), so EP is checked at class B (EXTRALARGE) and CG at class A (LARGE).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
import campaign  # noqa: E402
import harness_include  # noqa: E402
harness_include.install()

VERDICT = re.compile(r"Benchmark Completed \(class (\w), verification (SUCCESSFUL|UNSUCCESSFUL)\)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--sizes", required=True,
                    help="per program the dataset macro of the second class, e.g. ep=EXTRALARGE,cg=LARGE")
    ap.add_argument("--threads", type=int, default=12)
    ap.add_argument("--cc", default="clang-20")
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    sizes = dict(x.split("=", 1) for x in a.sizes.split(",") if x)
    res_path = a.out / "results.jsonl"
    done = {json.loads(x)["trial"] for x in res_path.read_text().splitlines() if x.strip()} if res_path.exists() else set()
    (a.out / "manifest.json").write_text(json.dumps({"tool": "second_class.py", "runs": a.runs, "sizes": sizes,
                                                    "threads": a.threads, "cc": a.cc,
                                                    "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, indent=1) + "\n")
    for run in [r for r in a.runs.split(",") if r]:
        root = campaign.find_run(run)
        if root is None:
            sys.exit(f"run {run} is not in the archive")
        for tj in sorted(root.glob("benchmarks/npbc_c1/*/*/*/rep*/trial.json")):
            t = json.loads(tj.read_text())
            key = str(tj.parent.relative_to(campaign.RESULTS))
            if key in done:
                continue
            final = tj.parent / "final"
            meta_p = tj.parent / "original" / "meta.json"      # a trial keeps the program's files, not always meta.json
            if not meta_p.exists():
                meta_p = TOOLS.parent / "prepared" / str(t.get("benchmark")) / "meta.json"
            rec: Dict[str, Any] = {"trial": key, "benchmark": t.get("benchmark"), "arm": t.get("arm"),
                                   "model": t.get("model"), "repeat": t.get("repeat"), "harness_outcome": t.get("outcome")}
            size = sizes.get(str(t.get("benchmark", "")).split("/")[-1])
            rec["size"] = size
            if size is None:
                rec["verdict"] = "no-second-class-given"
            elif not final.is_dir():
                rec["verdict"] = "no-final-files"
            else:
                meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
                proj = meta.get("project") or {}
                units: List[str] = list(proj.get("units") or [])
                with tempfile.TemporaryDirectory(prefix="e11_second_") as tmp:
                    exe = Path(tmp) / "prog"
                    cmd = [a.cc, "-O2", f"-D{size}_DATASET", *[str(final / u) for u in units],
                           *[f"-I{final / d}" for d in proj.get("include_dirs") or ["."]],
                           *(proj.get("cflags") or []), "-o", str(exe), "-lm"]
                    b = subprocess.run(cmd, capture_output=True, text=True)
                    if b.returncode != 0:
                        rec.update(verdict="does-not-build", stderr=b.stderr[-600:])
                    else:
                        t0 = time.time()
                        try:
                            r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=a.timeout,
                                               env={**os.environ, "OMP_NUM_THREADS": str(a.threads)})
                            m = VERDICT.search(r.stderr)
                            rec.update(exit=r.returncode, seconds=round(time.time() - t0, 2),
                                       npb_class=m.group(1) if m else None,
                                       verdict=(m.group(2) if m else "no-verdict-printed"))
                        except subprocess.TimeoutExpired:
                            rec.update(verdict="timeout", seconds=a.timeout)
            with res_path.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            print(f"{rec['benchmark']} {rec['arm']} rep{rec['repeat']} ({rec['harness_outcome']}): {rec['verdict']}",
                  flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
