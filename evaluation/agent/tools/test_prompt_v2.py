#!/usr/bin/env python3
"""Stage 0 of the prompt review (docs/PROMPT_REVIEW_2026_09_28.md): what prompt version 2 renders, checked
mechanically on the captured profile fixtures (tools/fixtures/prompt/), with no model call.

  * the words the review found harmful or false are gone from every v2 text (and present in v1, so each
    check can fail);
  * the dependence direction reaches the text: ORDER-2 X reads `line 7 writes → line 6 reads`, Y the reverse;
  * only pairs inside the region are listed as RAW (s211, s244: c, d, e and v cross the region's edge);
  * the no-evidence request is byte-identical between versions, and its system prompt differs only by the
    contract's closing bullet (A1); the twin and the model alone carry the same change;
  * the model alone's speed-off prompt names neither a profile nor evidence (M3);
  * the pilot instrument (M1): no stray failure section, the order note before '### Task'.

Which ARMS a change touches is prompt_manifest.py's check; this one checks WHAT version 2 says.

    venv/bin/python evaluation/agent/tools/test_prompt_v2.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, List, Set

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
import evidence_pilot  # noqa: E402
import prompt_manifest as pm  # noqa: E402

from discopop_agent import bare_llm, twin  # noqa: E402
from discopop_agent.llm.prompts import (PROMPT_VERSIONS, _CONTRACT_CLOSE, _CONTRACT_CLOSE_V2,  # noqa: E402
                                        _sub, _system_prompt)
from discopop_agent.llm.render import fmt_blockers  # noqa: E402
from discopop_agent.llm.request import _build_direct_prompt  # noqa: E402
from discopop_agent.types import GateFacts  # noqa: E402

V2 = PROMPT_VERSIONS[2]
# In the request and the feedback (the contract's own "a second buffer, one more pass" is about cost: review A6).
BANNED = ("must be removed", "GEPRESULT", "sub-passes", "second buffer", "Choosing the fix", "the blocking ones",
          "see 'Choosing")
BANNED_SYSTEM = ("must be removed", "has to be gone")
MIRROR_LEAKS = ("DiscoPoP", "profil", "evidence", "RAW", "re-profile")
D10 = "A RAW carried by a loop is a value in transit"
WS = Path("/workspace/x.c")
failures: List[str] = []


def flat(text: str) -> str:
    return " ".join(text.split())


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'pass' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(label)


def gates(**kw: Any) -> "tuple[GateFacts, GateFacts]":
    base = dict(require_speedup=False, n_inputs=2, stress=True)
    base.update(kw)
    return GateFacts(**base), GateFacts(**base, changes=V2)     # type: ignore[arg-type]


def raw_rows(req: str) -> Set[str]:
    """The variables listed under the RAW heading of the dependence section."""
    m = re.search(r"RAW — read-after-write[^\n]*\n(.*?)\n\s*\n", req, re.S)
    return set(re.findall(r"^    `?([\w*()\[\] ]+?)`? \[(?:array element|scalar)\]", m.group(1), re.M)) if m else set()


def digest_raw(req: str) -> Set[str]:
    m = re.search(r"(?:RAW on array elements within these lines|Loop-carried RAW on ARRAY ELEMENTS of): ([^.—\n]+)", req)
    return {v.strip() for v in m.group(1).split(",")} if m else set()


def main() -> int:
    print("1. versions")
    check("the pilot's v2 arms name prompt version 2", tuple(sorted(evidence_pilot._V2)) == tuple(sorted(V2)))
    try:
        _sub("abc", "x", "y")
        check("a derived text whose anchor is gone raises", False)
    except ValueError:
        check("a derived text whose anchor is gone raises", True)

    print("2. fixtures: banned words, direction, in-region RAW")
    fixtures = sorted(p.name for p in pm.FIXTURES.iterdir() if (p / "fixture.json").exists())
    for f in fixtures:
        loop, ev = pm.fixture_evidence(f)
        g1, g2 = gates()
        r1, r2 = (_build_direct_prompt(ev, WS, None, False, g) for g in (g1, g2))
        s2 = _system_prompt("direct", False, False, g2, None)
        fb2 = fmt_blockers(list(ev.prevented_deps or []), frozenset(V2))
        bad = [w for w in BANNED if w in r2 + fb2] + [w for w in BANNED_SYSTEM if w in flat(s2)]
        check(f"{f}: v2 carries none of the banned words ({len(r1)} → {len(r2)} chars)", not bad, str(bad))
        if f == "k17":
            check("k17: v1 did carry them (the check can fail)", "must be removed" in r1 and "Choosing the fix" in r1)
            check("k17: `v` line 7 writes → line 6 reads",
                  "`v` [array element]: line 7 writes → line 6 reads" in r2)
        if f == "k42":
            check("k42: `u` line 6 writes → line 7 reads",
                  "`u` [array element]: line 6 writes → line 7 reads" in r2)
        if f in ("s211", "s244"):
            crossing = {"c", "d", "e", "v"}
            was = (raw_rows(r1) | digest_raw(r1)) & crossing
            now = (raw_rows(r2) | digest_raw(r2)) & crossing
            check(f"{f}: v1 listed crossing-only names as RAW ({sorted(was)})", bool(was))
            check(f"{f}: v2 lists none of c, d, e, v as RAW", not now, str(sorted(now)))
            check(f"{f}: v2 names them as values crossing the edge",
                  "Values that cross the region's edge only" in r2)
        if f == "s151":
            check("s151: 'structural' is not claimed while an array RAW is listed",
                  not ("structural" in r2 and digest_raw(r2)))

    print("3. what stays: the no-evidence request, and each change only where it belongs")
    loop, ev = pm.fixture_evidence("k17")
    g1, g2 = gates()
    check("no-evidence request: v2 == v1",
          _build_direct_prompt(ev, WS, set(), False, g1) == _build_direct_prompt(ev, WS, set(), False, g2))
    for llm_pragmas in (False, True):
        n1, n2 = (_system_prompt("direct", llm_pragmas, False, g, set()) for g in (g1, g2))
        check(f"no-evidence system prompt (llm_pragmas={llm_pragmas}): v2 is v1 with A1's closing bullet only",
              n1.replace(_CONTRACT_CLOSE, _CONTRACT_CLOSE_V2) == n2 and n1 != n2)
        e2 = _system_prompt("direct", llm_pragmas, False, g2, None)
        check(f"evidence system prompt (llm_pragmas={llm_pragmas}): says what a RAW is (D10)", D10 in flat(e2))
    t_none = [twin._system(g, set(), False) for g in (g1, g2)]
    check("twin, no evidence: v2 is v1 with A1's closing bullet only",
          t_none[0].replace(_CONTRACT_CLOSE, _CONTRACT_CLOSE_V2) == t_none[1])
    check("twin, evidence: D10 and A1", D10 in flat(twin._system(g2, None, False))
          and _CONTRACT_CLOSE_V2 in twin._system(g2, None, False))
    check("twin: no feedback clause in either version",
          all("after a failed attempt" not in flat(twin._system(g, None, False)) for g in (g1, g2)))
    check("agent: the feedback clause kept", "after a failed attempt" in flat(_system_prompt("direct", False, False, g2, None)))
    check("bare 'contract' prompt frozen (E1-bare)", _CONTRACT_CLOSE_V2 not in bare_llm._system("contract"))

    print("4. the model alone (M3)")
    for speed in (True, False):
        for ver in (1, 2):
            g = bare_llm.mirror_gate(speed, ver)
            text = bare_llm._system("mirror", g) + bare_llm._request_mirror(["s000.c"], ["main"], gate=g)
            leaks = [w for w in MIRROR_LEAKS if w.lower() in text.lower()]
            check(f"mirror speed={'on' if speed else 'off'} v{ver}: no DiscoPoP, profile or evidence", not leaks, str(leaks))
            check(f"mirror speed={'on' if speed else 'off'} v{ver}: the contract's closing bullet of v{ver}",
                  (_CONTRACT_CLOSE_V2 if ver == 2 else _CONTRACT_CLOSE) in text)

    print("5. the pilot instrument (M1)")
    k = pm.FIXTURES / "k17"
    reqs = evidence_pilot.build_requests(loop, k / ".discopop", {"id": "k17", "src": k / "k17.c"},
                                         ("full_clean", "arrow_only", "order_clean", "full_v2", "none_v2"))
    for arm, (_s, r) in reqs.items():
        check(f"{arm}: no stray failure section, nothing between '### Task' and its text",
              "What went wrong" not in r and "### Task\n###" not in r)
    oc = reqs["order_clean"][1]
    check("order_clean: the order note is the last evidence section, before '### Task'",
          0 < oc.find("### What the observed dependence means") < oc.find("### Task"))
    ao = reqs["arrow_only"][1]
    check("arrow_only: the direction, and otherwise version 1 (D2 alone)",
          "line 7 writes → line 6 reads" in ao and "must be removed" in ao and "Choosing the fix" in ao)
    check("none_v2: no evidence", "Runtime data dependences" not in reqs["none_v2"][1])

    print("\nALL PASS" if not failures else f"\nFAILURES: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
