#!/usr/bin/env python3
"""E2-B1's routing pre-check: where does the agent send a candidate's hot loop? (no model)

The selection rule (record §6, 26 Sep) admits an E2-B1 candidate only when "the region reaches the
model" in every one of its three T0.11 draws; for direction (b) the measured condition is also that
DiscoPoP's own pragma for the hot loop is applied. Both are read from the agent logs of those draws
(the `discopop_capability` arm: budget 0, no model) — the same agent code decides the routing with a
model, before any model call:

  table        the "Initial candidates" table: every region's type, runtime share, tier and depth
               after the share floor (a region absent from it never reaches Phase A);
  Phase A      per region `┌─ [depth=N] <type> <id> (lines a–b)` … `└─ <OUTCOME>`: DEFERRED (Tier 1,
               DiscoPoP's pattern kept for Phase B), SKIPPED (budget exhausted = the model would be
               asked), re-queued (Tier 1 whose pragma the safety gate refused, Fix 101);
  Phase B      `┌─ pattern #N do_all @ lines a–b` … `└─ APPLIED | DROPPED`, and D41's
               `└─ APPLIED as D40 judged it`.

The HOT LOOP of a package is the one its meta.json declares (`hot_loop.line`; every E2-B1 package,
prepare_tsvc.hot_loop / prepare_bfs.hot_loop): the loop region of the table whose first line is that
line — the same loop naive_pragma.py and the coverage check use. The meta is read from the run's own
profile copy (`profiles/<benchmark>/meta.json`), else from prepared/. A package that declares none
(every one before E2-B1) falls back to the loop region with the largest measured share other than
the repetition loop (`for (int nl …)`, read from the archived source); ties go to the innermost.
Rodinia bfs needs the declaration: it has no `nl` loop, and its level loop (`do … while`) encloses
everything.

  reaches the model   the hot loop is Tier 2 at depth 0 in the table, or its Phase-A block says a
                      re-queue sent it to the model
  DiscoPoP applied    a Phase-B pattern on the hot loop's lines ended APPLIED

    agent/tools/routing_check.py t0_11_b1_a t0_11_b1_b t0_11_b1_c [--benchmarks s151,s161] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

AGENT_DIR = Path(__file__).resolve().parent.parent
RUNS = AGENT_DIR / "runs"
RESULTS = AGENT_DIR / "results"

_ROW = re.compile(r"^\s+(\d+:\d+)\s+(loop|function|block)\s+\S+\s+\S+\s+([\d.]+)%\s+(\S+)\s+(\d)\s+(\d+)\s+(.*)$")
_A_HEAD = re.compile(r"^┌─ \[depth=(\d+)\] (loop|function|block) (\d+:\d+) \(lines (\d+)–(\d+)\)")
_B_HEAD = re.compile(r"^┌─ pattern #\d+\s+\S+ @ lines (\d+)–(\d+)")
_D41_HEAD = re.compile(r"^┌─ D41: the file is the one D40 judged for (\d+:\d+)")


def _run_dir(run_id: str) -> Optional[Path]:
    """A run fetched into runs/, or archived under results/<experiment>/runs/."""
    if (RUNS / run_id).is_dir():
        return RUNS / run_id
    hits = sorted(RESULTS.glob(f"**/runs/{run_id}"))
    return hits[0] if hits else None


def parse_log(text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """The table, the Phase-A blocks and the Phase-B blocks of one agent log."""
    rows: List[Dict[str, Any]] = []
    in_table = False
    for line in text.splitlines():
        if line.strip().startswith("Region ID"):
            in_table = True
            continue
        if in_table:
            m = _ROW.match(line)
            if m:
                rid, typ, share, hot, tier, depth, name = m.groups()
                lines = re.search(r"lines (\d+)–(\d+)", name)
                rows.append({"id": rid, "type": typ, "share": float(share), "hot": hot, "tier": int(tier),
                             "depth": int(depth), "name": name.strip(),
                             "span": (int(lines.group(1)), int(lines.group(2))) if lines else None})
            elif line.startswith("=") or (rows and not line.strip()):
                in_table = False
    phase_a: List[Dict[str, Any]] = []
    phase_b: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None
    for line in text.splitlines():
        a = _A_HEAD.match(line)
        b = _B_HEAD.match(line)
        d = _D41_HEAD.match(line)
        if a:
            cur = {"kind": "A", "depth": int(a.group(1)), "type": a.group(2), "id": a.group(3),
                   "span": (int(a.group(4)), int(a.group(5))), "lines": []}
            phase_a.append(cur)
        elif b:
            cur = {"kind": "B", "span": (int(b.group(1)), int(b.group(2))), "lines": []}
            phase_b.append(cur)
        elif d:
            cur = {"kind": "D41", "id": d.group(1), "span": None, "lines": []}
            phase_b.append(cur)
        elif cur is not None and line.startswith("│"):
            cur["lines"].append(line)
        elif cur is not None and line.startswith("└─"):
            cur["outcome"] = line[2:].strip()
            cur = None
    return rows, phase_a, phase_b


def repetition_line(source: str) -> Optional[int]:
    for i, l in enumerate(source.splitlines(), 1):
        if re.match(r"\s*for \(int nl = 0;", l):
            return i
    return None


def declared_line(run_dir: Path, bench: str) -> Optional[int]:
    """The hot loop's line from the package's meta.json: the run's profile copy, else prepared/."""
    for meta in (run_dir / "profiles" / bench / "meta.json", AGENT_DIR / "prepared" / bench / "meta.json"):
        if meta.exists():
            hot = json.loads(meta.read_text()).get("hot_loop")
            return int(hot["line"]) if hot else None
    return None


