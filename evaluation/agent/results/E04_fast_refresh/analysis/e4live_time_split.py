#!/usr/bin/env python3
"""E4 step 4, the fast refresh's whole trials: where their time goes.

Descriptive, added on 15 Nov 2026 for the thesis's fast-refresh figure (the author asked where the time saved is; the
registered read-out states the agent's seconds per trial and the cost, not how those seconds divide). No trial, count
or test changes.

For each set (the 18 loops; the contrast set with its control) and setup (the full re-profile = `default_v5`, E3's and
E3b's corrected cells; the fast refresh and the model's report = `fast_recon_v5`):
  * the agent's seconds and how many of them are model calls: each trial's `llm_usage.model_seconds`, which must equal
    the sum of the `duration_ms` of the rows of its usage log `llm_usage.jsonl` (checked per trial);
  * the calls in the usage log, the rewrite calls (`llm_calls`), the reports (one after each fast refresh), and the
    seconds per call.
The trials are those of the registered read-out, loaded with its own functions (agent/tools/e4live_readout.py). The
script stops unless it reproduces that read-out's trial counts, agent seconds and cost (e4live_readout.json).

Run from anywhere:  venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/e4live_time_split.py
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[2] / "tools"))
import e4live_readout as E  # noqa: E402
from e8_readout import E3_RACES, E3_REPLACED, E3_RUNS, load  # noqa: E402

SETS = (("The 18 loops", E.LOOPS18), ("The contrast set and its control (`s311`)", E.CONTRAST))
SETUPS = (("full", "full re-profile (`default_v5`, E3/E3b)"), ("fast", "fast refresh + report (`fast_recon_v5`)"))


def trials():
    fast = [t for r in E.RUNS for t in load(r, (E.FAST,))]
    full18, _ = E.comparison(E.LOOPS18, E3_RUNS, E3_REPLACED, E3_RACES)
    fullc, _ = E.comparison(E.CONTRAST, E.E3B_RUNS, E.E3B_REPLACED, E.E3B_RACES)
    out = {}
    for (title, loops), full in zip(SETS, (full18, fullc)):
        names = {b.split("/")[1] for b in loops}
        out[title] = {"full": full, "fast": [t for t in fast if str(t.get("benchmark")).split("/")[1] in names]}
    assert sum(len(v["fast"]) for v in out.values()) == len(fast), "a fast-refresh trial belongs to neither set"
    return out


def cell(ts):
    model_s, calls = 0.0, 0
    for t in ts:
        rows = [json.loads(line) for line in (Path(t["_dir"]) / "llm_usage.jsonl").read_text().splitlines() if line.strip()]
        from_log = sum(float(r.get("duration_ms") or 0) for r in rows) / 1000.0
        recorded = float((t.get("llm_usage") or {}).get("model_seconds") or 0)
        if abs(from_log - recorded) > 0.5:  # the trial record rounds to a tenth of a second
            sys.exit(f"{t['_dir']}: model seconds {recorded} in the trial record, {from_log:.1f} in its usage log")
        model_s += from_log
        calls += len(rows)
    agent_s = sum(float(t.get("agent_s") or 0) for t in ts)
    return {"trials": len(ts), "agent_s": round(agent_s, 1), "model_s": round(model_s, 1),
            "other_s": round(agent_s - model_s, 1), "calls_usage_log": calls,
            "rewrite_calls": sum(int(t.get("llm_calls") or 0) for t in ts),
            "reports": sum(int(t.get("refresh_fast") or 0) for t in ts),
            "full_profiles": sum(int(t.get("refresh_full") or 0) for t in ts),
            "s_per_call": round(model_s / calls, 1),
            "cost": round(sum(float((t.get("llm_usage") or {}).get("cost_usd") or 0) for t in ts), 2),
            "finished_from": min(str(t.get("finished_at"))[:10] for t in ts),
            "finished_to": max(str(t.get("finished_at"))[:10] for t in ts),
            "hosts": sorted({str(t.get("host")) for t in ts})}


def main():
    archived = json.loads((OUT / "e4live_readout.json").read_text())["sets"]
    res = {"sets": {}, "all": {}}
    for title, arms in trials().items():
        res["sets"][title] = {}
        for arm, _ in SETUPS:
            c = cell(arms[arm])
            a = archived[title][arm]
            same = (c["trials"] == a["n"] and abs(c["agent_s"] - sum(a["agent_s"])) < 0.5
                    and abs(c["cost"] - sum(a["cost"])) < 0.01)
            if not same:
                sys.exit(f"{title}, {arm}: does not reproduce the registered read-out ({OUT / 'e4live_readout.json'})")
            c["faster_race_free"] = a["faster_race_free"]  # the registered read-out's count, quoted
            res["sets"][title][arm] = c
    for arm, _ in SETUPS:
        cells = [res["sets"][t][arm] for t, _ in SETS]
        tot = {k: round(sum(c[k] for c in cells), 2) for k in cells[0]
               if k not in ("s_per_call", "finished_from", "finished_to", "hosts")}
        tot["finished_from"] = min(c["finished_from"] for c in cells)
        tot["finished_to"] = max(c["finished_to"] for c in cells)
        tot["hosts"] = sorted({h for c in cells for h in c["hosts"]})
        tot["s_per_call"] = round(tot["model_s"] / tot["calls_usage_log"], 1)
        res["all"][arm] = tot
    saved = res["all"]["fast"]["reports"] * (E.STEP1_FULL_S - E.STEP1_FAST_S)
    res["profiling_seconds_saved_estimate"] = round(saved, 1)
    (OUT / "e4live_time_split.json").write_text(json.dumps(res, indent=1) + "\n")

    def row(name, arm_label, c):
        return (f"| {name} | {arm_label} | {c['trials']} | {c['faster_race_free']} | {c['agent_s']:,.0f} | {c['model_s']:,.0f} | "
                f"{100 * c['model_s'] / c['agent_s']:.0f} % | {c['other_s']:,.0f} | {c['calls_usage_log']} | "
                f"{c['rewrite_calls']} | {c['reports']} | {c['s_per_call']:.1f} | {c['cost']:.2f} |")

    md = ["# E4 step 4 — where the time of the whole trials goes", "",
          "Descriptive, added 15 Nov 2026 (`e4live_time_split.py`); no trial, count or test changes. The trials are those of "
          "the registered read-out (`e4live_readout.md`), whose trial counts, agent seconds and cost this script reproduces "
          "before it writes anything. *In model calls*: the seconds the agent waited for the model, each trial's "
          "`llm_usage.model_seconds`, equal to the summed `duration_ms` of its usage log. *Model calls*: the rows of the usage "
          "log; with the fast refresh they include the reports, one after each fast refresh, which `llm_calls` (the rewrite "
          "calls) does not count.", "",
          "| set | setup | trials | race-free FASTER | agent time, s | in model calls, s | share | everything else, s | "
          "model calls | rewrite calls | reports | s per call | cost $ |",
          "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for title, _ in SETS:
        for arm, label in SETUPS:
            md.append(row(title, label, res["sets"][title][arm]))
    for arm, label in SETUPS:
        md.append(row("**both sets**", label, res["all"][arm]))
    f, u = res["all"]["fast"], res["all"]["full"]
    md += ["",
           f"Over both sets the agent's time rose from {u['agent_s'] / 3600:.1f} to {f['agent_s'] / 3600:.1f} hours "
           f"(+{f['agent_s'] - u['agent_s']:,.0f} s). The time in model calls rose from {u['model_s'] / 3600:.1f} to "
           f"{f['model_s'] / 3600:.1f} hours (+{f['model_s'] - u['model_s']:,.0f} s); everything else (building, the refresh or "
           f"re-profile, the gate's checks, timing) went from {u['other_s'] / 3600:.2f} to {f['other_s'] / 3600:.2f} hours "
           f"({f['other_s'] - u['other_s']:+,.0f} s). The usage log holds {f['calls_usage_log']} calls against "
           f"{u['calls_usage_log']}: {f['reports']} of the difference are reports. A call took {u['s_per_call']:.1f} s on "
           f"average with the full re-profile and {f['s_per_call']:.1f} s with the fast refresh, so the added time is added "
           "calls, not slower ones.", "",
           f"What skipping the instrumented run saved, as the registered read-out estimates it (step 1's medians per refresh, "
           f"{E.STEP1_FULL_S} s against {E.STEP1_FAST_S} s): {f['reports']} fast refreshes × "
           f"{E.STEP1_FULL_S - E.STEP1_FAST_S:.2f} s = {saved:.1f} s. The difference in \"everything else\" above is not this "
           "saving: it also holds the directive checks and the timing, which differ from trial to trial.", "",
           f"The two setups were not run side by side: the full re-profile's trials are E3's and E3b's and finished between "
           f"{u['finished_from']} and {u['finished_to']}, the fast refresh's between {f['finished_from']} and "
           f"{f['finished_to']}; "
           + ("both on one machine." if u["hosts"] == f["hosts"] and len(u["hosts"]) == 1 else "not all on one machine.")]
    (OUT / "e4live_time_split.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
