"""By-hand reading of one program of an E7 corpus: its candidates, the diff from its base, the replayed checks with
their diagnostics, and the judge's record.   usage: inspect_prog.py a1|a2 <benchmark> <index> [--diff] [--judge RUNS] [--checks RUN]"""
import collections, difflib, json, sys
from pathlib import Path

EVAL = Path(__file__).resolve().parents[5]            # .../evaluation
R = EVAL / "agent/results/E07_gate_as_classifier"
sys.path.insert(0, str(EVAL / "agent/tools"))
import campaign  # noqa: E402


def run_dir(run_id):
    d = campaign.find_run(run_id)
    return d if d is not None else EVAL / "agent/runs" / run_id


def main():
    name, bench, idx = sys.argv[1], sys.argv[2], int(sys.argv[3])
    args = sys.argv[4:]
    C = R / "corpus" / name
    c = json.loads((C / "corpus.json").read_text())
    progs, cands = c["programs"], c["candidates"]
    h = next(k for k, v in progs.items() if v["benchmark"] == bench and v["index"] == idx)
    mine = [x for x in cands if x["program"] == h]
    print(f"== {bench} #{idx}  {h[:12]}  directive={progs[h]['directive']}  final_of={progs[h]['final_of']}")
    print("   candidates:", len(mine), dict(collections.Counter((x["kind"], x["phase"], x["gate"]) for x in mine)))
    print("   e.g.", [x["id"] for x in mine[:3]])
    bases = collections.Counter(x["base"] for x in mine)
    judge_runs = (args[args.index("--judge") + 1].split(",") if "--judge" in args else
                  ([f"e7_{name}_judge_{k}" for k in (1, 2, 3, 4, 5)] if name == "a1" else [f"e7_{name}_judge_{k}" for k in (1, 2)]))
    checks_runs = (args[args.index("--checks") + 1].split(",") if "--checks" in args else
                   ([f"e7_{name}_checks", f"e7_{name}_checks_2"] if name == "a1" else [f"e7_{name}_checks"]))
    # judge
    for rid in judge_runs:
        d = run_dir(rid)
        if not d.is_dir():
            continue
        tj = d / "benchmarks" / bench / "e7" / "none" / f"rep{idx}" / "trial.json"
        if tj.is_file():
            rec = json.loads(tj.read_text())
            v = rec.get("verify") or {}
            print(f"   J1 [{rid}]: outcome={rec.get('outcome')} status={v.get('status')} pragmas={rec.get('pragmas_in_final')}")
            keep = {k: v[k] for k in v if k in ("dump_max_rel_err", "dump_seeded_max_rel_err", "digest_max_rel_err", "digest_seeded_rel_err",
                                               "stable_at_fixed_threads", "speed_measurable", "final_run_failure", "dump_exact", "dump_exact_seeded")}
            print("      ", keep)
            par = v.get("par") or {}
            print("       speedups:", {k: round(p.get("speedup") or 0, 2) for k, p in par.items()})
        f2 = d / "gate_study" / "j2.jsonl"
        if f2.is_file():
            for ln in f2.read_text().splitlines():
                if ln.strip() and json.loads(ln)["program"] == h:
                    r = json.loads(ln)
                    print(f"   J2 [{rid}]: {r['verdict']} at {r.get('verify_size')}  runs={[(x['rc'], x['race'], x['seconds']) for x in r['runs']]}")
                    for x in r["runs"]:
                        if x["race"]:
                            print("      ", x["report"][:700].replace("\n", "\n       "))
                            break
    # checks
    recs = {}
    for rid in checks_runs:
        d = run_dir(rid)
        for f in (sorted(d.rglob("checks.jsonl")) if d.is_dir() else []):
            for ln in f.read_text().splitlines():
                if ln.strip():
                    r = json.loads(ln)
                    recs[r["pair"]] = r
    for b, n in bases.items():
        r = recs.get(f"{b} {h}")
        bname = "the original" if progs[b]["original"] else f"#{progs[b]['index']}"
        print(f"   base {bname} ({n} candidates):")
        if r is None:
            print("      no replay record")
            continue
        for k in ("G", "T", "S", "O1", "O2"):
            v = r.get(k)
            if v is None:
                continue
            runs = [v] if isinstance(v, dict) else v
            pat = " ".join("pass" if x["passed"] else x["stage"] for x in runs)
            mx = [(x.get("matrix") or {}).get("verdict") for x in runs if x.get("matrix")]
            print(f"      {k:2}: {pat}" + (f"   matrix: {mx}" if mx else ""))
            bad = next((x for x in runs if not x["passed"]), None)
            if bad:
                print("          " + bad["diagnostic"][:420].replace("\n", "\n          "))
        print(f"      noise floor {r.get('noise_floor')}  note={r.get('note')} error={r.get('error')}")
        if "--diff" in args:
            a = (C / progs[b]["path"]).read_text().splitlines()
            bt = (C / progs[h]["path"]).read_text().splitlines()
            print("\n".join(list(difflib.unified_diff(a, bt, "base", "program", lineterm="", n=2))[:140]))


main()
