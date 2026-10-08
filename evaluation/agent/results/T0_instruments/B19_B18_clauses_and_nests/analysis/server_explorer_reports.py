"""Read-only, on the server: for each kept profile of the named runs, what the explorer reported — the Do-All and
reduction loops and, per blocked loop, the dependence that blocked it. Prints one JSON object."""
import json, sys, os, glob
R = "/home/ahmedabosamaha/discopop_agent/evaluation/agent/runs"
out = {}
for run in sys.argv[1:]:
    for dp in sorted(glob.glob(f"{R}/{run}/profiles/*/*/.discopop")):
        bench = "/".join(dp.split("/")[-3:-1])
        rec = {}
        try:
            fm = {}
            for ln in open(dp + "/FileMapping.txt"):
                a, b = ln.split(None, 1)
                fm[a] = os.path.basename(b.strip())
            p = json.load(open(dp + "/explorer/patterns.json"))["patterns"]
            name = lambda s: fm.get(str(s).split(":")[0], "?") + ":" + str(s).split(":")[1]
            rec["do_all"] = sorted(name(x["start_line"]) for x in p.get("do_all", []))
            rec["reduction"] = sorted(name(x["start_line"]) for x in p.get("reduction", []))
            bl = set()
            pv = dp + "/explorer/doall_prevented.json"
            for r in (json.load(open(pv)) if os.path.exists(pv) else []):
                bl.add((fm.get(str(r.get("loop_file")), "?") + ":" + str(r.get("loop_start")), str(r.get("dep_type")).split(".")[-1],
                        str(r.get("var_name")), str(r.get("origin")).split(".")[-1], str(r.get("reason"))))
            rec["blocked"] = sorted(bl)
            log = os.path.dirname(dp) + "/profiled_run.log"
            rec["loop_results_line"] = os.path.exists(log) and ("Outputting instrumentation results" in open(log, errors="replace").read())
            rec["explore_logs"] = sorted(os.path.basename(x) for x in glob.glob(os.path.dirname(dp) + "/explore_*.log"))
        except Exception as e:  # noqa: BLE001
            rec["error"] = repr(e)
        out.setdefault(run, {})[bench] = rec
print(json.dumps(out))
