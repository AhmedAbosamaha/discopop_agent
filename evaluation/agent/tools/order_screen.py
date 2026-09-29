#!/usr/bin/env python3
"""Where does the split order matter, and is it hidden? — a no-model screen over DiscoPoP profiles (29 Sep 2026).

E2-V3 showed the evidence helps the agent where a loop has to be split and the ORDER of the parts is decided by a
dependence the model cannot read off the code (ORDER-2 X: 10/10 with evidence vs 1/10 without). This screen looks
for that situation in real programs, with the agent's own code: for every Tier-2 loop region of every profile it
finds, prompt version 3's order statement (llm/render.order_statement) is built from DiscoPoP's records. A region
is a candidate when the statement orders a split AGAINST the text — the writing line comes after the reading line,
so a split in textual order is wrong. Whether the order is visible in the text is then read from the two lines'
subscripts: an index read from another array (`a[ip[i]]`) or an offset that is neither a constant nor the loop's
own counter hides it; `a[i-1]` shows it.

    venv/bin/python evaluation/agent/tools/order_screen.py RUNS_DIR [RUNS_DIR ...] --out screen.json

Each RUNS_DIR is searched for `profiles/<suite>/<bench>/.discopop` with its source beside it (the harness's runs).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))

ORDER_RX = re.compile(r"Line (\d+) \(`(.*?)`\) reads an element of `(\w+)` that line (\d+) \(`(.*?)`\) writes; "
                      r"DiscoPoP names the loop at line (\d+)")
CYCLE_RX = re.compile(r"Lines (\d+) \(`(.*?)`\) and (\d+) \(`(.*?)`\) feed each other")


def subscripts(stmt: str, var: str) -> List[str]:
    return re.findall(r"\b" + re.escape(var) + r"\s*\[([^\]]*(?:\[[^\]]*\][^\]]*)*)\]", stmt)


def hidden(sub: str, counters: List[str]) -> str:
    """'indirect' (an index read from an array), 'offset' (a variable other than the loop counters), '' (visible)."""
    if "[" in sub:
        return "indirect"
    names = set(re.findall(r"[A-Za-z_]\w*", sub)) - set(counters) - {"LEN_1D", "LEN_2D", "N", "n"}
    return "offset" if names else ""


def screen_profile(dp: Path, src: Path, exclude: Tuple[str, ...]) -> List[Dict[str, Any]]:
    from discopop_agent.args import parse_args
    from discopop_agent.evidence import assemble
    from discopop_agent.llm.render import order_statement
    from discopop_agent.plan import build_candidates
    saved = sys.argv
    sys.argv = ["x", "--discopop-dir", str(dp), "--source-file", str(src), "--min-runtime-share", "0"]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            args = parse_args()
    finally:
        sys.argv = saved
    out: List[Dict[str, Any]] = []
    with contextlib.redirect_stdout(io.StringIO()):
        cands = build_candidates(dp, str(src), args.lambda_penalty, args.min_workload, impact=None,
                                 min_impact=args.min_impact, min_runtime_share=0.0, exclude_functions=exclude)
    seen = set()
    for c in cands:
        if c.tier != 2 or c.region.region_type != "loop":
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            ev = assemble(c, dp / "profiler", "screen")
        note = order_statement(ev)
        counters = sorted({v for lp in ev.loop_nest for v in lp["index_vars"]})
        for m in ORDER_RX.finditer(note):
            s, s_txt, var, w, w_txt, loop = int(m[1]), m[2], m[3], int(m[4]), m[5], int(m[6])
            key = (s, w, var)
            if key in seen:
                continue
            seen.add(key)
            kinds = sorted({hidden(x, counters) for x in subscripts(s_txt, var) + subscripts(w_txt, var)} - {""})
            out.append({"region": [ev.start_line, ev.end_line], "loop": loop, "var": var, "writer": w, "reader": s,
                        "writer_text": w_txt, "reader_text": s_txt, "against_text": w > s, "hidden_by": kinds})
        for m in CYCLE_RX.finditer(note):
            key = (int(m[1]), int(m[3]), "cycle")
            if key not in seen:
                seen.add(key)
                out.append({"region": [ev.start_line, ev.end_line], "cycle": [int(m[1]), int(m[3])],
                            "texts": [m[2], m[4]]})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    results: Dict[str, Any] = {}
    for root in a.runs:
        for dp in sorted(root.glob("*/profiles/*/*/.discopop")):
            bench = f"{dp.parent.parent.name}/{dp.parent.name}"
            if bench in results:
                continue                              # one profile per benchmark is enough for a screen
            meta_p = dp.parent / "meta.json"
            meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
            src_name = meta.get("file") or next((p.name for p in dp.parent.iterdir()
                                                 if p.suffix in (".c", ".cpp", ".cc")), "")
            if not src_name or not (dp.parent / src_name).exists():
                continue
            try:
                found = screen_profile(dp, dp.parent / src_name, tuple(meta.get("exclude_functions") or ("main",)))
            except Exception as e:                   # noqa: BLE001 - a screen reports what it could not read
                results[bench] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
                continue
            results[bench] = {"profile": str(dp), "findings": found}
            hits = [f for f in found if f.get("against_text")]
            print(f"{bench:32s} order statements {sum(1 for f in found if 'var' in f)}, against the text {len(hits)}, "
                  f"cycles {sum(1 for f in found if 'cycle' in f)}"
                  + "".join(f"\n    {f['var']}: line {f['writer']} `{f['writer_text']}` before line {f['reader']} "
                            f"`{f['reader_text']}`  hidden by: {', '.join(f['hidden_by']) or 'nothing (visible)'}"
                            for f in hits), flush=True)
    a.out.write_text(json.dumps(results, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
