#!/usr/bin/env python3
"""E4 step 4 — the fast refresh's live trials, read out as pre-registered (THESIS_EXPERIMENTS §6, 18 Oct 2026),
written before any of its trials ran (the smoke included).

The agent with the fast refresh and the model's report of the dependences of its new lines (`fast_recon_v5` =
`default_v5` + `--fast-refresh --llm-recon`; the report is a follow-up turn of the rewrite's own session) on the 18
loops and on the contrast set with its control, × 5, beside the cells of the same agent with the full re-profile
(`default_v5`): E3's (corrected: `s341` from `e3c_v8_s341`) and E3b's (corrected: `s316` from `e3bc_s316`).
No test, as registered: the decision effect was tested in step 1 (E4-1); the live trials are read descriptively.

The outcome of a trial is E3's (main_comparison_stats' definitions, through e8_readout's `cell`): race-free verified
FASTER = the harness's FASTER and the race check clean (a program the gate kept counts as clean unless race_check.py
says otherwise); unusable = BROKEN, slower than the original, racy, not compiling, or the measurement edited.

  R1  per loop and per set: race-free verified FASTER, unusable programs, outcomes, beside the comparison cell
  R2  the refresh in the trials: refreshes per trial by kind (fast, full, fallback, failed), rewrites kept, reverts —
      the last two, with the agent's recorded reasons, printed since 19 Oct (§6)
  R3  the report: follow-ups answered ("reconstruction: …" in the log, the audit `llm_recon.json`), calls that failed,
      the agent's warnings that the model called a loop independent where static analysis records a dependence —
      the agent prints at most three per report, so beside that count the whole one from the audit (added 19 Oct,
      before the race check: §6)
  R4  model calls, cost and agent time per trial against the comparison cells; the profiling seconds a refresh saves
      are not logged per trial — estimated as the fast refreshes × (1.75 s − 1.54 s), step 1's medians on these loops
  R5  listed to be read by hand: every unusable program, every trial without a verdict, every loop whose race-free
      FASTER count moved by 2 or more against its comparison cell

    venv/bin/python evaluation/agent/tools/e4live_readout.py --out evaluation/agent/results/E04_fast_refresh/analysis \\
        --races evaluation/agent/results/E04_fast_refresh/checks/e4live_race_check/<part>/results.jsonl ...
    venv/bin/python evaluation/agent/tools/e4live_readout.py --smoke e4live_smoke     # the smoke's criterion only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import campaign  # noqa: E402
import main_comparison_stats as mcs  # noqa: E402
from e8_readout import E3_RACES, E3_REPLACED, E3_RUNS, _med, cell, cost, load, race_of, speedups  # noqa: E402

FAST, FULL = "fast_recon_v5", "default_v5"
RUNS = ("e4live_1", "e4live_2", "e4live_3", "e4live_4")
LOOPS18 = tuple(["tsvc_c2/" + k for k in "s112 s121 s1213 s127 s211 s212 s243 s244 s252 s254 s255 s281 s291 s292 "
                 "s293".split()] + ["tsvc_c3/s241", "tsvc_c3/s331", "tsvc_c4/s341"])
CONTRAST = tuple("tsvc_c4/" + k for k in "s314 s316 s3113 s315 s318 s319 s311".split())
E3B_RUNS = ("e3b_1", "e3b_2", "e3b_3", "e3b_4", "e3bc_s316")
E3B_REPLACED = {("e3b_1", "tsvc_c4/s316")}          # E3b's corrected table takes s316 from e3bc_s316
E3B_RACES = ("E03b_contrast_set/checks/e3b_race_check/discopop_writes/results.jsonl",
             "E03b_contrast_set/checks/e3bc_race_check/discopop_writes/results.jsonl")
STEP1_FULL_S, STEP1_FAST_S = 1.75, 1.54             # step 1's medians per refresh on these loops (e4_replay)

REFRESH = re.compile(r"\[refresh\] kind=(\w+)")
RECON = re.compile(r"reconstruction: (.*)")


def trial_log(t: Dict[str, Any]) -> Dict[str, Any]:
    """What the agent's own log says the refresh and the report did in one trial."""
    d = Path(t["_dir"])
    log = (d / "agent.log").read_text(errors="replace") if (d / "agent.log").exists() else ""
    audits = list(d.rglob("llm_recon.json"))
    # the audit holds one entry per report with every contradiction; the log's `[warn]` lines are only the first three
    # of each report (`phase_a.py`, `rep.contradicted[:3]`)
    entries: List[Dict[str, Any]] = [e for p in audits for e in json.loads(p.read_text())]
    return {"refresh": dict(Counter(REFRESH.findall(log))),
            "reports": RECON.findall(log),
            "report_call_failed": log.count("reconstruction call failed"),
            "fast_not_usable": log.count("fast refresh not usable"),
            "independent_warnings": log.count("[warn] model called loop"),
            "explorer_broke": log.count("reconstruction broke the explorer"),
            "audit": bool(audits),
            "audit_reports": len(entries),
            "contradicting": sum(len(e.get("contradicting_static_analysis") or []) for e in entries),
            "reports_contradicting": sum(1 for e in entries if e.get("contradicting_static_analysis")),
            "declared_independent": sum(len(e.get("loops_declared_independent") or []) for e in entries)}


