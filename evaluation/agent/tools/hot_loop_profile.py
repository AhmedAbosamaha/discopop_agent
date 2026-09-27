#!/usr/bin/env python3
"""E2-B1's measured condition 4, second half: what does DiscoPoP's profile say about the HOT LOOP? (no model)

T0.11 gives a unit's class (`class_table.py`): R when no draw of DiscoPoP alone reaches a verified
parallel program, A when most do. E2-B1 asks one thing more of each draw's profile, on the loop under
study itself (docs/e2b1/PREPARATION.md §3, condition 4):

  direction (a)  the profile NAMES the deciding dependence: DiscoPoP's Do-All detector did not report
                 the hot loop Do-All, and the dependence it recorded as the blocker
                 (`explorer/doall_prevented.json`, written by new_do_all_detector — the first blocking
                 dependence it found for the loop) is on one of the hot loop's variables
  direction (b)  the profile reports the hot loop Do-All (`explorer/patterns.json`), the deciding
                 dependence absent

The hot loop is the one the package declares (meta.json `hot_loop`: its line, and its `writes`,
`shared` and `aliases` — the hot variables). DiscoPoP names a variable as the IR does: a subscripted
access `GEPRESULT_a`, an internal-linkage global `_ZL1a`; both are reduced to the source name.

Reads each run's profile trees, `runs/<run>/profiles/<suite>/<name>/.discopop/` — which `fetch` does
NOT copy back, so run it where the run ran (the server):

    venv/bin/python evaluation/agent/tools/hot_loop_profile.py t0_11_b1_a t0_11_b1_b t0_11_b1_c [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

AGENT_DIR = Path(__file__).resolve().parent.parent
RUNS = AGENT_DIR / "runs"


def source_name(var: str) -> str:
    """DiscoPoP's variable name as the source spells it: `GEPRESULT_a` -> a, `_ZL1a` -> a."""
    v = re.sub(r"^GEPRESULT_", "", var)
    m = re.match(r"^_ZL(\d+)(\w+)$", v)
    if m and len(m.group(2)) >= int(m.group(1)):
        v = m.group(2)[:int(m.group(1))]
    return v


def _file_id(dp: Path, file_name: str) -> Optional[int]:
    fm = dp / "FileMapping.txt"
    if not fm.exists():
        return None
    for line in fm.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and Path(parts[1]).name == file_name:
            return int(parts[0])
    return None


def _line(lid: Any) -> Tuple[Optional[int], Optional[int]]:
    m = re.match(r"^(\d+):(\d+)$", str(lid))
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def judge(dp: Path, meta: Dict[str, Any]) -> Dict[str, Any]:
    hot = meta["hot_loop"]
    line = int(hot["line"])
    hot_vars: Set[str] = set(hot.get("writes") or []) | set(hot.get("shared") or []) | set(hot.get("aliases") or [])
    fid = _file_id(dp, meta["file"])
    out: Dict[str, Any] = {"line": line, "hot_vars": sorted(hot_vars), "file_id": fid}
    pats = json.loads((dp / "explorer" / "patterns.json").read_text()).get("patterns", {})
    do_all = [p for p in pats.get("do_all") or [] if _line(p.get("start_line")) == (fid, line)]
    out["do_all"] = bool(do_all)
    out["do_all_applicable"] = any(p.get("applicable_pattern", True) for p in do_all)
    prev = dp / "explorer" / "doall_prevented.json"
    recs = json.loads(prev.read_text()) if prev.exists() else []
    blockers = [r for r in recs if r.get("loop_file") == fid and r.get("loop_start") == line]
    out["blockers"] = [{"dep": str(r.get("dep_type", "")).replace("DepType.", ""),
                        "var": source_name(str(r.get("var_name", ""))),
                        "origin": str(r.get("origin", "")).replace("DepOrigin.", "")} for r in blockers]
    out["names_hot_var"] = any(b["var"] in hot_vars for b in out["blockers"])
    direction = "a" if "hidden dependence" in str(meta.get("restructuring_class")) else "b"
    out["direction"] = direction
    out["holds"] = (not out["do_all"] and out["names_hot_var"]) if direction == "a" else out["do_all"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    rows: List[Dict[str, Any]] = []
    for run_id in a.runs:
        for meta_p in sorted((RUNS / run_id / "profiles").glob("*/*/meta.json")):
            meta = json.loads(meta_p.read_text())
            if not meta.get("hot_loop"):
                continue
            dp = meta_p.parent / ".discopop"
            bench = f"{meta_p.parent.parent.name}/{meta_p.parent.name}"
            if not (dp / "explorer" / "patterns.json").exists():
                rows.append({"run": run_id, "benchmark": bench, "problem": "no explorer output in the profile"})
                continue
            rows.append({"run": run_id, "benchmark": bench, **judge(dp, meta)})
    lines = ["| benchmark | draw | dir | hot loop | Do-All on it | blocker (first found) | names a hot variable | condition 4 |",
             "|---|---|---|---:|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["benchmark"], r["run"])):
        if "problem" in r:
            lines.append(f"| `{r['benchmark']}` | {r['run']} | | | | {r['problem']} | | no data |")
            continue
        bl = ", ".join(f"{b['dep']} `{b['var']}` ({b['origin']})" for b in r["blockers"]) or "—"
        lines.append(f"| `{r['benchmark']}` | {r['run']} | {r['direction']} | {r['line']} | {'yes' if r['do_all'] else 'no'} "
                     f"| {bl} | {'yes' if r['names_hot_var'] else 'no'} | {'holds' if r['holds'] else 'FAILS'} |")
    per: Dict[str, List[bool]] = {}
    for r in rows:
        per.setdefault(r["benchmark"], []).append(bool(r.get("holds")))
    lines += ["", "| benchmark | draws | condition 4 holds |", "|---|---:|---:|"]
    lines += [f"| `{b}` | {len(v)} | {sum(v)} of {len(v)} |" for b, v in sorted(per.items())]
    text = "\n".join(lines) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text)
        a.out.with_suffix(".json").write_text(json.dumps(rows, indent=1) + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
