#!/usr/bin/env python3
"""Fix 105, what the repaired dependence stage changes — read-out of the no-model replay `f105_replay`.

    venv/bin/python evaluation/agent/results/T0_instruments/F105_gate_dependence_lines/analysis/f105_readout.py

The replay hands the 69 pragma-free rewrites accepted in the 38 agent trials of E1-v6 whose final pass judged two
or more directives to today's pipeline at budget 0 (`candidate_replay.py replay`, the repaired gate). The repair's
own signal is a directive refused at the stage `dependences`; everything else a replay shows can differ from the
trial for other reasons (the replay runs on today's DiscoPoP). Counted here: the replays' results, the stages that
refused a directive, and — from each replay's log of the final pass — the directives judged with a directive
already applied ABOVE their loop: the case in which the stage used to read the profile at a shifted line."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "checks" / "f105_replay"
rows = []
for lane in sorted(ROOT.glob("lane*")):
    man = json.loads((lane / "manifest.json").read_text())
    print(f"{lane.name}: commit {man['commit'][:9]}, DiscoPoP pass {str(man.get('discopop_pass_sha256'))[:12]}, "
          f"{len(man['trials'])} trials, finished {man.get('finished')}")
    rows += [json.loads(ln) for ln in (lane / "results.jsonl").read_text().splitlines() if ln.strip()]
print(f"\nrewrites: {len(rows)} — " + ", ".join(f"{k} {v}" for k, v in sorted(collections.Counter(r["result"] for r in rows).items())))
ran = [r for r in rows if r.get("applied") is not None]
rej: collections.Counter = collections.Counter()
for r in ran:
    rej.update(r.get("rejected_by") or {})
print(f"handed to the pipeline (the others are the same text as one of these): {len(ran)}; directives refused by stage: {dict(rej) or 'none'}; "
      f"refused at `dependences`: {rej.get('dependences', 0)}")
ship = [r for r in rows if r.get("is_shipped_rewrite")]
print(f"the rewrite the trial shipped: {len(ship)} — " + ", ".join(
    f"{o} in the trial → {res} {n}" for (o, res), n in sorted(collections.Counter((r["harness_outcome"], r["result"]) for r in ship).items())))
aborted = [r for r in rows if r["result"] == "AGENT_ABORTED"]
print(f"stopped at start-up ({len(aborted)}): " + "; ".join(sorted({str(r.get('detail'))[:90] for r in aborted})))

PAT = re.compile(r"┌─ pattern #\S+\s+\S+ @ lines (\d+)[–-]\d+")
END = re.compile(r"└─ (\w+)")
tot: collections.Counter = collections.Counter()
shifted: collections.Counter = collections.Counter()
refused: collections.Counter = collections.Counter()
loops: collections.Counter = collections.Counter()
passes = with_shift = 0
for log in sorted(ROOT.glob("lane*/*@*/agent.log")):
    text = log.read_text(errors="replace")
    at = text.find("PHASE B")
    if at < 0:
        continue
    passes += 1
    applied: list = []
    cur = None
    stage = None
    hit = False
    for line in text[at:].splitlines():
        m = PAT.search(line)
        if m:
            cur, stage = int(m.group(1)), None
            continue
        if cur is not None and "gate failed at" in line:
            stage = line.split("gate failed at '")[1].split("'")[0]
        e = END.search(line)
        if e and cur is not None:
            tot[e.group(1)] += 1
            if any(a < cur for a in applied):
                shifted[e.group(1)] += 1
                hit = True
                if e.group(1) == "DROPPED":
                    refused[str(stage)] += 1
            if e.group(1) == "APPLIED":
                applied.append(cur)
            cur = None
    if hit:
        with_shift += 1
        loops[log.parent.name.split("@")[0].split("_")[-1]] += 1
print(f"\nfinal passes in the logs: {passes}; directives judged one by one: {sum(tot.values())} ({dict(tot)})")
print(f"judged with a directive already applied above their loop: {sum(shifted.values())} ({dict(shifted)}) in {with_shift} "
      f"replays; refused among them: {dict(refused) or 'none'}")
print(f"their loops: {dict(sorted(loops.items()))}")
