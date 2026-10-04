#!/usr/bin/env python3
"""The prototype trees as a scratch SUITE the harness's no-model tools can read: prepared/_c2proto/<loop>/
(git-ignored, never registered) — the three files of the form with the repetition loop inside the function,
and a meta.json taken from the clean package's. Run from evaluation/agent:

    venv/bin/python c2_suite.py PROBE_DIR [--arrays]
"""
import json
import shutil
import sys
from pathlib import Path

probe = Path(sys.argv[1]).resolve()
arrays = "--arrays" in sys.argv
tree, suite = ("c2arr", "_c2arrproto") if arrays else ("c2", "_c2proto")
out = Path("prepared") / suite
shutil.rmtree(out, ignore_errors=True)
man = json.loads((probe / "manifest.json").read_text())
if arrays:      # the arrays variant's measurement headers sit beside the others
    (Path("prepared") / "_harness" / "arr").mkdir(parents=True, exist_ok=True)
n_done = 0
for n, row in man["loops"].items():
    if tree not in row["variants"]:
        continue
    d = out / n
    d.mkdir(parents=True)
    for f in (probe / tree / n / "orig").iterdir():
        shutil.copy2(f, d / f.name)
    if arrays:
        shutil.copy2(probe / "_h" / "arr" / f"{n}.h", Path("prepared") / "_harness" / "arr" / f"{n}.h")
    meta = json.loads((Path("prepared") / "tsvc_c1" / n / "meta.json").read_text())
    meta["suite"] = suite
    meta["exclude_functions"] = ["main", "dummy"]
    meta["generator_version"] = "prototype"
    meta.pop("hot_loop", None)
    meta.pop("output_sha256", None)
    (d / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    n_done += 1
print(f"{n_done} packages → {out}")
