#!/usr/bin/env python3
"""E8's third smoke, the criterion pre-registered in §6 (14 Oct, "Plan, E8's third smoke"), on the agent with
Fix 106 and Fix 108:

  pass  — in neither trial does a defect already found show: Settle drops no rewrite that a later kept rewrite
          depended on (a "depended on a change that was dropped" note — Fix 106's defect); no orphan with
          candidate Fix 107's signature; none of Fix 108's residual signature (a timing failure D40 names as the
          program before the rewrite's, a pragma Phase B drops because the program before it crashed at the timing
          size, the noise measurement crashing); every model call returned; both trials end with a verdict of the
          harness.
  held  — any of those signatures.
  rerun — a model call failed (the smoke is run again, never counted).

What the chain reached is printed and is not the condition; Fix 108 acting (`D40 size run: CRASHED`, the rewrite
sent back) is the repair working.  Usage: smoke3_check.py RUN_DIR
"""
import json
import re
import sys
from pathlib import Path

BLOCK = re.compile(r"^┌─ \[depth=(\d+)\] \S+ (\S+) \(lines (\d+)–(\d+)\)")
FINDS = re.compile(r"\w+ @ lines (\d+)–(\d+)")
PATTERN = re.compile(r"^┌─ pattern #\d+\s+\S+ @ lines (\d+)–(\d+)")

run = Path(sys.argv[1])
trials = sorted(run.glob("benchmarks/*/*/*/*/rep*/trial.json"))
held, failed_calls, verdict_missing = [], 0, 0
for tj in trials:
    t = json.loads(tj.read_text())
    log = (tj.parent / "agent.log").read_text(errors="replace")
    head, _, settle = log.partition("SETTLING")
    rewrites, cur = [], None
    for ln in head.splitlines():
        m = BLOCK.match(ln)
        if m:
            cur = {"depth": int(m.group(1)), "rid": m.group(2), "finds": []}
            continue
        if cur is None:
            continue
        if "DiscoPoP now finds:" in ln:
            cur["finds"] = [(int(a), int(b)) for a, b in FINDS.findall(ln)]
        if ln.startswith("└─ ACCEPTED"):
            rewrites.append(cur)
            cur = None
        elif ln.startswith("└─") and not ln.startswith("└─ retry"):
            cur = None
    applied, pat = [], None
    for ln in head.splitlines():
        m = PATTERN.match(ln)
        if m:
            pat = (int(m.group(1)), int(m.group(2)))
        elif pat is not None and ln.startswith("└─"):
            if ln.startswith("└─ APPLIED"):
                applied.append(pat)
            pat = None
    notes = re.findall(r"^\s+· (.*)$", settle, re.M)
    keeps = re.findall(r"^\s+\[keep\] (.*)$", settle, re.M)
    repairs = re.findall(r"^\s+\[(?:repair|revert)\] (.*)$", settle, re.M)
    verified = re.findall(r"^\s+\[ok\] finished source verified — (.*)$", settle, re.M)
    orphans = [n for n in notes if "none kept a pragma" in n]
    cascades = [n for n in notes if n.startswith("rewrite for") and "depended on" in n]
    fix107 = False
    if rewrites and orphans:
        last = rewrites[-1]
        k = len(last["finds"])
        for n in orphans:
            m = re.match(r"rewrite of (\S+) — exposed (\d+) region", n)
            if (m and m.group(1) == last["rid"] and (int(m.group(2)) == k if k < 3 else int(m.group(2)) >= 3)
                    and set(last["finds"]) & set(applied)):
                fix107 = True
    before_named = len(re.findall(r"D40: the timing failed, and not on this rewrite", head))
    unsafe_before = len(re.findall(r"^│  the program BEFORE this pragma CRASHED at the timing size", head, re.M))
    unsafe_own = len(re.findall(r"^│  the program CRASHED at the timing size", head, re.M))
    noise_crash = "timing noise on this machine: not measurable (run failed: non-zero exit (-" in head
    size_runs = re.findall(r"D40 size run: (ok|CRASHED|failed without a crash)", head)
    signatures = ([f"Fix 106 defect: {len(cascades)} rewrite(s) depended on a dropped change"] if cascades else []) \
        + (["candidate Fix 107's signature"] if fix107 else []) \
        + ([f"Fix 108 residual: {before_named} timing failure(s) named as the program before the rewrite's"]
           if before_named else []) \
        + ([f"Fix 108 residual: {unsafe_before} pragma(s) dropped, the program before them crashed"] if unsafe_before else []) \
        + (["Fix 108 residual: the noise measurement crashed"] if noise_crash else [])
    held += [f"{t['arm']}: {s}" for s in signatures]
    failed_calls += int(t.get("llm_call_failures") or 0)
    has_verdict = t.get("outcome") not in (None, "")
    verdict_missing += 0 if has_verdict else 1
    par = (t.get("verify") or {}).get("par") or {}
    req = tj.parent / "agent_patches" / "requests" / "requests.jsonl"
    told = req.read_text(errors="replace").count("CRASHED at the timing size") if req.exists() else 0
    print(f"{t['arm']:10s} rep{t.get('repeat', '?')}: outcome={t.get('outcome')} status={t.get('status')} "
          f"llm_calls={t.get('llm_calls')} failures={t.get('llm_call_failures')} agent_s={t.get('agent_s')} "
          f"cost={(t.get('llm_usage') or {}).get('cost_usd')} rewrites_kept={t.get('rewrites_kept')} "
          f"pragmas_in_final={t.get('pragmas_in_final')} speedups={ {k: x.get('speedup') for k, x in par.items()} }")
    print(f"   Phase A kept: {[(r['depth'], r['rid'], r['finds']) for r in rewrites]}; Phase B applied: {applied}")
    print(f"   D40 verdicts: {t.get('d40_verdicts')}; size runs: {size_runs}; crash messages to the model: {told}; "
          f"Phase B own-pragma crashes: {unsafe_own}")
    print(f"   Settle: keep={keeps}; repair/revert={repairs}; verified={verified}")
    print(f"           notes={notes}")
    print(f"   signatures: {signatures or 'none'}; verdict of the harness: {has_verdict}")
print(f"\ntrials {len(trials)}; failed model calls {failed_calls}; trials without a harness verdict {verdict_missing}")
if held:
    print("SMOKE3 HELD: " + "; ".join(held))
elif failed_calls:
    print("SMOKE3 RERUN (a model call failed)")
elif len(trials) == 2 and not verdict_missing:
    print("SMOKE3 PASSES")
else:
    print("SMOKE3 INCOMPLETE (a trial is missing or has no verdict) — read by hand")
