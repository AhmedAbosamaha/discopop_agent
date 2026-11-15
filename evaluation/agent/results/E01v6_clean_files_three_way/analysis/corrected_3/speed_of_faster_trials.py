#!/usr/bin/env python3
"""E1-v6, third corrected read-out: how fast were the programs of each setup where it succeeded?

Descriptive, added on 15 Nov 2026 for the thesis's main comparison (the author asked how fast the models alone were;
the registered read-out states the agent's speed per loop and, per setup, one median over the trials the harness
judged FASTER, which for a model alone still includes its racy programs). No trial, count or test changes.

For the agent and for each model alone, over the 18 class-R loops:
  * the median speedup of the trials that are FASTER AND RACE-FREE (the thesis's "faster"), beside the median over all
    FASTER trials, which must reproduce `median_speedup_of_faster` of the archived read-out (checked below);
  * per loop, the median speedup of those trials, and the comparison with the agent on the loops both solved.
A speedup is the harness's own measurement: the better of 6 and 12 threads at the verification size.

The trials, the dropped loops, the same-loop rule and the race files are those of build.sh in this folder, loaded with
the functions of agent/tools/main_comparison_stats.py. Run from evaluation/:
    ../venv/bin/python agent/results/E01v6_clean_files_three_way/analysis/corrected_3/speed_of_faster_trials.py
"""
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, "agent/tools")
import campaign  # noqa: E402
import figures  # noqa: E402
import main_comparison_stats as m  # noqa: E402

E = Path("agent/results/E01v6_clean_files_three_way")
OUT = E / "analysis" / "corrected_3"
AGENT_ARM, BARE_ARM = "default_v4", "bare_llm_v4"
AD = f"{AGENT_ARM}+discopop_gate_v4"
figures.BASELINE_ARM = "discopop_gate_v4"
AGENT_RUNS = ("e1v6_r_1", "e1v6_r_2", "e1v6_r_3", "e1v6_r_4", "e1v6_a", "e1v6_d", "e1v6c_s281", "e1v6c_v7_agent",
              "e1v6c_v7_control", "e1v6c_s241", "e1v6c_v8_agent")
BASE_DROPS = ("e1v6_r_3:tsvc_c2/s281", "e1v6_r_4:tsvc_c2/s331", "e1v6_a:tsvc_c2/s313", "e1v6_r_2:tsvc_c2/s241",
              "e1v6_r_4:tsvc_c2/s341")
MODELS = (("haiku", "Haiku 4.5"), ("sonnet", "Sonnet 5"), ("opus", "Opus 5.5"), ("fable", "Fable 5.1"))


def load(mod):
    """The trials and race verdicts of one model's three-way read-out, as build.sh names them."""
    same_loop = m.same_loop_map(["tsvc_c2/s241=tsvc_c3/s241"])
    runs = [f"{r}:{AD}" for r in AGENT_RUNS]
    runs += [f"e1v6_bare_{mod}:{BARE_ARM}", f"e1v6c_v7_bare_{mod}:{BARE_ARM}", f"e1v6c_v8_bare_{mod}:{BARE_ARM}"]
    drops = {tuple(d.split(":", 1)) for d in BASE_DROPS
             + (f"e1v6_bare_{mod}:tsvc_c2/s331", f"e1v6_bare_{mod}:tsvc_c2/s313", f"e1v6_bare_{mod}:tsvc_c2/s341")}
    races = m.load_races(
        [E / f"checks/e1v6_race_check/{mod}/results.jsonl", E / f"checks/e1v6c_race_check/v7_{mod}/results.jsonl",
         E / "checks/e1v6_race_check/control_agent/results.jsonl", E / "checks/e1v6c_race_check/s281_agent/results.jsonl",
         E / "checks/e1v6c_race_check/v7_agent/results.jsonl", E / "checks/e1v6c_s241_race_check/s241_agent/results.jsonl",
         E / "checks/e1v6c_v8_race_check/v8_agent/results.jsonl", E / f"checks/e1v6c_v8_race_check/v8_{mod}/results.jsonl"],
        same_loop)
    trials = []
    for spec in runs:
        run, _, arms = spec.partition(":")
        keep = set(arms.split("+"))
        root = next((d for d in (m.HERE.parent / "runs" / run, campaign.find_run(run)) if d and d.exists()), None)
        if root is None:
            sys.exit(f"run {run} not found under runs/ or results/")
        for p in sorted(root.glob("benchmarks/**/trial.json")):
            t = json.loads(p.read_text())
            t.setdefault("run_id", run)
            if t.get("arm") not in keep or (run, str(t.get("benchmark"))) in drops:
                continue
            m.count_as(t, same_loop)
            trials.append(t)
    classes = figures._classes()
    ts = [t for t in trials if classes.get(str(t.get("benchmark")), "") == "R"]
    benches = sorted({str(t.get("benchmark")) for t in ts if t.get("arm") == BARE_ARM})
    return ts, benches, races


