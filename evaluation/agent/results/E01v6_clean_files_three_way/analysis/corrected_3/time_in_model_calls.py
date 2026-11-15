#!/usr/bin/env python3
"""E1-v6, third corrected read-out: how much of the agent's time is spent in model calls?

Descriptive, added on 15 Nov 2026. The thesis's main comparison and its discussion said since 31 Oct that most of the
agent's time goes into building, profiling and timing, not into the model; this file checks that sentence against the
read-out's own trial table and finds the opposite. No trial, count or test changes.

Over the agent's trials of `trials.csv` in this folder (arm `default_v4`: the 18 class-R loops x 5 and the controls):
  * the agent's seconds (`agent_s`) and the seconds it waited for the model (`model_seconds`, the summed duration of
    the trial's model calls), in sum and as each trial's share;
  * the seconds of profiling: the trial's first profile (`profile_s`) and its re-profiles after kept rewrites
    (`refresh_full`), each re-profile counted at the first profile's seconds, because a trial times only its first
    profile and the rewritten programs are of the same size (the record's method of 9 Oct 2026);
  * the three numbers the thesis's cost sentence states, recomputed: the median model calls and agent minutes per
    trial and the mean model cost per trial.
Run from anywhere:
    venv/bin/python evaluation/agent/results/E01v6_clean_files_three_way/analysis/corrected_3/time_in_model_calls.py
"""
import csv
import json
import statistics
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARM = "default_v4"


def main():
    rows = [r for r in csv.DictReader((OUT / "trials.csv").open()) if r["arm"] == ARM]
    agent = [float(r["agent_s"]) for r in rows]
    model = [float(r["model_seconds"]) for r in rows]
    share = sorted(m / a for m, a in zip(model, agent))
    if not rows or min(agent) <= 0 or max(share) > 1:
        raise SystemExit("a trial without agent seconds, or with more model seconds than agent seconds")
    profiles = sum(1 + int(float(r["refresh_full"])) for r in rows)
    profiling = sum((1 + float(r["refresh_full"])) * float(r["profile_s"]) for r in rows)
    if any(float(r["refresh_fast"]) for r in rows):
        raise SystemExit("a trial with a fast refresh: the profiling seconds above would not hold")
    res = {"arm": ARM, "trials": len(rows), "agent_s": round(sum(agent), 1), "model_s": round(sum(model), 1),
           "profiles": profiles, "profiling_s": round(profiling, 1), "profiling_share": round(profiling / sum(agent), 4),
           "share_of_all_seconds": round(sum(model) / sum(agent), 4),
           "share_per_trial": {"median": round(statistics.median(share), 4), "lower_quartile": round(share[len(share) // 4], 4),
                               "upper_quartile": round(share[3 * len(share) // 4], 4), "smallest": round(share[0], 4),
                               "largest": round(share[-1], 4)},
           "trials_with_more_than_half_in_model_calls": sum(1 for s in share if s > 0.5),
           "median_agent_minutes": round(statistics.median(agent) / 60, 2),
           "median_model_calls": statistics.median(float(r["llm_calls"]) for r in rows),
           "mean_cost_usd": round(statistics.mean(float(r["cost_usd_equivalent"]) for r in rows), 3)}
    (OUT / "time_in_model_calls.json").write_text(json.dumps(res, indent=1) + "\n")
    sp = res["share_per_trial"]
    md = ["# E1-v6, third corrected read-out: the agent's time in model calls", "",
          "Descriptive, added 15 Nov 2026 (`time_in_model_calls.py`, from `trials.csv` of this folder); no trial, count or test "
          f"changes. The agent's {res['trials']} trials (`{ARM}`: the 18 class-R loops × 5 and the controls).", "",
          "| | |", "|---|---:|",
          f"| the agent's seconds, all trials | {res['agent_s']:,.0f} |",
          f"| of them in model calls | {res['model_s']:,.0f} |",
          f"| **share of the agent's time in model calls** | **{100 * res['share_of_all_seconds']:.1f} %** |",
          f"| the share within a trial, median | {100 * sp['median']:.0f} % |",
          f"| lower and upper quartile | {100 * sp['lower_quartile']:.0f} % – {100 * sp['upper_quartile']:.0f} % |",
          f"| smallest and largest | {100 * sp['smallest']:.0f} % – {100 * sp['largest']:.0f} % |",
          f"| trials with more than half of their time in model calls | {res['trials_with_more_than_half_in_model_calls']} of "
          f"{res['trials']} |",
          f"| profiles (the first of each trial and {profiles - res['trials']} re-profiles) | {profiles} |",
          f"| seconds of profiling, each profile at its trial's first profile's seconds | {res['profiling_s']:,.0f} |",
          f"| **share of the agent's time in profiling** | **{100 * res['profiling_share']:.1f} %** |",
          f"| median model calls per trial | {res['median_model_calls']:g} |",
          f"| median agent minutes per trial | {res['median_agent_minutes']:.1f} |",
          f"| mean model cost per trial | ${res['mean_cost_usd']:.2f} |", "",
          "The share of all seconds is larger than the median share within a trial because long trials are long through "
          "their model calls: a trial that uses all its attempts waits for the model almost all of its time.", "",
          "Profiling is a small part of the rest. A trial times its first profile only; a re-profile after a kept rewrite "
          "is counted at the same seconds, the rewritten program being of the same size. The instrumented runs that a fast "
          "refresh would skip are a part of that again: 0.08 % of the agent's time on the 90 trials of the 18 loops (the "
          "record's row of 9 Oct 2026, from the second corrected read-out)."]
    (OUT / "time_in_model_calls.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
