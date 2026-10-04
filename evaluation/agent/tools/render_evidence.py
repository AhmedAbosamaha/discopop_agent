#!/usr/bin/env python3
"""Print the evidence sections the model reads for a captured fixture under a given prompt version (no model).

The thesis compares what the model was told under prompt version 1 and version 3 about the same DiscoPoP
measurement; this prints exactly that, from the agent's own rendering code and a fixture of tools/fixtures/prompt/.

    venv/bin/python evaluation/agent/tools/render_evidence.py k17 --version 1
    venv/bin/python evaluation/agent/tools/render_evidence.py k17 --version 3
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
import prompt_manifest as pm  # noqa: E402

SECTIONS = ("### Evidence digest", "### Runtime data dependences", "### Choosing the fix",
            "### Why DiscoPoP could not", "### What the observed flow")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fixture", help="a fixture under tools/fixtures/prompt/ (e.g. k17, s211)")
    ap.add_argument("--version", type=int, choices=(1, 2, 3, 4), default=3)
    ap.add_argument("--full", action="store_true", help="the whole request, not only the evidence sections")
    a = ap.parse_args()
    from discopop_agent.llm.prompts import PROMPT_VERSIONS
    from discopop_agent.llm.request import _build_direct_prompt
    from discopop_agent.types import GateFacts
    _loop, ev = pm.fixture_evidence(a.fixture)
    gate = GateFacts(require_speedup=False, n_inputs=2, changes=PROMPT_VERSIONS[a.version])
    req = _build_direct_prompt(ev, Path("/workspace") / pm._fixture_meta(a.fixture)["source"], None, False, gate)
    if a.full:
        print(req)
        return 0
    for head in SECTIONS:
        i = req.find(head)
        if i < 0:
            continue
        j = req.find("\n###", i + 4)
        print(req[i:j if j > 0 else len(req)].rstrip() + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