def comparison(loops: Sequence[str], runs: Sequence[str], replaced: set, races_rel: Sequence[str]
               ) -> Tuple[List[Dict[str, Any]], Dict[Tuple[str, str, str, int], str]]:
    races = mcs.load_races([campaign.RESULTS / p for p in races_rel])
    names = {b.split("/")[1] for b in loops}
    ts = [t for r in runs for t in load(r, (FULL,))
          if (r, str(t.get("benchmark"))) not in replaced and str(t.get("benchmark")).split("/")[1] in names]
    return ts, races


def smoke(run: str) -> int:
    """The smoke's criterion as registered: both trials done without a failed call; in at least one, a kept rewrite
    refreshed fast and the report asked and placed (a `reconstruction:` line and the audit); no report call failed."""
    ts = load(run, (FAST,))
    ok = True
    print(f"smoke {run}: {len(ts)} trial(s) of `{FAST}`")
    mech = False
    for t in ts:
        lg = trial_log(t)
        flags = " ".join(t.get("agent_cmd") or []) if isinstance(t.get("agent_cmd"), list) else str(t.get("agent_cmd"))
        arm_ok = "--fast-refresh" in flags and "--llm-recon" in flags
        done = t.get("status") == "done" and int(t.get("llm_call_failures") or 0) == 0
        fast = int(t.get("refresh_fast") or 0) >= 1
        rep = bool(lg["reports"]) and lg["audit"]
        print(f"  {t.get('benchmark')} rep{t.get('repeat')}: status {t.get('status')}, failed calls "
              f"{t.get('llm_call_failures')}, outcome {t.get('outcome')}, flags {'ok' if arm_ok else 'MISSING'}; "
              f"refreshes {lg['refresh']} (record: fast {t.get('refresh_fast')}, full {t.get('refresh_full')}, "
              f"fallback {t.get('refresh_fallback')}); reports {len(lg['reports'])}, audit {lg['audit']}, "
              f"report calls failed {lg['report_call_failed']}, fast refresh unusable {lg['fast_not_usable']}")
        for r in lg["reports"]:
            print(f"      reconstruction: {r[:160]}")
        ok = ok and done and arm_ok and lg["report_call_failed"] == 0
        mech = mech or (fast and rep)
    ok = ok and mech and len(ts) >= 2
    print(f"criterion: {'PASSED' if ok else 'NOT PASSED'} (mechanism shown: {mech})")
    return 0 if ok else 1


