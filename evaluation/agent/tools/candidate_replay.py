#!/usr/bin/env python3
"""What would the pipeline do TODAY with a rewrite an archived trial got from its model — no model.

`replay`: for the given archived trials of one arm (`RUN:BENCHMARK@REPEAT`), every pragma-free rewrite that
passed the gate's first stages in that trial (`agent_patches/candidates.jsonl`: stage `accepted`, no `#pragma
omp` among the patch's added lines) is rebuilt from the trial's original file and its saved patch, and handed
to the pipeline the way `default_arm_ceiling.py` hands over an expert's rewrite: the agent runs on it with
`--budget 0` — DiscoPoP profiles the rewritten program, its pragmas go through the gate with the speed check
at the kernel's timing size, Settle verifies the finished file. Where at least one pragma is kept the finished
file is saved (`finals/<label>.c`).

`verify`: every saved finished file is judged by the harness's own verification against the benchmark's
ORIGINAL (`agent/benchmark verify-source`, the kernel's verification size, the given threads) into `--run-id`,
one after the other, label `replay_<loop>_r<repeat>_c<n>`.

Written for E1-v6's correction (8 Oct 2026; THESIS_EXPERIMENTS §6): the profiler defect B14 could make the
agent discard a right rewrite — DiscoPoP reported no pattern in it, or only one of two loops side by side, so
that the staged directives were judged not faster. Run on the fixed profiler this says, per trial, whether a
rewrite it discarded is kept by the pipeline and what the harness says of the result. Two limits, by
construction: a replay cannot say what the model would have done next, so it bounds a trial from above; and
the pipeline judges the pragmas against the pragma-free rewrite (Phase B's marginal timing and Settle), where
the agent in the trial judged the rewrite with its pragmas against the program before it (D40) — the harness's
verdict against the original is therefore the one that counts.

    venv/bin/python evaluation/agent/tools/candidate_replay.py replay --arm default_v4 \\
        --trials e1v6_r_2:tsvc_c2/s241@4,e1v6_r_2:tsvc_c2/s241@5 --out evaluation/agent/runs/e1v6c_replay/s241
    venv/bin/python evaluation/agent/tools/candidate_replay.py verify --out evaluation/agent/runs/e1v6c_replay \\
        --run-id e1v6c_replay_verify
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
AGENT_DIR = HERE.parent
HARNESS_ROOT = AGENT_DIR.parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HARNESS_ROOT / "shared"))
import campaign  # noqa: E402
import default_arm_ceiling as ceiling  # noqa: E402
import harness_include  # noqa: E402

PRAGMA = re.compile(r"^\+\s*#\s*pragma\s+omp\b")


def pass_digest() -> Optional[str]:
    """sha256 of the installed DiscoPoP pass — which profiler build answered."""
    hits = [h for h in sorted((REPO / "venv").glob("lib/python*/site-packages/**/LLVMDiscoPoP*")) if h.is_file()]
    return hashlib.sha256(hits[0].read_bytes()).hexdigest() if hits else None


def trial_dir(spec: str, arm: str) -> Path:
    run, _, rest = spec.partition(":")
    bench, _, rep = rest.partition("@")
    root = campaign.find_run(run)
    if root is None:
        sys.exit(f"run {run} is not in the archive")
    hits = sorted(root.glob(f"benchmarks/{bench}/{arm}/*/rep{rep}/trial.json"))
    if len(hits) != 1:
        sys.exit(f"{spec}: {len(hits)} trial(s) of arm {arm}")
    return hits[0].parent


def rebuild(trial: Path, name: str, patch: Path, dst: Path) -> Optional[str]:
    """The candidate's file: the trial's original with the saved patch applied. None when it does not apply."""
    r = subprocess.run(["patch", "-s", "-o", str(dst), str(trial / "original" / name), "-i", str(patch)],
                       capture_output=True, text=True)
    if r.returncode != 0 or not dst.is_file():
        dst.unlink(missing_ok=True)
        return None
    return dst.read_text()


def cmd_replay(a: argparse.Namespace) -> int:
    harness_include.install()
    a.out = a.out.resolve()
    (a.out / "candidates").mkdir(parents=True, exist_ok=True)
    (a.out / "finals").mkdir(exist_ok=True)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    specs = [s for s in a.trials.split(",") if s]
    manifest: Dict[str, Any] = {"tool": "candidate_replay.py replay", "commit": head, "host": platform.node(),
                                "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "arm": a.arm, "trials": specs,
                                "discopop_pass_sha256": pass_digest()}
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    results = a.out / "results.jsonl"
    done: Dict[str, Dict[str, Any]] = {}
    if results.exists():
        done = {r["label"]: r for r in map(json.loads, filter(str.strip, results.read_text().splitlines()))}
    seen: Dict[str, str] = {r["sha256"]: r["label"] for r in done.values() if r.get("sha256") and not r.get("same_as")}
    for spec in specs:
        d = trial_dir(spec, a.arm)
        t = json.loads((d / "trial.json").read_text())
        bench, rep = str(t["benchmark"]), int(t["repeat"])
        name = list(t.get("editable") or [Path(str(t.get("source") or "")).name])[0]
        loop = bench.split("/")[1]
        cands = [json.loads(ln) for ln in (d / "agent_patches" / "candidates.jsonl").read_text().splitlines() if ln.strip()]
        for c in cands:
            patch = d / "agent_patches" / str(c["patch"])
            added = [ln for ln in patch.read_text().splitlines() if ln.startswith("+") and not ln.startswith("+++")]
            if c.get("stage") != "accepted" or any(PRAGMA.match(ln) for ln in added):
                continue
            label = f"replay_{loop}_r{rep}_c{int(c['n']):02d}"
            if label in done:
                continue
            rec: Dict[str, Any] = {"label": label, "trial": str(d.relative_to(campaign.RESULTS)), "benchmark": bench,
                                   "repeat": rep, "candidate": int(c["n"]), "harness_outcome": t.get("outcome")}
            src = a.out / "candidates" / f"{label}.c"
            text = rebuild(d, name, patch, src)
            if text is None:
                rec["result"] = "PATCH_DOES_NOT_APPLY"      # a later rewrite on top of an earlier, kept one
            else:
                rec["sha256"] = hashlib.sha256(text.encode()).hexdigest()
                rec["is_shipped_rewrite"] = ceiling.strip_pragmas(text) == ceiling.strip_pragmas((d / "final" / name).read_text())
                if rec["sha256"] in seen:
                    rec.update(result="SAME_PROGRAM", same_as=seen[rec["sha256"]])
                else:
                    seen[rec["sha256"]] = label
                    try:
                        r = ceiling.run_one(bench, a.out, REPO, a.timeout, speed=True, source=src)
                    except subprocess.TimeoutExpired:
                        r = {"result": "TIMEOUT"}
                    rec.update({k: r.get(k) for k in ("result", "candidates", "applied", "rejected_by", "dropped_slower",
                                                      "marginals", "settle_ok", "seconds", "detail")})
                    if r.get("result") == "KEPT":
                        work = a.out / (bench.replace("/", "_") + f"@{src.stem}")
                        shutil.copy2(work / name, a.out / "finals" / f"{label}.c")
            with results.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            print(f"{label}  ({rec['harness_outcome']}{', the shipped rewrite' if rec.get('is_shipped_rewrite') else ''}): "
                  f"{rec['result']}" + (f"  pragmas kept {rec.get('applied')}, rejected by {rec.get('rejected_by')}, "
                                        f"marginals {rec.get('marginals')}" if "applied" in rec else "")
                  + (f"  = {rec['same_as']}" if rec.get("same_as") else ""), flush=True)
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return 0


def cmd_verify(a: argparse.Namespace) -> int:
    a.out = a.out.resolve()
    py = str(REPO / "venv" / "bin" / "python")
    verdicts = a.out / "verdicts.jsonl"
    done = set()
    if verdicts.exists():
        done = {json.loads(ln)["label"] for ln in verdicts.read_text().splitlines() if ln.strip()}
    recs: List[Dict[str, Any]] = []
    for results in sorted(a.out.glob("**/results.jsonl")):
        for ln in results.read_text().splitlines():
            if ln.strip():
                r = json.loads(ln)
                final = results.parent / "finals" / f"{r['label']}.c"
                if r.get("result") == "KEPT" and final.is_file() and r["label"] not in done:
                    recs.append({**r, "final": str(final)})
    for r in recs:
        bench = str(r["benchmark"])
        proc = subprocess.run([py, "agent/benchmark", "verify-source", bench, "--label", r["label"], "--source", r["final"],
                               "--run-id", a.run_id, "--threads", a.threads, "--repeats", str(a.repeats)],
                              cwd=HARNESS_ROOT, capture_output=True, text=True)
        tj = AGENT_DIR / "runs" / a.run_id / "benchmarks" / bench / r["label"] / "none" / "rep1" / "trial.json"
        out: Dict[str, Any] = {"label": r["label"], "benchmark": bench, "returncode": proc.returncode}
        if tj.is_file():
            t = json.loads(tj.read_text())
            par = (t.get("verify") or {}).get("par") or {}
            out.update(outcome=t.get("outcome"), pragmas=t.get("pragmas_in_final"),
                       speedups={k: v.get("speedup") for k, v in par.items()})
        else:
            out["error"] = (proc.stdout + proc.stderr)[-300:]
        with verdicts.open("a") as f:
            f.write(json.dumps(out) + "\n")
        print(f"{r['label']}: {out.get('outcome') or 'NO TRIAL'}  {out.get('speedups') or out.get('error')}", flush=True)
    print(f"{len(recs)} finished file(s) verified into {a.run_id}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("replay", help="hand every accepted pragma-free rewrite of the trials to the pipeline")
    sp.add_argument("--trials", required=True, help="comma-separated RUN:BENCHMARK@REPEAT of archived trials")
    sp.add_argument("--arm", required=True)
    sp.add_argument("--out", type=Path, required=True)
    sp.add_argument("--timeout", type=int, default=3600)
    sp.set_defaults(func=cmd_replay)
    sp = sub.add_parser("verify", help="the harness's verdict on every finished file the replay kept")
    sp.add_argument("--out", type=Path, required=True, help="the replay's --out, or the directory above several")
    sp.add_argument("--run-id", required=True)
    sp.add_argument("--threads", default="6,12")
    sp.add_argument("--repeats", type=int, default=5)
    sp.set_defaults(func=cmd_verify)
    a = ap.parse_args()
    return int(a.func(a))


if __name__ == "__main__":
    sys.exit(main())
