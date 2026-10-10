#!/usr/bin/env python3
"""E2-v6's read-out beside the registered tests (THESIS_EXPERIMENTS §6, 5 Oct 2026, with its amendment of the
same day) — the hidden order on clean files, evidence × attempts.

The two registered tests are `e2b1_stats.py`'s own output (V6-i: `stats/v6_i`, V6-ii: `stats/v6_ii`). This tool
writes what the registration lists as DESCRIPTIVE, from the same trials judged the same way
(`e2b1_stats.judge`: the race check on every model-alone parallel program, the hot-loop coverage, a failed call
out of every denominator), and repeats the two tests from its own tables as a cross-check:

  * the four agent setups (evidence in the request: yes / no × attempts: one / three) per unit and pooled;
  * can the feedback stand in for the evidence (three attempts without against one attempt with), what three
    attempts add with evidence, the evidence effect at three attempts, and the interaction in H5b's form
    (extra attempts help most where the evidence is absent);
  * the control `k48` and the decline unit `k53` in all eight setups — on `k53`: how many trials ship a parallel
    program at all, how many of those are wrong, and whether the loop over the index tables stands inside a
    parallel region or outside every one (then only a loop the program added is parallel);
  * what every changed program did to the repetition loop, and where it keeps temporary data of the data's
    length (an automatic array lies on the stack);
  * every unsafe program of the agent, with what the harness recorded;
  * model calls, calls per success and the API-equivalent cost per setup.

    venv/bin/python evaluation/agent/tools/e2v6_readout.py --out evaluation/agent/results/history/E02v6_hidden_order_clean_files/analysis
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "shared"))
import campaign  # noqa: E402
import e2b1_stats as es  # noqa: E402

SUITE = "tsvc_c2"
ORDER_UNITS = ("k19", "k23", "k27", "k31", "s161")          # direction (a): the order is hidden
CONTROL, DECLINE = "k48", "k53"
FULL1, NONE1 = "full_b1_nospeed_v4", "no_evidence_b1_nospeed_v4"
FULL3, NONE3 = "full_nospeed_v4", "no_evidence_nospeed_v4"
BARE = "bare_llm_nospeed_v4"
# The experiment as it ran (E2-v6, 5–6 Oct 2026) and run again on the fixed DiscoPoP (E2-v6b, from 7 Oct: defect B14
# of the profiler). The models alone have no DiscoPoP in their path: E2-v6b reuses E2-v6's four runs and their
# race check.
EXPERIMENTS: Dict[str, str] = {"e2v6": "e2v6", "e2v6b": "e2v6b"}


def setups(stem: str) -> List[Tuple[str, Tuple[str, ...], str]]:
    """(label, runs, arm) — the order of every table."""
    one = tuple(f"{stem}_agent_{n}" for n in (1, 2, 3))
    three = tuple(f"{stem}_fb_{n}" for n in (1, 2, 3))
    return [
        ("Haiku agent, evidence, one attempt", one, FULL1),
        ("Haiku agent, no evidence, one attempt", one, NONE1),
        ("Haiku agent, evidence, three attempts", three, FULL3),
        ("Haiku agent, no evidence, three attempts", three, NONE3),
        ("Haiku alone", ("e2v6_bare_haiku",), BARE),
        ("Sonnet 5 alone", ("e2v6_bare_sonnet",), BARE),
        ("Opus 5.5 alone", ("e2v6_bare_opus",), BARE),
        ("Fable 5.1 alone", ("e2v6_bare_fable",), BARE),
    ]


SETUPS: List[Tuple[str, Tuple[str, ...], str]] = setups("e2v6")
AGENT_LABELS = [s[0] for s in SETUPS[:4]]
RACE_PARTS = ("haiku", "sonnet", "opus", "fable")            # the model-alone parts of e2v6_race_check
REFERENCES = "t0_14_c2_refs"                                 # the expert versions, verified the same way
K53_TABLES = ("ju[", "kv[", "jv[", "ku[")                      # the kernel's four index tables


def load(runs: Sequence[str], arm: str) -> List[dict]:
    """The archived trials of one arm, each with the folder it lies in (`_dir`)."""
    out: List[dict] = []
    for run in runs:
        root = campaign.find_run(run)
        if root is None:
            sys.exit(f"run {run} is not in the archive")
        for p in sorted(root.glob(f"benchmarks/{SUITE}/*/{arm}/*/rep*/trial.json")):
            t = json.loads(p.read_text())
            t.setdefault("run_id", run)
            t["_dir"] = str(p.parent)
            out.append(t)
    return out


def unit(t: dict) -> str:
    return str(t.get("benchmark", "")).split("/")[-1]


def best_speedup(t: dict) -> Optional[float]:
    """The larger of the speedups the harness measured at its thread counts (None when no timed run ended)."""
    par = (t.get("verify") or {}).get("par") or {}
    xs = [float(p["speedup"]) for p in par.values() if isinstance(p, dict) and p.get("speedup")]
    return max(xs) if xs else None


def reference_speedups() -> Dict[str, float]:
    """The expert versions through the same verification (`t0_14_c2_refs`, T0.17's pre-flight): unit -> speedup."""
    root = campaign.find_run(REFERENCES)
    out: Dict[str, float] = {}
    if root is None:
        return out
    for p in sorted(root.glob(f"benchmarks/{SUITE}/*/*/none/rep1/trial.json")):
        t = json.loads(p.read_text())
        sp = best_speedup(t)
        if sp is not None and t.get("outcome") == "FASTER":
            out[unit(t)] = sp
    return out


def _p(x: Optional[float]) -> str:
    return "—" if x is None else f"{x:.3g}"


def _or(r: Dict[str, Any]) -> str:
    if r.get("or_infinite"):
        return "infinite"
    if r.get("or") is None:
        return "not estimable"
    ci = r.get("ci95")
    return f"{r['or']:.2f}" + (f" ({ci[0]:.2f}–{ci[1]:.2f})" if ci else "")


def tables(js: Dict[str, List[Dict[str, Any]]], x: str, y: str, outcome: str = "success") -> List[Tuple[str, es.Table]]:
    """Per unit of (a): (X with the outcome, X without, Y with, Y without), over trials with a verdict."""
    out: List[Tuple[str, es.Table]] = []
    for u in ORDER_UNITS:
        cx = [j for j in js[x] if j["unit"] == u and j["with_verdict"]]
        cy = [j for j in js[y] if j["unit"] == u and j["with_verdict"]]
        a, c = sum(1 for j in cx if j[outcome]), sum(1 for j in cy if j[outcome])
        out.append((u, (float(a), float(len(cx) - a), float(c), float(len(cy) - c))))
    return out


def contrast(js: Dict[str, List[Dict[str, Any]]], x: str, y: str, alternative: Optional[str]) -> Dict[str, Any]:
    """X against Y pooled over the five units, stratified by unit. `alternative` None = two-sided only."""
    tb = tables(js, x, y)
    strata = [t for _, t in tb]
    c = es.cmh(strata, alternative or "greater")
    per: Dict[str, Any] = {}
    for u, t in tb:
        ex = es.exact_conditional([t])
        per[u] = {"x": f"{int(t[0])}/{int(t[0] + t[1])}", "y": f"{int(t[2])}/{int(t[2] + t[3])}",
                  "fisher_two_sided": ex["p_two_sided"], "fisher_x_greater": ex["p_greater"]}
    ex = c.get("exact") or {}
    return {"x": x, "y": y, "alternative": alternative, "per_unit": per,
            "x_total": f"{int(sum(t[0] for t in strata))}/{int(sum(t[0] + t[1] for t in strata))}",
            "y_total": f"{int(sum(t[2] for t in strata))}/{int(sum(t[2] + t[3] for t in strata))}",
            "mh_or": es.mh_odds_ratio(strata), "informative_strata": c.get("informative_strata"),
            "cmh_p_one_sided": c.get("p_one_sided") if alternative else None,
            "cmh_p_two_sided": c.get("p_two_sided"),
            "exact_p_one_sided": ex.get("p_one_sided") if alternative else None,
            "exact_p_two_sided": ex.get("p_two_sided")}


def _stmt_end(src: str, i: int) -> int:
    """The index just past the statement that starts at or after `i`: a block, a loop or branch with its
    body, a pragma line with the statement it governs, or everything up to the next semicolon."""
    n = len(src)
    while i < n and src[i].isspace():
        i += 1
    if i >= n:
        return n
    if src[i] == "{":
        depth = 0
        while i < n:
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        return n
    m = re.match(r"(for|while|if)\b\s*\(", src[i:])
    if m:
        k = i + m.end() - 1
        depth = 0
        while k < n:
            if src[k] == "(":
                depth += 1
            elif src[k] == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        return _stmt_end(src, k + 1)
    if src.startswith("#pragma", i):
        nl = src.find("\n", i)
        return n if nl < 0 else _stmt_end(src, nl + 1)
    semi = src.find(";", i)
    return n if semi < 0 else semi + 1


def _functions(src: str) -> Dict[str, str]:
    """name -> body of every function the file defines (for a call made from inside a parallel region)."""
    out: Dict[str, str] = {}
    for m in re.finditer(r"^[A-Za-z_][\w \t\*]*?\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{", src, flags=re.M):
        start = m.end() - 1
        out[m.group(1)] = src[start:_stmt_end(src, start)]
    return out


def parallel_regions(src: str) -> List[str]:
    """The text every `#pragma omp parallel …` governs — the statement or block that follows it, and the body
    of every function of the file that is called from there (two levels)."""
    funcs = _functions(src)
    out: List[str] = []
    for m in re.finditer(r"#pragma[ \t]+omp[ \t]+parallel[^\n]*\n", src):
        text = src[m.end():_stmt_end(src, m.end())]
        for _ in range(2):
            text += "".join(body for name, body in funcs.items()
                            if re.search(r"\b" + re.escape(name) + r"\s*\(", text) and body not in text)
        out.append(text)
    return out


def _stripped(path: Path) -> str:
    src = re.sub(r"//[^\n]*", "", path.read_text())
    return re.sub(r"/\*.*?\*/", "", src, flags=re.S)


def k53_real_loop_parallel(t: dict) -> Optional[bool]:
    """Is the loop over the kernel's index tables inside a parallel region of the shipped program (as its text
    shows)? None when the program has no parallel region."""
    f = Path(t["_dir"]) / "final" / f"{DECLINE}.c"
    if not f.exists():
        return None
    regions = parallel_regions(_stripped(f))
    if not regions:
        return None
    return any(any(k in r for k in K53_TABLES) for r in regions)


REP_LOOP = re.compile(r"\bfor\s*\(\s*(?:int\s+)?nl\b")
AUTO_ARRAY = re.compile(r"(?:^|[;{}])\s*(static\s+)?(?:const\s+)?(?:real_t|double|float)\s+(\w+)\s*\[[^\]]*LEN_1D[^\]]*\]",
                        re.M)


def program_shape(t: dict) -> Dict[str, Any]:
    """From the text of the shipped benchmark file (comments removed): is the repetition loop kept as it is (one
    loop over `nl`, no directive on it, no parallel region opened before it, one `dummy` call), and where does
    the program keep temporary data of the data's length — an automatic array (`real_t x[LEN_1D]` inside a
    function: it lies on the stack, and so does every thread's `private`/`firstprivate` copy), the heap, static
    storage, or nowhere."""
    f = Path(t["_dir"]) / "final" / f"{unit(t)}.c"
    if not f.exists():
        return {"rep": "no file", "memory": "none", "auto_arrays": [], "auto_private": False}
    src = _stripped(f)
    lines = [ln for ln in src.splitlines() if ln.strip()]
    loops = [i for i, ln in enumerate(lines) if REP_LOOP.search(ln)]
    tags: List[str] = []
    if len(loops) != 1:
        tags.append(f"{len(loops)} repetition loops")
    dummies = len(re.findall(r"\bdummy\s*\(", src))
    if dummies != 1:
        tags.append(f"{dummies} dummy calls")
    if any(i > 0 and re.match(r"\s*#\s*pragma\s+omp\s+(parallel\s+for|for)\b", lines[i - 1]) for i in loops):
        tags.append("a directive on the repetition loop")
    if loops and re.search(r"#\s*pragma\s+omp\s+parallel\b(?!\s+for)", "\n".join(lines[:loops[0]])):
        tags.append("a parallel region around the repetition loop")
    auto: List[str] = []
    file_scope = False
    for m in AUTO_ARRAY.finditer(src):
        depth = src.count("{", 0, m.start(2)) - src.count("}", 0, m.start(2))
        if depth > 0 and not m.group(1):
            auto.append(m.group(2))
        else:
            file_scope = True
    heap = bool(re.search(r"\b(malloc|calloc|aligned_alloc|posix_memalign)\s*\(", src))
    clauses = " ".join(re.findall(r"(?:first|last)?private\s*\(([^)]*)\)", src))
    memory = ("automatic array" if auto else "heap" if heap else "static" if file_scope
              or re.search(r"\bstatic\s+(?:real_t|double|float)\b", src) else "none")
    return {"rep": ", ".join(tags) or "kept", "memory": memory, "auto_arrays": auto,
            "auto_private": any(re.search(r"\b" + re.escape(n) + r"\b", clauses) for n in auto)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--experiment", choices=sorted(EXPERIMENTS), default="e2v6",
                    help="e2v6 (default) or e2v6b — the same experiment on the fixed DiscoPoP")
    a = ap.parse_args()

    global SETUPS
    SETUPS = setups(EXPERIMENTS[a.experiment])
    group = campaign.find_run("e2v6_bare_haiku")           # the models alone and their race check: E2-v6's
    if group is None:
        sys.exit("E2-v6 is not in the archive")
    checks = group.parents[1] / "checks" / "e2v6_race_check"
    race_files = [checks / p / "results.jsonl" for p in RACE_PARTS]
    missing = [str(p) for p in race_files if not p.exists()]
    if missing:
        sys.exit("the race check is not archived: " + ", ".join(missing))
    races = es.load_races(race_files)

    trials: Dict[str, List[dict]] = {}
    js: Dict[str, List[Dict[str, Any]]] = {}
    for label, runs, arm in SETUPS:
        trials[label] = load(runs, arm)
        rows = []
        for t in trials[label]:
            j = es.judge(t, races)
            j["unit"] = unit(t)
            j["calls"] = int(t.get("llm_calls") or 0)
            j["cost"] = float((t.get("llm_usage") or {}).get("cost_usd") or 0.0)
            j["agent_s"] = float(t.get("agent_s") or 0.0)
            j["omp"] = int(t.get("pragmas_in_final") or 0) > 0     # ships a parallel program at all
            j["speedup"] = best_speedup(t)
            j["status"] = str((t.get("verify") or {}).get("status") or "")
            j["failure"] = (t.get("verify") or {}).get("final_run_failure")
            j["k53_real_loop_parallel"] = k53_real_loop_parallel(t) if j["unit"] == DECLINE else None
            j.update(program_shape(t))
            rows.append(j)
        js[label] = rows
    res: Dict[str, Any] = {"race_files": [str(p.relative_to(campaign.RESULTS)) for p in race_files]}
    title = {"e2v6": "E2-v6", "e2v6b": "E2-v6b (E2-v6 on the fixed DiscoPoP; the models alone are E2-v6's)"}[a.experiment]
    md: List[str] = [f"# {title} — the read-out beside the registered tests", "",
                     "Every trial is judged as the registration says (`e2b1_stats.judge`): a **success** is a race-free "
                     "verified parallel program whose parallel construct covers the hot loop; **unsafe** is a wrong "
                     "output, a crash at the verification size, a race or a program that does not compile; the speed "
                     "check is off in every setup, so FASTER (at least 1.1×) is reported beside the successes. A model "
                     "alone has no gate: its parallel programs are race-checked afterwards (`checks/e2v6_race_check`).", ""]

    # ---- 1. the cells -------------------------------------------------------------------------------------
    def cell(label: str, u: str) -> Dict[str, Any]:
        v = [j for j in js[label] if j["unit"] == u and j["with_verdict"]]
        return {"n": len(v), "success": sum(1 for j in v if j["success"]),
                "faster": sum(1 for j in v if j["success"] and j["faster"]),
                "unsafe": sum(1 for j in v if j["unsafe"]),
                "too_slow": sum(1 for j in v if j["bucket"] == "timed-out-correct"),
                "racy": sum(1 for j in v if j["bucket"] == "racy"),
                "unchanged": sum(1 for j in v if j["bucket"] in ("no-change", "changed-not-parallel")),
                "out": sum(1 for j in js[label] if j["unit"] == u and not j["with_verdict"])}

    cells = {label: {u: cell(label, u) for u in ORDER_UNITS + (CONTROL, DECLINE)} for label, _, _ in SETUPS}
    res["cells"] = cells
    md += ["## The five units whose order is hidden — every setup", "",
           "Per unit: successes of the trials (of them FASTER) · unsafe; \"too slow\" = the output is right and a "
           "timed run did not end in 30 minutes (reported, not unsafe).", "",
           "| setup | " + " | ".join(f"`{u}`" for u in ORDER_UNITS) + " | all five | 95 % interval |",
           "|---|" + "---|" * (len(ORDER_UNITS) + 2)]
    pooled: Dict[str, Dict[str, Any]] = {}
    for label, _, _ in SETUPS:
        row = [label]
        tot = {"n": 0, "success": 0, "faster": 0, "unsafe": 0, "too_slow": 0}
        for u in ORDER_UNITS:
            c = cells[label][u]
            for k in tot:
                tot[k] += c[k]
            row.append(f"{c['success']}/{c['n']} ({c['faster']}) · {c['unsafe']} unsafe"
                       + (f" · {c['too_slow']} too slow" if c["too_slow"] else ""))
        lo, hi = es.wilson(tot["success"], tot["n"])
        pooled[label] = dict(tot, wilson95=[lo, hi])
        row.append(f"**{tot['success']}/{tot['n']}** ({tot['faster']}) · {tot['unsafe']} unsafe"
                   + (f" · {tot['too_slow']} too slow" if tot["too_slow"] else ""))
        row.append(f"{100 * lo:.0f}–{100 * hi:.0f} %")
        md.append("| " + " | ".join(row) + " |")
    res["pooled"] = pooled
    md.append("")

    # ---- 1b. how fast the successes are ------------------------------------------------------------------
    refs = reference_speedups()
    shown = ORDER_UNITS + (CONTROL,)
    md += ["## How fast the successes are — beside the expert version", "",
           "A success only has to be parallel, right and race-free: the speed check is off. Median speedup of the "
           "successes over the original (the larger of 6 and 12 threads), lowest to highest, and how many; the last "
           f"row is the expert version of the unit through the same verification (`{REFERENCES}`; `s161` has none).", "",
           "| setup | " + " | ".join(f"`{u}`" for u in shown) + " |", "|---|" + "---|" * len(shown)]
    speed: Dict[str, Dict[str, Any]] = {}
    for label, _, _ in SETUPS:
        row = [label]
        speed[label] = {}
        for u in shown:
            xs = sorted(j["speedup"] for j in js[label] if j["unit"] == u and j["success"] and j["speedup"])
            if not xs:
                row.append("—")
                continue
            med = xs[len(xs) // 2] if len(xs) % 2 else (xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) / 2
            speed[label][u] = {"median": med, "min": xs[0], "max": xs[-1], "n": len(xs)}
            row.append(f"{med:.2f}× ({xs[0]:.2f}–{xs[-1]:.2f}, {len(xs)})")
        md.append("| " + " | ".join(row) + " |")
    md.append("| **expert version** | " + " | ".join(f"{refs[u]:.2f}×" if u in refs else "—" for u in shown) + " |")
    res["speedup_of_successes"] = speed
    res["reference_speedups"] = refs
    md.append("")

    # ---- 2. the contrasts between the agent's four setups ------------------------------------------------
    A1, N1, A3, N3 = AGENT_LABELS
    con = {
        "V6-i (registered, confirmatory): evidence against none, one attempt": contrast(js, A1, N1, "greater"),
        "V6-ii (registered): without evidence, three attempts against one": contrast(js, N3, N1, "greater"),
        "descriptive 1: three attempts without evidence against one attempt with it": contrast(js, N3, A1, None),
        "descriptive 2: with evidence, three attempts against one": contrast(js, A3, A1, None),
        "descriptive: evidence against none, three attempts": contrast(js, A3, N3, None),
    }
    res["contrasts"] = con
    md += ["## The agent's four setups against each other", "",
           "Pooled over the five units, stratified by unit: Mantel-Haenszel odds ratio (95 % RBG interval), the "
           "Cochran-Mantel-Haenszel p with the continuity correction and the exact conditional p. The two registered "
           "tests are one-sided as predicted and are `e2b1_stats.py`'s (`stats/v6_i`, `stats/v6_ii`); they are repeated "
           "here from this tool's own tables as a cross-check. The others are descriptive and two-sided.", "",
           "| contrast (X against Y) | X | Y | MH odds ratio | CMH p | exact p | per unit X vs Y (Fisher two-sided) |",
           "|---|---|---|---|---|---|---|"]
    for name, c in con.items():
        one = c["alternative"] is not None
        per = "; ".join(f"`{u}` {v['x']} vs {v['y']} ({_p(v['fisher_two_sided'])})" for u, v in c["per_unit"].items())
        md.append(f"| {name} | {c['x_total']} | {c['y_total']} | {_or(c['mh_or'])} | "
                  f"{_p(c['cmh_p_one_sided'] if one else c['cmh_p_two_sided'])} {'one-sided' if one else 'two-sided'} | "
                  f"{_p(c['exact_p_one_sided'] if one else c['exact_p_two_sided'])} | {per} |")
    first = [t for _, t in tables(js, N3, N1)]
    second = [t for _, t in tables(js, A3, A1)]
    inter = es.or_difference(first, second, "greater")
    rate = lambda lab: pooled[lab]["success"] / pooled[lab]["n"] if pooled[lab]["n"] else 0.0  # noqa: E731
    res["interaction"] = {"form": "H5b: extra attempts help most where the evidence is absent",
                          "gain_without_evidence": rate(N3) - rate(N1), "gain_with_evidence": rate(A3) - rate(A1),
                          "or_difference": inter}
    md += ["",
           f"**The interaction (H5b's form: extra attempts help most where the evidence is absent).** Two more "
           f"attempts raise the success rate by {100 * (rate(N3) - rate(N1)):+.0f} points without evidence "
           f"({pooled[N1]['success']}/{pooled[N1]['n']} → {pooled[N3]['success']}/{pooled[N3]['n']}) and by "
           f"{100 * (rate(A3) - rate(A1)):+.0f} with it ({pooled[A1]['success']}/{pooled[A1]['n']} → "
           f"{pooled[A3]['success']}/{pooled[A3]['n']}). Ratio of the two Mantel-Haenszel odds ratios "
           + (f"{inter['ratio_of_odds_ratios']:.2f} (95 % {inter['ci95'][0]:.2f}–{inter['ci95'][1]:.2f}), z = "
              f"{inter['z']:.2f}, one-sided p = {_p(inter['p_one_sided'])}"
              + (" — 1/2 added to every cell (a zero cell), flagged" if inter.get("corrected") else "")
              if "z" in inter else str(inter.get("note"))) + ". Descriptive.", ""]

    # ---- 3. calls and cost --------------------------------------------------------------------------------
    md += ["## Model calls and cost", "",
           "Over the five units: model calls, calls per trial and per success; API-equivalent cost of all seven "
           "units of the setup (the runs were paid by subscription).", "",
           "| setup | trials (five units) | model calls | per trial | per success | cost, all seven units | agent time, all seven |",
           "|---|---|---|---|---|---|---|"]
    cost: Dict[str, Any] = {}
    for label, _, _ in SETUPS:
        five = [j for j in js[label] if j["unit"] in ORDER_UNITS and j["with_verdict"]]
        calls = sum(j["calls"] for j in five)
        succ = sum(1 for j in five if j["success"])
        usd = sum(j["cost"] for j in js[label])
        hours = sum(j["agent_s"] for j in js[label]) / 3600
        cost[label] = {"trials": len(five), "calls": calls, "successes": succ, "cost_usd_all_units": usd,
                       "calls_all_units": sum(j["calls"] for j in js[label]), "agent_hours_all_units": hours}
        md.append(f"| {label} | {len(five)} | {calls} | {calls / len(five):.2f} | "
                  f"{(f'{calls / succ:.1f}' if succ else '—')} | ${usd:.2f} | {hours:.1f} h |")
    res["cost"] = cost
    md += ["", f"All setups, all seven units: {sum(c['calls_all_units'] for c in cost.values())} model calls, "
               f"${sum(c['cost_usd_all_units'] for c in cost.values()):.2f} API-equivalent.", ""]

    # ---- 4. the control and the decline unit ---------------------------------------------------------------
    md += [f"## The control `{CONTROL}` — the order in the file is right", "",
           "| setup | successes (FASTER) | unsafe | too slow | trials |", "|---|---|---|---|---|"]
    for label, _, _ in SETUPS:
        c = cells[label][CONTROL]
        md.append(f"| {label} | {c['success']} ({c['faster']}) | {c['unsafe']} | {c['too_slow']} | {c['n']} |")
    md += ["", f"## The decline unit `{DECLINE}` — the statements feed each other: the loop has to be left alone", "",
           "Nothing can be gained on this unit; the efficient answer is the unchanged program. A program that is "
           "parallel all the same is right only if the kernel's iterations still run in their order — because the "
           "loop over the index tables stays outside every parallel region (only a loop the program added is "
           "parallel), or because the program orders the iterations at run time from the tables (an inspector that "
           "sorts them into levels: right for any tables, and here close to one level per iteration). Per setup: "
           "trials that ship a parallel program at all; of those, wrong (unsafe) and too slow; and where the loop "
           "over the index tables stands, as the program's text shows.", "",
           "| setup | trials | left unchanged or not parallel | ship a parallel program | of those unsafe | too slow | "
           "index-table loop inside a parallel region | index-table loop outside every parallel region (an added loop "
           "is parallel) |",
           "|---|---|---|---|---|---|---|---|"]
    k53: Dict[str, Any] = {}
    for label, _, _ in SETUPS:
        v = [j for j in js[label] if j["unit"] == DECLINE and j["with_verdict"]]
        par = [j for j in v if j["omp"]]
        inside = sum(1 for j in par if j["k53_real_loop_parallel"] is True)
        side = sum(1 for j in par if j["k53_real_loop_parallel"] is False)
        k53[label] = {"n": len(v), "not_parallel": len(v) - len(par), "parallel": len(par),
                      "unsafe": sum(1 for j in par if j["unsafe"]),
                      "too_slow": sum(1 for j in par if j["bucket"] == "timed-out-correct"),
                      "index_loop_parallel": inside, "index_loop_sequential": side,
                      "no_parallel_region_found": len(par) - inside - side,
                      "buckets": {b: sum(1 for j in v if j["bucket"] == b) for b in sorted({j["bucket"] for j in v})}}
        d = k53[label]
        md.append(f"| {label} | {d['n']} | {d['not_parallel']} | {d['parallel']} | {d['unsafe']} | {d['too_slow']} | "
                  f"{inside} | {side} |")
    res["k53"] = k53
    md.append("")

    # ---- 5. every unsafe program of the agent --------------------------------------------------------------
    md += ["## Every unsafe program of the agent", ""]
    unsafe: List[Dict[str, Any]] = []
    for label in AGENT_LABELS:
        for j in js[label]:
            if j["unsafe"]:
                unsafe.append({"setup": label, "unit": j["unit"], "repeat": j["repeat"], "run": j["run"],
                               "bucket": j["bucket"], "status": j["status"], "failure": j["failure"]})
    res["agent_unsafe"] = unsafe
    if unsafe:
        md += ["| setup | unit | repetition | what the harness recorded |", "|---|---|---|---|"]
        for r in unsafe:
            f = r["failure"] or {}
            what = r["bucket"] + (f": the final run at {f.get('threads')} threads ended with return code {f.get('rc')} "
                                  f"after {f.get('seconds')} s" if f else f" ({r['status']})")
            md.append(f"| {r['setup']} | `{r['unit']}` | {r['repeat']} | {what} |")
    else:
        md.append("None.")
    n_agent = sum(1 for label in AGENT_LABELS for j in js[label] if j["with_verdict"])
    md += ["", f"{len(unsafe)} of the agent's {n_agent} trials with a verdict.", ""]

    # ---- 6. the repetition loop and the temporary data, read from every shipped program ----------------------
    md += ["## What the changed programs did to the repetition loop, and where they keep temporary data", "",
           "Read from the text of every shipped program that differs from the original, all seven units. "
           "\"Automatic array\": a local array of the data's length (`real_t x[LEN_1D]` inside the function) — it "
           "lies on the stack, as does every thread's `private` or `firstprivate` copy of it; the data is larger at "
           "the size the final check runs than at the size a setup works with.", "",
           "| setup | changed programs | repetition loop kept as it is | temporary data: automatic array | heap | static | none "
           "| automatic array: unsafe · success · other |", "|---|---|---|---|---|---|---|---|"]
    shape: Dict[str, Any] = {}
    listed: List[str] = []
    for label, _, _ in SETUPS:
        ch = [j for j in js[label] if j["with_verdict"] and j["bucket"] != "no-change"]
        mem = {k: sum(1 for j in ch if j["memory"] == k) for k in ("automatic array", "heap", "static", "none")}
        au = [j for j in ch if j["memory"] == "automatic array"]
        kept = sum(1 for j in ch if j["rep"] == "kept")
        shape[label] = {"changed": len(ch), "rep_kept": kept, "memory": mem,
                        "auto_unsafe": sum(1 for j in au if j["unsafe"]),
                        "auto_success": sum(1 for j in au if j["success"]),
                        "auto_private": sum(1 for j in au if j["auto_private"]),
                        "rep_changed": [f"{j['unit']} rep {j['repeat']}: {j['rep']} ({j['bucket']})"
                                        for j in ch if j["rep"] != "kept"],
                        "auto_cases": [f"{j['unit']} rep {j['repeat']}: {', '.join(j['auto_arrays'])}"
                                       f"{' — in a private clause' if j['auto_private'] else ''} ({j['bucket']})" for j in au]}
        d = shape[label]
        md.append(f"| {label} | {len(ch)} | {kept} | {mem['automatic array']} | {mem['heap']} | {mem['static']} | "
                  f"{mem['none']} | {d['auto_unsafe']} · {d['auto_success']} · "
                  f"{len(au) - d['auto_unsafe'] - d['auto_success']} |")
        if label in AGENT_LABELS:
            listed += [f"- {label} — repetition loop: {c}" for c in d["rep_changed"]]
            listed += [f"- {label} — automatic array: {c}" for c in d["auto_cases"]]
    res["shape"] = shape
    md += ["", "The agent's programs that changed the repetition loop or hold an automatic array:", ""]
    md += listed or ["None."]
    md.append("")

    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "e2v6_readout.md").write_text("\n".join(md) + "\n")
    (a.out / "e2v6_readout.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
