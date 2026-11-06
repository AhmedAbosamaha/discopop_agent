#!/usr/bin/env python3
"""E11 part 1's registered read-out, built from the archive only (no model, no profiling).

The pre-registration (record §6, 6 Nov, "E11 — the smoke, the main runs and the read-out") fixes what is read out,
descriptively (one program per comparison system, five trials per setup), per NAS program (EP, CG):
  (1) usable = the harness's FASTER, clean in the race check, NPB's verification SUCCESSFUL at the second class —
      per setup out of 5, and for each judged program; NPB's OpenMP EP by its NPB verdicts and its measured time
      (the output comparison does not apply to it: it prints NPB's full report);
  (2) the speedup of the timed region over the sequential input at 6 and 12 threads: the agent's median, range and
      best over usable trials, DiscoPoP alone's and Sonnet alone's medians, the judged programs' single values;
  (3) the headline: whether the agent reached a usable program as often as RepoOMP did (one published program), and
      its median and best speedup beside RepoOMP's — RepoOMP's one program may be its best of several;
  (4) calls and cost per trial (the agent, Sonnet alone); BROKEN split by cause — not repeatable at a fixed thread
      count (values within 1e-9 of the sequential program's), values outside 1e-9, does not build;
  (5) the directives in each usable program and the loop each one is on.
RepoOMP's published programs are `repoomp_published` in the text (label `repoomp_claude` in the archive), apart from
part 2's runs of its release (`repoomp_release`).

    python3 evaluation/agent/results/E11_repoomp/analysis/readout.py > evaluation/agent/results/E11_repoomp/analysis/readout.md
    python3 evaluation/agent/results/E11_repoomp/analysis/readout.py --json evaluation/agent/results/E11_repoomp/analysis/readout.json
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

E11 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E11.parents[1] / "tools"))
import campaign  # noqa: E402

SONNET = "claude-sonnet-4-5-20250929"
PROGRAMS = {"npbc_c1/ep": ("EP", "e11_r_ep", "ep.c"), "npbc_c1/cg": ("CG", "e11_r_cg", "cg.c")}
BARE, REF = "e11_bare", "e11_ref_check"
SETUPS = [("discopop_gate_v5", "DiscoPoP alone"), ("llm_pragmas_v5", "the agent"), ("bare_llm_v4", "Sonnet 4.5 alone")]
JUDGED = [("repoomp_claude", "RepoOMP's published Claude program (repoomp_published)"),
          ("claude_code", "RepoOMP's Claude Code program"), ("expert_openmp", "NPB's OpenMP version")]
PRAGMA = re.compile(r"^\s*#\s*pragma\s+omp\b.*$")


def _results(run_id: str, sub: str = "") -> Dict[str, Dict[str, Any]]:
    """Every results.jsonl under an archived check run (or one sub-folder of it), keyed on the trial's path under
    results/."""
    root = campaign.find_run(run_id)
    out: Dict[str, Dict[str, Any]] = {}
    if root is None:
        return out
    for f in sorted((root / sub).rglob("results.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out[str(r["trial"])] = r
    return out


RACES = _results("e11_race_check")
# the judged programs' verdicts at the second class are e11_ref_npb_verdicts/second_class (judged_class holds the
# same trials at the harness's class, so the two files are not merged)
SECOND = {**_results("e11_second_class"), **_results("e11_ref_npb_verdicts", "second_class")}


def trials(run: str, bench: str, arm: str, model: str) -> List[Path]:
    root = campaign.find_run(run)
    if root is None:
        return []
    return sorted((root / "benchmarks" / bench / arm / model).glob("rep*"), key=lambda p: int(p.name[3:]))


def key(d: Path) -> str:
    return str(d.relative_to(campaign.RESULTS))


def speed(t: Dict[str, Any], n: str) -> Optional[float]:
    s = (((t.get("verify") or {}).get("par") or {}).get(n) or {}).get("speedup")
    return float(s) if isinstance(s, (int, float)) else None


def cost(t: Dict[str, Any]) -> float:
    u = t.get("llm_usage") or {}
    return float(u.get("cost_usd") or 0.0) if isinstance(u, dict) else 0.0


def broken_cause(t: Dict[str, Any]) -> str:
    """The pre-registered split (E6's): a BROKEN program whose values are within 1e-9 failed on repeatability."""
    if t.get("outcome") == "VERIFY_FAILED" or str((t.get("verify") or {}).get("status", "")).startswith("verify_build"):
        return "does not build"
    if t.get("outcome") != "BROKEN":
        return ""
    err = (t.get("verify") or {}).get("dump_max_rel_err")
    return "not repeatable" if isinstance(err, (int, float)) and err <= 1e-9 else "values outside 1e-9"


def tsan_state(rc: Dict[str, Any]) -> str:
    """Whether ThreadSanitizer ran on the program and what it found. The race check's verdict names the FIRST stage
    that failed (apply, compile, openmp_compile/tsan, dependences, schedules, correctness), so a later stage's
    failure means TSan ran and found nothing, unless it was skipped."""
    v = rc.get("verdict")
    if not rc or v in (None, "not-checked", "unchanged", "apply", "compile", "openmp_compile"):
        return "not run"
    if v == "tsan":
        return "race"
    return "not run" if "tsan" in (rc.get("skipped_stages") or []) else "clean"


def race_location(rc: Dict[str, Any], d: Path, editable: str) -> str:
    """For a TSan verdict: the variable ThreadSanitizer names, the lines of the editable file in its report, and every
    line of the final file the name stands on (whether the program ever reads it is then a matter of those lines)."""
    if rc.get("verdict") != "tsan":
        return ""
    diag = str(rc.get("diagnostic") or "")
    m = re.search(r"Location is global '([^']+)'", diag)
    name = m.group(1).split(".")[-1] if m else ""
    lines = sorted(set(re.findall(re.escape(editable) + r":(\d+):\d+", diag)), key=int)
    f = d / "final" / editable
    uses = ([i + 1 for i, x in enumerate(f.read_text(errors="replace").splitlines())
             if re.search(r"\b" + re.escape(name) + r"\b", x)] if name and f.exists() else [])
    return (f"`{name or '?'}` — {editable} line(s) {', '.join(lines) or '?'} in the report; the name stands on line(s) "
            f"{', '.join(map(str, uses)) or '—'} of the final {editable}")


def directives(d: Path, editable: str) -> List[str]:
    """Each directive of the final file with the line it stands on and the loop header after it."""
    f = d / "final" / editable
    if not f.exists():
        return []
    lines = f.read_text(errors="replace").splitlines()
    out = []
    for i, line in enumerate(lines):
        if PRAGMA.match(line):
            nxt = next((x.strip() for x in lines[i + 1:i + 4] if x.strip() and not PRAGMA.match(x)), "")
            out.append(f"{i + 1}: {line.strip()}  →  {nxt[:90]}")
    return out


def record(setup: str, label: str, d: Path, editable: str) -> Dict[str, Any]:
    t = json.loads((d / "trial.json").read_text())
    rc = RACES.get(key(d)) or {}
    race = rc.get("verdict", "not checked")
    second = (SECOND.get(key(d)) or {}).get("verdict", "not checked")
    usable = t.get("outcome") == "FASTER" and race == "clean" and second == "SUCCESSFUL"
    s6, s12 = speed(t, "6"), speed(t, "12")
    return {"setup": setup, "label": label, "trial": key(d), "rep": int(d.name[3:]), "outcome": t.get("outcome"),
            "race_check": race, "tsan": tsan_state(rc), "race_location": race_location(rc, d, editable),
            "second_class": second, "usable": usable, "broken_cause": broken_cause(t),
            "speedup_6": s6, "speedup_12": s12, "best": max([x for x in (s6, s12) if x is not None], default=None),
            "calls": int(t.get("llm_calls") or 0), "call_failures": int(t.get("llm_call_failures") or 0),
            "cost_usd": round(cost(t), 4), "agent_s": t.get("agent_s"),
            "pragmas_discopop": t.get("pragmas_discopop"), "pragmas_llm": t.get("pragmas_llm"),
            "directives": directives(d, editable)}


def collect() -> Dict[str, List[Dict[str, Any]]]:
    rows: Dict[str, List[Dict[str, Any]]] = {}
    for bench, (_name, run, editable) in PROGRAMS.items():
        rs: List[Dict[str, Any]] = []
        for arm, label in SETUPS:
            src = BARE if arm == "bare_llm_v4" else run
            rs += [record(arm, label, d, editable) for d in trials(src, bench, arm, SONNET)]
        for arm, label in JUDGED:
            rs += [record(arm, label, d, editable) for d in trials(REF, bench, arm, "none")]
        rows[bench] = rs
    return rows


def _f(x: Optional[float]) -> str:
    return "—" if x is None else f"{x:.2f}"


def _med(xs: List[Optional[float]]) -> str:
    v = [x for x in xs if x is not None]
    return "—" if not v else (f"{statistics.median(v):.2f}" + (f" ({min(v):.2f}–{max(v):.2f})" if len(v) > 1 else ""))


def markdown(rows: Dict[str, List[Dict[str, Any]]]) -> str:
    L = ["# E11 part 1 — NPB EP and CG: the registered read-out", "",
         "Descriptive (one program per comparison system, five trials per setup). Usable = the harness's FASTER, clean "
         "in the race check, NPB's verification SUCCESSFUL at the second class (EP class B, CG class A).", ""]
    for bench, rs in rows.items():
        name = PROGRAMS[bench][0]
        L += [f"## {name}", "", "### (1)–(2) Usable programs and speedups", "",
              "| setup | trials | FASTER | race-clean | NPB second class OK | **usable** | speedup 6 thr, usable: median (range) | 12 thr | best |",
              "|---|---|---|---|---|---|---|---|---|"]
        for arm, label in SETUPS + JUDGED:
            c = [r for r in rs if r["setup"] == arm]
            if not c:
                L.append(f"| {label} | 0 | | | | | | | |")
                continue
            u = [r for r in c if r["usable"]]
            show = u if arm in ("llm_pragmas_v5", "discopop_gate_v5", "bare_llm_v4") else c
            L.append(f"| {label} | {len(c)} | {sum(r['outcome'] == 'FASTER' for r in c)} | "
                     f"{sum(r['race_check'] == 'clean' for r in c)} | {sum(r['second_class'] == 'SUCCESSFUL' for r in c)} | "
                     f"**{len(u)}** | {_med([r['speedup_6'] for r in show])} | {_med([r['speedup_12'] for r in show])} | "
                     f"{_f(max([r['best'] for r in show if r['best'] is not None], default=None))} |")
        exp = [r for r in rs if r["setup"] == "expert_openmp"]
        if name == "EP" and exp:
            e = exp[0]
            L += ["", f"NPB's OpenMP EP: harness outcome {e['outcome']} ({e['broken_cause'] or '—'}; it prints NPB's full "
                  f"report, so the output comparison does not apply), NPB's verification at the second class "
                  f"{e['second_class']}, measured speedup {_f(e['speedup_6'])} / {_f(e['speedup_12'])} at 6 / 12 threads; "
                  f"race check: ThreadSanitizer {e['tsan']}, its verdict `{e['race_check']}` the first stage that failed "
                  f"(the race check's last stages compare the output with the package's sequential program, as the "
                  f"harness does)."]
        flagged = [r for r in rs if r["race_check"] != "clean"]
        if flagged:
            L += ["", "Race check, every program not clean (verdict = the first stage that failed; ThreadSanitizer's "
                  "own result beside it):", ""]
            L += [f"- {r['label']} rep{r['rep']}: `{r['race_check']}`, ThreadSanitizer {r['tsan']}"
                  + (f"; the race: {r['race_location']}" if r["race_location"] else "") for r in flagged]
        ag = [r for r in rs if r["setup"] == "llm_pragmas_v5"]
        ro = [r for r in rs if r["setup"] == "repoomp_claude"]
        ua = [r for r in ag if r["usable"]]
        L += ["", "### (3) The headline", ""]
        if ro:
            r0 = ro[0]
            L.append(f"The agent reached a usable program in {len(ua)} of {len(ag)} trials; RepoOMP's published program is "
                     f"{'usable' if r0['usable'] else 'NOT usable'} (one program, possibly its best of several). Speedup at "
                     f"6 / 12 threads — the agent's usable trials: median {_med([r['speedup_6'] for r in ua])} / "
                     f"{_med([r['speedup_12'] for r in ua])}, best {_f(max([r['best'] for r in ua if r['best']], default=None))}; "
                     f"RepoOMP's: {_f(r0['speedup_6'])} / {_f(r0['speedup_12'])}.")
        L += ["", "### (4) Calls, cost, BROKEN by cause", "",
              "| setup | trials | calls | failed calls | cost (USD) | per trial | BROKEN: not repeatable | values outside 1e-9 | does not build |",
              "|---|---|---|---|---|---|---|---|---|"]
        for arm, label in SETUPS:
            c = [r for r in rs if r["setup"] == arm]
            if c:
                L.append(f"| {label} | {len(c)} | {sum(r['calls'] for r in c)} | {sum(r['call_failures'] for r in c)} | "
                         f"{sum(r['cost_usd'] for r in c):.2f} | {sum(r['cost_usd'] for r in c) / len(c):.2f} | "
                         f"{sum(r['broken_cause'] == 'not repeatable' for r in c)} | "
                         f"{sum(r['broken_cause'] == 'values outside 1e-9' for r in c)} | "
                         f"{sum(r['broken_cause'] == 'does not build' for r in c)} |")
        L += ["", "### Every trial", "",
              "| setup | rep | outcome | race check | NPB 2nd class | usable | 6 / 12 thr | BROKEN cause | calls | cost |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in rs:
            L.append(f"| {r['label']} | {r['rep']} | {r['outcome']} | {r['race_check']} | {r['second_class']} | "
                     f"{'yes' if r['usable'] else 'no'} | {_f(r['speedup_6'])} / {_f(r['speedup_12'])} | "
                     f"{r['broken_cause'] or '—'} | {r['calls']} | {r['cost_usd']:.2f} |")
        L += ["", "### (5) The directives of each usable program", ""]
        for r in rs:
            if r["usable"]:
                who = (f" (DiscoPoP {r['pragmas_discopop']}, model {r['pragmas_llm']})"
                       if r["pragmas_discopop"] is not None else "")
                L.append(f"- {r['label']} rep{r['rep']}{who}:")
                L += [f"    - `{x}`" for x in r["directives"]] or ["    - (none)"]
        L.append("")
    return "\n".join(L) + "\n"


def main() -> int:
    rows = collect()
    if len(sys.argv) > 2 and sys.argv[1] == "--json":
        Path(sys.argv[2]).write_text(json.dumps(rows, indent=1) + "\n")
        return 0
    sys.stdout.write(markdown(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
