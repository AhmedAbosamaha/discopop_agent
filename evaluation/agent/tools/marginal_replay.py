#!/usr/bin/env python3
"""Replay the agent's Phase-B speed check on archived states, at several thread counts — no model.

In E1, 18 of the 44 class-R TSVC trials that ended `no-change` had a correct rewrite whose
DiscoPoP pragmas passed every safety stage and were then dropped by Phase B's speed check
("marginal 0.62–0.98× — costs more than it saves"), while the model alone's comparable
programs were measured 1.3–3× faster by the harness. The two measurements differ in how they
time: the agent's `measure_marginal` runs the whole program built at the kernel's TIMING size
with every core the lane has (24 on a pinned node of the server, OMP_NUM_THREADS unset), the
harness times the kernel region at the VERIFICATION size at 6 and 12 threads. This tool asks
whether the verdict depends on that: it rebuilds, from a trial's archived patches, the state
Phase B measured each pragma against (the original plus the accepted Phase-A rewrite) and the
state with the pragma, and calls the agent's own `measure_marginal` on the pair — same
function, same pairs, same timing flags — once per thread setting. It also times the rewrite
with ALL its safety-passing pragmas together against the original, the comparison Settle makes.

    venv/bin/python evaluation/agent/tools/marginal_replay.py e1_r_b:tsvc/s281@2 e1_r_a:tsvc/s121@1 \
        --threads 6,12,all --out evaluation/agent/analysis/marginal_replay
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
import campaign  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_include  # noqa: E402
harness_include.install()   # every build finds prepared/_harness (D39)


def _trial_dir(spec: str, arm: str) -> Path:
    run, rest = spec.split(":", 1)
    bench, rep = rest.split("@")
    root = campaign.find_run(run)
    if root is None:
        sys.exit(f"run {run} is not in the archive")
    hits = sorted((root / "benchmarks" / bench / arm).glob(f"*/rep{rep}"))
    if not hits:
        sys.exit(f"no trial {spec} ({arm})")
    return hits[0]


def _apply(text: str, patch: Path, name: str) -> str:
    with tempfile.TemporaryDirectory(prefix="replay_") as tmp:
        f = Path(tmp) / name
        f.write_text(text)
        # Some archived patches end without a newline, which `patch` refuses ("unexpectedly
        # ends in middle of line"); the agent's own _apply writes them back with one.
        p = Path(tmp) / "change.patch"
        body = patch.read_text()
        p.write_text(body if body.endswith("\n") else body + "\n")
        r = subprocess.run(["patch", "-s", "--forward", str(f), str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"{patch.name} does not apply: {r.stdout}{r.stderr}")
        return f.read_text()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="+", help="run:suite/benchmark@repeat")
    ap.add_argument("--arm", default="default")
    ap.add_argument("--threads", default="6,12,all", help="`all` = OMP_NUM_THREADS unset, as in the agent's runs")
    ap.add_argument("--pairs", type=int, default=5, help="as measure_marginal's default")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    from discopop_agent.gate.timing import measure_marginal

    a.out.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    settings = [s for s in a.threads.split(",") if s]
    manifest: Dict[str, Any] = {"tool": "marginal_replay.py", "commit": head, "host": platform.node(),
                                "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "threads": settings, "pairs": a.pairs,
                                "cpus_available": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity")
                                else os.cpu_count(), "specs": a.specs}
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    results = a.out / "results.jsonl"
    base_env = os.environ.get("OMP_NUM_THREADS")
    for spec in a.specs:
        d = _trial_dir(spec, a.arm)
        t = json.loads((d / "trial.json").read_text())
        name = str(t.get("source"))
        cmd = [str(x) for x in t.get("agent_cmd") or []]
        flags = [x.split("=", 1)[1] for x in cmd if x.startswith("--timing-cflags=")]
        cands = [json.loads(l) for l in (d / "agent_patches" / "candidates.jsonl").read_text().splitlines() if l.strip()]
        original = (d / "original.c").read_text()
        # A Phase-A candidate can pass the gate and still be reverted ("DiscoPoP sees a
        # pattern, but no pragma it generates for it can run — reverting"); candidates.jsonl
        # does not say so, the log does, in the same order. Only the kept ones are the base.
        phase_a_log = (d / "agent.log").read_text().split("PHASE B")[0]
        verdicts: List[bool] = []
        for line in phase_a_log.splitlines():
            if "Quality gate PASSED" in line:
                verdicts.append(True)
            elif "reverting" in line and verdicts:
                verdicts[-1] = False
        passed_a = [c for c in cands if c["phase"] == "A" and c["passed"]]
        if len(passed_a) != len(verdicts):
            sys.exit(f"{spec}: {len(passed_a)} passing Phase-A candidates but {len(verdicts)} in the log")
        rewrite = original
        for c, kept in zip(passed_a, verdicts):
            if kept:
                rewrite = _apply(rewrite, d / "agent_patches" / c["patch"], name)
        pragmas = [c for c in cands if c["phase"] == "B" and c["passed"]]
        states: List[Dict[str, Any]] = []
        allp = rewrite
        for c in pragmas:
            states.append({"what": f"pragma {c['region_id']} ({c.get('pattern_type')}) vs the rewrite",
                           "before": rewrite, "after": _apply(rewrite, d / "agent_patches" / c["patch"], name)})
            allp = _apply(allp, d / "agent_patches" / c["patch"], name)
        if len(pragmas) > 1:
            states.append({"what": "all safe pragmas together vs the rewrite", "before": rewrite, "after": allp})
        if pragmas:
            states.append({"what": "rewrite + all safe pragmas vs the ORIGINAL (Settle's question)",
                           "before": original, "after": allp})
        (a.out / f"{spec.replace(':', '_').replace('/', '_')}_final.c").write_text(allp)
        for st in states:
            rec: Dict[str, Any] = {"spec": spec, "harness_outcome": t.get("outcome"), "what": st["what"],
                                   "timing_flags": flags, "ratio": {}}
            with tempfile.TemporaryDirectory(prefix="replay_src_") as tmp:
                src = Path(tmp) / name
                src.write_text(original)
                for s in settings:
                    if s == "all":
                        os.environ.pop("OMP_NUM_THREADS", None)
                    else:
                        os.environ["OMP_NUM_THREADS"] = s
                    ok, ratio, diag = measure_marginal(st["before"], st["after"], str(src),
                                                       pairs=a.pairs, extra_flags=flags or None)
                    rec["ratio"][s] = round(ratio, 3) if ok else f"failed: {diag[:200]}"
            if base_env is None:
                os.environ.pop("OMP_NUM_THREADS", None)
            else:
                os.environ["OMP_NUM_THREADS"] = base_env
            with results.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            print(f"{spec} [{t.get('outcome')}] {st['what']}: "
                  + "  ".join(f"{k}={v}" for k, v in rec["ratio"].items()), flush=True)
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
