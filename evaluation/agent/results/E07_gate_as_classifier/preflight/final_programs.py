#!/usr/bin/env python3
"""What the trials in hand already say about the gate (9 Oct 2026) — read from the archive, nothing run.

    venv/bin/python evaluation/agent/results/E07_gate_as_classifier/preflight/final_programs.py

The harness judges every trial's final program on its own (`trial.json` `outcome`), whatever the gate said on the
way. This prints, for the valid runs of groups E1-v6 and E2-v6b: per arm, the trials whose source changed and the
harness's verdict on them; and the verdicts of the race checks that were run over final programs (`race_check.py`,
the gate's own safety validation applied to a finished file). It says nothing about a candidate the gate refused:
such a candidate is in no final program."""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
EVAL = HERE.parents[4]
sys.path[:0] = [str(EVAL / "agent/tools"), str(EVAL / "shared")]
import campaign  # noqa: E402

GROUPS = ("E1-v6", "E2-v6b")
WRONG = ("BROKEN", "VERIFY_FAILED")
reg = json.loads((EVAL / "agent/results/campaign.json").read_text())
runs = sorted(r for r, v in reg["runs"].items() if v.get("status") == "valid" and v.get("group") in GROUPS)
changed: dict = collections.defaultdict(collections.Counter)
trials = 0
for run in runs:
    for tj in campaign.find_run(run).glob("benchmarks/**/trial.json"):
        t = json.loads(tj.read_text())
        trials += 1
        if t.get("source_changed"):
            changed[str(t.get("arm"))][str(t.get("outcome"))] += 1
print(f"valid runs of {' and '.join(GROUPS)}: {len(runs)}; trials: {trials}")
print("trials whose source changed, and the harness's verdict on the final program:")
for arm in sorted(changed):
    if arm.startswith("replay_"):
        continue
    n = sum(changed[arm].values())
    print(f"  {arm}: {n} — " + ", ".join(f"{k} {v}" for k, v in sorted(changed[arm].items()))
          + f" — wrong or not verifiable: {sum(changed[arm][w] for w in WRONG)}")
replays = sum(sum(c.values()) for a, c in changed.items() if a.startswith("replay_"))
print(f"  (candidate_replay.py arms, one program each, no agent trial: {replays})")
gated = [a for a in changed if not a.startswith(("bare_llm", "replay_", "discopop_"))]
print(f"the agent's arms together ({', '.join(sorted(gated))}): "
      f"{sum(sum(changed[a].values()) for a in gated)} changed, "
      f"{sum(changed[a][w] for a in gated for w in WRONG)} wrong or not verifiable")

print("\nrace checks over final programs (race_check.py):")
total: dict = collections.defaultdict(collections.Counter)
for group in reg["groups"]:
    if group["id"] not in GROUPS:
        continue
    for res in sorted((EVAL / "agent/results" / group["folder"] / "checks").glob("*/*/results.jsonl")):
        man = json.loads((res.parent / "manifest.json").read_text())
        if man.get("tool") != "race_check.py":
            continue
        who = "the models alone" if str(man.get("arm")).startswith("bare_llm") else "the agent"
        c = collections.Counter(str(json.loads(ln).get("verdict")) for ln in res.read_text().splitlines() if ln.strip())
        total[who].update(c)
        print(f"  {res.parent.parent.name}/{res.parent.name} ({who}, {man.get('arm')}): "
              + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
for who, c in sorted(total.items()):
    print(f"{who}: {sum(c.values())} programs — " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
