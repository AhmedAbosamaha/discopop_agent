#!/usr/bin/env python3
"""T0.13 — the ceiling of the `default` arm: what the pipeline does with a PERFECT rewrite.

Under the campaign's default the model restructures and DiscoPoP annotates: a rewrite is kept
only if, after it, DiscoPoP reports a pattern in the changed lines AND its pragma survives the
gate (races, schedules, output, speed) AND Settle verifies the finished file. Every smoke
before `e1_smoke5` ended `no-change`, and the fair question is whether that chain can succeed
at all — whether every code change is bound to be rejected — or whether it was the rewrites.

This asks it with no model and known ground truth. For every TSVC loop there is an EXPERT
restructuring, verified correct and faster (T0.10). Its pragmas are stripped — leaving exactly
what a perfect model would hand over under `--no-llm-pragmas` — and the agent is run on it with
`--budget 0`: DiscoPoP profiles the restructured code, Phase B pushes its pragmas through the
same gate with the campaign's flags, Settle verifies. A loop where at least one pragma is kept
is one the `default` arm CAN win; a loop where none is, no model could have won here, and the
reason (no pattern found / which gate stage rejected) says whether the fault is DiscoPoP's
analysis, the gate, or the speed at this machine.

    agent/tools/default_arm_ceiling.py [LOOP...] --out DIR [--agent-repo PATH]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

HERE = Path(__file__).resolve().parent
AGENT_DIR = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(AGENT_DIR.parent / "shared"))
import cli  # noqa: E402

PRAGMA = re.compile(r"^\s*#\s*pragma\s+omp\b")


def strip_pragmas(text: str) -> str:
    return "\n".join(l for l in text.splitlines() if not PRAGMA.match(l)) + "\n"


def run_one(loop: str, out: Path, repo: Path, timeout: int) -> Dict[str, object]:
    bench = f"tsvc/{loop}"
    ref = AGENT_DIR / "reference_solutions" / "tsvc" / f"{loop}.c"
    meta = json.loads((AGENT_DIR / "prepared" / bench / "meta.json").read_text())
    work = out / loop
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    src = work / f"{loop}.c"
    text = ref.read_text()
    n_expert = sum(1 for l in text.splitlines() if PRAGMA.match(l))
    src.write_text(strip_pragmas(text))
    env = {**os.environ, **cli._agent_env(repo)}
    py = str(repo / "venv" / "bin" / "python")
    rec: Dict[str, object] = {"loop": loop, "expert_pragmas": n_expert}
    t0 = time.time()
    prof = subprocess.run([py, "-c",
                           "import sys; from pathlib import Path; from discopop_agent.profiling import _reprofil; "
                           "sys.exit(0 if _reprofil(sys.argv[1], Path('.discopop'), None) else 1)", src.name],
                          cwd=work, env=env, capture_output=True, text=True, timeout=timeout)
    if prof.returncode != 0:
        rec.update(result="PROFILE_ERROR", detail=(prof.stdout + prof.stderr)[-300:])
        return rec
    size = cli._timing_size(bench)
    flags = [*cli._common_flags(), "--budget", "0",
             *([f"--timing-cflags=-D{size}_DATASET"] if size else ["--no-require-speedup"])]
    cmd = [py, "-m", "discopop_agent", "--source-file", src.name, "--discopop-dir", ".discopop",
           "--provider", "claude-agent-sdk", "--model", "none", *flags, "--check-input", "7",
           "--exclude-functions", ",".join(meta.get("exclude_functions") or [])]
    proc = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=timeout)
    log = proc.stdout + proc.stderr
    (work / "agent.log").write_text(log)
    rec["seconds"] = round(time.time() - t0)
    m = re.search(r"SUMMARY: (\d+) rewrite\(s\) kept\s*\|\s*(\d+) pragma\(s\) applied", log)
    applied = int(m.group(2)) if m else -1
    cands = re.search(r"PHASE B — annotate\s+\((\d+) candidate", log)
    stages = re.findall(r"gate failed at '(\w+)'", log)
    rec.update(candidates=int(cands.group(1)) if cands else 0, applied=applied,
               rejected_by={s: stages.count(s) for s in sorted(set(stages))},
               dropped_slower=log.count("DROPPED (slower)"),
               marginals=re.findall(r"marginal ([0-9.]+)×", log),
               settle_ok="finished source verified" in log,
               result=("KEPT" if applied > 0 and "finished source verified" in log
                       else "NO_PATTERN" if not cands or int(cands.group(1)) == 0
                       else "ALL_REJECTED" if applied == 0 else "UNVERIFIED"))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("loops", nargs="*")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--agent-repo", type=Path, default=AGENT_DIR.parent.parent)
    ap.add_argument("--timeout", type=int, default=3600)
    a = ap.parse_args()
    classes = json.loads((AGENT_DIR / "benchmark_classes.json").read_text())["classes"]
    cls = {b.split("/")[1]: c for c, bs in classes.items() for b in bs if b.startswith("tsvc/")}
    loops = a.loops or sorted(p.stem for p in (AGENT_DIR / "reference_solutions" / "tsvc").glob("*.c"))
    a.out.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, object]] = []
    for loop in loops:
        try:
            rec = run_one(loop, a.out, a.agent_repo.resolve(), a.timeout)
        except subprocess.TimeoutExpired:
            rec = {"loop": loop, "result": "TIMEOUT"}
        rec["class"] = cls.get(loop, "?")
        rows.append(rec)
        print(f"{loop:7s} class {rec['class']}  {rec.get('result'):13s} candidates={rec.get('candidates')} "
              f"applied={rec.get('applied')} rejected_by={rec.get('rejected_by')} slower={rec.get('dropped_slower')} "
              f"marginals={rec.get('marginals')} ({rec.get('seconds')} s)", flush=True)
        keys = ["loop", "class", "result", "expert_pragmas", "candidates", "applied", "rejected_by",
                "dropped_slower", "marginals", "settle_ok", "seconds", "detail"]
        with (a.out / "ceiling.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    kept = [r for r in rows if r.get("result") == "KEPT"]
    r_rows = [r for r in rows if r.get("class") == "R"]
    print(f"\nKEPT on {len(kept)} of {len(rows)} loops; class R: "
          f"{sum(1 for r in r_rows if r.get('result') == 'KEPT')} of {len(r_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
