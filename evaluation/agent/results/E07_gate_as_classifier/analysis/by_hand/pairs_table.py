"""By-hand reading of an E7 corpus, one line per (base, program) pair that holds a directive: what the gate recorded,
what the judge found (J1 the harness's verification, J2 its race check), and what each check alone did in its runs
(T ThreadSanitizer x3, S the schedule matrix x3, O1/O2 the output on the shipped/perturbed input x3; p = pass,
F = refused on what the check saw, t = refused because a run hit the gate's time limit, in run order).  A refusal by
a time limit is no detection: the summaries count it apart.  Then the same pairs counted by KIND of check (the sanitizer, the matrix, the output
comparison on either input), which the generated read-out does not hold: it treats the two inputs as two checks.
usage: pairs_table.py a1|a2 [--all] [--judge RUNS] [--checks RUNS]      (without --all: the wrong pairs and the
right pairs some check refuses)"""
import collections, json, sys
from pathlib import Path

EVAL = Path(__file__).resolve().parents[5]
R = EVAL / "agent/results/E07_gate_as_classifier"
sys.path.insert(0, str(EVAL / "agent/tools"))
import gate_study as gs  # noqa: E402


def main():
    name = sys.argv[1]
    args = sys.argv[2:]
    C = R / "corpus" / name
    c = json.loads((C / "corpus.json").read_text())
    progs, cands = c["programs"], c["candidates"]
    judge_runs = (args[args.index("--judge") + 1].split(",") if "--judge" in args else
                  ([f"e7_{name}_judge_{k}" for k in (1, 2, 3, 4, 5)] if name == "a1" else [f"e7_{name}_judge_{k}" for k in (1, 2)]))
    checks_runs = (args[args.index("--checks") + 1].split(",") if "--checks" in args else
                   ([f"e7_{name}_checks", f"e7_{name}_checks_2"] if name == "a1" else [f"e7_{name}_checks"]))
    by_key = {(str(v["benchmark"]), int(v["index"])): h for h, v in progs.items()}
    j1, j2, checks = {}, {}, {}
    for rid in judge_runs:
        d = gs._run_dir(rid)
        if d is None:
            continue
        for tj in sorted(d.glob("benchmarks/*/*/e7/none/rep*/trial.json")):
            rec = gs._trial(tj)
            if rec is None:
                continue
            h = by_key.get((str(rec["benchmark"]), int(rec["repeat"])))
            if h is not None:
                j1[h] = (gs._j1_class(rec), rec)
        for r in gs._records(d / "gate_study" / "j2.jsonl"):
            if str(r.get("program")) in progs and "verdict" in r:
                j2[str(r["program"])] = r
    for rid in checks_runs:
        d = gs._run_dir(rid)
        if d is None:
            continue
        for fc in sorted(d.rglob("checks.jsonl")):
            for r in gs._records(fc):
                if "pair" in r and ("G" in r or str(r["pair"]) not in checks):
                    checks[str(r["pair"])] = r

    def judge(h):
        if progs[h]["original"]:
            return "right", "the original", "n/a"
        if h not in j1:
            return "not-judged", "", "-"
        (cls, why), _ = j1[h]
        rv = str(j2[h]["verdict"]) if h in j2 else ("n/a" if not progs[h]["directive"] else "not run")
        if cls == "right" and rv == "race":
            return "wrong", "output right; race reported", rv
        if cls == "right" and rv not in ("clean", "n/a"):
            return "no-race-verdict", why, rv
        return cls, why, rv

    seen = {}
    for x in cands:
        if x["kind"] != "directive" or x["gate"] in ("compile", "openmp_compile", "apply"):
            continue
        p = f"{x['base']} {x['program']}"
        seen.setdefault(p, []).append(x)
    rows = []
    for p, xs in seen.items():
        b, h = p.split()
        if judge(b)[0] != "right":
            continue
        cls, why, rv = judge(h)
        r = checks.get(p) or {}

        def pat(k):
            v = r.get(k)
            if v is None:
                return "-"
            runs = [v] if isinstance(v, dict) else v
            return "".join("p" if y["passed"] else ("t" if "timed out" in str(y.get("diagnostic")) else "F") for y in runs)

        def stages(k):
            v = r.get(k)
            runs = [v] if isinstance(v, dict) else (v or [])
            return sorted({y["stage"] for y in runs if not y["passed"]})

        soft = any((y.get("matrix") or {}).get("verdict") == "beyond-floor" for y in (r.get("S") or []))
        rows.append({"name": f"{progs[h]['benchmark']} #{progs[h]['index']}", "n": len(xs), "gate": sorted({x["gate"] for x in xs}),
                     "cls": cls, "why": why, "race": rv, "G": pat("G"), "T": pat("T"), "S": pat("S"), "O1": pat("O1"), "O2": pat("O2"),
                     "soft": soft, "Gstage": stages("G")})
    rows.sort(key=lambda z: (z["cls"], z["name"].split(" #")[0], int(z["name"].split("#")[1])))
    show_all = "--all" in args
    print(f"{'pair':34} {'n':>2} {'recorded':14} {'judge':6} {'J2':7} {'G':2} {'T':4} {'S':4} {'O1':4} {'O2':4}  why (judge)")
    for z in rows:
        refused_by_some = any(("F" in z[k] or "t" in z[k]) for k in ("T", "S", "O1", "O2"))
        if not show_all and z["cls"] == "right" and not refused_by_some and z["gate"] == ["accepted"]:
            continue
        print(f"{z['name']:34} {z['n']:>2} {','.join(z['gate']):14} {z['cls']:6} {z['race']:7} {z['G']:2} {z['T']:4} {z['S']:4} {z['O1']:4} {z['O2']:4}  "
              f"{z['why'][:110]}{'  [matrix: beyond the noise]' if z['soft'] else ''}")
    for cls in ("wrong", "right"):
        sel = [z for z in rows if z["cls"] == cls]
        kinds = collections.Counter()
        for z in sel:
            k = tuple(nm for nm, on in (("sanitizer", "F" in z["T"]), ("matrix", "F" in z["S"]),
                                        ("output", "F" in z["O1"] or "F" in z["O2"])) if on)
            kinds[k] += 1
        timed = [z["name"] for z in sel if any("t" in z[k] for k in ("G", "T", "S", "O1", "O2"))]
        print(f"\n{cls} pairs: {len(sel)}; refused by which KINDS of check (alone, in at least one run, on what the check saw; "
              f"a time limit is not counted):")
        for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
            print(f"   {v:4}  {' + '.join(k) if k else 'none'}")
        j = collections.Counter(("output right" if cls == "right" or z["why"].startswith("output right") else "output wrong")
                                + ", J2 " + z["race"] for z in sel)
        print("   the judge:", dict(j))
        print(f"   pairs where some run hit a time limit: {len(timed)}" + (": " + ", ".join(timed) if timed else ""))
        both = [z for z in sel if z["T"] and set(z["T"]) == {"F"}]
        print(f"   the gate's sanitizer reports in every run on {len(both)}; the judge's race check on those:",
              dict(collections.Counter(z["race"] for z in both)))


main()
