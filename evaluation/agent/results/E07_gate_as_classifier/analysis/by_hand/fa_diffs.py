"""Every false accept / false refusal of a corpus (from readout_<name>.json): the candidate that made it, the lines it
added and removed against its base, and what became of the trial.   usage: fa_diffs.py a1|a2 false_accepts|false_refusals [filter]"""
import difflib, json, sys
from pathlib import Path
EVAL = Path(__file__).resolve().parents[5]            # .../evaluation
R = EVAL / "agent/results/E07_gate_as_classifier"
sys.path.insert(0, str(EVAL / "agent/tools"))
import campaign  # noqa: E402
name, which = sys.argv[1], sys.argv[2]
flt = sys.argv[3] if len(sys.argv) > 3 else ""
C = R / "corpus" / name
c = json.loads((C / "corpus.json").read_text())
progs, cands = c["programs"], c["candidates"]
ro = json.loads((R / "analysis" / f"readout_{name}.json").read_text())
for row in ro[which]:
    if flt and flt not in row["program"]:
        continue
    h = row["hash"]
    mine = [x for x in cands if x["program"] == h]
    print(f"\n=== {row['program']}  [{row['kind']} {row['phase']}]  gate: {row['gate']}  judge: {row['judge'][:110]}")
    for x in mine:
        b = x["base"]
        bname = "the original" if progs[b]["original"] else f"#{progs[b]['index']}"
        print(f"    candidate {x['id']}  on base {bname}")
        a = (C / progs[b]["path"]).read_text().splitlines()
        t = (C / progs[h]["path"]).read_text().splitlines()
        for ln in difflib.unified_diff(a, t, "base", "program", lineterm="", n=0):
            if ln.startswith(("---", "+++", "@@")):
                continue
            print("      " + ln[:150])
        # what the trial went on to do with it
        later = [y for y in cands if y["run"] == x["run"] and y["benchmark"] == x["benchmark"] and y["arm"] == x["arm"] and y["rep"] == x["rep"]]
        later.sort(key=lambda y: (y["phase"] != "A", y["n"]))
        print("    the trial's candidates: " + "; ".join(f"n{y['n']} {y['kind'][:3]} {y['phase']} {y['gate']}" + (" <== this" if y["program"] == h and y["id"] == x["id"] else "") for y in later))
        d = campaign.find_run(x["run"])
        if d is not None:
            tj = next(iter(sorted((d / "benchmarks" / x["benchmark"] / x["arm"]).glob(f"*/{x['rep']}/trial.json"))), None)
            if tj is not None:
                rec = json.loads(tj.read_text())
                v = rec.get("verify") or {}
                print(f"    the trial ended: outcome={rec.get('outcome')} verify={v.get('status')} pragmas_in_final={rec.get('pragmas_in_final')}")
