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


def run_one(loop: str, out: Path, repo: Path, timeout: int, speed: bool = True) -> Dict[str, object]:
    # `s211` is a TSVC loop; `rodinia-3.1/hotspot` names any package that has an expert
    # reference: reference_solutions/<suite>/<kernel>.<ext> (one file — for a project it
    # replaces the unit of that name) or reference_solutions/<suite>/<kernel>/ (several files,
    # each replacing its namesake: LLNL's LULESH).
    bench = loop if "/" in loop else f"tsvc/{loop}"
    bench_dir = AGENT_DIR / "prepared" / bench
    meta = json.loads((bench_dir / "meta.json").read_text())
    proj = cli._project_of(bench_dir)
    ext = Path(meta["file"]).suffix
    ref_root = AGENT_DIR / "reference_solutions" / bench.split("/")[0]
    ref_dir, ref = ref_root / bench.split("/")[1], ref_root / f"{bench.split('/')[1]}{ext}"
    work = out / bench.replace("/", "_")
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    env = {**os.environ, **cli._agent_env(repo)}
    py = str(repo / "venv" / "bin" / "python")
    t0 = time.time()
    if proj is None:
        src = work / Path(meta["file"]).name
        text = ref.read_text()
        n_expert = sum(1 for l in text.splitlines() if PRAGMA.match(l))
        src.write_text(strip_pragmas(text))
        rec: Dict[str, object] = {"loop": loop, "expert_pragmas": n_expert}
        prof = subprocess.run([py, "-c",
                               "import sys; from pathlib import Path; from discopop_agent.profiling import _reprofil; "
                               "sys.exit(0 if _reprofil(sys.argv[1], Path('.discopop'), None) else 1)", src.name],
                              cwd=work, env=env, capture_output=True, text=True, timeout=timeout)
        if prof.returncode != 0:
            rec.update(result="PROFILE_ERROR", detail=(prof.stdout + prof.stderr)[-300:])
            return rec
        target = ["--source-file", src.name]
    else:
        # A project: the package with the expert's files laid over it, their pragmas stripped,
        # profiled exactly as the harness profiles a project (through the unity unit).
        staged = out / "_staged" / bench.replace("/", "_")
        shutil.rmtree(staged, ignore_errors=True)
        cli._copy_tree(bench_dir, staged)
        shutil.copy2(bench_dir / "meta.json", staged / "meta.json")   # _copy_tree takes the program only
        given = ([f for f in sorted(ref_dir.rglob("*")) if f.is_file()] if ref_dir.is_dir() else [ref])
        n_expert = 0
        for f in given:
            rel = f.relative_to(ref_dir) if ref_dir.is_dir() else Path(meta["file"]).name
            text = f.read_text(errors="replace")
            n_expert += sum(1 for l in text.splitlines() if PRAGMA.match(l))
            (staged / rel).write_text(strip_pragmas(text) if f.suffix in (".c", ".cc", ".cpp") else text)
        rec = {"loop": loop, "expert_pragmas": n_expert}
        prof_rec = cli.profile_once(staged, Path(meta["file"]).name, work, repo, timeout)
        if prof_rec.get("error"):
            rec.update(result="PROFILE_ERROR", detail=str(prof_rec["error"])[-300:])
            return rec
        target = cli._project_agent_flags(proj)
    size = cli._timing_size(bench)
    # `speed=False`: the SAFETY ceiling only. Speed belongs on the campaign's server at the
    # kernel's timing size (T0.10 measured the expert versions there); on a laptop, or with
    # anything else running, a timing verdict masks the question this instrument asks —
    # whether the gate rejects CORRECT code.
    flags = [*cli._common_flags(), "--budget", "0",
             *([f"--timing-cflags=-D{size}_DATASET"] if size and speed else ["--no-require-speedup"])]
    cmd = [py, "-m", "discopop_agent", *target, "--discopop-dir", ".discopop",
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
    ap.add_argument("--no-speed", action="store_true",
                    help="safety ceiling only: run the gate without its speed check")
    a = ap.parse_args()
    classes = json.loads((AGENT_DIR / "config" / "benchmark_classes.json").read_text())["classes"]
    cls = {(b.split("/")[1] if b.startswith("tsvc/") else b): c for c, bs in classes.items() for b in bs}
    loops = a.loops or sorted(p.stem for p in (AGENT_DIR / "reference_solutions" / "tsvc").glob("*.c"))
    a.out.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, object]] = []
    for loop in loops:
        try:
            rec = run_one(loop, a.out, a.agent_repo.resolve(), a.timeout, speed=not a.no_speed)
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