def to_markdown(fast: List[Dict[str, Any]], races: Dict[Tuple[str, str, str, int], str],
                full: List[Dict[str, Any]], full_races: Dict[Tuple[str, str, str, int], str],
                logs: Dict[str, Dict[str, Any]], races_given: bool) -> Tuple[str, Dict[str, Any]]:
    def by_name(ts: List[Dict[str, Any]], b: str) -> List[Dict[str, Any]]:
        # a comparison cell is matched by the loop's name: E3 ran `s341` from tsvc_c2, its corrected cell from tsvc_c4
        return [t for t in ts if str(t.get("benchmark")).split("/")[1] == b.split("/")[1]]
    out = ["# E4 step 4 — the fast refresh's live trials: the read-out as pre-registered", "",
           "Registered in THESIS_EXPERIMENTS §6 on 18 Oct 2026 before any trial (\"Plan, E4 step 4 pre-registration\"). "
           f"`{FAST}` (the fast refresh and the model's report) beside `{FULL}` (the full re-profile; E3's and E3b's "
           "corrected cells). No test, as registered."
           + ("" if races_given else " **No race file was given: every gate-kept program counts as clean.**"), ""]
    res: Dict[str, Any] = {"sets": {}, "loops": {}, "r2": {}}
    r2_rows: List[str] = []
    for title, loops in (("The 18 loops", LOOPS18), ("The contrast set and its control (`s311`)", CONTRAST)):
        out += [f"## {title}", "",
                "| loop | full re-profile (E3/E3b) race-free FASTER | fast refresh + report | unusable full / fast | "
                "outcomes, fast | speed-up 6 / 12, fast (median) | fast refreshes (sum) | reports answered (sum) |",
                "|---|---:|---:|---|---|---:|---:|---:|"]
        set_f: List[Dict[str, Any]] = []
        set_c: List[Dict[str, Any]] = []
        for b in loops:
            tf, tc = by_name(fast, b), by_name(full, b)
            cf, cc = cell(tf, races), cell(tc, full_races)
            set_f += tf
            set_c += tc
            res["loops"][b] = {"fast": cf, "full": cc}
            nfast = sum(int(t.get("refresh_fast") or 0) for t in tf)
            nrep = sum(len(logs[t["_dir"]]["reports"]) for t in tf)
            out.append(f"| `{b.split('/')[1]}` | {cc['faster_race_free']} of {cc['n']} | {cf['faster_race_free']} of "
                       f"{cf['n']} | {cc['unusable']} / {cf['unusable']} | "
                       f"{', '.join(f'{k} {n}' for k, n in sorted(cf['outcomes'].items()))} | "
                       f"{_med(cf['speedup_6'])} / {_med(cf['speedup_12'])} | {nfast} | {nrep} |")
        sf, sc = cell(set_f, races), cell(set_c, full_races)
        res["sets"][title] = {"fast": sf, "full": sc}
        # `llm_calls` counts the rewrite requests only; the follow-up report goes through another path and is in
        # the usage log (`llm_usage.calls_recorded`) and the cost, not in `llm_calls` (seen in the smoke, 18 Oct)
        out += ["", "| setup | trials | race-free FASTER | unusable | rewrite calls (median) | all calls, usage log "
                "(median) | cost $ (sum) | full profiles (median) | agent s (median) |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for name, c, ts in ((f"`{FULL}` (E3/E3b)", sc, set_c), (f"`{FAST}`", sf, set_f)):
            usage_calls = [float(((t.get("llm_usage") or {}).get("calls_recorded")) or 0) for t in ts]
            out.append(f"| {name} | {c['trials']} | {c['faster_race_free']} of {c['n']} | {c['unusable']} | "
                       f"{_med(c['calls'])} | {_med(usage_calls)} | {sum(c['cost']):.2f} | {_med(c['full_profiles'])} | "
                       f"{_med(c['agent_s'])} |")
            # R2's rewrites kept and reverts, with the reasons the agent recorded (added 19 Oct: registered in R2, not
            # printed by the read-out as first written; §6)
            ex: Counter = Counter()
            d40: Counter = Counter()
            for t in ts:
                ex.update(t.get("exposure_verdicts") or {})
                d40.update(t.get("d40_verdicts") or {})
            kept = sum(int(t.get("rewrites_kept") or 0) for t in ts)
            reverts = sum(int(t.get("reverts") or 0) for t in ts)
            ex_other = sum(ex.values()) - ex["exposed"] - ex["no_pattern"] - ex["no_usable_pragma"]
            d40_other = sum(d40.values()) - d40["ok"] - d40["not_faster"] - d40["pattern_broken"]
            r2_rows.append(f"| {title.split(' (')[0]} | {name} | {len(ts)} | {kept} | {reverts} | {ex['exposed']} | "
                           f"{ex['no_pattern']} | {ex['no_usable_pragma']} | {ex_other} | {d40['ok']} | "
                           f"{d40['not_faster']} | {d40['pattern_broken']} | {d40_other} |")
            res["r2"][f"{title} / {name}"] = {"trials": len(ts), "rewrites_kept": kept, "reverts": reverts,
                                              "exposure": dict(ex), "d40": dict(d40)}
        out.append("")
    kinds: Counter = Counter()
    for t in fast:
        kinds.update(logs[t["_dir"]]["refresh"])
    n_fast = sum(int(t.get("refresh_fast") or 0) for t in fast)
    out += ["## The refresh and the report in the trials", "",
            f"- refreshes after a kept rewrite, by kind (the agent's own `[refresh]` lines): "
            f"{', '.join(f'{k} {n}' for k, n in sorted(kinds.items())) or 'none'}",
            f"- trials with at least one fast refresh: {sum(1 for t in fast if int(t.get('refresh_fast') or 0))} of "
            f"{len(fast)}; with a fallback to the full re-profile: "
            f"{sum(1 for t in fast if logs[t['_dir']]['fast_not_usable'])}",
            f"- reports answered and placed: {sum(len(logs[t['_dir']]['reports']) for t in fast)} in "
            f"{sum(1 for t in fast if logs[t['_dir']]['reports'])} trials; report calls that failed: "
            f"{sum(logs[t['_dir']]['report_call_failed'] for t in fast)}; reports that broke the explorer: "
            f"{sum(logs[t['_dir']]['explorer_broke'] for t in fast)}",
            f"- the agent's warnings that the model called a loop independent where static analysis records a "
            f"dependence: {sum(logs[t['_dir']]['independent_warnings'] for t in fast)} (the agent prints at most three "
            f"per report); the whole count, from the audit `llm_recon.json` (one per loop, variable and dependence "
            f"type): {sum(logs[t['_dir']]['contradicting'] for t in fast)} in "
            f"{sum(logs[t['_dir']]['reports_contradicting'] for t in fast)} of "
            f"{sum(logs[t['_dir']]['audit_reports'] for t in fast)} reports, in "
            f"{sum(1 for t in fast if logs[t['_dir']]['contradicting'])} trials; loops the model declared independent: "
            f"{sum(logs[t['_dir']]['declared_independent'] for t in fast)}",
            f"- profiling seconds a refresh saved, estimated (step 1's medians, {STEP1_FULL_S} s against "
            f"{STEP1_FAST_S} s): {n_fast} fast refreshes × {STEP1_FULL_S - STEP1_FAST_S:.2f} s = "
            f"{n_fast * (STEP1_FULL_S - STEP1_FAST_S):.1f} s, against "
            f"{sum(float(t.get('agent_s') or 0) for t in fast):.0f} s of agent time in these trials", ""]
    out += ["## Rewrites kept and reverted, with the agent's recorded reasons (R2)", "",
            "After a rewrite that passed the quality gate and its refresh: did DiscoPoP find a usable pattern in the "
            "changed lines (the exposure verdict), and for a pattern found, D40's judgement of its pragmas — `ok` kept, "
            "`not_faster` reverted, `pattern_broken` reverted because a pragma failed the safety gate. Sums over the "
            "trials, from their records.", "",
            "| set | setup | trials | rewrites kept | reverts | pattern found | no pattern | no usable pragma | other | "
            "D40 ok | D40 not faster | D40 pragma failed the safety gate | D40 other |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"] + r2_rows + [""]
    moved = [b for b, v in res["loops"].items() if abs(v["fast"]["faster_race_free"] - v["full"]["faster_race_free"]) >= 2]
    allc = [v[k] for v in res["loops"].values() for k in ("fast", "full")]
    out += ["## Every unusable program", ""] + ([f"- {u}" for c in allc for u in c["unusable_cases"]] or ["- none"])
    out += ["", "## Trials without a verdict (left out of every rate)", ""] + (
        [f"- {u}" for c in allc for u in c["without_verdict"]] or ["- none"])
    out += ["", "## To be read by hand (registered): loops that moved by 2 or more race-free FASTER", ""] + (
        [f"- `{b}`: full {res['loops'][b]['full']['faster_race_free']} of {res['loops'][b]['full']['n']}, fast "
         f"{res['loops'][b]['fast']['faster_race_free']} of {res['loops'][b]['fast']['n']}" for b in moved] or ["- none"])
    res["moved"] = moved
    res["refresh_kinds"] = dict(kinds)
    res["trials"] = [{"dir": str(Path(t["_dir"]).relative_to(campaign.RESULTS)), "benchmark": t.get("benchmark"),
                      "repeat": t.get("repeat"), "outcome": t.get("outcome"), "race": race_of(t, races),
                      "speedups": speedups(t), "cost": cost(t), "agent_s": t.get("agent_s"),
                      "llm_calls": t.get("llm_calls"), **logs[t["_dir"]]} for t in fast]
    return "\n".join(out) + "\n", res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--races", type=Path, action="append", default=[], help="race_check.py results of the live runs")
    ap.add_argument("--runs", default=",".join(RUNS), help="the live runs, comma-separated")
    ap.add_argument("--smoke", default="", help="check only the smoke's criterion on this run")
    a = ap.parse_args()
    if a.smoke:
        return smoke(a.smoke)
    if a.out is None:
        ap.error("--out is required for the read-out")
    races = mcs.load_races(a.races)
    fast = [t for r in a.runs.split(",") if r for t in load(r, (FAST,))]
    full3, r3 = comparison(LOOPS18, E3_RUNS, E3_REPLACED, E3_RACES)
    full3b, r3b = comparison(CONTRAST, E3B_RUNS, E3B_REPLACED, E3B_RACES)
    full_races = {**r3, **r3b}
    logs = {t["_dir"]: trial_log(t) for t in fast}
    md, res = to_markdown(fast, races, full3 + full3b, full_races, logs, bool(a.races))
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "e4live_readout.md").write_text(md)
    (a.out / "e4live_readout.json").write_text(json.dumps(res, indent=1, default=str))
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
