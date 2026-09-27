#!/usr/bin/env python3
"""The H13/C2 property of a benchmark: does the NAIVE pragma on its hot loop fail the gate? (no model)

The property every experiment's benchmarks must have (record §6, 26 Sep, "The benchmark property of
every experiment"): the naive pragma on the hot loop — `#pragma omp parallel for` with default
sharing — fails the gate (a race, or a changed output), checked mechanically. For E2-B1's direction
(a) it must fail; for direction (b) — a hidden independence — it is expected to pass, and the record
says how that is treated. This tool inserts the pragma in front of the hot loop and hands the result
to the agent's own gate exactly as `race_check.py` does — `validate(mode="safety")`: apply, compile,
the `-fopenmp` build under ThreadSanitizer, the schedule matrix, the output against the ORIGINAL on
the shipped input and on `--check-input 7`, with the reference and the numerical noise floor captured
the way the agent captures them. Run it where archer is found (the server, LLVM 20).

The HOT LOOP is the first `for (` statement of the package's source that is not the repetition loop
(`for (int nl …)`) — for a TSVC package the loop under study, in the kernel or in the callee it calls
(s151's `s151s`); for Rodinia's bfs (`rodinia_b1`, written `for(`) the frontier loop, the first loop of
its level loop; `--line bench=N` names another.

    venv/bin/python evaluation/agent/tools/naive_pragma.py --suite tsvc_b1 --out <dir> [names...]
"""
from __future__ import annotations

import argparse
import difflib
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
AGENT_DIR = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
import harness_include  # noqa: E402

harness_include.install()   # every build finds prepared/_harness (D39)
CHECK_INPUTS = [["7"]]


def hot_loop_line(source: str) -> Optional[int]:
    # `for\s*\(`: Rodinia writes `for(`. Every TSVC package (v3 and v4) resolves to the same line as with
    # the earlier `for \(` (checked 27 Sep when bfs was added).
    for i, l in enumerate(source.splitlines(), 1):
        if re.match(r"\s*for\s*\(", l) and not re.match(r"\s*for\s*\(int nl = 0;", l):
            return i
    return None


def naive_diff(src: Path, line: int) -> str:
    lines = src.read_text().splitlines(keepends=True)
    indent = re.match(r"\s*", lines[line - 1]).group(0)  # type: ignore[union-attr]
    new = lines[:line - 1] + [f"{indent}#pragma omp parallel for\n"] + lines[line - 1:]
    return "".join(difflib.unified_diff(lines, new, fromfile=src.name, tofile=src.name))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="package names in the suite (default: all)")
    ap.add_argument("--suite", required=True, help="a directory under prepared/ (tsvc, tsvc_b1, ...)")
    ap.add_argument("--line", action="append", default=[], help="bench=N: the hot loop's line, when not the first loop")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    from discopop_agent.gate.equivalence import numerical_noise_floor
    from discopop_agent.gate.timing import capture_reference
    from discopop_agent.gate.toolchain import _find_clangpp, find_archer
    from discopop_agent.gate.validate import validate

    suite_dir = AGENT_DIR / "prepared" / a.suite
    pkgs = sorted(p for p in suite_dir.iterdir() if (p / "meta.json").exists())
    if a.names:
        pkgs = [p for p in pkgs if p.name in set(a.names)]
    lines_override = {k: int(v) for k, v in (x.split("=", 1) for x in a.line)}
    a.out.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    manifest: Dict[str, Any] = {
        "tool": "naive_pragma.py", "commit": head, "host": platform.node(),
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "suite": a.suite, "packages": [p.name for p in pkgs],
        "clangpp": _find_clangpp(), "archer": find_archer(),
        "gate": "validate(mode='safety'): apply, compile, -fopenmp + TSan, schedule matrix, output vs original",
        "check_inputs": CHECK_INPUTS,
    }
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"{len(pkgs)} package(s); clang++ {manifest['clangpp']}; archer {manifest['archer'] or 'NOT FOUND'}")
    if not manifest["archer"]:
        print("  [warn] no archer: TSan cannot see OpenMP's barriers here — run this on the server")
    results: List[Dict[str, Any]] = []
    for pkg in pkgs:
        meta = json.loads((pkg / "meta.json").read_text())
        rec: Dict[str, Any] = {"benchmark": f"{a.suite}/{pkg.name}", "class": meta.get("restructuring_class")}
        t0 = time.time()
        with tempfile.TemporaryDirectory(prefix="naive_pragma_") as tmp:
            src = Path(tmp) / meta["file"]
            shutil.copy2(pkg / meta["file"], src)
            line = lines_override.get(pkg.name) or hot_loop_line(src.read_text())
            if line is None:
                rec.update(verdict="no loop found")
            else:
                diff = naive_diff(src, line)
                ref_out, _t, ref_pairs = capture_reference(str(src), None, extra_inputs=CHECK_INPUTS)
                floor = numerical_noise_floor(str(src), None, extra_inputs=CHECK_INPUTS).value
                res = validate(diff, str(src), reference_output=ref_out, reference_outputs=ref_pairs,
                               binary_args=None, mode="safety", noise_floor=floor, stress=True)
                rec.update(line=line, loop=src.read_text().splitlines()[line - 1].strip(),
                           verdict="fails the gate" if not res.passed else "passes the gate",
                           stage=None if res.passed else res.stage, diagnostic=res.diagnostic[:1500],
                           noise_floor=floor, diff_sha256=hashlib.sha256(diff.encode()).hexdigest())
        rec["seconds"] = round(time.time() - t0, 1)
        results.append(rec)
        print(f"{rec['benchmark']:22s} line {rec.get('line')}: {rec['verdict']}"
              + (f" at {rec['stage']}" if rec.get("stage") else "") + f"  ({rec['seconds']} s)", flush=True)
    with (a.out / "results.jsonl").open("w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
