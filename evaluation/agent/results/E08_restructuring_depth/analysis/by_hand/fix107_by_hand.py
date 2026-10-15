#!/usr/bin/env python3
"""E8's trials that match candidate Fix 107's pattern after a repair of Settle's finished-program check (listed by
e8_readout.py "to be read by hand"): for each, what Settle's repairs dropped, which rewrites it then dropped as orphans,
and what the finished program kept. A trial whose finished program kept NO pragma has every orphan drop explained by
the repairs (each rewrite's pragmas were dropped for speed first); the others are printed in full for reading."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "evaluation/agent/tools")   # run from the repository root
import e8_readout as r  # noqa: E402
import campaign  # noqa: E402

set_trials = r.load(r.SET_RUN, r.ARMS)
loop_trials = [t for run in r.LOOP_RUNS for t in r.load(run, (r.DEPTH1, r.DEPTH2))]
flagged = [t for t in set_trials + loop_trials if r.chain(t)["fix107_read_by_hand"]]
print("flagged:", len(flagged))
explained, to_read = [], []
for t in flagged:
    log = (Path(t["_dir"]) / "agent.log").read_text(errors="replace")
    settle = log.partition("SETTLING")[2]
    summ = re.search(r"SUMMARY: (\d+) rewrite\(s\) kept\s+\|\s+(\d+) pragma\(s\) applied", settle)
    kept_rw, kept_pr = (int(summ.group(1)), int(summ.group(2))) if summ else (None, None)
    repairs = re.findall(r"→ dropping the pragma for (\S+)", settle)
    orphans = re.findall(r"· rewrite of (\S+) — exposed (\d+) region\(s\), none kept a pragma", settle)
    tag = f"{t['run_id']} {str(t['benchmark']).split('/')[1]} {t['arm']} rep{t['repeat']}"
    row = (tag, t.get("outcome"), repairs, orphans, kept_rw, kept_pr)
    (explained if kept_pr == 0 else to_read).append(row)
print(f"finished program kept no pragma (every orphan drop follows the repairs): {len(explained)}")
for x in explained: print("  ", x)
print(f"finished program kept pragmas — read in full: {len(to_read)}")
for x in to_read: print("  ", x)