def setup(ts, benches, races, arm):
    at = [t for t in ts if t.get("arm") == arm and str(t.get("benchmark")) in benches]
    fast = [t for t in at if m._with_verdict(t) and t.get("outcome") == "FASTER"]

    def race(t):  # as main_comparison_stats.three_way
        key = (m._run_of(t), str(t.get("benchmark")), str(arm), int(t.get("repeat") or 0))
        if arm != BARE_ARM and not m._model_only(arm):
            return "clean" if races.get(key, "clean") in ("clean", "unchanged") else races[key]
        return races.get(key, "unchecked")

    clean = [t for t in fast if race(t) == "clean"]
    sp_fast = [x for x in (m._best_speedup(t) for t in fast) if x]
    sp_clean = [x for x in (m._best_speedup(t) for t in clean) if x]
    per_loop = {}
    for t in clean:
        per_loop.setdefault(str(t.get("benchmark")).split("/")[-1], []).append(m._best_speedup(t))
    return {"trials": len(at), "faster": len(fast), "faster_race_free": len(clean),
            "median_speedup_of_faster": statistics.median(sp_fast) if sp_fast else None,
            "median_speedup_of_faster_race_free": statistics.median(sp_clean) if sp_clean else None,
            "lowest": min(sp_clean) if sp_clean else None, "highest": max(sp_clean) if sp_clean else None,
            "loops_solved": len(per_loop),
            "per_loop_median": {k: statistics.median(v) for k, v in sorted(per_loop.items())}}


def main():
    res = {}
    for mod, name in MODELS:
        ts, benches, races = load(mod)
        archived = json.loads((OUT / mod / "main_comparison_stats.json").read_text())["three_way"]["classes"]["R"]["arms"]
        if mod == "haiku":
            res["the agent (Haiku 4.5)"] = setup(ts, benches, races, AGENT_ARM)
            checks = [("the agent (Haiku 4.5)", "DiscoPoP + agent")]
        else:
            checks = []
        res[f"{name} alone"] = setup(ts, benches, races, BARE_ARM)
        checks.append((f"{name} alone", "model alone"))
        for mine, theirs in checks:  # the same trials as the archived read-out, or stop
            a, b = res[mine], archived[theirs]
            same = (a["trials"] == b["trials"] and a["faster"] == b["faster"]["k"]
                    and a["faster_race_free"] == b["faster_race_free"]["k"]
                    and a["median_speedup_of_faster"] == b["median_speedup_of_faster"])
            if not same:
                sys.exit(f"{mine}: does not reproduce the archived read-out ({OUT / mod / 'main_comparison_stats.json'})")
    agent = res["the agent (Haiku 4.5)"]["per_loop_median"]
    for name, v in res.items():
        if name.startswith("the agent"):
            continue
        common = sorted(set(v["per_loop_median"]) & set(agent))
        ratios = [v["per_loop_median"][lp] / agent[lp] for lp in common]
        v["against_the_agent"] = {"loops_both_solved": len(common),
                                  "model_alone_faster": sum(1 for r in ratios if r > 1),
                                  "agent_faster": sum(1 for r in ratios if r < 1),
                                  "median_ratio_model_alone_over_agent": statistics.median(ratios)}
    (OUT / "speed_of_faster_trials.json").write_text(json.dumps(res, indent=1) + "\n")
    md = ["# E1-v6, third corrected read-out: the speed of each setup's faster trials", "",
          "Descriptive, added 15 Nov 2026 (`speed_of_faster_trials.py`); no trial, count or test changes. Speedup: the "
          "harness's measurement, the better of 6 and 12 threads at the verification size, over the sequential original. "
          "The 18 class-R loops, 90 trials per setup. \"Faster\" in the thesis means faster and race-free; the registered "
          "read-out's median is over all trials the harness judged FASTER, racy ones included, and is reproduced here.", "",
          "| setup | FASTER | median | faster and race-free | median | lowest | highest | loops solved |",
          "|---|---|---|---|---|---|---|---|"]
    for name, v in res.items():
        md.append(f"| {name} | {v['faster']} | {v['median_speedup_of_faster']:.2f}× | {v['faster_race_free']} | "
                  f"**{v['median_speedup_of_faster_race_free']:.2f}×** | {v['lowest']:.2f}× | {v['highest']:.2f}× | "
                  f"{v['loops_solved']} of 18 |")
    md += ["", "Each median covers the setup's own faster trials, so the setups are compared on different loops. On the "
               "loops that the agent and a model alone both solved (median speedup of the faster and race-free trials per "
               "loop):", "",
           "| model alone | loops both solved | model alone faster | the agent faster | median ratio, model alone / agent |",
           "|---|---|---|---|---|"]
    for name, v in res.items():
        if "against_the_agent" in v:
            c = v["against_the_agent"]
            md.append(f"| {name} | {c['loops_both_solved']} | {c['model_alone_faster']} | {c['agent_faster']} | "
                      f"{c['median_ratio_model_alone_over_agent']:.2f} |")
    loops = sorted({lp for v in res.values() for lp in v["per_loop_median"]})
    md += ["", "Per loop, the median speedup of the faster and race-free trials (— : none):", "",
           "| loop | " + " | ".join(res) + " |", "|---|" + "---|" * len(res)]
    for lp in loops:
        md.append(f"| `{lp}` | " + " | ".join(f"{v['per_loop_median'][lp]:.2f}×" if lp in v["per_loop_median"] else "—"
                                              for v in res.values()) + " |")
    (OUT / "speed_of_faster_trials.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
