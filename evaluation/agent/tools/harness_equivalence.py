#!/usr/bin/env python3
"""T0.15 — does moving the measurement harness out of a package change anything but the harness?

Packaging v4 (D39, 25 Sep 2026) takes our measurement code — sizes, data, initial values,
perturbed input, digest, timing, the per-repetition perturbation — out of the file the models
read and DiscoPoP profiles, into a header outside the package (`prepared/_harness/`). The
claim that makes it a clean change: the PROGRAM is the same, and DiscoPoP's view of the code
under test is the same; only the harness disappears from sight. This checks it per benchmark,
with the agent's OWN code for everything it measures:

  output        both layouts built plainly: digest on the shipped input and on the perturbed
                one (seed 7), and the full dump of every value — byte for byte
  DiscoPoP      each layout profiled by the agent's `_reprofil` (instrumented run + explorer)
                and measured by its `_measure_hotspots`: functions instrumented, dependence
                records, loops, patterns — and, for the code under test:
  candidates    the agent's own `build_candidates` (hotspots ON, --min-runtime-share 0.01, the
                package's exclude list): region, lines, tier, pattern — keyed by the kernel's
                own line offset, so the two layouts' line numbers are comparable
  evidence      the dependences `assemble` hands the model for every candidate: the new
                layout's must be the old one's MINUS those with an endpoint in harness code,
                and nothing else
  shares        each candidate's measured runtime share and the queue ORDER; a share is expected
                to rise (the harness's time leaves the denominator) — what must not happen is a
                region crossing the 1 % floor or the order changing

Run with the agent's venv (it imports discopop_agent), sequentially — one profile at a time:

    venv/bin/python evaluation/agent/tools/harness_equivalence.py --old evaluation/agent/prepared/tsvc \\
        --new <v4>/tsvc --harness <v4>/_harness --out <dir> [names...]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from discopop_agent.args import parse_args                      # noqa: E402
from discopop_agent.evidence import assemble                    # noqa: E402
from discopop_agent.plan import build_candidates                # noqa: E402
from discopop_agent.plan import impact as impact_mod            # noqa: E402
from discopop_agent.profiling import _measure_hotspots, _reprofil  # noqa: E402
from discopop_agent.profiling import tools as profiling_tools   # noqa: E402

MIN_SHARE = 0.01          # the campaign's --min-runtime-share (D1)


def _cc() -> List[str]:
    cc = shutil.which("clang-20") or shutil.which("clang") or "clang"
    if sys.platform == "darwin":
        brew = Path("/usr/local/Cellar/llvm@19")
        found = sorted(brew.glob("*/bin/clang")) if brew.exists() else []
        cc = str(found[-1]) if found else cc
        sdk = subprocess.run(["xcrun", "--show-sdk-path"], capture_output=True, text=True).stdout.strip()
        return [cc, "-isysroot", sdk] if sdk else [cc]
    return [cc]


def _outputs(src: Path, work: Path) -> Dict[str, str]:
    """stdout of the plain build (digest) on both inputs, and of the full-dump build."""
    out: Dict[str, str] = {}
    for tag, flags, args in (("digest", [], []), ("digest_seed7", [], ["7"]), ("dump", ["-DPB_FULL_DUMP"], [])):
        exe = work / f"plain_{tag}"
        r = subprocess.run([*_cc(), "-O2", *flags, str(src), "-o", str(exe), "-lm"], capture_output=True, text=True)
        if r.returncode != 0:
            out[tag] = "BUILD FAILED: " + r.stderr[-300:]
            continue
        out[tag] = subprocess.run([str(exe), *args], capture_output=True, text=True, timeout=600).stdout
    return out


def _kernel_span(src: Path, name: str) -> Tuple[int, int]:
    lines = src.read_text().splitlines()
    start = next(i + 1 for i, l in enumerate(lines) if l.startswith(f"static real_t kernel_{name}("))
    end = next(i + 1 for i in range(start, len(lines)) if lines[i].startswith("}"))
    return start, end


def _profile(pkg: Path, name: str, work: Path, exclude: List[str]) -> Dict[str, Any]:
    """Profile one layout exactly as a trial does, and read what the agent would plan."""
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    src = work / f"{name}.c"
    shutil.copy2(pkg / f"{name}.c", src)
    dp = work / ".discopop"
    t0 = time.time()
    ok = _reprofil(str(src), dp, None)
    t_prof = time.time() - t0
    if not ok:
        return {"error": "profile failed"}
    old_argv = sys.argv
    sys.argv = ["x", "--discopop-dir", str(dp), "--source-file", str(src),
                "--exclude-functions", ",".join(exclude), "--min-runtime-share", str(MIN_SHARE)]
    try:
        args = parse_args()
    finally:
        sys.argv = old_argv
    t0 = time.time()
    hs_ok, hs_note = _measure_hotspots(args, dp)
    t_hot = time.time() - t0
    impact = impact_mod.load_hotspots(dp, threads=os.cpu_count() or 1)
    cands = build_candidates(dp, str(src), args.lambda_penalty, args.min_workload, impact=impact,
                             min_impact=args.min_impact, min_runtime_share=args.min_runtime_share,
                             exclude_functions=args.exclude_functions)
    ks, ke = _kernel_span(src, name)
    xml = (dp / "profiler" / "Data.xml").read_text(errors="replace")
    import re
    funcs = sorted(set(re.findall(r'type="1" name="([^"]+)"', xml)))
    dd = (dp / "profiler" / "dynamic_dependencies.txt").read_text(errors="replace").splitlines()
    pats = json.loads((dp / "explorer" / "patterns.json").read_text()).get("patterns", {})
    out: Dict[str, Any] = {
        "kernel_span": [ks, ke], "profile_s": round(t_prof, 2), "hotspots_s": round(t_hot, 2),
        "hotspots": hs_note if not hs_ok else "ok", "functions": funcs,
        "dependence_lines": sum(1 for l in dd if " NOM " in l), "loops": sum(1 for l in dd if " BGN loop " in l),
        "patterns": {k: len(v) for k, v in pats.items() if v},
        "candidates": [], "total_runtime": getattr(impact, "total_runtime", None),
        "lines": src.read_text().splitlines(),
    }
    for rank, c in enumerate(cands):
        r = c.region
        ev = assemble(c, dp / "profiler", "x")
        deps = sorted({(x.dep_type, x.from_line, x.to_line, x.variable)
                       for x in ev.raw_deps + ev.war_deps + ev.waw_deps})
        out["candidates"].append({
            "rank": rank, "type": r.region_type, "start": r.start_line, "end": r.end_line,
            "tier": c.tier, "pattern": c.pattern_type, "share": c.runtime_fraction, "deps": deps})
    return out


def _compare(name: str, old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Old (v3) against new (v4), every line keyed by its TEXT (as T0.8 does): the kernel and
    `pb_mix` have the same text in both layouts at different line numbers, and a line of the
    old file whose text the new file does not contain is harness code."""
    lo, ln = old["lines"], new["lines"]
    new_texts = {l.strip() for l in ln}

    def txt(lines: List[str], n: int) -> str:
        return lines[n - 1].strip() if n and 1 <= n <= len(lines) else ""

    def ckey(c: Dict[str, Any], lines: List[str]) -> Tuple[Any, ...]:
        return (c["type"], txt(lines, c["start"]), c["end"] - c["start"], c["tier"], c["pattern"])

    oc = [ckey(c, lo) for c in old["candidates"]]
    nc = [ckey(c, ln) for c in new["candidates"]]
    problems: List[str] = []
    if sorted(oc) != sorted(nc):
        problems.append(f"candidates differ: old {sorted(oc)} new {sorted(nc)}")
    elif oc != nc:
        problems.append(f"queue ORDER differs: old {oc} new {nc}")
    removed_harness, removed_other, added = 0, [], []
    for c_new in new["candidates"]:
        c_old = next((c for c in old["candidates"] if ckey(c, lo) == ckey(c_new, ln)), None)
        if c_old is None:
            continue
        nd = [(t, txt(ln, f), txt(ln, to), v) for t, f, to, v in c_new["deps"]]
        od = [(t, txt(lo, f), txt(lo, to), v) for t, f, to, v in c_old["deps"]]
        for d in set(od) - set(nd):
            _t, f, to, _v = d
            if (f and f not in new_texts) or (to and to not in new_texts):
                removed_harness += 1          # an endpoint on a line only the old file has
            else:
                removed_other.append(d)
        added += [d for d in set(nd) - set(od)]
        so, sn = c_old.get("share"), c_new.get("share")
        if so is not None and sn is not None and ((so < MIN_SHARE) != (sn < MIN_SHARE)):
            problems.append(f"region {ckey(c_new, ln)[:2]} crosses the {MIN_SHARE:.0%} floor: {so:.4f} -> {sn:.4f}")
    if removed_other:
        problems.append(f"kernel dependences LOST: {removed_other[:4]}")
    if added:
        problems.append(f"dependences ADDED: {added[:4]}")
    return {"name": name, "ok": not problems, "problems": problems,
            "harness_dependences_removed_from_evidence": removed_harness,
            "shares_old": [(c["type"], txt(lo, c["start"]), c.get("share")) for c in old["candidates"]],
            "shares_new": [(c["type"], txt(ln, c["start"]), c.get("share")) for c in new["candidates"]]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", required=True, type=Path, help="v3 packages (one directory per loop)")
    ap.add_argument("--new", required=True, type=Path, help="v4 packages")
    ap.add_argument("--harness", required=True, type=Path, help="v4 harness headers root (CPATH)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--explorer-timeout", type=int, default=120)
    ap.add_argument("names", nargs="*")
    a = ap.parse_args()
    os.environ["CPATH"] = os.pathsep.join([str(a.harness.resolve())] + [p for p in os.environ.get("CPATH", "").split(os.pathsep) if p])
    os.environ["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}"
    profiling_tools.set_explorer_timeout(a.explorer_timeout)
    a.out.mkdir(parents=True, exist_ok=True)
    names = a.names or sorted(p.name for p in a.new.iterdir() if (p / "meta.json").exists())
    results = []
    with tempfile.TemporaryDirectory(prefix="t0_15_") as tmp:
        t = Path(tmp)
        for n in names:
            mo = json.loads((a.old / n / "meta.json").read_text())
            mn = json.loads((a.new / n / "meta.json").read_text())
            outs_o, outs_n = _outputs(a.old / n / f"{n}.c", t), _outputs(a.new / n / f"{n}.c", t)
            same_out = {k: outs_o[k] == outs_n[k] and not outs_o[k].startswith("BUILD FAILED") for k in outs_o}
            po = _profile(a.old / n, n, t / "old", mo.get("exclude_functions") or [])
            pn = _profile(a.new / n, n, t / "new", mn.get("exclude_functions") or [])
            (a.out / "raw").mkdir(exist_ok=True)
            (a.out / "raw" / f"{n}.json").write_text(json.dumps({"old": po, "new": pn}))
            rec: Dict[str, Any] = {"name": n, "output_identical": same_out}
            if "error" in po or "error" in pn:
                rec.update(ok=False, problems=[f"profile: old {po.get('error')} new {pn.get('error')}"])
            else:
                rec.update(_compare(n, po, pn))
                rec["discopop"] = {k: {"old": po[k], "new": pn[k]} for k in
                                   ("functions", "dependence_lines", "loops", "patterns", "profile_s", "hotspots_s", "hotspots")}
            rec["ok"] = bool(rec.get("ok")) and all(same_out.values())
            results.append(rec)
            (a.out / "results.jsonl").open("a").write(json.dumps(rec) + "\n")
            print(f"{n:7s} {'OK ' if rec['ok'] else 'DIFF'} output {'identical' if all(same_out.values()) else same_out} "
                  f"| harness deps removed from evidence: {rec.get('harness_dependences_removed_from_evidence')} "
                  f"| {'; '.join(rec.get('problems') or [])[:200]}", flush=True)
    ok = sum(1 for r in results if r["ok"])
    summary = {"host": platform.node(), "python": sys.version.split()[0], "when": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "loops": len(results), "equivalent": ok, "different": [r["name"] for r in results if not r["ok"]]}
    (a.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\n{ok} of {len(results)} equivalent" + (f"; different: {summary['different']}" if summary["different"] else ""))
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
