#!/usr/bin/env python3
"""T0.16 — does the clean two-file layout (packaging v5) change anything but where the harness sits?

The author (4 Oct 2026): the file a model reads has to be an ordinary code file — no note of ours, no
measurement code. Packaging v5 (prepare_tsvc.py, suite `tsvc_c1`) puts the loop's function alone in the
benchmark's file and `main`, the repetition loop and `pb_mix` in a second file no model can change. The claim
that makes this a clean change: the PROGRAM is the same and DiscoPoP's view of the loop under study is the
same. This checks it per loop against the v4 package (`tsvc_b1`), with the agent's OWN code:

  output      plain builds: digest on the shipped and the perturbed input (seed 7), full dump — byte for byte
  time        (--time SIZE) the sequential timed region, median of N alternating runs, new / old
  DiscoPoP    each layout profiled as a trial is (`_reprofil`; v5 as a project, through the unity unit), then
              the agent's `build_candidates`, `assemble`, `order_statement`:
    candidates   on the benchmark's own code (the repetition loop is measurement): region, tier, pattern
    Do-All set   the loops DiscoPoP reports parallel, by their text
    blocker      what blocks the loop under study: (variable, type) — and whether the repetition loop is blocked
    statement    the order statement under prompt version 4 (and 3, reported)
    flows        the RAW records between two lines of the loop, with what carries each (version 4's basis)
  A difference in the WAR/WAW lists of version 3's reading is NOT a criterion: that reading applies a line's
  first type to all of its targets, and the order on a line changes from profile to profile (deps.py, D12).

Every profile is kept (without build products and AST dumps) under <out>/profiles/ — a rule about the evidence
is replayed on them (order_replay.py), never argued. Run with the agent's venv, one profile at a time:

    venv/bin/python evaluation/agent/tools/layout_equivalence.py --out <dir> [--time STANDARD] [names...]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))
import harness_include  # noqa: E402
from harness_equivalence import _cc  # noqa: E402
from discopop_agent import project as project_mod                 # noqa: E402
from discopop_agent.args import parse_args                         # noqa: E402
from discopop_agent.evidence import assemble                       # noqa: E402
from discopop_agent.llm.prompts import PROMPT_VERSIONS             # noqa: E402
from discopop_agent.llm.render import order_statement              # noqa: E402
from discopop_agent.plan import build_candidates                   # noqa: E402
from discopop_agent.plan import impact as impact_mod               # noqa: E402
from discopop_agent.profiling import _measure_hotspots, _reprofil  # noqa: E402
from discopop_agent.profiling import tools as profiling_tools      # noqa: E402

PREPARED = HERE.parent / "prepared"
KEEP_OUT = ("a.out", "ast_dump.json", "patch_generator", "patch_applicator", "private", "statistics")
MIX = ("a[k] +=", "d[k] +=", "a[0] +=", "long k =", "pb_mix(", "static long n", "n++;")      # v6: the lines of `dummy`
# the repetition loop's header: v4's, and v6's — where it is the function's own, as in TSVC
REPETITION = ("nl < R", "nl < iterations")


def _rep(text: str) -> bool:
    return any(r in text for r in REPETITION)


def _run(cmd: List[str], args: List[str]) -> Tuple[str, str]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return "BUILD FAILED: " + r.stderr[-300:], ""
    p = subprocess.run([cmd[cmd.index("-o") + 1], *args], capture_output=True, text=True, timeout=1800)
    return (p.stdout if p.returncode == 0 else f"RUN FAILED rc={p.returncode}"), p.stderr


def _sources(pkg: Path) -> Tuple[List[str], List[str]]:
    """(units, include flags) of a package: one file (v4) or a project (v5)."""
    meta = json.loads((pkg / "meta.json").read_text())
    proj = meta.get("project")
    if proj:
        return [str(pkg / u) for u in proj["units"]], [f"-I{pkg / d}" for d in proj.get("include_dirs") or ["."]]
    return [str(pkg / meta["file"])], []


def outputs(pkg: Path, work: Path) -> Dict[str, str]:
    units, inc = _sources(pkg)
    out = {}
    for tag, flags, args in (("digest", [], []), ("digest_seed7", [], ["7"]), ("dump", ["-DPB_FULL_DUMP"], [])):
        out[tag] = _run([*_cc(), "-O2", *flags, *inc, *units, "-o", str(work / f"plain_{tag}"), "-lm"], args)[0]
    return out


def timed(pkg: Path, work: Path, size: str, runs: int, tag: str) -> List[float]:
    units, inc = _sources(pkg)
    exe = work / f"timed_{tag}"
    r = subprocess.run([*_cc(), "-O2", f"-D{size}_DATASET", *inc, *units, "-o", str(exe), "-lm"], capture_output=True, text=True)
    if r.returncode != 0:
        return []
    out = []
    for _ in range(runs):
        p = subprocess.run([str(exe)], capture_output=True, text=True, timeout=3600)
        m = re.search(r"DP_TIMED_REGION_SECONDS ([0-9.]+)", p.stderr)
        if m:
            out.append(float(m.group(1)))
    return out


def profile(pkg: Path, name: str, work: Path) -> Dict[str, Any]:
    """Profile one layout exactly as a trial does, and read what the agent would plan and say."""
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    meta = json.loads((pkg / "meta.json").read_text())
    proj = meta.get("project")
    for f in pkg.iterdir():
        if f.suffix in (".c", ".h"):
            shutil.copy2(f, work / f.name)
    src = work / meta["file"]
    dp = work / ".discopop"
    project_mod.activate(None)
    argv = ["--source-file", str(src)]
    if proj:
        project_mod.activate(project_mod.Project.discover(work, units=proj["units"], include_dirs=["."],
                                                          editable=proj.get("editable")))
        project_mod.set_focus(str(src))
        argv = ["--project-dir", str(work), "--project-units", ",".join(proj["units"]), "--project-include", ".",
                *(["--project-editable", ",".join(proj["editable"])] if proj.get("editable") else [])]
    try:
        t0 = time.time()
        if not _reprofil(str(src), dp, None):
            return {"error": "profile failed"}
        t_prof = time.time() - t0
        old = sys.argv
        sys.argv = ["x", "--discopop-dir", str(dp), *argv, "--exclude-functions",
                    ",".join(meta.get("exclude_functions") or []), "--min-runtime-share", "0.01"]
        try:
            args = parse_args()
        finally:
            sys.argv = old
        hs_ok, hs_note = _measure_hotspots(args, dp)
        impact = impact_mod.load_hotspots(dp, threads=os.cpu_count() or 1)
        cands = build_candidates(dp, args.source_file, args.lambda_penalty, args.min_workload, impact=impact,
                                 min_impact=args.min_impact, min_runtime_share=args.min_runtime_share,
                                 exclude_functions=args.exclude_functions)
        files = {fid: p for fid, p in project_mod.load_file_mapping(dp).items()}

        def text_at(fid: int, line: int) -> str:
            try:
                return files[fid].read_text().splitlines()[line - 1].strip()
            except (KeyError, OSError, IndexError):
                return f"?{fid}:{line}"
        pats = json.loads((dp / "explorer" / "patterns.json").read_text()).get("patterns", {})
        doall = sorted(text_at(int(str(p.get("start_line", "0:0")).split(":")[0]), int(str(p.get("start_line", "0:0")).split(":")[-1]))
                       for p in pats.get("do_all", []))
        prevented = dp / "explorer" / "doall_prevented.json"
        blockers = sorted({(re.sub(r"^GEPRESULT_", "", str(b.get("var_name"))), str(b.get("dep_type", "")).split(".")[-1],
                            text_at(int(b.get("loop_file") or 0), int(b.get("loop_start") or 0)))
                           for b in (json.loads(prevented.read_text()) if prevented.exists() else [])})
        out: Dict[str, Any] = {"profile_s": round(t_prof, 1), "hotspots": "ok" if hs_ok else hs_note,
                               "do_all": doall, "blockers": blockers, "candidates": []}
        for rank, c in enumerate(cands):
            lines = Path(c.source_file).read_text().splitlines()

            def t(n: int) -> str:
                return lines[n - 1].strip() if 1 <= n <= len(lines) else ""
            ev = assemble(c, dp / "profiler", "")
            statements = {}
            for v in (3, 4):
                note = order_statement(ev, frozenset(PROMPT_VERSIONS[v]))
                statements[str(v)] = sorted(re.sub(r"\b[Ll]ines? \d+| and \d+ \(", lambda m: re.sub(r"\d+", "N", m.group(0)), l.strip())
                                            for l in note.splitlines() if l.strip().startswith("- "))
            flows = sorted((k[0], t(k[2]), t(k[1]), k[3], "+".join(sorted(v))) for k, v in ev.flow_relations.items()
                           if k[0] == "RAW" and ev.start_line <= k[1] <= ev.end_line and ev.start_line <= k[2] <= ev.end_line)
            out["candidates"].append({"rank": rank, "file": Path(c.source_file).name, "type": c.region.region_type,
                                      "text": t(c.region.start_line), "tier": c.tier, "pattern": c.pattern_type,
                                      "share": round(c.runtime_fraction or 0.0, 4), "statements": statements,
                                      "flows": flows})
        return out
    finally:
        project_mod.activate(None)
        for junk in KEEP_OUT:
            for p in list(work.rglob(junk)) + list(work.rglob(junk + ".dSYM")):
                shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)
        for p in list(work.glob("*.dSYM")) + list(work.glob(".dp_hotspot*")):
            shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)


def view(p: Dict[str, Any]) -> Dict[str, Any]:
    """What the comparison is about, by line TEXT: the benchmark's own code."""
    ks = [c for c in p.get("candidates", []) if not _rep(c["text"])]

    def mine(tx: str) -> bool:
        return bool(tx) and not _rep(tx) and not tx.startswith(MIX)
    def shape(c: Dict[str, Any]) -> str:
        # a function is named without its parameter list (v5 hands `vas` its index array as a parameter)
        text = str(c["text"]).replace("static ", "")
        return re.sub(r"\(.*\)\s*$", "()", text) if c["type"] == "function" else text
    return {"candidates": sorted((c["type"], shape(c), c["tier"], str(c["pattern"])) for c in ks),
            "do_all": sorted(d for d in p.get("do_all", []) if not _rep(d)),
            "blocker": sorted((b[0], b[1], b[2]) for b in p.get("blockers", []) if not _rep(b[2])),
            "repetition": ("Do-All" if any(_rep(d) for d in p.get("do_all", [])) else
                           "blocked" if any(_rep(b[2]) for b in p.get("blockers", [])) else "no verdict"),
            "statement": sorted({s for c in ks for s in c["statements"]["4"]}),
            "statement_v3": sorted({s for c in ks for s in c["statements"]["3"]}),
            # a stack scalar's flow carries no call path (`unknown`): only the placed ones are compared
            "flows": sorted({tuple(f) for c in ks for f in c["flows"]
                             if mine(f[1]) and mine(f[2]) and f[4] != "unknown"})}


