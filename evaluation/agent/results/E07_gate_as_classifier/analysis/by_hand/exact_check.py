"""For every candidate of a corpus: does its archived patch apply EXACTLY to the base the builder put it on, and does it
reproduce the program the corpus holds?   usage: exact_check.py a1|a2"""
import collections, json, sys, tempfile
from pathlib import Path
EVAL = Path(__file__).resolve().parents[5]            # .../evaluation
sys.path.insert(0, str(EVAL / "agent/tools"))
sys.path.insert(0, str(EVAL.parent))
import campaign, gate_study  # noqa: E402
R = EVAL / "agent/results/E07_gate_as_classifier"
name = sys.argv[1]
C = R / "corpus" / name
c = json.loads((C / "corpus.json").read_text())
progs, cands = c["programs"], c["candidates"]
tmp = Path(tempfile.mkdtemp(prefix="e7_exact_"))
bad = []
for x in cands:
    base = (C / progs[x["base"]]["path"]).read_text()
    prog = (C / progs[x["program"]]["path"]).read_text()
    ptext = (campaign.RESULTS / x["patch"]).read_text(errors="replace")
    got = gate_study._apply(base, ptext, progs[x["program"]]["file"], True, tmp)
    if got is None or got != prog:
        bad.append((x, got is None))
print(f"{name}: {len(cands)} candidates; the patch does not apply exactly to the recorded base for {len(bad)}")
print("by (phase, kind, gate):", dict(collections.Counter((x['phase'], x['kind'], x['gate']) for x, _ in bad)))
trials = collections.Counter(" ".join(x["id"].split(" ")[:-1]) for x, _ in bad)
print("trials touched:", len(trials))
nv = set(c["not_verified"])
print("of them in not_verified:", sum(1 for t in trials if t in nv), "| not_verified trials in all:", len(nv))
for t, n in sorted(trials.items()):
    print(f"   {t}: {n}  {'(not verified)' if t in nv else ''}")
print("\nnot_verified trials:")
for t in sorted(nv):
    print("   ", t)
json.dump([x["id"] for x, _ in bad], open(tmp / "bad.json", "w"))
print("list:", tmp / "bad.json")
