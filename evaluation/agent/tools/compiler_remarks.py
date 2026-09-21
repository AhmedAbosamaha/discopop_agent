#!/usr/bin/env python3
"""The compiler's OWN remarks about a benchmark's kernel — E2's static-tool evidence (D16).

E2 asks whether DiscoPoP's evidence helps a model restructure code. Two arms alone (full
evidence, none) cannot tell "this evidence helps" from "any hint helps", so a third source
stands between them: what clang itself says about the loops — why the vectorizer left a loop
alone, why Polly found no SCoP. Static, free, and what a developer without DiscoPoP would have.

    none  ->  static tool (this file)  ->  dynamic DiscoPoP

The remarks are taken with the campaign's compiler, kept only where they concern code the
agent may edit (functions NOT in the package's `exclude_functions` — a remark about the
packaging's own timer or digest loop is not evidence about the kernel), de-duplicated, sorted
by line, and written as plain text for the agent's `--evidence-file`.

    agent/tools/compiler_remarks.py polybench/2mm tsvc/s211 [--out DIR] [--cc clang-20]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

AGENT_DIR = Path(__file__).resolve().parents[1]
PREPARED = AGENT_DIR / "prepared"
VEC = ["-Rpass-missed=loop-vectorize", "-Rpass-analysis=loop-vectorize"]
POLLY = ["-mllvm", "-polly", "-Rpass-missed=polly.*", "-Rpass-analysis=polly.*"]
REMARK = re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+):(?P<col>\d+): remark: (?P<text>.*?)(?: \[-Rpass[^\]]*\])?$")
# Polly's bracketing remarks say where a region starts and ends, not why: noise for a model.
NOISE = ("Invalid Scop candidate ends here", "SCoP begins here", "SCoP ends here",
         "The following errors keep this region from being a Scop")
MAX_CHARS = 6000                                     # the agent uses at most this much


def _strip_comments_keep_lines(text: str) -> str:
    """Comments and string literals blanked, line structure kept, so braces can be counted."""
    out: List[str] = []
    i, n, mode = 0, len(text), ""
    while i < n:
        c, nxt = text[i], text[i + 1] if i + 1 < n else ""
        if mode == "":
            if c == "/" and nxt == "/":
                mode = "//"; i += 2; continue
            if c == "/" and nxt == "*":
                mode = "/*"; i += 2; continue
            if c in "\"'":
                mode = c; out.append(" "); i += 1; continue
            out.append(c)
        elif mode == "//":
            if c == "\n":
                mode = ""; out.append(c)
        elif mode == "/*":
            if c == "*" and nxt == "/":
                mode = ""; i += 2; continue
            if c == "\n":
                out.append(c)
        else:                                        # inside a string or char literal
            if c == "\\":
                i += 2; continue
            if c == mode:
                mode = ""
            if c == "\n":
                out.append(c)
        i += 1
    return "".join(out)


def function_spans(text: str) -> List[Tuple[str, int, int]]:
    """(name, first line, last line) of every function DEFINED at file scope. A scanner, not a
    parser: good for benchmark C/C++ (one definition per `name(...) {` at brace depth 0)."""
    lines = _strip_comments_keep_lines(text).splitlines()
    spans: List[Tuple[str, int, int]] = []
    depth, header, header_start = 0, "", 0
    current: Optional[Tuple[str, int]] = None
    for ln, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            continue
        for ch_i, ch in enumerate(line):
            if ch == "{":
                if depth == 0:
                    m = re.findall(r"([A-Za-z_]\w*)\s*\([^()]*(?:\([^()]*\)[^()]*)*\)\s*$",
                                   (header + " " + line[:ch_i]).strip())
                    if m and m[-1] not in ("if", "for", "while", "switch", "struct", "union", "enum"):
                        current = (m[-1], header_start or ln)
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    if current:
                        spans.append((current[0], current[1], ln))
                    current, header, header_start = None, "", 0
            elif ch == ";" and depth == 0:
                header, header_start = "", 0
        if depth == 0 and current is None:
            stripped = line.strip()
            if stripped and not stripped.endswith(";") and not stripped.endswith("}"):
                if not header:
                    header_start = ln
                header = (header + " " + stripped).strip()
            elif stripped.endswith(";") or stripped.endswith("}"):
                header, header_start = "", 0
    return spans


def _units(bench_dir: Path) -> Tuple[List[Path], List[str]]:
    meta = json.loads((bench_dir / "meta.json").read_text())
    proj = meta.get("project") or {}
    if proj.get("units"):
        incs = [f"-I{bench_dir}"] + [f"-I{bench_dir / d}" for d in proj.get("include_dirs") or []]
        return [bench_dir / u for u in proj["units"]], incs + list(proj.get("cflags") or [])
    return [bench_dir / meta["file"]], []


def remarks_for(bench: str, cc: str, cxx: str, prepared: Path = PREPARED) -> Dict[str, object]:
    bench_dir = prepared / bench
    meta = json.loads((bench_dir / "meta.json").read_text())
    excluded = set(meta.get("exclude_functions") or [])
    units, extra = _units(bench_dir)
    kept: Dict[Tuple[str, int, int, str], None] = {}
    dropped_scaffold = dropped_noise = 0
    commands: List[str] = []
    polly_ok = True
    for unit in units:
        comp = cc if unit.suffix == ".c" else cxx
        spans = function_spans(unit.read_text(errors="replace"))
        in_scope = [(a, b) for name, a, b in spans if name not in excluded]
        for label, flags in (("vectorizer", VEC), ("polly", POLLY)):
            cmd = [comp, "-O3", "-g", "-c", str(unit), "-o", "/dev/null", *extra, *flags]
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=bench_dir, timeout=600)
            commands.append(" ".join([Path(comp).name, "-O3 -g -c", unit.name, *flags]))
            if proc.returncode != 0:
                if label == "polly":
                    polly_ok = False                 # a clang built without Polly: said, not fatal
                    continue
                raise RuntimeError(f"{bench}: {comp} failed on {unit.name}: {proc.stderr[-300:]}")
            for raw in proc.stderr.splitlines():
                m = REMARK.match(raw.strip())
                if not m or Path(m["file"]).name != unit.name:
                    continue
                line, text = int(m["line"]), m["text"].strip()
                if any(nz in text for nz in NOISE):
                    dropped_noise += 1
                    continue
                if not any(a <= line <= b for a, b in in_scope):
                    dropped_scaffold += 1
                    continue
                kept[(unit.name, line, int(m["col"]), text)] = None
    ordered = sorted(kept)
    body = "\n".join(f"{f}:{ln}:{col}: {text}" for f, ln, col, text in ordered)
    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS].rsplit("\n", 1)[0]
    return {"benchmark": bench, "text": body, "remarks": len(ordered),
            "dropped_in_packaging_code": dropped_scaffold, "dropped_bracketing": dropped_noise,
            "polly_available": polly_ok, "commands": commands}


def write(bench: str, out_dir: Path, cc: str, cxx: str, prepared: Path = PREPARED) -> Path:
    res = remarks_for(bench, cc, cxx, prepared)
    out_dir.mkdir(parents=True, exist_ok=True)
    txt = out_dir / "compiler_remarks.txt"
    txt.write_text(str(res["text"]) + "\n")
    (out_dir / "compiler_remarks.json").write_text(
        json.dumps({k: v for k, v in res.items() if k != "text"}, indent=2) + "\n")
    return txt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("benchmarks", nargs="+")
    ap.add_argument("--out", type=Path, default=None, help="directory (default: print only)")
    ap.add_argument("--cc", default="clang")
    ap.add_argument("--cxx", default="clang++")
    ap.add_argument("--prepared", type=Path, default=PREPARED, help="the packages' root")
    a = ap.parse_args()
    for b in a.benchmarks:
        res = remarks_for(b, a.cc, a.cxx, a.prepared)
        print(f"== {b}: {res['remarks']} remark(s) kept, {res['dropped_in_packaging_code']} in packaging code "
              f"dropped, {res['dropped_bracketing']} bracketing dropped, polly={res['polly_available']}")
        print(res["text"] or "   (the compiler has nothing to say about the kernel)")
        if a.out:
            write(b, a.out / b, a.cc, a.cxx, a.prepared)
    return 0


if __name__ == "__main__":
    sys.exit(main())
