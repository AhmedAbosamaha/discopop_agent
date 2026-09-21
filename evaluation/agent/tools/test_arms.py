#!/usr/bin/env python3
"""Every arm in arms.json runs what it declares — on a timeable AND on an untimeable kernel.

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


def main() -> int:
    arms = json.loads((HERE.parent / "arms.json").read_text())["arms"]
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
    print("\nALL PASS" if not failures else f"\nFAILURES: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
