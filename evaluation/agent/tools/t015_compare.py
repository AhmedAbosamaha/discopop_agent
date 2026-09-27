#!/usr/bin/env python3
"""T0.15's read-out: which v3/v4 differences are the layout's, and which are DiscoPoP's draw-to-draw noise?

`harness_equivalence.py` compares ONE profile of each layout and flags every difference. DiscoPoP's
view of a loop is itself a draw (record §6, 26 Sep: B4 re-measured), so one pair cannot tell the
layout from the draw. This reads two or more runs of it (each a v3 profile and a v4 profile of every
package) and compares, per package, the code under test only:

  candidates    the agent's candidates that start inside the kernel function: type, first line and
                length relative to the kernel's first line, tier, pattern
  dependences   the dependences in those candidates' evidence whose BOTH endpoints lie in the model's
                file code shared by the layouts — the kernel and `pb_mix` — each line relative to its
                function's first line. An endpoint elsewhere is harness code: in the file in v3, in
                the header in v4 (whose line numbers name no line of the file — the evidence carries
                no file id, so `harness_equivalence.py` reads such a line as "" and reports the
                dependence as ADDED; this read-out leaves them out as the harness's)

and classifies each dimension of each package:

  same          every draw of both layouts equal
  noise         the draws of a layout differ among themselves, and some draw of v3 equals some draw of v4
  LAYOUT        each layout equal across its draws, the two layouts different: a stable difference
  undecided     the draws of a layout differ AND no draw of v3 equals any draw of v4 — two draws cannot say

    venv/bin/python evaluation/agent/tools/t015_compare.py RUN_DIR RUN_DIR [...] [--out FILE]
      RUN_DIR: a harness_equivalence.py output directory (its raw/<name>.json)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

Key = Tuple[Any, ...]


def _span(lines: List[str], head: str) -> Optional[Tuple[int, int]]:
    """The 1-based first and last line of the function whose header line is `head`."""
    for i, l in enumerate(lines, 1):
        if l.strip() == head:
            for j in range(i + 1, len(lines) + 1):
                if lines[j - 1].rstrip() == "}":
                    return i, j
    return None


def view(side: Dict[str, Any]) -> Tuple[FrozenSet[Key], FrozenSet[Key]]:
    """(candidates, dependences) of one profile of one layout, lines made layout-independent."""
    k0, k1 = side["kernel_span"]
    mix = _span(side["lines"], "static void pb_mix(int nl)")

    def where(n: int) -> Optional[Tuple[str, int]]:
        if k0 <= n <= k1:
            return ("kernel", n - k0)
        if mix and mix[0] <= n <= mix[1]:
            return ("pb_mix", n - mix[0])
        return None

    cands, deps = set(), set()
    for c in side["candidates"]:
        if not k0 <= c["start"] <= k1:
            continue
        cands.add((c["type"], c["start"] - k0, c["end"] - c["start"], c["tier"], c["pattern"]))
        for t, f, to, var in c["deps"]:
            a, b = where(f), where(to)
            if a and b:
                deps.add((t, a, b, var))
    return frozenset(cands), frozenset(deps)


def classify(old: List[FrozenSet[Key]], new: List[FrozenSet[Key]]) -> str:
    stable_old, stable_new = len(set(old)) == 1, len(set(new)) == 1
    if stable_old and stable_new:
        return "same" if old[0] == new[0] else "LAYOUT"
    return "noise" if set(old) & set(new) else "undecided"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    if len(a.runs) < 2:
        ap.error("two runs at least: one pair cannot tell the layout from the draw")
    names = sorted(p.stem for p in (a.runs[0] / "raw").glob("*.json"))
    rows: List[Dict[str, Any]] = []
    for n in names:
        per: List[Tuple[Tuple[FrozenSet[Key], FrozenSet[Key]], Tuple[FrozenSet[Key], FrozenSet[Key]]]] = []
        for r in a.runs:
            raw = json.loads((r / "raw" / f"{n}.json").read_text())
            if "error" in raw["old"] or "error" in raw["new"]:
                per = []
                break
            per.append((view(raw["old"]), view(raw["new"])))
        if not per:
            rows.append({"name": n, "candidates": "profile error", "dependences": "profile error"})
            continue
        row: Dict[str, Any] = {"name": n}
        for k, label in ((0, "candidates"), (1, "dependences")):
            o = [p[0][k] for p in per]
            w = [p[1][k] for p in per]
            row[label] = classify(o, w)
            if row[label] in ("LAYOUT", "undecided"):
                only_old = frozenset.intersection(*o) - frozenset().union(*w)
                only_new = frozenset.intersection(*w) - frozenset().union(*o)
                row[f"{label}_detail"] = {"in every v3 draw, no v4 draw": sorted(map(str, only_old)),
                                          "in every v4 draw, no v3 draw": sorted(map(str, only_new))}
        rows.append(row)
    lines = [f"# T0.15 read-out over {len(a.runs)} runs: " + ", ".join(r.name for r in a.runs), "",
             "| package | candidates | dependences |", "|---|---|---|"]
    lines += [f"| `{r['name']}` | {r['candidates']} | {r['dependences']} |" for r in rows]
    counts: Dict[str, Dict[str, int]] = {}
    for dim in ("candidates", "dependences"):
        for r in rows:
            counts.setdefault(dim, {}).setdefault(r[dim], 0)
            counts[dim][r[dim]] += 1
    classes = ("same", "noise", "LAYOUT", "undecided")
    lines += ["", "| dimension | " + " | ".join(classes) + " |", "|---|---:|---:|---:|---:|"]
    for dim in ("candidates", "dependences"):
        lines.append(f"| {dim} | " + " | ".join(str(counts[dim].get(c, 0)) for c in classes) + " |")
    details = [r for r in rows if any(k.endswith("_detail") for k in r)]
    if details:
        lines += ["", "## Stable or undecided differences, per package", ""]
        for r in details:
            for dim in ("candidates", "dependences"):
                d = r.get(f"{dim}_detail")
                if d:
                    lines.append(f"- `{r['name']}` {dim} ({r[dim]}): "
                                 f"v3 only {d['in every v3 draw, no v4 draw'] or '—'}; "
                                 f"v4 only {d['in every v4 draw, no v3 draw'] or '—'}")
    text = "\n".join(lines) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text)
        (a.out.with_suffix(".json")).write_text(json.dumps(rows, indent=1) + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
