#!/usr/bin/env python3
"""The gate's race stages over programs that never went through the gate — no model.

The harness verification judges every trial by its OUTPUT: the full value dump on the shipped
and the perturbed input, and a digest repeated five times at each of two thread counts. It
runs neither ThreadSanitizer nor a schedule matrix; only the agent's gate does. So a trial
the harness scores FASTER from an arm WITHOUT a gate (`bare_llm`, E1-bare) is output-checked,
and one from the agent is output-checked AND race-checked — not the same claim. This tool
closes the gap: it hands each archived program to the agent's own gate, exactly as Phase B
hands it a pragma — `validate(mode="safety")`: apply, compile, the `-fopenmp` build under
ThreadSanitizer, the schedule matrix (threads 1/2/4 × static / dynamic,1 / guided, the
program's loops given `schedule(runtime)`), and the output against the ORIGINAL on the shipped
input and on `--check-input 7` — with the reference and the numerical noise floor captured
the way the agent captures them at the start of a run.

The patch is original → final of the archived trial, so what is judged is exactly the file
the harness verified. `validate()` is called directly, not through the agent's cache wrapper:
that wrapper re-runs a TSan failure with the race check OFF when it looks like the macOS
barrier artefact, which would hide the very thing this check is for. Whether that heuristic
would have fired is recorded instead. Run it where archer is found (the server, LLVM 20) —
without archer TSan cannot see OpenMP's barriers; the manifest records which was used.

A positive control belongs in every run of this tool: the agent's own parallel programs from
the same loops passed this gate once already, so they must come out clean here; one that does
not means the tool or the toolchain is wrong, not the program.

    venv/bin/python evaluation/agent/tools/race_check.py --runs e1_bare_a,e1_bare_b --arm bare_llm \
        --out evaluation/agent/analysis/race_check_e1b/bare
    venv/bin/python evaluation/agent/tools/race_check.py --runs e1_r_a,e1_r_b --arm default --suite tsvc \
        --outcomes FASTER,parallel-not-faster --out evaluation/agent/analysis/race_check_e1b/control
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
import campaign  # noqa: E402

CHECK_INPUTS = [["7"]]        # E1's `--check-input 7`; the harness passes no other argument


def _trials(runs: List[str], arm: str, suite: Optional[str], outcomes: Optional[List[str]],
            only: Optional[List[str]] = None) -> List[Path]:
    out: List[Path] = []
    for run in runs:
        root = campaign.find_run(run)
        if root is None:
            sys.exit(f"run {run} is not in the archive")
        for p in sorted(root.glob(f"benchmarks/*/*/{arm}/*/rep*/trial.json")):
            t = json.loads(p.read_text())
            if suite and not str(t.get("benchmark", "")).startswith(suite + "/"):
                continue
            if outcomes and t.get("outcome") not in outcomes:
                continue
            if only and f"{t.get('benchmark')}@{t.get('repeat')}" not in only and str(t.get("benchmark")) not in only:
                continue
            out.append(p.parent)
    return out


def _unified_diff(original: Path, final: Path) -> str:
    # `diff -u` rather than difflib: it writes the "\ No newline at end of file" markers
    # that `patch` needs, and it is what the gate's own patches look like.
    r = subprocess.run(["diff", "-u", str(original), str(final)], capture_output=True, text=True)
    return r.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, help="comma-separated archived runs")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--suite", default=None)
    ap.add_argument("--outcomes", default=None, help="only trials the harness gave one of these outcomes")
    ap.add_argument("--only", default=None, help="comma-separated benchmarks or benchmark@repeat (a smoke test)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    from discopop_agent.gate.equivalence import numerical_noise_floor
    from discopop_agent.gate.timing import capture_reference
    from discopop_agent.gate.toolchain import _find_clangpp, find_archer
    from discopop_agent.gate.tsan import _is_omp_barrier_false_positive
    from discopop_agent.gate.validate import validate

    runs = [r for r in a.runs.split(",") if r]
    outcomes = [o for o in a.outcomes.split(",") if o] if a.outcomes else None
    only = [o for o in a.only.split(",") if o] if a.only else None
    trials = _trials(runs, a.arm, a.suite, outcomes, only)
    a.out.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    manifest: Dict[str, Any] = {
        "tool": "race_check.py", "commit": head, "host": platform.node(), "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "runs": runs, "arm": a.arm, "suite": a.suite, "outcomes": outcomes, "trials": len(trials),
        "clangpp": _find_clangpp(), "archer": find_archer(),
        "cpus_available": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count(),
        "gate": "validate(mode='safety'): apply, compile, -fopenmp + TSan, schedule matrix, output vs original",
        "check_inputs": CHECK_INPUTS,
    }
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"{len(trials)} trial(s); clang++ {manifest['clangpp']}; archer {manifest['archer'] or 'NOT FOUND'}")
    if not manifest["archer"]:
        print("  [warn] no archer: TSan cannot see OpenMP's barriers here — run this on the server")

    results_path = a.out / "results.jsonl"
    done = set()
    if results_path.exists():
        done = {json.loads(l)["trial"] for l in results_path.read_text().splitlines() if l.strip()}
    floors: Dict[str, float] = {}
    for i, d in enumerate(trials, 1):
        t = json.loads((d / "trial.json").read_text())
        key = str(d.relative_to(campaign.RESULTS))
        if key in done:
            continue
        rec: Dict[str, Any] = {"trial": key, "benchmark": t.get("benchmark"), "arm": t.get("arm"),
                               "repeat": t.get("repeat"), "harness_outcome": t.get("outcome")}
        t0 = time.time()
        with tempfile.TemporaryDirectory(prefix="race_check_") as tmp:
            src = Path(tmp) / str(t.get("source") or "program.c")
            shutil.copy2(d / "original.c", src)
            diff = _unified_diff(src, d / "final.c")
            if not diff:
                rec.update(verdict="unchanged")
            else:
                ref_out, _ref_t, ref_pairs = capture_reference(str(src), None, extra_inputs=CHECK_INPUTS)
                sha = hashlib.sha256(src.read_bytes()).hexdigest()
                if sha not in floors:
                    floors[sha] = numerical_noise_floor(str(src), None, extra_inputs=CHECK_INPUTS).value
                res = validate(diff, str(src), reference_output=ref_out, reference_outputs=ref_pairs,
                               binary_args=None, mode="safety", noise_floor=floors[sha], stress=True)
                barrier_fp = (not res.passed and res.stage == "tsan"
                              and _is_omp_barrier_false_positive(res.diagnostic, src.read_text() + "\n" + diff))
                rec.update(verdict="clean" if res.passed else res.stage, passed=res.passed, stage=res.stage,
                           diagnostic=res.diagnostic[:2000], skipped_stages=res.skipped_stages,
                           evidence={k: v for k, v in res.evidence.items()}, noise_floor=floors[sha],
                           barrier_heuristic_would_fire=barrier_fp, reference_inputs=len(ref_pairs or []))
        rec["seconds"] = round(time.time() - t0, 1)
        with results_path.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        print(f"[{i}/{len(trials)}] {rec['benchmark']} rep{rec['repeat']} ({rec['harness_outcome']}): "
              f"{rec['verdict']}  {rec['seconds']} s", flush=True)
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
