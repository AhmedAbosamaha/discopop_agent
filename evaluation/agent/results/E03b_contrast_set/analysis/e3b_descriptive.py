#!/usr/bin/env python3
"""E3b, the descriptive read-outs fixed in the pre-registration (THESIS_EXPERIMENTS §6, 10 Oct 2026), from the
archived trials: per loop — outcomes, the speed-ups of the winning programs, model calls and cost; which form of
directive each final program carries and who wrote it; the directives DiscoPoP itself wrote on the model's
rewrites and what the gate said to each; the gate's refusals by stage. No test is run here. Written after the
trials (the list of read-outs was fixed before them).

    ../venv/bin/python agent/results/E03b_contrast_set/analysis/e3b_descriptive.py     (from evaluation/)
"""
import collections
import csv
import glob
import json
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"
TEST = "s314 s316 s3113 s315 s318 s319".split()
CONTROL = ["s311"]
SETUPS = [("discopop_gate_v5", "DiscoPoP alone"), ("default_v5", "DiscoPoP writes"), ("llm_pragmas_v5", "the model writes"),
          ("bare_llm_v4", "Haiku alone")]
rows = []
for f in sorted(glob.glob(str(RUNS / "e3b_*" / "figures" / "trials.csv"))):
    rows += list(csv.DictReader(open(f)))
assert all(int(float(r["llm_call_failures"] or 0)) == 0 for r in rows)
by = collections.defaultdict(list)
for r in rows:
    by[(r["benchmark"].split("/")[1], r["arm"])].append(r)
out = ["# E3b — descriptive read-outs (fixed in the pre-registration of 10 Oct 2026)", "",
       f"{len(rows)} trials in five runs; no trial with a failed model call. Outcomes are the harness's; the race check "
       "(`checks/e3b_race_check`) finds every changed program of the agent's two setups clean and one of Haiku alone's racy.", "",
       "## Per loop", "",
       "Outcomes (FASTER · parallel, not faster · no change · BROKEN); the speed-ups of the FASTER trials (best of 6 and 12 "
       "threads, against the original), their median; model calls and cost per trial.", "",
       "| loop | setup | outcomes | speed-ups of the FASTER trials | median | calls | $ |", "|---|---|---|---|---:|---:|---:|"]
for k in TEST + CONTROL:
    for arm, name in SETUPS:
        t = by[(k, arm)]
        c = collections.Counter(x["outcome"] for x in t)
        sp = sorted(float(x["best_speedup"]) for x in t if x["outcome"] == "FASTER" and x["best_speedup"])
        o = f"{c['FASTER']} · {c['parallel-not-faster']} · {c['no-change']} · {c['BROKEN']}"
        out.append(f"| `{k}`{' (control)' if k in CONTROL else ''} | {name} | {o} | {' '.join(f'{v:.2f}' for v in sp) or '—'} | "
                   + (f"{statistics.median(sp):.2f}×" if sp else "—")
                   + f" | {sum(int(float(x['llm_calls'] or 0)) for x in t) / len(t):.1f} | {sum(float(x['cost_usd_equivalent'] or 0) for x in t) / len(t):.2f} |")
out += ["", "## Totals", "", "| setup | trials | FASTER | model calls | cost |", "|---|---:|---:|---:|---:|"]
for arm, name in SETUPS:
    t = [r for r in rows if r["arm"] == arm]
    out.append(f"| {name} | {len(t)} | {sum(1 for r in t if r['outcome'] == 'FASTER')} | {sum(int(float(r['llm_calls'] or 0)) for r in t)} | "
               f"${sum(float(r['cost_usd_equivalent'] or 0) for r in t):.2f} |")
out.append(f"\nAll setups together: ${sum(float(r['cost_usd_equivalent'] or 0) for r in rows):.2f}.")


def kinds(src):
    ks = []
    for line in src.splitlines():
        m = re.search(r"#pragma omp\s+(.*)", line)
        if not m:
            continue
        p = m.group(1).strip()
        ks.append("reduction(max)" if "reduction(max" in p else "reduction(min)" if "reduction(min" in p
                  else "reduction(+)" if "reduction(+" in p else "critical" if p.startswith("critical")
                  else "parallel region" if re.fullmatch(r"parallel(\s+\w+\([^)]*\))*", p) else "for inside a region" if p.startswith("for")
                  else "parallel for" if p.startswith("parallel for") else p.split()[0])
    return " + ".join(sorted(set(ks))) or "no directive"


out += ["", "## The directives in the final programs", "",
        "By setup and loop: the forms the final program carries (number of trials). Where DiscoPoP writes, every directive is "
        "DiscoPoP's; where the model writes, the model's except where noted in the trial records (`pragmas_discopop`).", "",
        "| loop | DiscoPoP writes | the model writes | Haiku alone |", "|---|---|---|---|"]
for k in TEST + CONTROL:
    cells = []
    for arm in ("default_v5", "llm_pragmas_v5", "bare_llm_v4"):
        c = collections.Counter()
        for f in sorted(glob.glob(str(RUNS / "e3b_*" / "benchmarks" / "tsvc_c4" / k / arm / "*" / "rep*" / "final" / f"{k}.c"))):
            c[kinds(Path(f).read_text())] += 1
        cells.append("; ".join(f"{a} ({b})" for a, b in sorted(c.items(), key=lambda kv: -kv[1])))
    out.append(f"| `{k}` | " + " | ".join(cells) + " |")

own = collections.Counter()
stages = collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(str(RUNS / "e3b_*" / "benchmarks" / "tsvc_c4" / "*" / "*" / "*" / "rep*" / "agent_patches" / "candidates.jsonl"))):
    p = Path(f)
    k, arm = p.parts[-6], p.parts[-5]
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        ph = str(c.get("phase"))
        res = "passed" if c.get("passed") else f"refused: {c.get('stage')}"
        stages[arm][(ph, res)] += 1
        if arm == "default_v5" and ph in ("A-D40", "B"):
            try:
                patch = (p.parent / c["patch"]).read_text()
            except (OSError, KeyError):
                continue
            forms = set()                     # a candidate counts once per form: a task construct is four lines
            for pr in re.findall(r"^\+\s*(#pragma omp[^\n]*)", patch, re.M):
                forms.add("reduction(max:…)" if "reduction(max" in pr else "reduction(min:…)" if "reduction(min" in pr
                          else "reduction(+:…)" if "reduction(+" in pr else "lastprivate" if "lastprivate" in pr
                          else "a task construct" if re.search(r"task|single|parallel\s*$", pr) else "parallel for")
            for kind in forms:
                own[(k, kind, res)] += 1
out += ["", "## The directives DiscoPoP itself wrote on the model's rewrites (the setup in which DiscoPoP writes)", "",
        "Every candidate carrying a directive of DiscoPoP's that the gate judged, by loop and form — while the model's budget "
        "lasted (a rewrite judged as it would ship) and at the end. A candidate with two forms is counted under each.", "",
        "| loop | DiscoPoP's directive | the gate | candidates |", "|---|---|---|---:|"]
for (k, kind, res), n in sorted(own.items()):
    out.append(f"| `{k}` | `{kind}` | {res} | {n} |")
out += ["", "## The gate's verdicts on every candidate, by stage", ""]
for arm, name in (("default_v5", "DiscoPoP writes"), ("llm_pragmas_v5", "the model writes")):
    out.append(f"**{name}** — {sum(stages[arm].values())} candidates recorded")
    out += [f"- phase {ph}, {res}: {n}" for (ph, res), n in sorted(stages[arm].items())] + [""]
(HERE / "e3b_descriptive.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
