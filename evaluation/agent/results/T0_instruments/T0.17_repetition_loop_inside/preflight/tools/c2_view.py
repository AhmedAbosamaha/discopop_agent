#!/usr/bin/env python3
"""layout_equivalence.py (T0.16) for the prototype with the repetition loop inside the function: the same
tool, with the repetition loop recognised under both of its spellings (`nl < R`, `nl < iterations`) and the
lines of `dummy` counted as measurement. Run from evaluation/agent with the agent's venv:

    venv/bin/python c2_view.py --old tsvc_b1 --new _c2proto --out DIR [names...]
"""
import re
import sys
from typing import Any, Dict

sys.path.insert(0, "tools")
import layout_equivalence as L  # noqa: E402

REP = ("nl < R", "nl < iterations")
L.MIX = (*L.MIX, "dummy(", "static int nl", "nl++;", "return 0;")


def rep(text: str) -> bool:
    return any(r in text for r in REP)


def view(p: Dict[str, Any]) -> Dict[str, Any]:
    ks = [c for c in p.get("candidates", []) if not rep(c["text"])]

    def mine(tx: str) -> bool:
        return bool(tx) and not rep(tx) and not tx.startswith(L.MIX)

    def shape(c: Dict[str, Any]) -> str:
        text = str(c["text"]).replace("static ", "")
        return re.sub(r"\(.*\)\s*$", "()", text) if c["type"] == "function" else text
    return {"candidates": sorted((c["type"], shape(c), c["tier"], str(c["pattern"])) for c in ks),
            "do_all": sorted(d for d in p.get("do_all", []) if not rep(d)),
            "blocker": sorted((b[0], b[1], b[2]) for b in p.get("blockers", []) if not rep(b[2])),
            "repetition": ("Do-All" if any(rep(d) for d in p.get("do_all", [])) else
                           "blocked" if any(rep(b[2]) for b in p.get("blockers", [])) else "no verdict"),
            "statement": sorted({s for c in ks for s in c["statements"]["4"]}),
            "statement_v3": sorted({s for c in ks for s in c["statements"]["3"]}),
            "flows": sorted({tuple(f) for c in ks for f in c["flows"]
                             if mine(f[1]) and mine(f[2]) and f[4] != "unknown"})}


L.view = view
sys.exit(L.main())
