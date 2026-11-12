"""For each accepted rewrite the judge finds wrong: why its trial reverted it, from the trial's own records (the D40
verdicts in trial.json, the log block, and what the next request told the model).   usage: fate19.py [--full]"""
import json, re, sys
from pathlib import Path
EVAL = Path(__file__).resolve().parents[5]            # .../evaluation
sys.path.insert(0, str(EVAL / "agent/tools"))
import campaign
E = EVAL / "agent/results/E07_gate_as_classifier"
c = json.loads((E / "corpus/a1/corpus.json").read_text())
ro = json.loads((E / "analysis/readout_a1.json").read_text())
full = "--full" in sys.argv
for row in ro["false_accepts"]:
    x = next(y for y in c["candidates"] if y["program"] == row["hash"])
    d = campaign.find_run(x["run"])
    tdir = next(iter(sorted((d / "benchmarks" / x["benchmark"] / x["arm"]).glob(f"*/{x['rep']}"))))
    recs = [json.loads(l) for l in (tdir / "agent_patches/candidates.jsonl").read_text().splitlines() if l.strip()]
    rew = [r for r in recs if r["phase"] == "A"]
    k = next(i for i, r in enumerate(rew) if r["n"] == x["n"])
    passed_before = sum(1 for r in rew[:k] if r["passed"])       # index among gate-passing rewrites
    tj = json.loads((tdir / "trial.json").read_text())
    log = (tdir / "agent.log").read_text().splitlines()
    calls = [i for i, l in enumerate(log) if "Diff received — running quality gate" in l]
    end = calls[k + 1] if k + 1 < len(calls) else len(log)
    blk = log[calls[k]:end]
    cut = next((i for i, l in enumerate(blk) if l.startswith(("└─", "┌─"))), len(blk))
    blk = blk[:cut + 1]
    crash_line = [l for l in blk if "non-zero exit" in l or "CRASH" in l or "crash" in l]
    d40 = [l.strip("│ ").strip() for l in blk if "D40" in l or "exposure verdict" in l or "reverting" in l]
    ev, dv = tj.get("exposure_verdicts"), tj.get("d40_verdicts")
    print(f"\n=== {row['program']}  {x['id']}   (gate-passing rewrite no. {passed_before + 1} of the trial; arm {x['arm']})")
    print("   trial.json exposure_verdicts:", json.dumps(ev)[:300])
    print("   trial.json d40_verdicts:", json.dumps(dv)[:400])
    for l in d40:
        print("   | " + l[:210])
    if crash_line:
        print("   crash lines in the block:", [l.strip()[:120] for l in crash_line])
    # what the model was told next
    req_dir = tdir / "agent_patches/requests"
    if req_dir.is_dir():
        reqs = sorted(req_dir.iterdir())
        hits = [p.name for p in reqs if "CRASHED" in p.read_text(errors="replace") or "crash" in p.read_text(errors="replace").lower()]
        print("   requests:", len(reqs), "| mentioning a crash:", hits[:6])
    if full:
        print("\n".join("      " + l[:230] for l in blk))
