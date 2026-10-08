#!/usr/bin/env python3
"""Tests for scaffold.py, the harness's check that a rewrite left the packaging's code alone.

Run: `python3 agent/tools/test_scaffold.py` (exit status 1 on any failure). Uses the packaged
sources, and the recorded runs `pilot2` and `local_obs1` when present. Every case states
what must be caught and what must be allowed; see THESIS_EXPERIMENTS.md for why each exists.
"""
import glob
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scaffold as S  # noqa: E402

R = str(Path(__file__).resolve().parent.parent)
fails = 0
def expect(label, res, ok):
    global fails
    good = res["ok"] == ok; fails += not good
    print(f"  [{'pass' if good else 'FAIL'}] {label}: ok={res['ok']} {res['problems'][:1]}")
n_self = 0
for meta in sorted(glob.glob(f"{R}/prepared/*/*/meta.json")):
    m = json.load(open(meta))
    if m.get("suite") == "calibration":
        continue
    f = f"{meta[:-len('meta.json')]}{m['file']}"      # the unit holding main and the harness code
    t = open(f).read(); r = S.check(t, t); n_self += 1
    if (m.get("project") or {}).get("editable"):
        # packaging v5 (4 Oct 2026): `file` is the benchmark's OWN file and holds nothing of the measurement,
        # so the check has nothing to apply to there; it applies to the program as a whole (main.c has the
        # timer and the repetition loop) — and the judge compares every other file byte for byte.
        whole = "".join(open(f"{meta[:-len('meta.json')]}{u}").read() for u in sorted(m["project"]["units"]))
        w = S.check(whole, whole)
        if not (r["ok"] and not r["applies"] and w["ok"] and w["applies"]):
            fails += 1; print("  FAIL self (v5)", f, r, w)
        continue
    if not (r["ok"] and r["applies"]): fails += 1; print("  FAIL self", f, r)
print(f"  {n_self} unchanged sources checked")
for run, name, want in [  # recorded runs: skipped when absent
("pilot2", "seidel-2d", False), ("local_obs1", "seidel-2d", False),
                        ("local_obs1", "2mm", True), ("local_obs1", "jacobi-2d-imper", True)]:
    found = glob.glob(f"{R}/runs/{run}/benchmarks/polybench/{name}/full/*/rep1")
    if not found:
        print(f"  [skip] {run} {name}: run not present")
        continue
    d = found[0]
    expect(f"{run} {name}", S.check(open(d+"/original.c").read(), open(d+"/final.c").read()), want)
# The harness judges a project on ALL its files as one text (cli._project_text ==
# bench.project_text): since D6 the timer and the digest live in pb_harness.h, not in the
# kernel file, so the cases below edit the same text the harness would see.
import bench  # noqa: E402
_sd = Path(f"{R}/prepared/polybench/seidel-2d")
src = bench.project_text(_sd, bench.load_meta(_sd))
moved = src.replace("  pb_timer_stop();\n", "", 1).replace("  pb_timer_start();\n", "  pb_timer_start();\n  pb_timer_stop();\n", 1)
expect("timer stop moved before the kernel call", S.check(src, moved), False)
expect("timer body edited", S.check(src, src.replace("CLOCK_MONOTONIC", "CLOCK_REALTIME", 1)), False)
expect("perturbation removed", S.check(src, re.sub(r"\n\s*PB_PERTURB\(A[^\n]*", "", src, 1)), False)
expect("digest edited", S.check(src, src.replace("% 9973", "% 9967", 1)), False)
expect("comment edited", S.check(src, src.replace("/* Run kernel. */", "/* Run the kernel now. */", 1)), True)
k = src.index("void kernel_seidel_2d"); body = src.index("for", k)
expect("pragma in kernel", S.check(src, src[:body] + "#pragma omp parallel for\n  " + src[body:]), True)
call = "  kernel_seidel_2d (tsteps, n, POLYBENCH_ARRAY(A));\n"
assert call in src
inline = "  {\n    int t, i, j;\n    for (t = 0; t < tsteps; t++)\n      for (i = 1; i <= n - 2; i++)\n        (*A)[i][1] = 0.5 * (*A)[i][1];\n  }\n"
expect("kernel inlined INSIDE the timer", S.check(src, src.replace(call, inline, 1)), True)
out = src.replace(call, "", 1).replace("  pb_timer_start();\n", inline + "  pb_timer_start();\n", 1)
expect("kernel inlined BEFORE the timer (moved out)", S.check(src, out), False)
before = "  {\n    int t, j;\n    for (t = 0; t < tsteps; t++)\n      for (j = 1; j <= n - 2; j++)\n        (*A)[1][j] = 0.25 * (*A)[1][j];\n  }\n"
inside = "  {\n    int i;\n    for (i = 1; i <= n - 2; i++)\n      (*A)[i][1] = 0.5 * (*A)[i][1];\n  }\n"
expect("part of the computation moved before the timer", S.check(src, src.replace(call, inside, 1).replace("  pb_timer_start();\n", before + "  pb_timer_start();\n", 1)), False)
expect("timed region emptied", S.check(src, src.replace(call, "  ;\n", 1)), False)
for app in ["burkardt/md", "rodinia-3.1/pathfinder", "npb/mg", "npb/lu", "npb/is", "rodinia-3.1/hotspot", "rodinia-3.1/nw"]:
    # the unit holding main and the harness code (a project since D6: NPB is `<B>/<b>.cpp`)
    f = f"{R}/prepared/{app}/" + json.load(open(f"{R}/prepared/{app}/meta.json"))["file"]; t = open(f).read()
    m_start = re.search(r"\n[ \t]*pb_timer_start\s*\(\s*\)\s*;", t)
    assert m_start is not None, f"{app}: no pb_timer_start"
    a = m_start.end()
    m_stop = re.search(r"\n[ \t]*pb_timer_stop\s*\(\s*\)\s*;", t[a:])
    assert m_stop is not None, f"{app}: no pb_timer_stop"
    b = m_stop.start() + a
    win = t[a:b]; m = re.search(r"\n([ \t]*)for\s*\(", win)
    if m:
        expect(f"{app} pragma in computation window", S.check(t, t[:a] + win[:m.start()] + "\n" + m.group(1) + "#pragma omp parallel for" + win[m.start():] + t[b:]), True)
    stop = m_stop.group(0)
    expect(f"{app} timer stop moved to window start", S.check(t, t[:a] + stop + win + "\n  (void)0;" + t[b + len(stop):]), False)

