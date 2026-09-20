#!/usr/bin/env python3
"""T0.11 — the class of every benchmark, from several independent profile draws.

A benchmark's CLASS is what DiscoPoP plus the gate does on it with no model at all:

  R  needs restructuring   no draw reaches a verified parallel program
  A  parallel as written   the majority of draws do
  D  must decline          a genuine recurrence — R by measurement, and the reference
                           solution IS the sequential program (declared in the package's
                           `restructuring_class`, not inferred here)

Why several draws rather than several repeats of one: a run profiles each benchmark ONCE, and
DiscoPoP's answer depends on the profile it draws — `polybench/lu` gave 0.21x on the server and
3.4x on the Mac for the same kernel. Repeats inside a run share one profile, so they are not
independent; separate runs are.

A draw that ends `PROFILE_ERROR` is NOT evidence that DiscoPoP finds nothing — it is evidence
that DiscoPoP could not run, which is a different thing (D26) and the commonest cause here is
the random explorer stall (L5). Such draws are reported and excluded from the majority, and a
benchmark with no usable draw is left undetermined rather than filed as R.

    agent/tools/class_table.py t0_11_classes_a t0_11_classes_b t0_11_classes_c [--out DIR]
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

AGENT_DIR = Path(__file__).resolve().parent.parent
PARALLEL = {"FASTER", "parallel-not-faster", "parallel-speed-not-measurable"}
NO_DATA = {"PROFILE_ERROR", "VERIFY_FAILED", "AGENT_ERROR", "AGENT_TIMEOUT"}


def _speedup(t: dict) -> Optional[float]:
    par = (t.get("verify") or {}).get("par") or {}
    vals = [p.get("speedup") for p in par.values() if p.get("speedup")]
    return max(vals) if vals else None


def _declared_class(bench: str) -> Optional[str]:
    """What the package itself says it is, where it says anything (TSVC only)."""
    meta = AGENT_DIR / "prepared" / f"{bench}" / "meta.json"
    if not meta.exists():
        return None
    try:
        d = json.loads(meta.read_text())
    except (OSError, ValueError):
        return None
    return {"restructure": "R", "annotate": "A", "decline": "D"}.get(d.get("restructuring_class", ""))


def collect(runs: List[str], root: Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for run in runs:
        for p in sorted((root / run / "benchmarks").glob("**/trial.json")):
            t = json.loads(p.read_text())
            rec = out.setdefault(t["benchmark"], {"draws": {}})
            rec["draws"][run] = {"outcome": t["outcome"], "speedup": _speedup(t),
                                 "pragmas": t.get("pragmas_in_final"),
                                 "load": (t.get("host_load_start") or [None])[0],
                                 "explore_s": (t.get("profile") or {}).get("explore_s")}
    for bench, rec in out.items():
        draws = rec["draws"]
        usable = {k: v for k, v in draws.items() if v["outcome"] not in NO_DATA}
        par = sum(1 for v in usable.values() if v["outcome"] in PARALLEL)
        rec["draws_total"], rec["draws_usable"], rec["draws_parallel"] = len(draws), len(usable), par
        rec["declared"] = _declared_class(bench)
        if not usable:
            rec["class"] = "?"                       # DiscoPoP never ran: undetermined, not R
        elif par * 2 > len(usable):
            rec["class"] = "A"
        elif par == 0:
            rec["class"] = "D" if rec["declared"] == "D" else "R"
        else:
            rec["class"] = "split"                   # the draws disagree: report, do not average
        sp = [v["speedup"] for v in usable.values() if v["speedup"]]
        rec["median_speedup"] = round(statistics.median(sp), 3) if sp else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--root", type=Path, default=AGENT_DIR / "runs")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    data = collect(a.runs, a.root)
    if not data:
        sys.exit(f"no trials found under {a.root} for {', '.join(a.runs)}")

    counts: Counter[str] = Counter(r["class"] for r in data.values())
    by_suite: Dict[str, Counter[str]] = {}
    for b, r in data.items():
        by_suite.setdefault(b.split("/")[0], Counter())[r["class"]] += 1

    print(f"{'benchmark':26s} {'class':6s} {'draws':>12s} {'DiscoPoP alone':>16s}  outcomes")
    for b in sorted(data, key=lambda x: (data[x]["class"], x)):
        r = data[b]
        outs = ", ".join(f"{v['outcome']}" for v in r["draws"].values())
        sp = f"{r['median_speedup']:.2f}x" if r["median_speedup"] else "—"
        mism = "  (package says " + str(r["declared"]) + ")" if r["declared"] and r["declared"] != r["class"] else ""
        draws = f"{r['draws_usable']}/{r['draws_total']}"
        print(f"{b:26s} {r['class']:6s} {draws:>12s} {sp:>16s}  {outs}{mism}")
    print(f"\ntotals: {dict(counts)}")
    for suite, c in sorted(by_suite.items()):
        print(f"   {suite:14s} {dict(c)}")

    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        with (a.out / "classes.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["benchmark", "class", "declared_class", "draws_total", "draws_usable",
                        "draws_parallel", "median_speedup_discopop_alone", "outcomes"])
            for b in sorted(data):
                r = data[b]
                w.writerow([b, r["class"], r["declared"] or "", r["draws_total"], r["draws_usable"],
                            r["draws_parallel"], r["median_speedup"] or "",
                            ";".join(v["outcome"] for v in r["draws"].values())])
        (a.out / "classes.json").write_text(json.dumps(
            {"runs": a.runs, "totals": dict(counts), "benchmarks": data}, indent=2, sort_keys=True) + "\n")
        print(f"\nwrote {a.out / 'classes.csv'} and {a.out / 'classes.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
