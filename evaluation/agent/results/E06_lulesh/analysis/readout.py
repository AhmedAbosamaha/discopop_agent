"""E6's registered read-out, built from the archive only (no model, no profiling).

The pre-registration (record §6, 3 Nov, "E6 pre-registered") fixes what is read out: per setup the harness
outcomes and, after `race_check.py`, how many are racy; the speedups at 6 and 12 threads against the
sequential program and against LLNL's OpenMP version; the agent against DiscoPoP alone trial by trial;
calls, cost and time; and by hand what each agent trial kept. No test: one program, five trials per setup.
The second configuration (record §6, 3 Nov, "E6, second configuration") is read out the same way.

    python3 evaluation/agent/results/E06_lulesh/analysis/readout.py > evaluation/agent/results/E06_lulesh/analysis/readout.md
    python3 evaluation/agent/results/E06_lulesh/analysis/readout.py --json evaluation/agent/results/E06_lulesh/analysis/readout.json

The JSON holds the same per-trial facts for the thesis's figure and table (thesis/tools/make_figures.py, make_tables.py).
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

E6 = Path(__file__).resolve().parents[1]
BENCH = "benchmarks/llnl_c1/lulesh"
HAIKU = "claude-haiku-4-5-20251001"
CONFIG1 = ["e6c_r1", "e6c_r2", "e6c_r3b"]          # the first configuration's main runs
CONFIG2 = ["e6x_1", "e6x_2", "e6x_3"]              # the second configuration (byte-exact contract)
MODELS = ["claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5", HAIKU]
FORCE_FUNCTIONS = ("IntegrateStressForElems", "CalcFBHourglassForceForElems")
REFERENCE = E6 / "preflight/e6c_ref_check" / BENCH / "expert_openmp/none/rep1/trial.json"


def trials(run: str, arm: str, model: str = HAIKU) -> List[Path]:
    root = E6 / "runs" / run / BENCH / arm / model
    return sorted(root.glob("rep*"), key=lambda p: int(p.name[3:]))


def races() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for f in (E6 / "checks/e6c_race_check").glob("*/results.jsonl"):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out[r["trial"].split("E06_lulesh/", 1)[1]] = r
    return out


RACES = races()


def rel(d: Path) -> str:
    return str(d.relative_to(E6))


def speed(t: Dict[str, Any], n: str) -> Optional[float]:
    par = (t.get("verify") or {}).get("par") or {}
    s = (par.get(n) or {}).get("speedup")
    return float(s) if isinstance(s, (int, float)) else None


def cost(t: Dict[str, Any]) -> float:
    u = t.get("llm_usage") or {}
    return float(u.get("cost_usd") or 0.0) if isinstance(u, dict) else 0.0


def floor_ratio(d: Path) -> str:
    log = d / "agent.log"
    if not log.exists():
        return ""
    m = re.search(r"\[floor\] (kept the agent's program|shipped DiscoPoP's own program \(D32\)) — "
                  r"(?:the agent's was )?([\d.]+)× DiscoPoP's own", log.read_text(errors="replace"))
    if not m:
        return ""
    return f"{m.group(2)}× ({'agent kept' if m.group(1).startswith('kept') else 'DiscoPoP shipped'})"


def function_span(text: str, name: str) -> str:
    """The body of the function `name` in `text` (its signature line to the matching brace)."""
    m = re.search(r"^[^\n;]*\b" + name + r"\s*\(", text, re.M)
    if not m:
        return ""
    i = text.find("{", m.end())
    depth, j = 0, i
    while j < len(text):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[m.start(): j + 1]
        j += 1
    return text[m.start():]


def force_loops(d: Path) -> str:
    final = d / "final" / "lulesh.cc"
    if not final.exists():
        return ""
    text = final.read_text(errors="replace")
    kinds = []
    for name in FORCE_FUNCTIONS:
        body = function_span(text, name)
        if "#pragma omp parallel" not in body:
            kinds.append("sequential")
        elif "omp atomic" in body:
            kinds.append("atomic")
        elif "omp critical" in body:
            kinds.append("critical")
        else:
            kinds.append("parallel, no atomic")
    return " / ".join(kinds)


def directives(d: Path) -> Tuple[int, int, int]:
    final = d / "final" / "lulesh.cc"
    text = final.read_text(errors="replace") if final.exists() else ""
    return text.count("#pragma omp"), text.count("omp atomic"), text.count("omp critical")


def who_wrote(d: Path) -> str:
    log = d / "agent.log"
    m = re.search(r"SUMMARY: (\d+) rewrite\(s\) kept\s+\|\s+(\d+) pragma\(s\) applied(?: \((\d+) DiscoPoP \+ (\d+) LLM\))?",
                  log.read_text(errors="replace")) if log.exists() else None
    if not m:
        return ""
    return f"{m.group(1)} kept; {m.group(2)} applied" + (f" ({m.group(3)} DiscoPoP + {m.group(4)} model)" if m.group(3) else "")


def race_verdict(d: Path) -> str:
    r = RACES.get(rel(d))
    return r["verdict"] if r else "not checked"


def fmt(x: Optional[float], nd: int = 2) -> str:
    return "—" if x is None else f"{x:.{nd}f}"


def rng(values: List[Optional[float]]) -> str:
    xs = [x for x in values if x is not None]
    if not xs:
        return "—"
    return f"{statistics.median(xs):.2f} ({min(xs):.2f}–{max(xs):.2f})"


def setup_row(label: str, dirs: List[Path]) -> str:
    ts = [json.loads((d / "trial.json").read_text()) for d in dirs]
    outs = [t["outcome"] for t in ts]
    # a FASTER program the race check refused at a race stage (TSan or the schedule matrix), not at a build
    racy = sum(1 for d, t in zip(dirs, ts) if t["outcome"] == "FASTER"
               and race_verdict(d) not in ("clean", "not checked", "compile", "openmp_compile"))
    faster_clean = sum(1 for d, t in zip(dirs, ts) if t["outcome"] == "FASTER" and race_verdict(d) == "clean")
    usable = [(speed(t, "6"), speed(t, "12")) for d, t in zip(dirs, ts) if t["outcome"] == "FASTER" and race_verdict(d) == "clean"]
    return (f"| {label} | {len(ts)} | {outs.count('FASTER')} | {outs.count('parallel-not-faster')} | {outs.count('no-change')} | "
            f"{outs.count('BROKEN')} | {outs.count('VERIFY_FAILED')} | {sum(1 for o in outs if o.startswith('AGENT_'))} | {racy} | "
            f"**{faster_clean}** | {rng([u[0] for u in usable])} | {rng([u[1] for u in usable])} | "
            f"{sum(int(t.get('llm_calls') or 0) for t in ts)} | ${sum(cost(t) for t in ts):.2f} | "
            f"{statistics.median([float(t.get('agent_s') or 0) for t in ts]) / 3600:.1f} h |")


def main() -> None:
    ref = json.loads(REFERENCE.read_text())
    r6, r12 = speed(ref, "6"), speed(ref, "12")
    dp = [d for run in CONFIG1 + CONFIG2 for d in trials(run, "discopop_gate_v5")]
    a1 = [d for run in CONFIG1 for d in trials(run, "llm_pragmas_v5")]
    a2 = [d for run in CONFIG2 for d in trials(run, "llm_pragmas_v5_exact")]
    bare = {m: trials("e6c_bare", "bare_llm_v4", m) for m in MODELS}

    print("# E6 read-out — LULESH 2.0 (`llnl_c1/lulesh`)\n")
    print("*Generated by `readout.py` from the archived trial records and the race check; regenerate, do not edit.*\n")
    print(f"LLNL's OpenMP version (`e6c_ref_check`, the expert reference): {fmt(r6)}× at 6 threads, {fmt(r12)}× at 12 "
          f"(values within {ref['verify'].get('dump_max_rel_err'):.1e}, stable).\n")
    print("## 1. Outcomes per setup\n")
    print("FASTER here is the harness verdict; *racy* counts FASTER programs in which `race_check.py` found a data race; "
          "*usable* = FASTER and race-free. Speedups: median (range) over the usable programs, against the sequential "
          "program at LARGE. Time: median agent phase per trial.\n")
    print("| setup | trials | FASTER | par-not-faster | no-change | BROKEN | does not compile | agent error | racy | usable | "
          "speedup 6 thr | speedup 12 thr | calls | cost | time |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|")
    print(setup_row("DiscoPoP alone (both configurations' runs)", dp))
    print(setup_row("agent, first configuration (`llm_pragmas_v5`)", a1))
    print(setup_row("agent, second configuration (`llm_pragmas_v5_exact`)", a2))
    for m in MODELS:
        print(setup_row(f"model alone — {m.replace('claude-', '')}", bare[m]))
    print()
    print("## 2. The agent against DiscoPoP alone, trial by trial\n")
    print("Each agent trial beside the DiscoPoP-alone trial of the same run and repetition (same profile). *Paired* is the "
          "floor's in-trial measurement (D32): the agent's program and DiscoPoP's own timed in turn.\n")
    print("| configuration | trial | agent outcome | race check | agent 6 / 12 thr | DiscoPoP alone 6 / 12 thr | "
          "agent ÷ DiscoPoP (6 / 12) | paired (floor) | ÷ LLNL (6 / 12) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for label, runs, arm in (("first", CONFIG1, "llm_pragmas_v5"), ("second", CONFIG2, "llm_pragmas_v5_exact")):
        for run in runs:
            for d in trials(run, arm):
                t = json.loads((d / "trial.json").read_text())
                dd = E6 / "runs" / run / BENCH / "discopop_gate_v5" / HAIKU / d.name
                tdp = json.loads((dd / "trial.json").read_text())
                a6, a12, d6, d12 = speed(t, "6"), speed(t, "12"), speed(tdp, "6"), speed(tdp, "12")
                q = lambda a, b: fmt(a / b) if a and b else "—"   # noqa: E731
                print(f"| {label} | `{run}` {d.name} | {t['outcome']} | {race_verdict(d)} | {fmt(a6)} / {fmt(a12)} | "
                      f"{fmt(d6)} / {fmt(d12)} | {q(a6, d6)} / {q(a12, d12)} | {floor_ratio(d)} | {q(a6, r6)} / {q(a12, r12)} |")
    print()
    print("## 3. What each agent trial kept (by hand, from its log and its program)\n")
    print("*Force loops*: the two node-force accumulations (`IntegrateStressForElems` / `CalcFBHourglassForceForElems`) in "
          "the shipped program — sequential, parallel with `atomic` or with a `critical` section, or parallel without either. "
          "*Repeatable*: the harness's digest identical over 5 runs at each fixed thread count; *values*: the largest "
          "relative difference from the original on the shipped input.\n")
    print("| configuration | trial | rewrites; directives (who) | directives in file (atomic, critical) | force loops | "
          "repeatable | values | calls | cost | time | explorer stalls |")
    print("|---|---|---|---|---|---|---|---:|---:|---:|---:|")
    for label, runs, arm in (("first", CONFIG1, "llm_pragmas_v5"), ("second", CONFIG2, "llm_pragmas_v5_exact")):
        for run in runs:
            for d in trials(run, arm):
                t = json.loads((d / "trial.json").read_text())
                v = t.get("verify") or {}
                n, at, cr = directives(d)
                print(f"| {label} | `{run}` {d.name} | {who_wrote(d)} | {n} ({at}, {cr}) | {force_loops(d)} | "
                      f"{'yes' if v.get('stable_at_fixed_threads') else 'no'} | {v.get('dump_max_rel_err'):.1e} | "
                      f"{t.get('llm_calls')} | ${cost(t):.2f} | {float(t.get('agent_s') or 0) / 3600:.1f} h | "
                      f"{t.get('explorer_stalls')} |")
    print()
    print("## 4. The models alone, trial by trial\n")
    print("| model | trial | outcome | race check | 6 / 12 thr | values | repeatable | force loops | cost | time |")
    print("|---|---|---|---|---|---|---|---|---:|---:|")
    for m in MODELS:
        for d in bare[m]:
            t = json.loads((d / "trial.json").read_text())
            v = t.get("verify") or {}
            err = v.get("dump_max_rel_err")
            print(f"| {m.replace('claude-', '')} | {d.name} | {t['outcome']} | {race_verdict(d)} | "
                  f"{fmt(speed(t, '6'))} / {fmt(speed(t, '12'))} | {'—' if err is None else f'{err:.1e}'} | "
                  f"{'yes' if v.get('stable_at_fixed_threads') else ('—' if err is None else 'no')} | {force_loops(d)} | "
                  f"${cost(t):.2f} | {float(t.get('agent_s') or 0) / 60:.0f} min |")


def trial_record(setup: str, d: Path) -> Dict[str, Any]:
    t = json.loads((d / "trial.json").read_text())
    s6, s12 = speed(t, "6"), speed(t, "12")
    verdict = race_verdict(d)
    out = t["outcome"]
    if out == "FASTER" and verdict == "clean":
        kind = "faster"
    elif out == "FASTER":
        kind = "racy"
    elif out == "BROKEN":
        kind = "not repeatable" if (t.get("verify") or {}).get("dump_max_rel_err", 1.0) <= 1e-9 else "wrong values"
    elif out == "VERIFY_FAILED":
        kind = "does not compile"
    else:
        kind = out
    n, at, cr = directives(d)
    return {"setup": setup, "trial": rel(d), "model": d.parent.name, "rep": int(d.name[3:]), "outcome": out,
            "race_check": verdict, "kind": kind, "speedup_6": s6, "speedup_12": s12,
            "best": max([x for x in (s6, s12) if x is not None], default=None),
            "force_loops": force_loops(d), "directives": n, "atomic": at, "critical": cr,
            "calls": t.get("llm_calls"), "cost_usd": round(cost(t), 4), "hours": round(float(t.get("agent_s") or 0) / 3600, 2),
            "floor": floor_ratio(d)}


def write_json(path: Path) -> None:
    ref = json.loads(REFERENCE.read_text())
    rows = [trial_record("DiscoPoP alone", d) for run in CONFIG1 + CONFIG2 for d in trials(run, "discopop_gate_v5")]
    rows += [trial_record("agent, first configuration", d) for run in CONFIG1 for d in trials(run, "llm_pragmas_v5")]
    rows += [trial_record("agent, second configuration", d) for run in CONFIG2 for d in trials(run, "llm_pragmas_v5_exact")]
    for m in MODELS:
        rows += [trial_record("model alone", d) for d in trials("e6c_bare", "bare_llm_v4", m)]
    path.write_text(json.dumps({"reference": {"speedup_6": speed(ref, "6"), "speedup_12": speed(ref, "12"),
                                              "dump_max_rel_err": ref["verify"].get("dump_max_rel_err")},
                                "trials": rows}, indent=1) + "\n")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--json":
        write_json(Path(sys.argv[2]))
    else:
        main()