# How a trial counts in the statistics (main_comparison_stats.py; record §6, 25 Sep). A harness
# edit is its own row and never unusable, even when its program does not build (E2's twin_full
# s331 rep 4 was counted "did not compile"); a rewrite with no pragma has a verdict, and is
# unusable when it runs slower than the original (E2's twin_full s244 rep 1, 0.63×).
print("\ncounting")
import main_comparison_stats as M  # noqa: E402
def holds(label, cond):
    global fails
    fails += not cond
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
NOBUILD = {"status": "verify_build_failed", "build_errors": {"final_dump": "e", "final_par": "e"}}
def trial(outcome, speedup=None, verify=None, rep=1, arm="twin_full"):
    v = dict(verify or {"status": "ok"})
    if speedup is not None:
        v["par"] = {"6": {"speedup": speedup}}
    return {"arm": arm, "benchmark": "tsvc/s244", "repeat": rep, "outcome": outcome, "verify": v}
holds("harness edit that does not build: no verdict", not M._with_verdict(trial("SCAFFOLD_MODIFIED", verify=NOBUILD)))
holds("harness edit that builds: no verdict", not M._with_verdict(trial("SCAFFOLD_MODIFIED", 1.5)))
holds("changed, not parallel: a verdict", M._with_verdict(trial("changed-not-parallel", 1.04)))
holds("changed, not parallel, 1.04x: no slowdown", not M._ships_slowdown(trial("changed-not-parallel", 1.04)))
holds("changed, not parallel, 0.63x: a slowdown", M._ships_slowdown(trial("changed-not-parallel", 0.63)))
holds("parallel, 0.8x: a slowdown", M._ships_slowdown(trial("parallel-not-faster", 0.8)))
holds("FASTER: no slowdown", not M._ships_slowdown(trial("FASTER", 2.0)))
holds("unchanged: a verdict, no slowdown", M._with_verdict(trial("no-change")) and not M._ships_slowdown(trial("no-change")))
holds("final program does not build: a verdict", M._with_verdict(trial("VERIFY_FAILED", verify=NOBUILD)))
holds("original does not build: no verdict", not M._with_verdict(
    trial("VERIFY_FAILED", verify={"status": "verify_build_failed", "build_errors": {"orig_dump": "e"}})))
holds("agent error: no verdict", not M._with_verdict(trial("AGENT_ERROR")))
tw = M.three_way([trial("FASTER", 2.0, rep=1), trial("SCAFFOLD_MODIFIED", verify=NOBUILD, rep=2),
                  trial("changed-not-parallel", 0.63, rep=3), trial("no-change", arm="default"),
                  trial("no-change", arm="discopop_gate")], "default", "twin_full")
got = tw["classes"]["R"]["arms"]["model alone"] if "R" in tw["classes"] else {}
holds("three-way: 2 with a verdict, 1 harness edit, 1 unusable (the slow rewrite), 0 not compiling",
      (got.get("with_verdict"), got.get("tampered"), got.get("unusable"), got.get("did_not_compile")) == (2, 1, 1, 0))
