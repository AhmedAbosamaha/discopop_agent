#!/usr/bin/env python3
"""T0.8 — does DiscoPoP see the same program in the project layout as in the merged file?

Decision D6 (THESIS_EXPERIMENTS.md §5g) replaces the one-file merge by the benchmark's
original files, profiled through a unity unit. Every earlier instrument study was taken on
the merged files, so before a benchmark is switched this study checks that DiscoPoP's
analysis of the two layouts is the same. Three things are compared, each keyed by the TEXT
of the source line rather than its number (the merged file prepends the utilities, so the
numbers differ while the lines do not):

  dependences   the observed dependence multiset (sink line, type, source line, variable)
                — T0.2 showed this is deterministic per program, so it is the strongest
                comparison: a difference here means DiscoPoP measured a different program
  blockers      the Do-All blockers (variable, loop header line, origin)
  patterns      the applicable do_all / reduction patterns (kind, header line)
                — subject to the explorer's own variation (T0.7), so a difference here
                on its own is a draw, not a verdict

Usage: packaging_equivalence.py --single agent/prepared_single/polybench \\
           --project agent/prepared/polybench --out agent/runs/t0_8_packaging [kernel ...]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

AGENT_DIR = Path(__file__).resolve().parent.parent
EXPLORER_ATTEMPTS = 20   # as the harness (cli.py)


def _env() -> Dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{env.get('PATH', '')}"
    return env


def _run(cmd: List[str], cwd: Path, timeout: float) -> Tuple[bool, str]:
    p = subprocess.Popen(cmd, cwd=cwd, env=_env(), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), 9)
        except (ProcessLookupError, PermissionError):
            p.kill()
        p.wait(timeout=10)
        return False, "timeout"
    return p.returncode == 0, (err or out)[-300:]


def _profile(bench: Path, meta: dict, work: Path, timeout: float) -> Tuple[bool, str]:
    """Profile one packaged benchmark exactly as the harness does (cli.profile_once)."""
    is_c = meta.get("language", "c") == "c"
    wrapper = "discopop_cc" if is_c else "discopop_cxx"
    proj = meta.get("project")
    if proj:
        for item in bench.rglob("*"):
            rel = item.relative_to(bench)
            if item.is_file() and rel.suffix in (".c", ".cpp", ".cc", ".h", ".hpp"):
                (work / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, work / rel)
        unity = work / ("dp_unity.c" if is_c else "dp_unity.cpp")
        unity.write_text("".join(f'#include "{u}"\n' for u in proj["units"]))
        cmd = ([wrapper, str(unity.resolve()), f"-I{work.resolve()}",
                *[f"-I{(work / d).resolve()}" for d in proj.get("include_dirs") or []],
                *(proj.get("cflags") or []), "-o", "a.out", *(proj.get("ldflags") or [])]
               + (["-lm"] if is_c else []))
    else:
        shutil.copy2(bench / meta["file"], work / meta["file"])
        cmd = [wrapper, meta["file"], "-o", "a.out"] + (["-lm"] if is_c else [])
    ok, err = _run(cmd, work, timeout)
    if proj:
        unity.unlink(missing_ok=True)
    if not ok:
        return False, f"instrument: {err}"
    ok, err = _run(["./a.out"], work, timeout)
    if not ok:
        return False, f"run: {err}"
    for _ in range(EXPLORER_ATTEMPTS):
        shutil.rmtree(work / ".discopop" / "explorer", ignore_errors=True)
        ok, err = _run(["discopop_explorer"], work / ".discopop", timeout)
        if ok:
            return True, ""
    return False, f"explorer: {err}"


def _file_mapping(dp: Path) -> Dict[int, Path]:
    out: Dict[int, Path] = {}
    for raw in (dp / "FileMapping.txt").read_text().splitlines():
        parts = raw.split("\t", 1) if "\t" in raw else raw.split(None, 1)
        if len(parts) == 2:
            out[int(parts[0])] = Path(parts[1].strip())
    return out


def _line_text(fmap: Dict[int, Path]) -> Dict[Tuple[int, int], str]:
    """(file id, line) -> normalised text of that line, over every mapped file."""
    out: Dict[Tuple[int, int], str] = {}
    for fid, path in fmap.items():
        try:
            for n, ln in enumerate(path.read_text(errors="replace").splitlines(), 1):
                out[(fid, n)] = " ".join(ln.split())
        except OSError:
            continue
    return out


def _instr_pos(profiler: Path) -> Dict[str, Tuple[int, int]]:
    out: Dict[str, Tuple[int, int]] = {}
    for raw in (profiler / "instructionID_to_lineID_mapping.txt").read_text().splitlines():
        parts = raw.split()
        if len(parts) >= 2 and parts[1] != "*" and ":" in parts[1]:
            f, l = parts[1].split(":")[:2]
            try:
                out[parts[0]] = (int(f), int(l))
            except ValueError:
                pass
    return out


def _text_of(tok: str, pos: Dict[str, Tuple[int, int]], text: Dict[Tuple[int, int], str]) -> str:
    tok = tok.split("@")[0]
    if ":" in tok:
        f, l = tok.split(":")[:2]
        key: Optional[Tuple[int, int]] = (int(f), int(l)) if f.isdigit() and l.isdigit() else None
    else:
        key = pos.get(tok)
    return text.get(key, "?") if key else "?"


def _plain_var(v: str) -> str:
    v = v.split("(")[0]
    if v.startswith("GEPRESULT"):
        v = v[len("GEPRESULT"):].lstrip("_")
    m = re.search(r"E(\d+)([A-Za-z_]\w*)$", v)       # _ZZ4mainE1a -> a
    if m and len(m.group(2)) == int(m.group(1)):
        v = m.group(2)
    m = re.match(r"_ZL?(\d+)([A-Za-z_]\w*)$", v)      # _ZL1b -> b
    if m and len(m.group(2)) == int(m.group(1)):
        v = m.group(2)
    return v


def _deps(dp: Path) -> Set[Tuple[str, str, str, str]]:
    """(sink text, type, source text, variable) for every observed dependence edge."""
    fmap = _file_mapping(dp)
    text = _line_text(fmap)
    pos = _instr_pos(dp / "profiler")
    out: Set[Tuple[str, str, str, str]] = set()
    for raw in (dp / "profiler" / "dynamic_dependencies.txt").read_text().splitlines():
        f = raw.split()
        if len(f) < 4 or f[1] != "NOM":
            continue
        sink = _text_of(f[0], pos, text)
        for i in range(2, len(f) - 1, 2):
            typ, payload = f[i], f[i + 1]
            if "|" not in payload or typ not in ("RAW", "WAR", "WAW"):
                continue
            src, var = payload.split("|", 1)
            out.add((sink, typ, _text_of(src, pos, text) if src not in ("*",) else "*", _plain_var(var)))
    return out


def _blockers(dp: Path) -> Set[Tuple[str, str, str]]:
    f = dp / "explorer" / "doall_prevented.json"
    if not f.exists():
        return set()
    fmap = _file_mapping(dp)
    text = _line_text(fmap)
    out: Set[Tuple[str, str, str]] = set()
    for b in json.loads(f.read_text()):
        key = (int(b.get("loop_file", 1)), int(b.get("loop_start", 0)))
        out.add((_plain_var(str(b.get("var_name", "?"))), text.get(key, "?"),
                 str(b.get("origin", "")).split(".")[-1]))
    return out


def _patterns(dp: Path) -> Set[Tuple[str, str]]:
    fmap = _file_mapping(dp)
    text = _line_text(fmap)
    pats = json.loads((dp / "explorer" / "patterns.json").read_text())["patterns"]
    out: Set[Tuple[str, str]] = set()
    for kind in ("do_all", "reduction"):
        for p in pats.get(kind, []) or []:
            if str(p.get("applicable_pattern")) != "True":
                continue
            f, l = (int(x) for x in str(p["start_line"]).split(":"))
            out.add((kind, text.get((f, l), "?")))
    return out


def compare(name: str, single: Path, project: Path, timeout: float) -> dict:
    rec: dict = {"benchmark": name}
    with tempfile.TemporaryDirectory() as tmp:
        works = {}
        for label, bench in (("single", single), ("project", project)):
            meta = json.loads((bench / "meta.json").read_text())
            work = Path(tmp) / label
            work.mkdir()
            t0 = time.perf_counter()
            ok, err = _profile(bench, meta, work, timeout)
            rec[f"{label}_seconds"] = round(time.perf_counter() - t0, 1)
            if not ok:
                rec["error"] = f"{label}: {err}"
                return rec
            works[label] = work / ".discopop"
        d_s, d_p = _deps(works["single"]), _deps(works["project"])
        b_s, b_p = _blockers(works["single"]), _blockers(works["project"])
        p_s, p_p = _patterns(works["single"]), _patterns(works["project"])
        # The comparison that decides: dependences whose sink is a line of the benchmark's
        # OWN file (the kernel).  The utilities are excluded from the agent's scope anyway,
        # and the merge had rewritten two of them (`ptr` for `new`), so they differ by
        # construction.
        meta_p = json.loads((project / "meta.json").read_text())
        own = {" ".join(ln.split()) for ln in (project / meta_p["file"]).read_text().splitlines()}
        k_s = {d for d in d_s if d[0] in own}
        k_p = {d for d in d_p if d[0] in own}
    # Lines that exist only in one layout (the merged file has no `#pragma scop`, the
    # project has no inlined utilities) never carry a kernel dependence; what is compared
    # is everything both layouts could have seen.
    rec.update({
        "kernel_deps_single": len(k_s), "kernel_deps_project": len(k_p),
        "kernel_deps_identical": k_s == k_p,
        "kernel_deps_only_single": sorted(k_s - k_p)[:8], "kernel_deps_only_project": sorted(k_p - k_s)[:8],
        "deps_single": len(d_s), "deps_project": len(d_p),
        "deps_only_single": sorted(d_s - d_p)[:8], "deps_only_project": sorted(d_p - d_s)[:8],
        "deps_identical": d_s == d_p,
        "blockers_single": sorted(b_s), "blockers_project": sorted(b_p),
        "blockers_identical": b_s == b_p,
        "patterns_single": sorted(p_s), "patterns_project": sorted(p_p),
        "patterns_identical": p_s == p_p,
    })
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--single", required=True, type=Path)
    ap.add_argument("--project", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--timeout", type=float, default=1800)
    ap.add_argument("kernels", nargs="*")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    names = a.kernels or sorted(p.name for p in a.project.iterdir() if (p / "meta.json").exists())
    rows = []
    for name in names:
        s, p = a.single / name, a.project / name
        if not (s / "meta.json").exists() or not (p / "meta.json").exists():
            print(f"{name:20s} skipped (missing in one layout)")
            continue
        rec = compare(name, s, p, a.timeout)
        rows.append(rec)
        if "error" in rec:
            print(f"{name:20s} ERROR {rec['error']}", flush=True)
            continue
        print(f"{name:20s} kernel deps {'same' if rec['kernel_deps_identical'] else 'DIFFER'} "
              f"({rec['kernel_deps_single']} vs {rec['kernel_deps_project']})  "
              f"all deps {'same' if rec['deps_identical'] else 'differ'} "
              f"({rec['deps_single']} vs {rec['deps_project']})  "
              f"blockers {'same' if rec['blockers_identical'] else 'DIFFER'}  "
              f"patterns {'same' if rec['patterns_identical'] else 'differ (draw?)'}  "
              f"[{rec['single_seconds']}s vs {rec['project_seconds']}s]", flush=True)
    (a.out / "summary.json").write_text(json.dumps(
        {"study": "T0.8 packaging equivalence", "host": platform.node(), "rows": rows}, indent=2))
    n = len([r for r in rows if "error" not in r])
    same = len([r for r in rows if r.get("kernel_deps_identical")])
    print(f"\n{same}/{n} benchmarks: identical kernel dependences in both layouts "
          f"(blockers and patterns are subject to the explorer's draw, T0.7)")
    print(f"wrote {a.out / 'summary.json'}")


if __name__ == "__main__":
    main()
