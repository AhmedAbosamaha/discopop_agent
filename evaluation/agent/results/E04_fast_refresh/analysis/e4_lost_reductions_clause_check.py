#!/usr/bin/env python3
"""E4 step 1 — why the reductions are lost after the fast refresh: the agent's clause check on the directive
DiscoPoP writes there.

For every rewrite the replay keeps only after the full re-profile because of a reduction, the rewritten file is
rebuilt from the trial's archive, the directive the FAST refresh made DiscoPoP write for that same loop is put in
front of it, and the agent's own static clause check (`pragmas.clauses.check_pragma_clauses`) is asked. Nothing is
compiled, profiled or run; no model.

    venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/e4_lost_reductions_clause_check.py

Writes `e4_lost_reductions_clause_check.md` beside itself.
"""
import collections
import difflib
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[2] / "tools"))
sys.path.insert(0, str(HERE.parents[3] / "shared"))
import refresh_replay as rr  # noqa: E402
from discopop_agent.pragmas.clauses import check_pragma_clauses  # noqa: E402

rows = []
for f in sorted((HERE.parent / "runs" / "e4_replay").glob("*/*/results.jsonl")):
    rows += [json.loads(ln) for ln in f.read_text().splitlines() if ln.strip()]


def kept(arm):
    if arm.get("status") != "exposed" or arm.get("judged") != "safe_deferred":
        return None
    singles = [c for c in arm["checks"] if c["lines"] is not None and c["passed"]]
    together = [c for c in arm["checks"] if c["lines"] is None]
    return singles[:1] if together and not together[-1]["passed"] else singles


md = ["# E4 step 1 — the reductions lost after the fast refresh, and the clause check", "",
      "Built by `e4_lost_reductions_clause_check.py` from the records of `e4_replay` and the trials' archives.", "",
      "| trial | rewrite | the loop | the full profile's directive | the fast refresh's directive, the same loop | "
      "dependences not carried over | the agent's clause check |", "|---|---:|---|---|---|---:|---|"]
reasons: "collections.Counter[str]" = collections.Counter()
for r in rows:
    full = kept(r["full"])
    if full is None or kept(r["fast"]) is not None or "reduction(" not in " ".join(full[0]["pragmas"]):
        continue
    trial = next(p for p in RESULTS.glob(f"*/runs/{r['trial']}") if p.is_dir())
    kernel = next((trial / "agent_patches").glob("*.original")).name[:-len(".original")]
    post = next(x for x in rr.rewrites_of(trial, kernel)[0] if x["n"] == r["n"])["post"]
    lines = tuple(full[0]["lines"])
    pragma = {(e[0], e[1]): e[3] for e in r["fast"].get("exposed", [])}[lines][0]
    src = post.splitlines(keepends=True)
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / kernel).write_text(post)
        staged = src[:lines[0] - 1] + [pragma + "\n"] + src[lines[0] - 1:]
        why = check_pragma_clauses("".join(difflib.unified_diff(src, staged, f"a/{kernel}", f"b/{kernel}")),
                                   str(Path(d) / kernel))
    note = re.search(r"(\d+)/(\d+) observed dependences carried forward \((\d+) in rewritten code", r["fast"]["note"])
    reasons["refused" if why else "passed"] += 1
    md.append(f"| `{r['trial'].split('/benchmarks/')[0]}` `{r['benchmark'].split('/')[1]}` repeat {r['repeat']} | "
              f"{r['n']} | `{src[lines[0] - 1].strip()}` | `{' '.join(full[0]['pragmas'])}` | `{pragma}` | "
              f"{note.group(3)} of {note.group(2)} | {why or 'passes'} |" if note else "")
md += ["", f"**{sum(reasons.values())} rewrites; the clause check refuses the fast refresh's directive in "
       f"{reasons['refused']} and passes it in {reasons['passed']}.**", ""]
(HERE / "e4_lost_reductions_clause_check.md").write_text("\n".join(md))
print("\n".join(md))
