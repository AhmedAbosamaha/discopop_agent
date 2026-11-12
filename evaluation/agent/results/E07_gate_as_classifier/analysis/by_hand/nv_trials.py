"""The trials of a corpus whose replayed history does not end in the archived final file: every candidate with the base
the builder gave it, whether the patch applies exactly there, and the log's own account of what was kept."""
import collections, json, re, sys, tempfile
from pathlib import Path
EVAL = Path(__file__).resolve().parents[5]            # .../evaluation
sys.path.insert(0, str(EVAL / "agent/tools")); sys.path.insert(0, str(EVAL.parent))
import campaign, gate_study  # noqa: E402
R = EVAL / "agent/results/E07_gate_as_classifier"
name = sys.argv[1]
only = sys.argv[2] if len(sys.argv) > 2 else ""
C = R / "corpus" / name
c = json.loads((C / "corpus.json").read_text())
progs, cands = c["programs"], c["candidates"]
tmp = Path(tempfile.mkdtemp(prefix="e7_nv_"))
def pname(h):
    return "orig" if progs[h]["original"] else f"#{progs[h]['index']}"
for t in sorted(c["not_verified"]):
    if only and only not in t:
        continue
    run, bench, arm, rep = t.split(" ")[:4]
    d = campaign.find_run(run)
    tdir = next(iter(sorted((d / "benchmarks" / bench / arm).glob(f"*/{rep}"))))
    print(f"\n=== {t}")
    nr = [x for x in c["not_rebuilt"] if x.startswith(t + " n")]
    if nr:
        print("   not rebuilt:", nr)
    recs = [json.loads(l) for l in (tdir / "agent_patches/candidates.jsonl").read_text().splitlines() if l.strip()]
    mine = {x["n"]: x for x in cands if x["id"].startswith(t + " n")}
    for r in recs:
        x = mine.get(r["n"])
        if x is None:
            print(f"   n{r['n']:<3} {r['phase']:8} {str(r.get('region_id')):6} {'pass' if r['passed'] else r['stage']:12} NOT IN CORPUS  cache={r.get('from_cache')}")
            continue
        base = (C / progs[x["base"]]["path"]).read_text()
        ptext = (campaign.RESULTS / x["patch"]).read_text(errors="replace")
        got = gate_study._apply(base, ptext, progs[x["program"]]["file"], True, tmp)
        print(f"   n{r['n']:<3} {r['phase']:8} {str(r.get('region_id')):6} {'pass' if r['passed'] else r['stage']:12} base {pname(x['base']):6} -> {pname(x['program']):6} exact={got is not None}  cache={r.get('from_cache')}  exposed={r.get('exposed_region')}")
    log = (tdir / "agent.log").read_text().splitlines()
    for l in log:
        if re.search(r"└─ |reverting|Dropped|^\s+· |SUMMARY|\[Phase-B\] Applied|┌─ pattern|┌─ \[depth|FLOOR|floor\]", l):
            print("      | " + l[:170])
    tj = json.loads((tdir / "trial.json").read_text())
    print("   trial:", tj.get("outcome"), "| pragmas_in_final", tj.get("pragmas_in_final"), "| rewrites_kept", tj.get("rewrites_kept"), "| settle_dropped", tj.get("settle_dropped"))
