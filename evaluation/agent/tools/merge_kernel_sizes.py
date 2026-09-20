#!/usr/bin/env python3
"""Merge a T0.1 run's `chosen.json` into the committed `agent/kernel_sizes.json`.

`kernel_sizes.json` is what the runner reads (`_verify_size`, `_timing_size`): per benchmark
the verification size (serial kernel ≥ 1 s), the timing size (≥ 0.25 s) and the longest
size measured. It is tracked in git, so a re-measurement goes through this script, which
prints every change before writing and records where each entry came from.

    python3 agent/tools/merge_kernel_sizes.py agent/runs/t0_1_sizes_v2/chosen.json [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parents[1]
TABLE = AGENT_DIR / "kernel_sizes.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chosen", type=Path, help="a T0.1 run's chosen.json")
    ap.add_argument("--dry-run", action="store_true", help="print the changes, write nothing")
    a = ap.parse_args()
    new = json.loads(a.chosen.read_text())
    table = json.loads(TABLE.read_text()) if TABLE.exists() else {"kernels": {}}
    kernels = table.setdefault("kernels", {})
    run = a.chosen.parent.name
    changed = added = same = 0
    for name, entry in sorted(new["kernels"].items()):
        old = kernels.get(name)
        stamped = dict(entry, source_run=run, measured=new.get("finished"), host=new.get("host"))
        if old is None:
            added += 1
            print(f"  + {name:26s} verify {entry.get('verification_size')}  timing {entry.get('timing_size')}")
        elif (old.get("verification_size"), old.get("timing_size")) != (entry.get("verification_size"), entry.get("timing_size")):
            changed += 1
            print(f"  ~ {name:26s} verify {old.get('verification_size')} -> {entry.get('verification_size')}  "
                  f"timing {old.get('timing_size')} -> {entry.get('timing_size')}  "
                  f"(longest {old.get('longest_measured', {}).get('kernel_s')} -> {entry.get('longest_measured', {}).get('kernel_s')} s)")
        else:
            same += 1
        kernels[name] = stamped
    print(f"{added} added, {changed} changed, {same} unchanged out of {len(new['kernels'])} in {run}")
    if a.dry_run:
        return 0
    table["note"] = (table.get("note", "") + f"\n{new.get('finished', '?')}: merged {run} "
                     f"({len(new['kernels'])} benchmarks, host {new.get('host')}, load at start "
                     f"{new.get('load_start')}, at end {new.get('load_end')})").strip()
    TABLE.write_text(json.dumps(table, indent=2) + "\n")
    print(f"wrote {TABLE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