# 3 Oct (the author): a harness edit is redone by the runner; one that survives every redo
# (`harness_edit_redos` recorded) is counted, as unusable — older trials keep their rule.
kept = dict(trial("SCAFFOLD_MODIFIED", 1.5, rep=4), harness_edit_redos=[{"attempt": 1}, {"attempt": 2}])
holds("harness edit after every redo: a verdict, not tampered", M._with_verdict(kept) and not M._tampered(kept))
holds("harness edit from before 3 Oct: still its own row", M._tampered(trial("SCAFFOLD_MODIFIED", 1.5)))
tw = M.three_way([trial("FASTER", 2.0, rep=1), kept, trial("no-change", arm="default"),
                  trial("no-change", arm="discopop_gate")], "default", "twin_full")
got = tw["classes"]["R"]["arms"]["model alone"] if "R" in tw["classes"] else {}
holds("three-way: the kept harness edit is unusable and in the denominator",
      (got.get("with_verdict"), got.get("tampered"), got.get("unusable"), got.get("measurement_kept_edited")) == (2, 0, 1, 1))
# 8 Oct: one kernel file in two packagings (--same-loop). The agent ran `s241` again on `tsvc_c3`, the models
# alone ran it on `tsvc_c2` only; the three-way comparison takes its benchmarks from the model alone.
def on(bench, arm, rep, outcome="FASTER", run="r"):
    return {"arm": arm, "benchmark": bench, "repeat": rep, "outcome": outcome, "run_id": run,
            "verify": {"status": "ok", "par": {"6": {"speedup": 2.0}}}}
def two_packagings():
    return ([on("tsvc_c3/s241", "default", r, run="agent") for r in (1, 2)] + [on("tsvc_c3/s241", "discopop_gate", 1, "no-change", "agent")]
            + [on("tsvc_c2/s241", "bare", r, run="alone") for r in (1, 2)])
SAME = M.same_loop_map(["tsvc_c2/s241=tsvc_c3/s241"])
tw = M.three_way(two_packagings(), "default", "bare")
got = tw["classes"]["R"]["per_benchmark"] if "R" in tw["classes"] else {}
holds("two packagings, not named the same loop: the agent's trials are left out of the model alone's row",
      list(got) == ["tsvc_c2/s241"] and not got["tsvc_c2/s241"]["DiscoPoP + agent"]["n"])
with tempfile.TemporaryDirectory() as tmp:
    rf = Path(tmp) / "results.jsonl"
    rf.write_text(json.dumps({"trial": "E/runs/alone/benchmarks/tsvc_c2/s241/bare/m/rep1", "benchmark": "tsvc_c2/s241",
                              "arm": "bare", "repeat": 1, "verdict": "clean"}) + "\n"
                  + json.dumps({"trial": "E/runs/alone/benchmarks/tsvc_c2/s241/bare/m/rep2", "benchmark": "tsvc_c2/s241",
                                "arm": "bare", "repeat": 2, "verdict": "tsan"}) + "\n")
    races = M.load_races([rf], SAME)
renamed = [M.count_as(t, SAME) for t in two_packagings()]
tw = M.three_way(renamed, "default", "bare", races)
got = tw["classes"]["R"]["per_benchmark"] if "R" in tw["classes"] else {}
row = got.get("tsvc_c3/s241", {})
holds("two packagings named the same loop: one row, every setup in it",
      list(got) == ["tsvc_c3/s241"] and (row["DiscoPoP alone"]["n"], row["DiscoPoP + agent"]["n"], row["model alone"]["n"]) == (1, 2, 2))
holds("... and the model alone's race verdicts follow the rename (1 clean, 1 racy)",
      (row["model alone"]["faster_race_free"], row["model alone"]["unusable"]) == (1, 1))
holds("... and the package a trial ran on stays in its record",
      {t.get("benchmark_as_run") for t in renamed if t["arm"] == "bare"} == {"tsvc_c2/s241"}
      and all("benchmark_as_run" not in t for t in renamed if t["arm"] != "bare"))
# The agent's model-only arms check with the judge's rules: a byte-identical copy (gate/harness_guard.py).
HERE = Path(__file__).resolve().parent
AGENT_COPY = HERE.parents[2] / "discopop_agent" / "gate" / "scaffold.py"
holds("discopop_agent/gate/scaffold.py is this scaffold.py, byte for byte",
      AGENT_COPY.exists() and AGENT_COPY.read_bytes() == (HERE / "scaffold.py").read_bytes())
print("\nFAILURES:", fails)
sys.exit(1 if fails else 0)