CRITERIA = ("candidates", "do_all", "blocker", "repetition", "statement")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", default="tsvc_b1")
    ap.add_argument("--new", default="tsvc_c1")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--time", default=None, metavar="SIZE", help="also time the sequential original at this size")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--explorer-timeout", type=int, default=180)
    ap.add_argument("names", nargs="*")
    a = ap.parse_args()
    harness_include.install()
    os.environ["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}"
    profiling_tools.set_explorer_timeout(a.explorer_timeout)
    a.out = a.out.resolve()          # the agent's project code reads a relative path as relative to the project
    a.out.mkdir(parents=True, exist_ok=True)
    names = a.names or sorted(p.name for p in (PREPARED / a.new).iterdir() if (p / "meta.json").exists())
    rows, fails = [], []
    with tempfile.TemporaryDirectory(prefix="t0_16_") as tmp:
        t = Path(tmp)
        for n in names:
            old_pkg, new_pkg = PREPARED / a.old / n, PREPARED / a.new / n
            oo, on = outputs(old_pkg, t), outputs(new_pkg, t)
            same_out = all(oo[k] == on[k] and len(oo[k]) > 0 and not oo[k].startswith(("BUILD", "RUN")) for k in oo)
            ratio: Optional[float] = None
            if a.time:
                to, tn = timed(old_pkg, t, a.time, a.runs, "old"), timed(new_pkg, t, a.time, a.runs, "new")
                ratio = round(statistics.median(tn) / statistics.median(to), 3) if to and tn else None
            po = profile(old_pkg, n, a.out / "profiles" / f"{n}_{a.old}")
            pn = profile(new_pkg, n, a.out / "profiles" / f"{n}_{a.new}")
            rec: Dict[str, Any] = {"name": n, "output_identical": same_out, "time_ratio": ratio, "old": po, "new": pn}
            if "error" in po or "error" in pn:
                rec["same"] = {}
                fails.append(n)
                rows.append([n, "same" if same_out else "DIFF", str(ratio or "—"), "PROFILE ERROR", "", "", "", "", ""])
            else:
                vo, vn = view(po), view(pn)
                rec["same"] = {k: vo[k] == vn[k] for k in CRITERIA}
                rec["flows_same"] = vo["flows"] == vn["flows"]
                rec["views"] = {"old": vo, "new": vn}
                if not same_out or not all(rec["same"].values()):
                    fails.append(n)
                rows.append([n, "same" if same_out else "DIFF", str(ratio or "—"),
                             *("same" if rec["same"][k] else "DIFF" for k in CRITERIA),
                             "same" if rec["flows_same"] else "differ"])
            (a.out / f"{n}.json").write_text(json.dumps(rec, indent=1, default=list))
            print(" | ".join(rows[-1]), flush=True)
    head = ["loop", "output", f"time new/old ({a.time})" if a.time else "time", "candidates (tier, pattern)", "Do-All set",
            "blocker of the loop under study", "repetition loop", "order statement (version 4)", "RAW flows with their carrier"]
    table = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]
    summary = (f"\n{len(rows)} loops on {platform.node()} ({time.strftime('%Y-%m-%d %H:%M')}): "
               f"{len(rows) - len(fails)} the same on every criterion; {len(fails)} differ"
               + (f" ({', '.join(fails)})" if fails else "") + ".")
    (a.out / "screen.md").write_text("\n".join(table) + "\n" + summary + "\n")
    print(summary)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