def hot_loop(rows: List[Dict[str, Any]], rep_line: Optional[int],
             line: Optional[int] = None) -> Optional[Dict[str, Any]]:
    if line is not None:
        hits = [r for r in rows if r["type"] == "loop" and r["span"] is not None and r["span"][0] == line]
        return hits[0] if hits else None
    loops = [r for r in rows if r["type"] == "loop" and r["span"] is not None
             and (rep_line is None or r["span"][0] != rep_line)]
    if not loops:
        return None
    return sorted(loops, key=lambda r: (-float(r["share"]), r["span"][1] - r["span"][0]))[0]


def judge(log_text: str, source: str, line: Optional[int] = None) -> Dict[str, Any]:
    """`line`: the hot loop's declared first line (None: the largest-share rule)."""
    rows, phase_a, phase_b = parse_log(log_text)
    hot = hot_loop(rows, repetition_line(source), line)
    out: Dict[str, Any] = {"hot": None, "tier": None, "share": None, "phase_a": None,
                              "reaches_model": False, "dp_applied": False}
    if hot is None:
        if line is not None:
            out["phase_a"] = f"no loop region at the declared line {line} in the table"
        return out
    out.update(hot=hot["id"], tier=hot["tier"], share=hot["share"], span=hot["span"])
    blocks = [blk for blk in phase_a if blk.get("id") == hot["id"]]
    first = blocks[0] if blocks else None
    requeued = first is not None and any("re-queue" in l.lower() or "requeue" in l.lower() or "→ tier-2" in l.lower()
                                         for l in first["lines"])
    out["phase_a"] = first.get("outcome") if first else "not in Phase A"
    out["reaches_model"] = (hot["tier"] == 2 and hot["depth"] == 0) or (hot["tier"] == 1 and requeued)
    span = hot["span"]
    for blk in phase_b:
        outcome = str(blk.get("outcome", ""))
        if not outcome.startswith("APPLIED"):
            continue
        if blk["kind"] == "B" and blk["span"] == span:
            out["dp_applied"] = True
        if blk["kind"] == "D41" and blk.get("id") == hot["id"]:
            out["dp_applied"] = True
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--benchmarks", default="", help="short names, comma-separated (default: all)")
    ap.add_argument("--arm", default="discopop_capability")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    wanted = {b for b in a.benchmarks.split(",") if b}
    per: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for run_id in a.runs:
        rd = _run_dir(run_id)
        if rd is None:
            print(f"{run_id}: not found in runs/ or results/", file=sys.stderr)
            return 2
        for log in sorted(rd.glob(f"benchmarks/*/*/{a.arm}/*/rep*/agent.log")):
            trial = log.parent
            bench = f"{trial.parents[3].name}/{trial.parents[2].name}"
            if wanted and trial.parents[2].name not in wanted:
                continue
            src = next((p for p in (trial / "original.c", trial / "original.cpp") if p.exists()), None)
            if src is None:
                srcs = [p for p in trial.parent.parent.parent.glob("*.c")]
                src = srcs[0] if srcs else None
            verdict = judge(log.read_text(errors="replace"), src.read_text() if src else "",
                            declared_line(rd, bench))
            per.setdefault(bench, []).append((f"{run_id}/{trial.name}", verdict))
    lines = ["| benchmark | draw | hot loop | tier | share | Phase A | reaches the model | DiscoPoP applied |",
             "|---|---|---|---:|---:|---|---|---|"]
    summary = ["", "| benchmark | draws | reaches the model | DiscoPoP applied |", "|---|---:|---:|---:|"]
    for bench in sorted(per):
        for draw, v in per[bench]:
            lines.append(f"| `{bench}` | {draw} | {v.get('hot')} {v.get('span', '')} | {v.get('tier')} | {v.get('share')} "
                         f"| {v.get('phase_a')} | {'yes' if v['reaches_model'] else 'no'} | {'yes' if v['dp_applied'] else 'no'} |")
        n = len(per[bench])
        summary.append(f"| `{bench}` | {n} | {sum(bool(v['reaches_model']) for _, v in per[bench])} of {n} "
                       f"| {sum(bool(v['dp_applied']) for _, v in per[bench])} of {n} |")
    text = "\n".join(lines + summary) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
