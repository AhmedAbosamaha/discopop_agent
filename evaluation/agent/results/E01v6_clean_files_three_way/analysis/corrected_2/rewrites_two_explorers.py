#!/usr/bin/env python3
"""Every pragma-free rewrite DiscoPoP saw in the agent trials of one archived run, given to TWO versions of the
explorer on ONE profile each (Mac, no model): do they report the same loops, the same clauses, the same blocked
loops? Written for `e1v6c_s241` (8 Oct 2026): the run used the explorer of commit f9e7744df, whose array rule was
corrected after the run had started (B19, the regression on burkardt/md); a trial in which the two explorers
disagree on a rewrite would have to be run again.

The rewrites: per trial, each candidate of phase A that the gate's first stages accepted and that holds no
directive (rebuilt from the trial's original and the saved patch, where the patch applies to the original), and the
trial's finished file with its directives taken out. The profile is made with the explorer of the checkout (the
corrected one); the other explorer (`--other DIR`, a tree holding `explorer/` and `library/`) then reads the same
profile. Compared: the Do-All and reduction patterns with their data-sharing clauses, and the set of blocked loops
(the variable a blocker record names is the first the detector meets and differs between two runs of one explorer).

    venv/bin/python rewrites_two_explorers.py --run e1v6c_s241 --bench tsvc_c3/s241 --arm default_v4 \
        --other DIR --work DIR --out FILE.md
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
AGENT = REPO / "evaluation" / "agent"
sys.path.insert(0, str(AGENT / "tools"))
sys.path.insert(0, str(AGENT.parent / "shared"))
import campaign  # noqa: E402
import default_arm_ceiling as ceiling  # noqa: E402

PRAGMA = re.compile(r"^\+\s*#\s*pragma\s+omp\b")
HERE = Path(__file__).resolve().parent
VIEW = HERE / "dp_view.py"
PY = str(REPO / "venv" / "bin" / "python")


def norm(d: dict) -> dict:
    return {"do_all": d["do_all"], "reduction": d["reduction"], "blocked_loops": sorted({b[0] for b in d["blocked"]})}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--bench", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--other", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    env = dict(os.environ, PATH=str(REPO / "venv" / "bin") + ":" + os.environ["PATH"])
    root = campaign.find_run(a.run)
    pkg = AGENT / "prepared" / a.bench
    a.work.mkdir(parents=True, exist_ok=True)
    rows, seen = [], {}
    for trial in sorted(root.glob(f"benchmarks/{a.bench}/{a.arm}/*/rep*/trial.json")):
        d = trial.parent
        t = json.loads(trial.read_text())
        rep = int(t["repeat"])
        name = list(t.get("editable") or [Path(str(t.get("source") or "")).name])[0]
        programs = []
        cj = d / "agent_patches" / "candidates.jsonl"
        for c in [json.loads(ln) for ln in (cj.read_text().splitlines() if cj.is_file() else []) if ln.strip()]:
            if "patch" not in c:
                continue
            patch = d / "agent_patches" / str(c["patch"])
            added = [ln for ln in patch.read_text().splitlines() if ln.startswith("+") and not ln.startswith("+++")]
            if c.get("phase") != "A" or c.get("stage") != "accepted" or any(PRAGMA.match(ln) for ln in added):
                continue
            dst = a.work / f"r{rep}_c{int(c['n']):02d}.c"
            r = subprocess.run(["patch", "-s", "-o", str(dst), str(d / "original" / name), "-i", str(patch)],
                               capture_output=True, text=True)
            if r.returncode != 0 or not dst.is_file():
                rows.append((rep, f"candidate {int(c['n'])}", "the patch does not apply to the original (a rewrite on top of an earlier one)", ""))
                continue
            programs.append((f"candidate {int(c['n'])}", dst))
        final = d / "final" / name
        if final.is_file():
            dst = a.work / f"r{rep}_final.c"
            dst.write_text(ceiling.strip_pragmas(final.read_text()))
            programs.append(("the finished file without its directives", dst))
        for label, src in programs:
            sha = hashlib.sha256(src.read_bytes()).hexdigest()
            if sha in seen:
                rows.append((rep, label, f"the same program as {seen[sha]}", ""))
                continue
            seen[sha] = f"repeat {rep}, {label}"
            if sha == hashlib.sha256((d / "original" / name).read_bytes()).hexdigest():
                rows.append((rep, label, "the original program (the 44 packages are compared separately)", ""))
                continue
            w = a.work / src.stem
            r = subprocess.run([PY, str(VIEW), "profile", str(pkg), str(w), "--source", str(src)], capture_output=True, text=True, env=env)
            if "profile ok" not in r.stdout:
                rows.append((rep, label, "PROFILE FAILED: " + (r.stdout + r.stderr)[-200:].replace("\n", " "), ""))
                continue
            subprocess.run([PY, str(VIEW), "dump", str(w), str(w) + ".new.json"], env=env)
            shutil.rmtree(w / ".discopop" / "explorer", ignore_errors=True)
            oenv = dict(env, PYTHONPATH=f"{a.other / 'explorer'}:{a.other / 'library'}")
            subprocess.run([PY, "-m", "discopop_explorer"], cwd=w / ".discopop", capture_output=True, text=True, env=oenv)
            if not (w / ".discopop" / "explorer" / "patterns.json").is_file():
                rows.append((rep, label, "THE OTHER EXPLORER WROTE NO PATTERNS", ""))
                continue
            subprocess.run([PY, str(VIEW), "dump", str(w), str(w) + ".other.json"], env=env)
            n, o = norm(json.loads(Path(str(w) + ".new.json").read_text())), norm(json.loads(Path(str(w) + ".other.json").read_text()))
            pats = "; ".join(f"{k} {e[0]} {json.dumps(e[1]) if e[1] else ''}".strip() for k in ("do_all", "reduction") for e in n[k]) or "no pattern"
            arrays = sorted(set(re.findall(r"^\s*(?:static\s+)?(?:real_t|double|float|int)\s+(\w+)\s*\[", src.read_text(), re.M)))
            rows.append((rep, label, "the same" if n == o else "DIFFERENT: " + json.dumps(o) + " (the run's explorer) against " + json.dumps(n),
                         pats + (f" — arrays declared in the file: {', '.join(arrays)}" if arrays else "")))
            shutil.rmtree(w, ignore_errors=True)
    same = sum(1 for r in rows if r[2] == "the same")
    diff = sum(1 for r in rows if r[2].startswith("DIFFERENT"))
    other = len(rows) - same - diff
    md = [f"# `{a.run}`: every rewrite DiscoPoP saw, given to both explorers on one profile", "",
          f"Generated by `{Path(__file__).name}` (Mac, no model). The run's explorer: `{a.other}`; the other: the checkout's.",
          "", f"**Programs profiled: {same + diff}. The two explorers report the same on {same}, differently on {diff}.** "
          f"Not profiled ({other}): repeats of a program already listed, the original, or a patch that does not apply to the original.", "",
          "| repeat | rewrite | the two explorers | what DiscoPoP reports (the corrected explorer) |", "|---|---|---|---|"]
    md += [f"| {rep} | {label} | {verdict} | {pats} |" for rep, label, verdict, pats in rows]
    a.out.write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
