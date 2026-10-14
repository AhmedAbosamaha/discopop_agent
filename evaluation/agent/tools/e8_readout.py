#!/usr/bin/env python3
"""E8's read-out as pre-registered (THESIS_EXPERIMENTS §6, 14 Oct 2026), written before any counted trial was fetched.

The one test and the descriptive read-outs fixed in "Plan, E8 pre-registration", with the two additions of the
afternoon rows: where Fix 106's `[keep]` acted, and candidate Fix 107's signature, counted in every log.

  H8   on the depth set (`e8v5_set`: `tsvc_c5` s2251 s221 s257 × 5), race-free verified FASTER with `depth1_v5`
       against `default_v5` — Cochran-Mantel-Haenszel stratified by loop, one-sided (depth 1 ahead), the
       Mantel-Haenszel odds ratio and the exact conditional test beside it, α 0.05; refuted as registered also
       if `depth1_v5` ships more unusable programs than `default_v5` on the depth set.  A member of the
       campaign's family already: the bound is p × 54.

The outcome of a trial is E3's, from main_comparison_stats' own definitions (imported, not restated): race-free
verified FASTER = the harness's FASTER and the race check clean (a program the gate kept counts as clean unless
race_check.py says otherwise); unusable = BROKEN, slower than the original, racy, not compiling, or the
measurement edited after every redo.  The statistics are e2b1_stats.py's (checked there by `--self-test`).

The 18 loops (`e8v5_r_1` to `_3`, depth 1 and 2 × 3) are read beside E3's depth-0 cells (`default_v5`, 5 per
loop: `e3_r_1` to `e3_r_4`, `s341` from `e3c_v8_s341` as in E3's corrected table) — no test, as registered.

    venv/bin/python evaluation/agent/tools/e8_readout.py --out evaluation/agent/results/E08_restructuring_depth/analysis \\
        --races evaluation/agent/results/E08_restructuring_depth/checks/e8v5_race_check/results.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import campaign  # noqa: E402
import figures  # noqa: E402
import main_comparison_stats as mcs  # noqa: E402
from e2b1_stats import Table, cmh, exact_conditional, mh_odds_ratio  # noqa: E402

FAMILY = 54
SET_RUN = "e8v5_set"
LOOP_RUNS = ("e8v5_r_1", "e8v5_r_2", "e8v5_r_3")
DEPTH0, DEPTH1, DEPTH2 = "default_v5", "depth1_v5", "depth2_v5"
ARMS = (DEPTH0, DEPTH1, DEPTH2)
SET_LOOPS = ("tsvc_c5/s2251", "tsvc_c5/s221", "tsvc_c5/s257")
E3_RUNS = ("e3_r_1", "e3_r_2", "e3_r_3", "e3_r_4", "e3c_v8_s341")
E3_REPLACED = {("e3_r_4", "tsvc_c2/s341")}          # E3's corrected table takes s341 from e3c_v8_s341
E3_RACES = ("E03_who_writes_the_pragmas/checks/e3_race_check/discopop_writes/results.jsonl",
            "E03_who_writes_the_pragmas/checks/e3c_v8_race_check/discopop_writes/results.jsonl")

BLOCK = re.compile(r"^┌─ \[depth=(\d+)\] \S+ (\S+) \(lines (\d+)–(\d+)\)")
FINDS = re.compile(r"\w+ @ lines (\d+)–(\d+)")
PATTERN = re.compile(r"^┌─ pattern #\d+\s+\S+ @ lines (\d+)–(\d+)")


def load(run: str, arms: Sequence[str]) -> List[Dict[str, Any]]:
    root = campaign.find_run(run)
    if root is None:
        raise SystemExit(f"run {run} is not in the archive")
    out: List[Dict[str, Any]] = []
    for p in sorted(root.glob("benchmarks/*/*/*/*/rep*/trial.json")):
        t = json.loads(p.read_text())
        if t.get("arm") not in arms:
            continue
        t["run_id"] = run
        t["_dir"] = str(p.parent)
        out.append(t)
    return out


def race_of(t: Dict[str, Any], races: Dict[Tuple[str, str, str, int], str]) -> str:
    """A program the gate kept is clean unless race_check.py says otherwise (main_comparison_stats.three_way)."""
    v = races.get((str(t["run_id"]), str(t.get("benchmark")), str(t.get("arm")), int(t.get("repeat") or 0)), "clean")
    return "clean" if v in ("clean", "unchanged") else v


def classify(t: Dict[str, Any], races: Dict[Tuple[str, str, str, int], str]) -> Dict[str, Any]:
    valid = mcs._with_verdict(t)
    race = race_of(t, races)
    out = t.get("outcome")
    why: List[str] = []
    if valid:
        if out == "BROKEN":
            why.append("BROKEN")
        if mcs._did_not_compile(t):
            why.append("did not compile")
        if mcs._ships_slowdown(t):
            why.append("slower than the original")
        if mcs._measurement_kept_edited(t):
            why.append("edits the measurement after every redo")
        if out in figures.PARALLEL_OK and race in mcs.RACE_STAGES:
            why.append("racy")
    return {"valid": valid, "faster": valid and out == "FASTER",
            "faster_race_free": valid and out == "FASTER" and race == "clean",
            "unusable": bool(why), "why": why, "race": race}


def chain(t: Dict[str, Any]) -> Dict[str, Any]:
    """What the log says a trial did at each level, and what Settle did with it."""
    log_p = Path(t["_dir"]) / "agent.log"
    log = log_p.read_text(errors="replace") if log_p.exists() else ""
    head, _, settle = log.partition("SETTLING")
    blocks: Counter = Counter()
    calls: Counter = Counter()
    kept: Counter = Counter()
    rewrites: List[Dict[str, Any]] = []
    depth: Optional[int] = None
    cur: Optional[Dict[str, Any]] = None
    for ln in head.splitlines():
        m = BLOCK.match(ln)
        if m:
            depth = int(m.group(1))
            blocks[depth] += 1
            cur = {"depth": depth, "rid": m.group(2), "finds": []}
            continue
        if depth is not None and re.match(r"│\s+\[Tier-2\] Calling ", ln):
            calls[depth] += 1
        if cur is not None and "DiscoPoP now finds:" in ln:
            cur["finds"] = [(int(a), int(b)) for a, b in FINDS.findall(ln)]
        if cur is not None and ln.startswith("└─ ACCEPTED"):
            kept[cur["depth"]] += 1
            rewrites.append(cur)
            cur = None
        elif cur is not None and ln.startswith("└─") and not ln.startswith("└─ retry"):
            cur = None
    applied: List[Tuple[int, int]] = []
    pat: Optional[Tuple[int, int]] = None
    for ln in head.splitlines():
        m = PATTERN.match(ln)
        if m:
            pat = (int(m.group(1)), int(m.group(2)))
        elif pat is not None and ln.startswith("└─"):
            if ln.startswith("└─ APPLIED"):
                applied.append(pat)
            pat = None
    notes = re.findall(r"^\s+· (.*)$", settle, re.M)
    orphans = [n for n in notes if "none kept a pragma" in n]
    signature = False                       # candidate Fix 107 (§6, 14 Oct): the LAST kept rewrite an orphan
    if rewrites and orphans:                # while Phase B applied a pragma on a span it exposed
        last = rewrites[-1]
        k = len(last["finds"])
        for n in orphans:
            m2 = re.match(r"rewrite of (\S+) — exposed (\d+) region", n)
            if (m2 and m2.group(1) == last["rid"] and (int(m2.group(2)) == k if k < 3 else int(m2.group(2)) >= 3)
                    and set(last["finds"]) & set(applied)):
                signature = True
    return {"blocks": dict(sorted(blocks.items())), "calls": dict(sorted(calls.items())),
            "kept": dict(sorted(kept.items())), "applied": len(applied),
            "fix106_keep": len(re.findall(r"^\s+\[keep\] ", settle, re.M)),
            "dropped": notes, "orphans": len(orphans),
            "rewrite_cascades": sum(1 for n in notes if n.startswith("rewrite for") and "depended on" in n),
            "repairs": len(re.findall(r"^\s+\[(?:repair|revert)\] ", settle, re.M)),
            "fix107_signature": signature}


def speedups(t: Dict[str, Any]) -> Dict[str, Optional[float]]:
    par = (t.get("verify") or {}).get("par") or {}
    return {k: (v.get("speedup") if isinstance(v, dict) else None) for k, v in sorted(par.items())}


def cost(t: Dict[str, Any]) -> float:
    return float((t.get("llm_usage") or {}).get("cost_usd") or 0.0)


def _med(xs: Sequence[float]) -> str:
    xs = [x for x in xs if x is not None]
    return f"{statistics.median(xs):.2f}" if xs else "—"


def _p(x: Optional[float]) -> str:
    return "—" if x is None else ("< 0.0001" if x < 1e-4 else f"{x:.4f}")


def cell(ts: List[Dict[str, Any]], races: Dict[Tuple[str, str, str, int], str]) -> Dict[str, Any]:
    cs = [classify(t, races) for t in ts]
    valid = [c for c in cs if c["valid"]]
    return {"trials": len(ts), "n": len(valid), "faster": sum(c["faster"] for c in valid),
            "faster_race_free": sum(c["faster_race_free"] for c in valid),
            "unusable": sum(c["unusable"] for c in valid),
            "unusable_cases": [f"{t.get('benchmark')} {t.get('arm')} rep{t.get('repeat')}: {', '.join(c['why'])}"
                               for t, c in zip(ts, cs) if c["valid"] and c["unusable"]],
            "without_verdict": [f"{t.get('benchmark')} {t.get('arm')} rep{t.get('repeat')}: {t.get('outcome')}"
                                for t, c in zip(ts, cs) if not c["valid"]],
            "outcomes": dict(Counter(str(t.get("outcome")) for t in ts)),
            "speedup_6": [speedups(t).get("6") for t in ts], "speedup_12": [speedups(t).get("12") for t in ts],
            "calls": [int(t.get("llm_calls") or 0) for t in ts], "cost": [cost(t) for t in ts],
            "full_profiles": [int(t.get("refresh_full") or 0) for t in ts],
            "agent_s": [float(t.get("agent_s") or 0.0) for t in ts]}


def h8(trials: List[Dict[str, Any]], races: Dict[Tuple[str, str, str, int], str]) -> Dict[str, Any]:
    strata: List[Table] = []
    rows: List[Dict[str, Any]] = []
    for loop in SET_LOOPS:
        c1 = cell([t for t in trials if t.get("benchmark") == loop and t.get("arm") == DEPTH1], races)
        c0 = cell([t for t in trials if t.get("benchmark") == loop and t.get("arm") == DEPTH0], races)
        strata.append((float(c1["faster_race_free"]), float(c1["n"] - c1["faster_race_free"]),
                       float(c0["faster_race_free"]), float(c0["n"] - c0["faster_race_free"])))
        rows.append({"loop": loop, "depth1": c1, "depth0": c0})
    u1 = cell([t for t in trials if t.get("arm") == DEPTH1], races)
    u0 = cell([t for t in trials if t.get("arm") == DEPTH0], races)
    return {"strata": strata, "rows": rows, "cmh": cmh(strata, alternative="greater"), "or": mh_odds_ratio(strata),
            "exact": exact_conditional(strata),
            "depth1": [sum(int(s[0]) for s in strata), sum(int(s[0] + s[1]) for s in strata)],
            "depth0": [sum(int(s[2]) for s in strata), sum(int(s[2] + s[3]) for s in strata)],
            "unusable": {"depth1": [u1["unusable"], u1["n"]], "depth0": [u0["unusable"], u0["n"]]},
            "refuted_by_unusable": u1["unusable"] > u0["unusable"]}


def verdict_h8(res: Dict[str, Any]) -> Tuple[float, str]:
    p1 = res["cmh"].get("p_one_sided")
    p1 = 1.0 if p1 is None else float(p1)
    v = ("refuted (more unusable programs at depth 1)" if res["refuted_by_unusable"]
         else "supported" if p1 < 0.05 else "not established")
    return p1, v


def to_markdown(res: Dict[str, Any], set_cells: Dict[Tuple[str, str], Dict[str, Any]],
                set_trials: List[Dict[str, Any]], loop_cells: Dict[Tuple[str, str], Dict[str, Any]],
                loop_trials: List[Dict[str, Any]], chains: Dict[str, Dict[str, Any]],
                races_given: bool) -> str:
    p1, v = verdict_h8(res)
    orr = res["or"]
    or_txt = (f"Mantel-Haenszel odds ratio {orr['or']:.3g} (95 % {orr['ci95'][0]:.3g}–{orr['ci95'][1]:.3g})"
              if orr.get("ci95") else "Mantel-Haenszel odds ratio infinite (no loop with a trial against depth 1)"
              if orr.get("or_infinite") else f"odds ratio: {orr.get('note', 'not estimable')}")
    mf = res["cmh"].get("mantel_fleiss")
    cmh_txt = (res["cmh"]["note"] if "note" in res["cmh"] else
               f"{res['cmh']['informative_strata']} informative loop(s); the normal approximation "
               + ("holds" if mf and mf["met"] else "does not hold (Mantel-Fleiss) — read the exact p"))
    un = res["unusable"]
    detail = (f"depth 1 {res['depth1'][0]} of {res['depth1'][1]}, depth 0 {res['depth0'][0]} of {res['depth0'][1]}; "
              f"{cmh_txt}; {or_txt}; exact conditional p {_p(res['exact'].get('p_greater'))}; unusable programs: "
              f"depth 1 {un['depth1'][0]} of {un['depth1'][1]}, depth 0 {un['depth0'][0]} of {un['depth0'][1]}")
    out = ["# E8 — restructuring depth: the read-out as pre-registered", "",
           "Registered in THESIS_EXPERIMENTS §6 on 14 Oct 2026 before any counted trial (\"Plan, E8 pre-registration\"; "
           "the agent with Fix 106, \"Agent, Fix 106\" and \"Plan, E8's second smoke\"). One test, one-sided as "
           f"registered, a member of the campaign's family: the bound is p × {FAMILY}."
           + ("" if races_given else " **No race file was given: every gate-kept program counts as clean.**"), "",
           "## The test", "",
           "| test | hypothesis | p (one-sided) | family bound | verdict | detail |", "|---|---|---:|---:|---|---|",
           f"| H8 | race-free verified FASTER more often at depth 1 than at depth 0 on the depth set (CMH stratified "
           f"by loop) | {_p(p1)} | {_p(min(1.0, p1 * FAMILY))} | {v} | {detail} |", "",
           "## The depth set, per loop and arm", "",
           "| loop | arm | race-free FASTER | FASTER | unusable | outcomes | speed-up 6 / 12 (median) | calls (median) "
           "| cost $ (sum) | full profiles (median) | agent s (median) |",
           "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|"]
    for loop in SET_LOOPS:
        for arm in ARMS:
            c = set_cells[(loop, arm)]
            out.append(f"| `{loop.split('/')[1]}` | `{arm}` | {c['faster_race_free']} of {c['n']} | {c['faster']} | "
                       f"{c['unusable']} | {', '.join(f'{k} {n}' for k, n in sorted(c['outcomes'].items()))} | "
                       f"{_med(c['speedup_6'])} / {_med(c['speedup_12'])} | {_med(c['calls'])} | {sum(c['cost']):.2f} | "
                       f"{_med(c['full_profiles'])} | {_med(c['agent_s'])} |")
    out += ["", "## Each trial of the depth set: what each level did, what Settle kept, what shipped", "",
            "Model calls and rewrites kept in Phase A per level (`{depth: n}`); Settle: changes kept by Fix 106's "
            "`[keep]`, changes dropped, repairs of the finished-program check; candidate Fix 107's signature.", "",
            "| loop | arm | rep | calls per level | rewrites kept per level | pragmas applied | Fix 106 kept | dropped "
            "| repairs | Fix 107 | outcome | speed-up 6 / 12 | race |",
            "|---|---|---:|---|---|---:|---:|---:|---:|---|---|---|---|"]
    for t in sorted(set_trials, key=lambda x: (str(x.get("benchmark")), ARMS.index(str(x.get("arm"))), int(x.get("repeat") or 0))):
        ch = chains[t["_dir"]]
        sp = speedups(t)
        out.append(f"| `{str(t.get('benchmark')).split('/')[1]}` | `{t.get('arm')}` | {t.get('repeat')} | {ch['calls']} | "
                   f"{ch['kept']} | {ch['applied']} | {ch['fix106_keep']} | {len(ch['dropped'])} | {ch['repairs']} | "
                   f"{'yes' if ch['fix107_signature'] else 'no'} | {t.get('outcome')} | "
                   f"{sp.get('6') or '—'} / {sp.get('12') or '—'} | {t.get('_race', 'clean')} |")
    out += ["", "## The speed question at depth 0 (the depth set): the judge's verdicts per trial", ""]
    for t in sorted([x for x in set_trials if x.get("arm") == DEPTH0], key=lambda x: (str(x.get("benchmark")), int(x.get("repeat") or 0))):
        out.append(f"- `{str(t.get('benchmark')).split('/')[1]}` rep {t.get('repeat')}: {t.get('d40_verdicts')}; "
                   f"exposure {t.get('exposure_verdicts')}; outcome {t.get('outcome')}")
    out += ["", "## Depth 2 against depth 1 on the depth set (\"a third adds little\") — no test", "",
            "| loop | depth 1 race-free FASTER | depth 2 race-free FASTER | depth 1 unusable | depth 2 unusable |",
            "|---|---:|---:|---:|---:|"]
    for loop in SET_LOOPS:
        c1, c2 = set_cells[(loop, DEPTH1)], set_cells[(loop, DEPTH2)]
        out.append(f"| `{loop.split('/')[1]}` | {c1['faster_race_free']} of {c1['n']} | {c2['faster_race_free']} of {c2['n']} | "
                   f"{c1['unusable']} | {c2['unusable']} |")
    out += ["", "## The 18 loops — depth 1 and 2 beside E3's depth 0 (no test)", "",
            "| loop | depth 0 (E3) race-free FASTER | depth 1 | depth 2 | unusable 0 / 1 / 2 |", "|---|---:|---:|---:|---|"]
    loops = sorted({str(t.get("benchmark")) for t in loop_trials if t.get("arm") != DEPTH0},
                   key=lambda b: b.split("/")[1])
    for bench in loops:
        row = [loop_cells.get((bench, arm)) for arm in ARMS]
        out.append(f"| `{bench}` | " + " | ".join(f"{x['faster_race_free']} of {x['n']}" if x else "—" for x in row)
                   + " | " + " / ".join(str(x["unusable"]) if x else "—" for x in row) + " |")
    out += ["", "| arm | trials | race-free FASTER | unusable | calls (median) | cost $ (sum) | full profiles (median) | "
            "agent s (median) |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for arm in ARMS:
        c = cell([t for t in loop_trials if t.get("arm") == arm and str(t.get("benchmark")) in loops], {})
        cs = [loop_cells[(bench, arm)] for bench in loops if (bench, arm) in loop_cells]
        out.append(f"| `{arm}`{' (E3)' if arm == DEPTH0 else ''} | {c['trials']} | {sum(x['faster_race_free'] for x in cs)} of "
                   f"{sum(x['n'] for x in cs)} | {sum(x['unusable'] for x in cs)} | {_med(c['calls'])} | {sum(c['cost']):.2f} | "
                   f"{_med(c['full_profiles'])} | {_med(c['agent_s'])} |")
    allc = list(set_cells.values()) + list(loop_cells.values())
    unusable = [u for c in allc for u in c["unusable_cases"]]
    missing = [u for c in allc for u in c["without_verdict"]]
    e8_chains = [chains[t["_dir"]] for t in set_trials + [x for x in loop_trials if x.get("arm") != DEPTH0]]
    out += ["", "## Every unusable program", ""] + ([f"- {u}" for u in unusable] or ["- none"])
    out += ["", "## Trials without a verdict (left out of every rate)", ""] + ([f"- {u}" for u in missing] or ["- none"])
    out += ["", "## Fix 106 and candidate Fix 107 in E8's trials", "",
            f"- trials in which Fix 106 kept a rewrite (`[keep]`): {sum(1 for c in e8_chains if c['fix106_keep'])} of "
            f"{len(e8_chains)} ({sum(c['fix106_keep'] for c in e8_chains)} rewrites)",
            f"- trials with candidate Fix 107's signature: {sum(1 for c in e8_chains if c['fix107_signature'])} of {len(e8_chains)}",
            f"- trials in which Settle's orphan rule still dropped a rewrite: "
            f"{sum(1 for c in e8_chains if c['orphans'])}; a rewrite that no longer applied: "
            f"{sum(1 for c in e8_chains if c['rewrite_cascades'])}", "",
            "## Read by hand (registered)", "",
            "The form the shipped program reached on the depth set — the original, step 1 or step 2 — is read program "
            "by program against the references (`e8_c5_refs`, `e8_c5_steps`): the changed programs are the trials "
            "above whose outcome is not `no-change`, each in its trial folder under `final/`."]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--races", type=Path, action="append", default=[], help="race_check.py results of E8's runs")
    ap.add_argument("--set-run", default=SET_RUN, help="the depth set's run (a smoke for a dry run of this script)")
    ap.add_argument("--loop-runs", default=",".join(LOOP_RUNS), help="the 18 loops' runs, comma-separated ('' for none)")
    a = ap.parse_args()
    races = mcs.load_races(a.races)
    e3_races = mcs.load_races([campaign.RESULTS / p for p in E3_RACES])
    set_trials = load(a.set_run, ARMS)
    loop_trials: List[Dict[str, Any]] = []
    for r in [x for x in a.loop_runs.split(",") if x]:
        loop_trials += load(r, (DEPTH1, DEPTH2))
    wanted = {str(t.get("benchmark")).split("/")[1] for t in loop_trials}
    e3 = [t for r in E3_RUNS for t in load(r, (DEPTH0,))
          if (r, str(t.get("benchmark"))) not in E3_REPLACED and str(t.get("benchmark")).split("/")[1] in wanted]
    for t in set_trials + loop_trials:
        t["_race"] = race_of(t, races)
    chains = {t["_dir"]: chain(t) for t in set_trials + loop_trials}
    set_cells = {(loop, arm): cell([t for t in set_trials if t.get("benchmark") == loop and t.get("arm") == arm], races)
                 for loop in SET_LOOPS for arm in ARMS}
    # E3's depth-0 cell of a loop is counted in the row of the package E8 ran it on (one kernel file per loop)
    by_name = {str(t.get("benchmark")).split("/")[1]: str(t.get("benchmark")) for t in loop_trials}
    loop_cells: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for name, b in by_name.items():
        for arm in (DEPTH1, DEPTH2):
            loop_cells[(b, arm)] = cell([t for t in loop_trials if t.get("benchmark") == b and t.get("arm") == arm], races)
        loop_cells[(b, DEPTH0)] = cell([t for t in e3 if str(t.get("benchmark")).split("/")[1] == name], e3_races)
    res = h8(set_trials, races)
    a.out.mkdir(parents=True, exist_ok=True)
    md = to_markdown(res, set_cells, set_trials, loop_cells, loop_trials + e3, chains, bool(a.races))
    (a.out / "e8_readout.md").write_text(md)
    p1, v = verdict_h8(res)
    (a.out / "e8_readout.json").write_text(json.dumps(
        {"h8": {k: res[k] for k in ("cmh", "or", "exact", "depth1", "depth0", "unusable", "refuted_by_unusable")},
         "h8_p_one_sided": p1, "h8_bound": min(1.0, p1 * FAMILY), "h8_verdict": v,
         "set_cells": {f"{k[0]}|{k[1]}": c for k, c in set_cells.items()},
         "loop_cells": {f"{k[0]}|{k[1]}": c for k, c in loop_cells.items()},
         "chains": {str(Path(d).relative_to(campaign.RESULTS)): c for d, c in chains.items()}}, indent=1, default=str))
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
