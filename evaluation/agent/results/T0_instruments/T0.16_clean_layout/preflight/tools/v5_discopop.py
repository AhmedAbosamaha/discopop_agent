#!/usr/bin/env python3
"""Pre-flight (2)+(3): DiscoPoP's view of the loop under study, v4 (one file) against the v5 prototype (a two-file
project, profiled as the agent profiles a project: a unity unit). With the agent's OWN code: `_reprofil`,
`_measure_hotspots`, `build_candidates`, `assemble`, `order_statement`, the Do-All blockers.

    venv/bin/python v5_discopop.py <v5 root> <out dir> [names...]
"""
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO))
from discopop_agent import project as project_mod                 # noqa: E402
from discopop_agent.args import parse_args                         # noqa: E402
from discopop_agent.evidence import assemble                       # noqa: E402
from discopop_agent.llm.render import order_statement              # noqa: E402
from discopop_agent.plan import build_candidates                   # noqa: E402
from discopop_agent.plan import impact as impact_mod               # noqa: E402
from discopop_agent.profiling import _measure_hotspots, _reprofil  # noqa: E402
from discopop_agent.profiling import tools as profiling_tools      # noqa: E402

V4 = REPO / "evaluation/agent/prepared/tsvc_b1"
V4_H = REPO / "evaluation/agent/prepared/_harness"
ROOT5 = Path(sys.argv[1]).resolve()
V5, V5_H = ROOT5 / "prepared/tsvc_c1", ROOT5 / "_harness"
OUT = Path(sys.argv[2]).resolve()
BASE_CPATH = [p for p in os.environ.get("CPATH", "").split(os.pathsep) if p]
os.environ["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}"
profiling_tools.set_explorer_timeout(180)


def read(work: Path, name: str, argv: list, src: Path) -> dict:
    dp = work / ".discopop"
    t0 = time.time()
    if not _reprofil(str(src), dp, None):
        return {"error": "profile failed"}
    t_prof = time.time() - t0
    old = sys.argv
    sys.argv = ["x", "--discopop-dir", str(dp), *argv, "--exclude-functions", "main,pb_mix",
                "--min-runtime-share", "0.01", "--prompt-version", "3"]
    try:
        args = parse_args()
    finally:
        sys.argv = old
    hs_ok, hs_note = _measure_hotspots(args, dp)
    impact = impact_mod.load_hotspots(dp, threads=os.cpu_count() or 1)
    cands = build_candidates(dp, args.source_file, args.lambda_penalty, args.min_workload, impact=impact,
                             min_impact=args.min_impact, min_runtime_share=args.min_runtime_share,
                             exclude_functions=args.exclude_functions)
    dd = (dp / "profiler" / "dynamic_dependencies.txt").read_text(errors="replace").splitlines()
    pats = json.loads((dp / "explorer" / "patterns.json").read_text()).get("patterns", {})
    prevented = dp / "explorer" / "doall_prevented.json"
    fmap = (dp / "FileMapping.txt").read_text() if (dp / "FileMapping.txt").exists() else ""
    files = {}
    for raw in fmap.splitlines():
        parts = raw.split("\t") if "\t" in raw else raw.split(None, 1)
        if len(parts) == 2:
            files[parts[0].strip()] = Path(parts[1].strip())

    def text_at(fid: str, line: int) -> str:
        p = files.get(str(fid))
        try:
            return p.read_text().splitlines()[line - 1].strip() if p else ""
        except (OSError, IndexError):
            return ""

    doall = []
    for p in pats.get("do_all", []):
        fid, ln = str(p.get("start_line", "")).split(":")[0], int(str(p.get("start_line", "0:0")).split(":")[-1])
        doall.append({"file": files.get(fid).name if files.get(fid) else fid, "line": ln, "text": text_at(fid, ln)})
    blockers = []
    if prevented.exists():
        raw = json.loads(prevented.read_text())
        items = raw if isinstance(raw, list) else raw.get("prevented", raw.get("doall_prevented", []))
        for b in items if isinstance(items, list) else []:
            ls = str(b.get("loop_start", ""))
            fid, ln = (ls.split(":") + ["0"])[:2] if ":" in ls else ("", ls or "0")
            blockers.append({"file": files.get(fid).name if files.get(fid) else fid,
                             "loop": text_at(fid, int(ln)), "var": b.get("var_name"), "type": b.get("dep_type")})
    out = {"profile_s": round(t_prof, 1), "hotspots": "ok" if hs_ok else hs_note,
           "dependence_lines": sum(1 for l in dd if " NOM " in l), "files": {k: v.name for k, v in files.items()},
           "do_all": doall, "blockers": blockers, "candidates": []}
    for rank, c in enumerate(cands):
        r = c.region
        ev = assemble(c, dp / "profiler", "x")
        lines = Path(c.source_file).read_text().splitlines()

        def t(n: int) -> str:
            return lines[n - 1].strip() if 1 <= n <= len(lines) else ""
        deps = sorted({(x.dep_type, t(int(x.from_line)), t(int(x.to_line)), x.variable)
                       for x in ev.raw_deps + ev.war_deps + ev.waw_deps})
        order = order_statement(ev)
        order = re.sub(r"[Ll]ines? \d+|line \d+", lambda m: re.sub(r"\d+", "N", m.group(0)), order)
        out["candidates"].append({"rank": rank, "file": Path(c.source_file).name, "type": r.region_type,
                                  "text": t(r.start_line), "span": r.end_line - r.start_line, "tier": c.tier,
                                  "pattern": c.pattern_type, "share": round(c.runtime_fraction or 0.0, 4),
                                  "deps": deps, "order": order})
    return out


def v4(name: str, work: Path) -> dict:
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    src = work / f"{name}.c"
    shutil.copy2(V4 / name / f"{name}.c", src)
    os.environ["CPATH"] = os.pathsep.join([str(V4_H)] + BASE_CPATH)
    project_mod.activate(None)
    return read(work, name, ["--source-file", str(src)], src)


def v5(name: str, work: Path) -> dict:
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    for f in (f"{name}.c", "data.h", "main.c"):
        shutil.copy2(V5 / name / f, work / f)
    os.environ["CPATH"] = os.pathsep.join([str(V5_H)] + BASE_CPATH)
    proj = project_mod.Project.discover(work, units=[f"{name}.c", "main.c"], include_dirs=["."])
    project_mod.activate(proj)
    project_mod.set_focus(str(work / f"{name}.c"))
    try:
        return read(work, name, ["--project-dir", str(work), "--project-units", f"{name}.c,main.c",
                                 "--project-include", "."], work / f"{name}.c")
    finally:
        project_mod.activate(None)


MIX = ("a[k] +=", "d[k] +=", "a[0] +=", "long k =", "pb_mix(")


def kernel_view(p: dict, name: str) -> dict:
    """What the comparison is about — the benchmark's own code, by line TEXT: the candidates other than the
    repetition loop (v4 holds it in the kernel, v5 in main.c), the order statement's bullets, and the dependences
    with both ends in the loop under study (an end in pb_mix or on the repetition loop is measurement)."""
    ks = [c for c in p.get("candidates", []) if "nl < R" not in c["text"]]

    def mine(t: str) -> bool:
        return bool(t) and "nl" not in t.split("(")[0] and "nl < R" not in t and not t.startswith(MIX)
    order = set()
    for c in ks:
        order |= {l.strip() for l in c["order"].splitlines() if l.strip().startswith("- ")}
    return {"candidates": sorted((c["type"], c["text"].replace("static ", ""), c["tier"], c["pattern"]) for c in ks),
            "first": [(c["type"], c["text"].replace("static ", "")) for c in p.get("candidates", [])][:1],
            "order": sorted(order),
            "deps": sorted({(d[0], d[1], d[2], d[3]) for c in ks for d in c["deps"] if mine(d[1]) and mine(d[2])})}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[3:]
    bad = 0
    for n in names:
        a = v4(n, OUT / "work" / f"{n}_v4")
        b = v5(n, OUT / "work" / f"{n}_v5")
        (OUT / f"{n}.json").write_text(json.dumps({"v4": a, "v5": b}, indent=1))
        if "error" in a or "error" in b:
            print(f"{n:6s} PROFILE ERROR v4={a.get('error')} v5={b.get('error')}", flush=True)
            bad += 1
            continue
        ka, kb = kernel_view(a, n), kernel_view(b, n)
        rep4 = [d for d in a["do_all"] if "nl < R" in d["text"]]
        rep5 = [d for d in b["do_all"] if "nl < R" in d["text"]]
        problems = []
        if ka["candidates"] != kb["candidates"]:
            problems.append(f"candidates v4 {ka['candidates']} | v5 {kb['candidates']}")
        if ka["order"] != kb["order"]:
            problems.append(f"order statement v4 {ka['order']} | v5 {kb['order']}")
        if ka["deps"] != kb["deps"]:
            only4 = [d for d in ka["deps"] if d not in kb["deps"]]
            only5 = [d for d in kb["deps"] if d not in ka["deps"]]
            problems.append(f"kernel deps only v4 {only4} | only v5 {only5}")
        if rep4 or rep5:
            problems.append(f"repetition loop Do-All: v4 {bool(rep4)} v5 {bool(rep5)}")
        bad += bool(problems)
        da4 = sorted(d["text"] for d in a["do_all"])
        da5 = sorted(d["text"] for d in b["do_all"])
        print(f"{n:6s} {'SAME' if not problems else 'DIFF'}  kernel cands {len(ka['candidates'])}/{len(kb['candidates'])}  "
              f"first region v4 {ka['first']} v5 {kb['first']}  order bullets {len(ka['order'])}/{len(kb['order'])}  "
              f"kernel deps {len(ka['deps'])}/{len(kb['deps'])}  do-all {len(da4)}/{len(da5)}  "
              f"profile {a['profile_s']}s/{b['profile_s']}s  {' ; '.join(problems)[:900]}", flush=True)
    print(f"{len(names)} loops: {'ALL SAME' if not bad else str(bad) + ' differ'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
