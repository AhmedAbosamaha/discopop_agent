#!/usr/bin/env python3
"""One kept profile, one explorer, N runs — what differs between the runs (Mac, no model; B21, 8 Oct 2026).

    repeat_explorer.py WORK_DIR N LABEL [OLD_EXPLORER_DIR]

Prints, per run, the Do-All and reduction loops with their clauses and every record of doall_prevented.json
(loop, dependence type, variable, origin). OLD_EXPLORER_DIR holds explorer/ and library/ of another commit; without
it the checkout's explorer is used."""
import collections
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
work, n, label = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
old = Path(sys.argv[4]) if len(sys.argv) > 4 else None
dp = work / ".discopop"
env = dict(os.environ, PATH=f"{REPO / 'venv' / 'bin'}:{os.environ['PATH']}")
if old is not None:
    env["PYTHONPATH"] = f"{old / 'explorer'}:{old / 'library'}"
fm = {}
for ln in (dp / "FileMapping.txt").read_text().splitlines():
    a, b = ln.split(None, 1)
    fm[a] = os.path.basename(b.strip())


def name(s: object) -> str:
    a, b = str(s).split(":")[:2]
    return f"{fm.get(a, '?')}:{b}"


seen: "collections.Counter[str]" = collections.Counter()
for i in range(1, n + 1):
    shutil.rmtree(dp / "explorer", ignore_errors=True)
    r = subprocess.run([str(REPO / "venv/bin/python"), "-m", "discopop_explorer"], cwd=dp, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{label} run {i}: explorer rc={r.returncode}: {r.stderr[-300:]}")
        continue
    p = json.loads((dp / "explorer" / "patterns.json").read_text())["patterns"]
    pats = []
    for kind in ("do_all", "reduction"):
        for x in p.get(kind, []):
            cl = " ".join(
                f"{k}={sorted((v.get('name') if isinstance(v, dict) else str(v)) for v in x.get(k, []))}"
                for k in ("first_private", "private", "last_private", "shared", "reduction")
                if x.get(k)
            )
            pats.append(f"{kind} {name(x['start_line'])} {cl}")
    pv = dp / "explorer" / "doall_prevented.json"
    blocked = set()
    for rec in json.loads(pv.read_text()) if pv.is_file() else []:
        blocked.add(
            f"blocked {fm.get(str(rec.get('loop_file')), '?')}:{rec.get('loop_start')} {str(rec.get('dep_type')).split('.')[-1]} "
            f"{rec.get('var_name')} {str(rec.get('origin')).split('.')[-1]} {rec.get('reason')}"
        )
    text = "\n".join(sorted(pats) + sorted(blocked))
    seen[text] += 1
    print(f"{label} run {i}: {len(pats)} pattern(s), {len(blocked)} blocked record(s), answer #{list(seen).index(text) + 1}", flush=True)
print(f"\n{label}: {len(seen)} different answer(s) in {n} runs")
for k, (text, c) in enumerate(seen.items(), 1):
    print(f"--- answer #{k} ({c} of {n} runs)")
    print(text)
