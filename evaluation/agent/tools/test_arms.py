#!/usr/bin/env python3
"""Every arm in arms.json runs what it declares, and every experiment's arms differ in exactly
its variable.

Part 1 — declarations, on a timeable AND on an untimeable kernel.

The check the runner makes before a launch (`verify_arm_settings`, D24), made here for ALL arms
at once, so a stale declaration is found when it is written, not when its experiment is due.
Three things it would have caught on 2026-09-21, all of which a smoke on two timeable
benchmarks with one arm could not:

  * `discopop_capability` still declared `fast_refresh: true` after D27 changed the default;
  * both no-evidence arms of E2 were refused, because `--print-config` printed an empty set as
    the string 'set()' where the arm declares `[]`;
  * the verification looked at the run's FIRST benchmark only, so an untimeable kernel listed
    first (the harness switches the speed check off for it) refused every arm of the run.

    venv/bin/python evaluation/agent/tools/test_arms.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "shared"))
import cli  # noqa: E402


# Settings that say WHERE a run happens, not WHAT it does; never an experiment's variable.
PLUMBING = {"source_file", "discopop_dir", "api_key", "api_base", "output_dir", "project", "verbose",
            "exclude_functions", "check_inputs", "reprofil_args", "dry_run", "profile_only", "model"}


def _resolved(name: str, spec: dict, repo: Path, benchmark: str) -> dict:
    """The agent's FULL resolved configuration for this arm on this benchmark."""
    import os
    import subprocess
    cmd = [str(repo / "venv" / "bin" / "python"), "-m", "discopop_agent", "--discopop-dir", ".",
           "--source-file", "x.c", *cli._common_flags(), *spec.get("flags", []),
           *cli._timing_flags(spec, benchmark), "--print-config"]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          env={**os.environ, **cli._agent_env(repo)}, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"{name}: {(proc.stderr or proc.stdout).strip().splitlines()[-1:]}")
    out: dict = json.loads(proc.stdout)
    return out


def check_experiments(doc: dict, repo: Path, benchmark: str) -> int:
    """The arms of an experiment differ in EXACTLY its variable.

    Nothing more: any other differing setting is a confound — D22 (the speed check became the
    default) silently confounded four experiments this way, and D27 did it to E2, whose cells
    carried a pinned --fast-refresh their baseline did not. Nothing less: a variable that does
    not vary means the arms cannot differ. Compared on the agent's FULL resolved configuration,
    not on the keys an arm happens to declare.
    """
    arms, failures = doc["arms"], 0
    for exp, spec in doc.get("experiments", {}).items():
        names = spec["arms"]
        missing = [n for n in names if n not in arms]
        if missing:
            print(f"  [FAIL] {exp}: unknown arm(s) {missing}")
            failures += 1
            continue
        cfg = {n: _resolved(n, arms[n], repo, benchmark) for n in names}
        keys = sorted({k for c in cfg.values() for k in c} - PLUMBING)
        differing = [k for k in keys
                     if len({json.dumps(cfg[n].get(k), sort_keys=True) for n in names}) > 1]
        allowed = set(spec["variable"]) | set(spec.get("consequences", []))
        confounds = [k for k in differing if k not in allowed]
        inert = [k for k in spec["variable"] if k not in differing] if len(names) > 1 else []
        dupes = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]
                 if all(cfg[a].get(k) == cfg[b].get(k) for k in keys)]
        ok = not (confounds or inert or dupes)
        print(f"  [{'pass' if ok else 'FAIL'}] {exp}: {len(names)} arm(s) differ in {differing or 'nothing'}")
        for k in confounds:
            print(f"         CONFOUND  {k}: " + ", ".join(f"{n}={cfg[n].get(k)!r}" for n in names))
        for k in inert:
            print(f"         the variable `{k}` does not vary across the arms")
        for a, b in dupes:
            print(f"         `{a}` and `{b}` resolve to the same configuration")
        failures += 0 if ok else 1
    return failures


def main() -> int:
    doc = json.loads((HERE.parent / "arms.json").read_text())
    arms = doc["arms"]
    repo = cli._agent_repo() if hasattr(cli, "_agent_repo") else HERE.parent.parent.parent
    sizes = json.loads(cli.KERNEL_SIZES_FILE.read_text())
    timeable = next((b for b in ("polybench/2mm",) if cli._timing_size(b)), None)
    untimeable = next((b for b in ("polybench/bicg", "polybench/trisolv") if cli._timing_size(b) is None), None)
    if not timeable or not untimeable:
        print(f"FAIL: need one timeable and one untimeable kernel in {cli.KERNEL_SIZES_FILE.name} "
              f"({len(sizes)} entries)")
        return 1
    failures = 0
    for order in ([untimeable, timeable], [timeable, untimeable]):
        problems = cli.verify_arm_settings(list(arms), arms, Path(repo), order)
        tag = "pass" if not problems else "FAIL"
        print(f"  [{tag}] {len(arms)} arms, benchmarks in the order {order}")
        for p in problems:
            print(f"         {p}")
        failures += len(problems)
    print()
    failures += check_experiments(doc, Path(repo), timeable)
    print("\nALL PASS" if not failures else f"\nFAILURES: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
