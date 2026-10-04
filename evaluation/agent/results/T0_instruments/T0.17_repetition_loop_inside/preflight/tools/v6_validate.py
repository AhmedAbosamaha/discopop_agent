#!/usr/bin/env python3
"""Does the prototype change the program? Every variant's original at SMALL — the full dump on the shipped and
the perturbed input, and the digest — against the clean layout's (c1, itself byte-identical to v4); every
reference, built with OpenMP at 4 threads, against its original. Run from evaluation/agent:

    venv/bin/python v6_validate.py PROBE_DIR
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, "tools")
import prepare_tsvc as P  # noqa: E402


def build_run(tree: Path, units: List[str], h: Path, out: Path, flags: List[str], args: List[str],
              threads: Optional[int]) -> Tuple[bool, str]:
    omp = []
    if "-fopenmp" in flags and sys.platform == "darwin" and Path("/usr/local/opt/libomp").exists():
        omp = ["-I/usr/local/opt/libomp/include", "-L/usr/local/opt/libomp/lib"]
    r = subprocess.run([P._cc(), "-O2", *P._sysroot(), *flags, *omp, f"-I{tree}", f"-I{h}",
                        *[str(tree / u) for u in units], "-o", str(out), "-lm"], capture_output=True, text=True)
    if r.returncode != 0:
        return False, "build: " + r.stderr[-400:]
    env = dict(os.environ)
    if threads:
        env["OMP_NUM_THREADS"] = str(threads)
    r = subprocess.run([str(out), *args], capture_output=True, text=True, timeout=600, env=env)
    if r.returncode != 0:
        return False, f"run rc={r.returncode}: {r.stderr[-200:]}"
    return True, r.stdout


def main() -> int:
    probe = Path(sys.argv[1]).resolve()
    man = json.loads((probe / "manifest.json").read_text())
    h = probe / "_h"
    bad = 0
    counts: Dict[str, int] = {}
    with tempfile.TemporaryDirectory(prefix="v6val_") as tmp:
        t = Path(tmp)
        for n, row in man["loops"].items():
            base: Dict[str, str] = {}
            for v in ["c1"] + [x for x in row["variants"] if x != "c1"]:
                units = [u.format(loop=n) for u in man["variants"][v]["units"]]
                for tag, flags, args in (("dump", ["-DPB_FULL_DUMP"], []), ("seeded", ["-DPB_FULL_DUMP"], ["7"]),
                                         ("digest", [], [])):
                    ok, out = build_run(probe / v / n / "orig", units, h, t / "o", [*flags, "-DSMALL_DATASET"], args, None)
                    if not ok:
                        print(f"FAIL {n} {v} orig {tag}: {out}"); bad += 1
                        continue
                    if v == "c1":
                        base[tag] = out
                    elif out != base.get(tag):
                        print(f"DIFF {n} {v} orig {tag}: not the clean layout's output"); bad += 1
                    else:
                        counts[v] = counts.get(v, 0) + 1
                    if tag == "digest" or not (probe / v / n / "ref").is_dir():
                        continue
                    ok, ref = build_run(probe / v / n / "ref", units, h, t / "r",
                                        [*flags, "-DSMALL_DATASET", "-fopenmp"], args, 4)
                    if not ok:
                        print(f"FAIL {n} {v} ref {tag}: {ref}"); bad += 1
                    elif P._max_rel(base[tag], ref) > 1e-9:
                        print(f"DIFF {n} {v} ref {tag}: max rel err {P._max_rel(base[tag], ref):.2e}"); bad += 1
                    else:
                        counts[v + ".ref"] = counts.get(v + ".ref", 0) + 1
    print("identical outputs (3 per loop: dump, perturbed dump, digest) / references equal (2 per loop):")
    for k in sorted(counts):
        print(f"  {k:12} {counts[k]}")
    print("problems:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
