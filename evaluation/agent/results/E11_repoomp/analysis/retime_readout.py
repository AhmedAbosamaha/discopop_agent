#!/usr/bin/env python3
"""E11 part 1 re-timed on a quiet server — the registered read-out (record §6, 6 Nov, written before the run).

For every program E11 part 1 judged, the harness's speedups at 6 and 12 threads as archived (e11_r_ep, e11_r_cg,
e11_bare, e11_ref_check) beside the same program re-timed one at a time on a quiet server (e11_retime); per setup
the median and range at 12 threads, archived and quiet; the harness outcome archived and quiet; the load average
before and after each re-timed program; and whether each re-timed program is byte for byte the archived one (the
digest `verify-source` records against the same digest of the archived files).

    python3 evaluation/agent/results/E11_repoomp/analysis/retime_readout.py \
        evaluation/agent/results/E11_repoomp/checks/e11_retime > evaluation/agent/results/E11_repoomp/analysis/retime_readout.md
    python3 ... --json evaluation/agent/results/E11_repoomp/analysis/retime_readout.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
E11 = HERE.parent
AGENT = E11.parent.parent
MODEL = "claude-sonnet-4-5-20250929"
SETUPS = [("llm_pragmas_v5", "the agent"), ("discopop_gate_v5", "DiscoPoP alone"), ("bare_llm_v4", "Sonnet 4.5 alone"),
          ("repoomp_claude", "RepoOMP's published program"), ("claude_code", "RepoOMP's Claude Code program"),
          ("expert_openmp", "NPB's OpenMP version")]
Key = Tuple[str, str, int]          # kernel, setup label, repeat


def _tree_digest(root: Path) -> str:
    """The digest `verify-source` records (cli._tree_digest): every file's relative path, size and bytes, sorted."""
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink():
            rel = str(p.relative_to(root)).encode()
            h.update(rel + b"\0" + str(p.stat().st_size).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def _speeds(t: Dict[str, Any]) -> Dict[str, Optional[float]]:
    par = (t.get("verify") or {}).get("par") or {}
    return {th: (par.get(th) or {}).get("speedup") for th in ("6", "12")}


def _source(kernel: str, label: str, rep: int) -> Path:
    if label in ("llm_pragmas_v5", "discopop_gate_v5"):
        return E11 / "runs" / f"e11_r_{kernel}" / "benchmarks" / "npbc_c1" / kernel / label / MODEL / f"rep{rep}" / "final"
    if label == "bare_llm_v4":
        return E11 / "runs" / "e11_bare" / "benchmarks" / "npbc_c1" / kernel / label / MODEL / f"rep{rep}" / "final"
    if label == "expert_openmp":
        return AGENT / "reference_solutions" / "npbc_c1" / kernel
    return AGENT / "comparison_programs" / label / "npbc_c1" / kernel


def _load(run_dir: Path) -> Dict[Key, Dict[str, Any]]:
    out: Dict[Key, Dict[str, Any]] = {}
    for t in json.loads((run_dir / "results.json").read_text())["runs"]:
        out[(t["kernel"], t["arm"], int(t.get("repeat") or 1))] = t
    return out


def build(quiet_dir: Path) -> Dict[str, Any]:
    archived: Dict[Key, Dict[str, Any]] = {}
    for run in ("e11_r_ep", "e11_r_cg", "e11_bare"):
        archived.update(_load(E11 / "runs" / run))
    archived.update(_load(E11 / "preflight" / "e11_ref_check"))
    quiet = _load(quiet_dir)
    rows: List[Dict[str, Any]] = []
    for kernel in ("ep", "cg"):
        for label, _name in SETUPS:
            reps = sorted(r for (k, l, r) in archived if k == kernel and l == label)
            for rep in reps:
                a, q = archived[(kernel, label, rep)], quiet.get((kernel, label, rep))
                src = _source(kernel, label, rep)
                rows.append({
                    "kernel": kernel, "setup": label, "repeat": rep,
                    "archived": _speeds(a), "archived_outcome": a.get("outcome"),
                    "quiet": _speeds(q) if q else None, "quiet_outcome": q.get("outcome") if q else None,
                    "load_start": q.get("host_load_start") if q else None, "load_end": q.get("host_load_end") if q else None,
                    "same_program": (q.get("candidate_sha256") == _tree_digest(src)) if q and src.exists() else None,
                })
    summary: Dict[str, Any] = {}
    for kernel in ("ep", "cg"):
        for label, _name in SETUPS:
            rs = [r for r in rows if r["kernel"] == kernel and r["setup"] == label]
            a12 = [r["archived"]["12"] for r in rs if r["archived"]["12"] is not None]
            q12 = [r["quiet"]["12"] for r in rs if r["quiet"] and r["quiet"]["12"] is not None]
            summary[f"{kernel}/{label}"] = {
                "n": len(rs), "re-timed": sum(1 for r in rs if r["quiet"]),
                "archived_median_12": round(statistics.median(a12), 2) if a12 else None,
                "archived_range_12": [min(a12), max(a12)] if a12 else None,
                "quiet_median_12": round(statistics.median(q12), 2) if q12 else None,
                "quiet_range_12": [min(q12), max(q12)] if q12 else None,
                "outcomes_changed": [r["repeat"] for r in rs if r["quiet"] and r["quiet_outcome"] != r["archived_outcome"]],
                "not_the_same_program": [r["repeat"] for r in rs if r["same_program"] is False],
            }
    loads = [x for r in rows for x in ((r["load_start"] or [None])[0], (r["load_end"] or [None])[0]) if x is not None]
    return {"rows": rows, "summary": summary, "load_1min_max": round(max(loads), 2) if loads else None,
            "load_1min_median": round(statistics.median(loads), 2) if loads else None}


def _f(x: Optional[float]) -> str:
    return "—" if x is None else f"{x:.2f}×"


def to_markdown(res: Dict[str, Any]) -> str:
    names = dict(SETUPS)
    out = ["# E11 part 1 re-timed on a quiet server — read-out", "",
           "Registered read-out (record §6, 6 Nov). Every program E11 part 1 judged, re-timed one at a time on cores "
           "0–11 (node 0's memory) through `verify-source` exactly as judged; archived beside quiet. Generated by "
           "`retime_readout.py` — do not edit.", "",
           f"Load average (1 min) before and after the re-timed programs: median {res['load_1min_median']}, "
           f"at most {res['load_1min_max']}.", "",
           "## Per setup, 12 threads", "",
           "| program | setup | trials | archived median (range) | quiet median (range) | outcome changed | not the same program |",
           "|---|---|---:|---|---|---|---|"]
    for key, s in res["summary"].items():
        kernel, label = key.split("/")
        ar = s["archived_range_12"]; qr = s["quiet_range_12"]
        out.append(f"| {kernel.upper()} | {names[label]} | {s['n']} | {_f(s['archived_median_12'])}"
                   + (f" ({_f(ar[0])}–{_f(ar[1])})" if ar and s["n"] > 1 else "")
                   + f" | {_f(s['quiet_median_12'])}" + (f" ({_f(qr[0])}–{_f(qr[1])})" if qr and s["n"] > 1 else "")
                   + f" | {', '.join('rep' + str(r) for r in s['outcomes_changed']) or 'none'}"
                   + f" | {', '.join('rep' + str(r) for r in s['not_the_same_program']) or 'none'} |")
    out += ["", "## Every program", "",
            "| program | setup | rep | archived 6 / 12 | quiet 6 / 12 | outcome archived → quiet | load before / after |",
            "|---|---|---:|---|---|---|---|"]
    for r in res["rows"]:
        q = r["quiet"] or {"6": None, "12": None}
        ls, le = [round(x, 2) if x is not None else None
                  for x in ((r["load_start"] or [None])[0], (r["load_end"] or [None])[0])]
        out.append(f"| {r['kernel'].upper()} | {names[r['setup']]} | {r['repeat']} | {_f(r['archived']['6'])} / "
                   f"{_f(r['archived']['12'])} | {_f(q['6'])} / {_f(q['12'])} | {r['archived_outcome']} → "
                   f"{r['quiet_outcome']} | {ls} / {le} |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("quiet_run", help="the archived e11_retime run directory")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    res = build(Path(a.quiet_run))
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1) + "\n")
    else:
        sys.stdout.write(to_markdown(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
