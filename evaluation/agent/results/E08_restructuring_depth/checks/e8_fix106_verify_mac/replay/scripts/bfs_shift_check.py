"""Is the bfs kind Phase B's fingerprint taken on lines an earlier pragma had shifted?"""
import json
import os, sys
from pathlib import Path
sys.path.insert(0, os.environ.get("DISCOPOP_AGENT_REPO", os.getcwd()))   # run from the repo root
sys.path.insert(0, str(Path(__file__).parent))
from settle_archive import accepted_rewrites, apply, body  # noqa: E402

rep = Path(sys.argv[1])
log = (rep / "agent.log").read_text(errors="replace")
cands = [json.loads(l) for l in (rep / "agent_patches" / "candidates.jsonl").read_text().splitlines() if l.strip()]
rws = accepted_rewrites(log)
name = "bfs.cpp"
orig = rep / "original" / name
if not orig.exists():
    orig = rep / "agent_patches" / f"{name}.original"
t = orig.read_text()
for r in rws:
    hits = [c for c in cands if c.get("phase") == "A" and c.get("passed") and c.get("region_id") == r["rid"] and c.get("depth") == r["depth"]]
    t = apply(t, (rep / "agent_patches" / hits[-1]["patch"]).read_text(), name)
last = rws[-1]
exposed = [body(t, a, b) for a, b in last["finds"]]
# Phase B: the pragmas applied, in order (passed B records whose region is not reported DROPPED)
applied = [c for c in cands if c.get("phase") == "B" and c.get("passed")]
print("orphan", last["rid"], "exposed spans", last["finds"])
tb = t
for c in applied:
    print("  B", c["region_id"], c["patch"])
spans = [(a, b) for a, b in last["finds"]]
# fingerprint Phase B would take for the exposed span, after each earlier applied pragma
for c in applied:
    d = (rep / "agent_patches" / c["patch"]).read_text()
    for a, b in spans:
        fb = body(tb, a, b)
        print(f"  before {c['region_id']}: body at {a}-{b} equals the exposed print: {fb in exposed}")
    t2 = apply(tb, d, name)
    if t2 is None:
        print("   (does not apply on top)"); continue
    tb = t2
