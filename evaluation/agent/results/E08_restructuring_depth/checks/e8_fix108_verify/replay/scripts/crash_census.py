"""How often D40 told the model its program crashed at the timing size, in the counted depth-0 trials (E3, E3b):
read from requests.jsonl (the agent.log's feedback panel is cut at 30 lines and loses the diagnostic). For each such
message: was any rewrite kept before it in the trial (else the program before the rewrite is the original, which runs
at the timing size, so the crash is the new rewrite's own), and was every rewrite kept before it timed by D40 (ok)?"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "evaluation/agent/tools")
import campaign  # noqa: E402

E3 = ("e3_r_1", "e3_r_2", "e3_r_3", "e3_r_4", "e3c_v8_s341")
E3_REPLACED = {("e3_r_4", "tsvc_c2/s341")}
reg = json.loads(Path("evaluation/agent/results/campaign.json").read_text())
runs = reg["runs"] if isinstance(reg, dict) and "runs" in reg else reg
e3b = ("e3b_1", "e3b_2", "e3b_3", "e3b_4", "e3bc_s316")       # E3b's corrected table: s316 from e3bc_s316
E3_REPLACED.add(("e3b_1", "tsvc_c4/s316"))
print("E3b runs:", e3b)
PHRASE = "the program with DiscoPoP's pragmas CRASHED at the timing size"


def trials(run, arm):
    root = campaign.find_run(run)
    for tj in sorted(root.glob(f"benchmarks/*/*/{arm}/*/rep*/trial.json")):
        t = json.loads(tj.read_text())
        yield t, tj.parent


out = {}
for label, runs_, arm in (("E3 default_v5", E3, "default_v5"), ("E3 llm_pragmas_v5", E3, "llm_pragmas_v5"),
                          ("E3b default_v5", e3b, "default_v5")):
    n = told_trials = msgs = 0
    rows = []
    for r in runs_:
        for t, d in trials(r, arm):
            if (r, str(t.get("benchmark"))) in E3_REPLACED:
                continue
            n += 1
            req = d / "agent_patches" / "requests" / "requests.jsonl"
            rows_ = [json.loads(x) for x in req.read_text().splitlines()] if req.exists() else []
            sent = [r.get("sent", "") for r in rows_]
            k = sum(PHRASE in s for s in sent)
            # does the model's answer to such a message name the stack?
            stack = any(PHRASE in r.get("sent", "") and re.search(r"stack", r.get("reply", ""), re.I) for r in rows_)
            if not k:
                continue
            told_trials += 1
            msgs += k
            log = (d / "agent.log").read_text(errors="replace")
            head = log.split("PHASE B", 1)[0]
            # order of events in Phase A: kept rewrites (ACCEPTED) and D40 verdicts
            events = re.findall(r"(└─ ACCEPTED|D40 verdict: \w+)", head)
            # every crash message comes with a pattern_broken verdict: count the rewrites kept before the LAST one
            last_pb = max((i for i, e in enumerate(events) if e == "D40 verdict: pattern_broken"), default=None)
            kept_before = [e for e in events[:last_pb] if e == "└─ ACCEPTED"] if last_pb is not None else []
            verdicts_before = [e for e in events[:last_pb] if e.startswith("D40 verdict")] if last_pb is not None else []
            rows.append((r, t.get("benchmark"), t.get("repeat") or d.name, k, len(kept_before), verdicts_before,
                         t.get("outcome"), stack))
    print(f"\n{label}: trials {n}; trials whose model was told 'CRASHED at the timing size' {told_trials}; messages {msgs}; "
          f"answers naming the stack in {sum(1 for row in rows if row[7])} of those trials"
          "\n   (run, loop, rep, messages, rewrites kept before the last pattern_broken verdict, outcome, "
          "the model's answer names the stack)")
    for row in rows:
        print("  ", row[:5] + row[6:8])
