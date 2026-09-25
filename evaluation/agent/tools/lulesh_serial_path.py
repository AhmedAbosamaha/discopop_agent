#!/usr/bin/env python3
"""LULESH 2.0 with ONLY its serial code path — the "before" of LLNL's own before/after.

`benchmarks/LULESH/LULESH_SEQ` has its pragmas removed, but the experts' parallel
restructuring is still in the file, next to the serial code it replaces:

* `IntegrateStressForElems` and `CalcFBHourglassForceForElems` scatter element forces into
  shared nodes on the serial path; under `if (numthreads > 1)` they write per-element
  arrays instead and a second loop gathers them through `nodeElemCornerList` — with the
  comment "Eliminate thread writing conflicts at the nodes by giving each element its own
  copy to write to".
* `Domain::SetupThreadSupportStructures` builds that corner list, only when threaded.
* The two time-constraint kernels keep per-thread minima under `#if <OPENMP>`.

A model given that file reads the solution (packaging rule §1a). This tool removes exactly
that, mechanically, and proves nothing else changed:

1. `unifdef -U_ALWAYS_FALSE_CHECK_FOR_OPENMP` — the preprocessor-dead OpenMP code.
2. every `if (numthreads > 1) {A} [else {B}]` becomes `B` (brace-matched), and the
   `numthreads` declarations go.
3. the thread-support structures: `SetupThreadSupportStructures`, `m_nodeElemStart`,
   `m_nodeElemCornerList`, their accessors, and the per-element force arrays that only the
   threaded branch used.
4. `--validate`: the ORIGINAL (`LULESH_SEQ`, which runs its serial path) and the result are
   built and run at two problem sizes; every deterministic output line must be identical,
   and the result may not mention threads, OpenMP or the corner list any more.

MPI guards are left alone: they say nothing about the OpenMP solution (package minimally).
The upstream OpenMP LULESH is the expert ceiling (`verify-source --label expert_openmp`).

    agent/tools/lulesh_serial_path.py --out agent/prepared_src/lulesh_serial --validate
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_include  # noqa: E402
harness_include.install()   # every build finds prepared/_harness (D39)

HARNESS_ROOT = Path(__file__).resolve().parents[2]
SOURCE = HARNESS_ROOT / "benchmarks" / "LULESH" / "LULESH_SEQ"
UNITS = ["lulesh.cc", "lulesh-comm.cc", "lulesh-init.cc", "lulesh-util.cc", "lulesh-viz.cc"]
HEADERS = ["lulesh.h"]
# `lulesh_tuple.h` (an alternative data layout) is included by nothing and carries the same
# corner-list accessors: it is not shipped.
OMP_SYMBOL = "_ALWAYS_FALSE_CHECK_FOR_OPENMP"
MPI_SYMBOL = "_ALWAYS_FALSE_CHECK_FOR_MPI"
# Anything left that names the threaded design. `thread` alone would hit MPI comments.
LEAKS = re.compile(r"numthreads|omp_get|_OPENMP|nodeElemCornerList|nodeElemStart|nodeElemCount|"
                   r"ThreadSupport|fx_elem|fy_elem|fz_elem|thread writing", re.I)
# NOT removed, and reported: the two time-constraint kernels are written, also on the serial
# path, as "one minimum per thread, then merge" with `threads = 1` — arrays of length one, a
# merge loop that never iterates. That is LLNL's serial computation; rewriting it into a plain
# scalar minimum would be rewriting the benchmark. What it means for the evaluation: in those
# two kernels the restructuring is already present and only the pragmas are missing.
KEPT = re.compile(r"per_thread|thread_num|\bthreads\b")
THREADED_IF = re.compile(r"^[ \t]*if[ \t]*\([ \t]*numthreads[ \t]*>[ \t]*1[ \t]*\)[ \t]*\{", re.M)


def _match_brace(text: str, open_idx: int) -> int:
    """Index of the `}` closing the `{` at open_idx. LULESH has no braces in strings here;
    comments inside the threaded blocks contain none either (asserted by the validation)."""
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced braces")


def _dedent(block: str, by: int) -> str:
    out = []
    for line in block.splitlines():
        strip = len(line) - len(line.lstrip(" "))
        out.append(line[min(by, strip):])
    return "\n".join(out)


def fold_numthreads(text: str) -> Tuple[str, int]:
    """`if (numthreads > 1) {A} else {B}` -> B ; without else -> nothing."""
    n = 0
    while True:
        m = THREADED_IF.search(text)
        if not m:
            return text, n
        line_start = m.start()
        indent = len(m.group(0)) - len(m.group(0).lstrip(" \t"))
        a_open = m.end() - 1
        a_close = _match_brace(text, a_open)
        rest = text[a_close + 1:]
        em = re.match(r"\s*else\s*\{", rest)
        if em:
            b_open = a_close + 1 + em.end() - 1
            b_close = _match_brace(text, b_open)
            body = text[b_open + 1:b_close].strip("\n")
            inner = len(body.splitlines()[0]) - len(body.splitlines()[0].lstrip(" ")) if body else indent
            replacement = _dedent(body, max(inner - indent, 0))
            end = b_close + 1
        else:
            replacement, end = "", a_close + 1
        # swallow the newline that followed the removed construct when nothing replaces it
        if not replacement and text[end:end + 1] == "\n":
            end += 1
        text = text[:line_start] + replacement + text[end:]
        n += 1


def _remove(text: str, pattern: str, what: str, removed: List[str], count: Optional[int] = None,
            flags: int = re.M) -> str:
    new, k = re.subn(pattern, "", text, flags=flags)
    if k == 0 or (count is not None and k != count):
        raise SystemExit(f"lulesh_serial_path: expected {count or '>=1'} × {what}, found {k} — source differs")
    removed.append(f"{what} ×{k}")
    return new


def _remove_unused_decl(text: str, decl: str, name: str, what: str, removed: List[str]) -> str:
    """Remove a declaration only in the functions where nothing uses the name any more
    (a function ends at the next `}` in column 0 — LULESH's layout)."""
    k = 0
    pos = 0
    while True:
        m = re.compile(decl, re.M).search(text, pos)
        if not m:
            break
        end_fn = text.find("\n}", m.end())
        body = text[m.end():end_fn if end_fn != -1 else len(text)]
        if re.search(rf"\b{re.escape(name)}\b", body):
            pos = m.end()
            continue
        text = text[:m.start()] + text[m.end():]
        pos = m.start()
        k += 1
    if not k:
        raise SystemExit(f"lulesh_serial_path: {what}: nothing to remove — source differs")
    removed.append(f"{what} ×{k}")
    return text


def _remove_function(text: str, signature: str, what: str, removed: List[str]) -> str:
    m = re.search(signature, text, flags=re.M)
    if not m:
        raise SystemExit(f"lulesh_serial_path: {what} not found — source differs")
    open_idx = text.index("{", m.end() - 1)
    close_idx = _match_brace(text, open_idx)
    end = close_idx + 1
    while text[end:end + 1] == "\n":
        end += 1
    removed.append(what)
    return text[:m.start()] + text[end:]


def make_serial(src: Path, out: Path) -> Dict[str, List[str]]:
    if not shutil.which("unifdef"):
        raise SystemExit("lulesh_serial_path: `unifdef` is required")
    out.mkdir(parents=True, exist_ok=True)
    log: Dict[str, List[str]] = {}
    for name in UNITS + HEADERS:
        removed: List[str] = []
        p = subprocess.run(["unifdef", f"-U{OMP_SYMBOL}", str(src / name)], capture_output=True, text=True)
        if p.returncode not in (0, 1):                     # 1 = "output differs", the normal case
            raise SystemExit(f"unifdef failed on {name}: {p.stderr}")
        text = p.stdout
        if p.returncode == 1:
            removed.append(f"preprocessor-dead code under #if {OMP_SYMBOL}")
        text, k = fold_numthreads(text)
        if k:
            removed.append(f"`if (numthreads > 1)` branch ×{k} (serial `else` kept where there was one)")
        if "numthreads" in text:
            text = _remove(text, r"^[ \t]*Index_t numthreads = 1;[ \t]*\n", "`Index_t numthreads = 1;`", removed)
        if name == "lulesh.cc":
            text = _remove_unused_decl(text, r"^[ \t]*Index_t numElem8 = numElem \* 8 ;[ \t]*\n", "numElem8",
                                       "`numElem8` where only the per-element force arrays used it", removed)
            text = _remove(text, r"^[ \t]*Real_t \*f[xyz]_elem;[ \t]*\n", "per-element force array pointers", removed)
        if name == "lulesh-init.cc":
            text = _remove_function(text, r"^/{20,}\nvoid\nDomain::SetupThreadSupportStructures\(\)\n",
                                    "Domain::SetupThreadSupportStructures()", removed)
            # its call stood under `#if <OPENMP>`: unifdef has already removed it
            if "SetupThreadSupportStructures" in text:
                raise SystemExit("lulesh_serial_path: a call to SetupThreadSupportStructures survived — source differs")
            text = _remove(text, r"^[ \t]*m_nodeElem(?:Start|CornerList)\(0\),[ \t]*\n", "corner-list initialisers", removed, 2)
            text = _remove(text, r"^[ \t]*delete \[\] m_nodeElem(?:Start|CornerList);[ \t]*\n", "corner-list deletes", removed, 2)
        if name == "lulesh.h":
            text = _remove(text, r"^[ \t]*Index_t nodeElemCount\(Index_t idx\)\n[^\n]*\n\n?", "accessor nodeElemCount", removed, 1)
            text = _remove(text, r"^[ \t]*Index_t \*nodeElemCornerList\(Index_t idx\)\n[^\n]*\n\n?",
                           "accessor nodeElemCornerList", removed, 1)
            text = _remove(text, r"^[ \t]*void SetupThreadSupportStructures\(\);[ \t]*\n", "declaration", removed, 1)
            text = _remove(text, r"^[ \t]*Index_t \*m_nodeElem(?:Start|CornerList) ;[ \t]*\n", "corner-list members", removed, 2)
        (out / name).write_text(text)
        if removed:
            log[name] = removed
    return log


DETERMINISTIC = re.compile(r"Problem size|Iteration count|Final Origin Energy|MaxAbsDiff|TotalAbsDiff|MaxRelDiff")


def _build_and_run(srcdir: Path, work: Path, cxx: str, sizes: List[Tuple[int, int]]) -> List[str]:
    exe = work / "lulesh"
    sysroot: List[str] = []
    if sys.platform == "darwin":                           # Homebrew clang needs the SDK named
        sdk = subprocess.run(["xcrun", "--show-sdk-path"], capture_output=True, text=True).stdout.strip()
        sysroot = ["-isysroot", sdk] if sdk else []
    # lulesh.h still tests the ORIGINAL name (`USE_MPI`) for "was it given", the renamed one for its value
    cmd = [cxx, "-O2", "-w", *sysroot, "-DUSE_MPI=0", f"-D{MPI_SYMBOL}=0", f"-I{srcdir}", *[str(srcdir / u) for u in UNITS],
           "-o", str(exe), "-lm"]
    b = subprocess.run(cmd, capture_output=True, text=True)
    if b.returncode:
        raise SystemExit(f"build failed in {srcdir}:\n{b.stderr[-1500:]}")
    lines: List[str] = []
    for s, i in sizes:
        r = subprocess.run([str(exe), "-s", str(s), "-i", str(i)], capture_output=True, text=True, timeout=1800)
        if r.returncode:
            raise SystemExit(f"run failed ({srcdir}, -s {s} -i {i}): {r.stderr[-500:]}")
        lines += [f"[-s {s} -i {i}] {l.strip()}" for l in r.stdout.splitlines() if DETERMINISTIC.search(l)]
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=SOURCE)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--cxx", default=shutil.which("clang++") or shutil.which("g++") or "c++")
    a = ap.parse_args()
    out = a.out.resolve()
    log = make_serial(a.src, out)
    for name, items in log.items():
        print(f"{name}:")
        for it in items:
            print(f"   - {it}")
    leaks = [(n, i + 1, l.strip()) for n in UNITS + HEADERS
             for i, l in enumerate((out / n).read_text().splitlines()) if LEAKS.search(l)]
    record: Dict[str, Any] = {
        "benchmark": "LULESH 2.0, serial code path only", "source": str(a.src.relative_to(HARNESS_ROOT)),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "removed": log,
        "leftover_mentions_of_the_threaded_design": [f"{n}:{i}: {l}" for n, i, l in leaks],
        "kept_serial_per_thread_minimum": [f"{n}:{i + 1}: {l.strip()}" for n in UNITS + HEADERS
                                           for i, l in enumerate((out / n).read_text().splitlines())
                                           if KEPT.search(l)],
        "not_shipped": ["lulesh_tuple.h (included by nothing; carries the corner-list accessors)"],
        "sha256": {n: hashlib.sha256((out / n).read_bytes()).hexdigest() for n in UNITS + HEADERS},
        "lines": {"before": sum(len((a.src / n).read_text().splitlines()) for n in UNITS + HEADERS),
                  "after": sum(len((out / n).read_text().splitlines()) for n in UNITS + HEADERS)},
    }
    ok = not leaks
    if leaks:
        print("LEFTOVER mentions of the threaded design:")
        for n, i, l in leaks:
            print(f"   {n}:{i}: {l}")
    if a.validate:
        sizes = [(8, 20), (12, 30)]
        with tempfile.TemporaryDirectory(prefix="lulesh_serial_") as tmp:
            (Path(tmp) / "a").mkdir()
            (Path(tmp) / "b").mkdir()
            before = _build_and_run(a.src, Path(tmp) / "a", a.cxx, sizes)
            after = _build_and_run(out, Path(tmp) / "b", a.cxx, sizes)
        same = before == after and bool(before)
        record["validation"] = {"sizes": [f"-s {s} -i {i}" for s, i in sizes], "identical": same,
                                "deterministic_lines": before, "compiler": a.cxx}
        print(f"validation: {len(before)} deterministic output lines, identical = {same}")
        if not same:
            for x, y in zip(before, after):
                if x != y:
                    print(f"   original: {x}\n   serial  : {y}")
        ok = ok and same
    (out / "SERIAL_PATH.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{record['lines']['before']} -> {record['lines']['after']} lines; record: {out / 'SERIAL_PATH.json'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
